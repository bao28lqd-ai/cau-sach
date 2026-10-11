"""Logic behind the Streamlit app (app.py), kept free of Streamlit so it can be tested."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .baselines import GREEDY_C_FIRST, GREEDY_SCHOOL_FIRST, greedy_nearest, no_coordination
from .data import District, Problem, build_problem
from .metrics import evaluate
from .model import Plan, Settings
from .optimize import solve
from .phieu.curriculum import Lesson
from .phieu.generate import read_problems
from .phieu.prompts import PROMPT_VERSION
from .phieu.render import clean_display, pretty, student_markdown, teacher_markdown
from .phieu.verify import STATUS_LABELS, Report, verify

MILP = "Tối ưu (MILP)"


# ---------------------------------------------------------------------------
# Book allocation
# ---------------------------------------------------------------------------
def run_allocation(district: District, settings: Settings, seed: int = 0) -> dict:
    problem = build_problem(district)
    plans = {
        "Không điều phối": no_coordination(problem),
        GREEDY_SCHOOL_FIRST: greedy_nearest(problem, settings, seed=seed, c_first=False),
        GREEDY_C_FIRST: greedy_nearest(problem, settings, seed=seed, c_first=True),
        MILP: solve(problem, settings),
    }
    stats = {name: evaluate(problem, plan, settings) for name, plan in plans.items()}
    return {"problem": problem, "plans": plans, "stats": stats}


def school_summary(problem: Problem, plan: Plan) -> pd.DataFrame:
    sent = np.zeros(len(problem.schools), dtype=int)
    received = np.zeros(len(problem.schools), dtype=int)
    for (s, d, _), copies in plan.flows.items():
        if s != d:
            sent[s] += copies
            received[d] += copies
    return pd.DataFrame({
        "Trường": problem.schools,
        "Em Luồng C cần sách": problem.need_c.sum(axis=1),
        "Được nhận sách": plan.covered_c.sum(axis=1),
        "Còn lại": problem.need_c.sum(axis=1) - plan.covered_c.sum(axis=1),
        "Sách gửi đi": sent,
        "Sách nhận về": received,
    })


# ---------------------------------------------------------------------------
# Worksheet review
# ---------------------------------------------------------------------------
def exercise_table(worksheet: dict, report: Report, unread: set[str] | None = None) -> pd.DataFrame:
    """One row per exercise for the teacher's review screen."""
    unread = unread or set()
    checks = report.by_id()
    rows = []
    for ex in worksheet["bai_tap"]:
        check = checks.get(ex["id"])
        if ex["id"] in unread:
            status = "Đề đã sửa, chưa đối chiếu lại"
        elif check is None:
            status = "Chưa kiểm tra"
        else:
            status = STATUS_LABELS.get(check.status, check.status)
            if check.message:
                status += f": {check.message}"
        rows.append({
            "Giữ": True, "Mã": ex["id"], "YCCĐ": ", ".join(ex.get("yccd", [])),
            "Đề": clean_display(ex["de_bai"]), "Lời giải": clean_display(ex["loi_giai"]),
            "Đáp án": pretty(ex["dap_an"]), "Kiểm tra": status,
        })
    return pd.DataFrame(rows)


def apply_edits(worksheet: dict, edited: pd.DataFrame) -> tuple[dict, list[str], list[str]]:
    """Apply the teacher's edits. Returns (new worksheet, ids with a changed problem text, removed ids).

    Only wording can be edited here; the machine-readable expression and answer
    stay as checked. If a teacher changes a number in a problem, the
    re-check flags it because the independent reading no longer matches.
    """
    by_id = {row["Mã"]: row for row in edited.to_dict("records")}
    kept, changed, removed = [], [], []
    for ex in worksheet["bai_tap"]:
        row = by_id.get(ex["id"])
        if row is None or not bool(row.get("Giữ", True)):
            removed.append(ex["id"])
            continue
        new = dict(ex)
        if str(row["Đề"]).strip() and str(row["Đề"]).strip() != clean_display(ex["de_bai"]):
            new["de_bai"] = str(row["Đề"]).strip()
            changed.append(ex["id"])
        if str(row["Lời giải"]).strip() and str(row["Lời giải"]).strip() != clean_display(ex["loi_giai"]):
            new["loi_giai"] = str(row["Lời giải"]).strip()
        kept.append(new)
    return {**worksheet, "bai_tap": kept}, changed, removed


def recheck(worksheet: dict, lesson: Lesson, readings: dict[str, tuple[str, str]],
            reader=None) -> tuple[Report, dict[str, tuple[str, str]], set[str]]:
    """Run the checks again after edits.

    readings maps exercise id -> (problem text that was read, independent expression).
    Problems whose text changed are re-read if a model is available; otherwise
    they are reported as not yet re-checked, never as passed.
    """
    readings = dict(readings)
    stale = [ex for ex in worksheet["bai_tap"] if readings.get(ex["id"], ("", ""))[0] != ex["de_bai"]]
    if stale and reader is not None:
        answers = read_problems(stale, lambda system, user, schema, name: reader.complete_json(system, user, schema, name)[0])
        for ex in stale:
            if ex["id"] in answers:
                readings[ex["id"]] = (ex["de_bai"], answers[ex["id"]])
    current = {ex["id"]: readings[ex["id"]][1] for ex in worksheet["bai_tap"]
               if readings.get(ex["id"], ("", ""))[0] == ex["de_bai"]}
    unread = {ex["id"] for ex in worksheet["bai_tap"] if ex["id"] not in current}
    return verify(worksheet, lesson, current), readings, unread


def save_approved(folder: Path, lesson: Lesson, worksheet: dict, report: Report, reviewer: str, *,
                  model: str, changed: list[str], removed: list[str], unread: set[str]) -> Path:
    """Write an approved worksheet to the shared bank (kho_phieu/<lesson>/<timestamp>/)."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = Path(folder) / lesson.code / stamp
    out.mkdir(parents=True, exist_ok=True)
    (out / "phieu.json").write_text(json.dumps(worksheet, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "phieu_hoc_sinh.md").write_text(student_markdown(worksheet, lesson), encoding="utf-8")
    (out / "phieu_giao_vien.md").write_text(teacher_markdown(worksheet, lesson, report, model=model), encoding="utf-8")
    record = {
        "nguoi_duyet": reviewer, "thoi_gian": stamp, "mo_hinh": model, "prompt_version": PROMPT_VERSION,
        "kiem_tra_tu_dong": report.summary(), "bai_sua_de": changed, "bai_bo": removed,
        "chua_doi_chieu_lai": sorted(unread), "giay_phep": "CC BY 4.0",
    }
    (out / "duyet.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
