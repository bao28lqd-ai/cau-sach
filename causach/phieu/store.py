"""Saving and loading generation runs (one folder per worksheet)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .curriculum import Lesson
from .generate import GenerationResult
from .prompts import PROMPT_VERSION
from .render import student_markdown, teacher_markdown


@dataclass
class Run:
    lesson: str
    path: Path
    worksheet: dict
    record: dict


def write_run(out: Path, lesson: Lesson, result: GenerationResult, cross_check: bool, max_rounds: int) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "phieu.json").write_text(json.dumps(result.worksheet, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "phieu_hoc_sinh.md").write_text(student_markdown(result.worksheet, lesson), encoding="utf-8")
    (out / "phieu_giao_vien.md").write_text(
        teacher_markdown(result.worksheet, lesson, result.final, result.log, result.model), encoding="utf-8")
    record = {
        "lesson": lesson.code, "model": result.model, "prompt_version": PROMPT_VERSION,
        "cross_check": cross_check, "max_rounds": max_rounds,
        "calls": result.calls, "input_tokens": result.input_tokens, "output_tokens": result.output_tokens,
        "seconds": round(result.seconds, 2),
        "doc_lap": result.readings,
        "doc_lai_tho": result.reader_log,
        "rounds": [
            {"summary": r.summary(), "passed": r.passed, "missing": r.missing_requirements,
             "structure_errors": r.structure_errors,
             "items": [{"id": i.id, "status": i.status, "message": i.message, "note": i.note} for i in r.items]}
            for r in result.reports
        ],
    }
    (out / "kiem_tra.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def load_runs(root: Path) -> list[Run]:
    runs = []
    for record_path in sorted(Path(root).rglob("kiem_tra.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        worksheet_path = record_path.with_name("phieu.json")
        if not worksheet_path.exists():
            continue
        worksheet = json.loads(worksheet_path.read_text(encoding="utf-8"))
        runs.append(Run(record["lesson"], record_path.parent, worksheet, record))
    return runs
