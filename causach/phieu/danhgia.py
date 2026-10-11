"""Evaluation of the Phiếu Cầu generator and, separately, of its checker.

1. Generation (`run_generation`)
   Every lesson, several samples, with the repair loop on. Round 0 of each run
   IS the one-shot result, so one batch gives both "one-shot" and "after
   repair" numbers on the same drafts.

2. Planted errors (`offline_mutants`, `online_mutants`)
   The model rarely makes arithmetic mistakes on grade-6 material, so "how
   often does the loop fix errors" says little about the checker. Instead we
   take exercises that passed and insert known errors, then count how many
   the checker catches.
   Offline (no model calls, uses the stored independent reading):
       sai_dap_an       final answer changed
       sai_dang         same value, wrong form (128 instead of 2**7, 10/12 …)
       lech_bieu_thuc   a number in the expression changed and the answer
                        recomputed to match, so checks 1–3 all pass
   Online (the model re-reads the edited problem text):
       doi_so_trong_de  a number in the problem text changed; expression and
                        answer left as they were
       them_cau_hoi     a second question appended to the problem
       goc              the original text re-read; anything flagged here is a
                        false alarm

3. Human review (`export_review_sheet`, `summarize_review`)
   A spreadsheet of sampled exercises with five yes/no criteria the
   machine cannot judge.

`write_report` puts all of it in one Markdown file.
"""
from __future__ import annotations

import ast
import random
import re
from collections import Counter
from pathlib import Path
from typing import Callable

import pandas as pd
import sympy as sp

from .curriculum import Lesson, get_lesson
from .generate import generate, read_problems
from .llm import Model
from .mathcheck import ExpressionError, evaluate, parse
from .render import clean_display, pretty
from .store import Run, load_runs, write_run
from .verify import STATUS_LABELS, check_exercise
from ..vn import fmt_dec, fmt_frac, fmt_int

# USD per 1M tokens (input, output), OpenAI list price checked October 2026.
PRICES = {"gpt-5-mini": (0.25, 2.00)}

SECOND_QUESTION = " Sau đó, hãy tính thêm tổng của kết quả vừa tìm được và 10."

CRITERIA = {
    "tieng_viet_tu_nhien": "Câu chữ tự nhiên, đúng tiếng Việt, hợp với học sinh lớp 6",
    "tinh_huong_hop_li": "Tình huống và số liệu hợp lí (để trống nếu không phải bài có tình huống)",
    "khong_tam_thuong": "Bài có giá trị luyện tập, không hiển nhiên đến mức vô nghĩa",
    "dung_yccd": "Bài thực sự luyện đúng các yêu cầu cần đạt được gắn",
    "loi_giai_hop_lop": "Lời giải đúng và trình bày phù hợp lớp 6",
}


# ---------------------------------------------------------------------------
# 1. Generation
# ---------------------------------------------------------------------------
def run_generation(lessons: list[Lesson], samples: int, model_factory: Callable[[], Model], root: Path,
                   max_rounds: int = 2, log: Callable[[str], None] = print) -> None:
    """Writes root/sinh/<lesson>/lan_<k>/. Existing runs are kept, so an interrupted batch can resume."""
    for lesson in lessons:
        for k in range(1, samples + 1):
            out = Path(root) / "sinh" / lesson.code / f"lan_{k}"
            if (out / "kiem_tra.json").exists():
                log(f"{lesson.code} lần {k}: đã có, bỏ qua")
                continue
            try:
                result = generate(lesson, model_factory(), max_rounds=max_rounds, cross_check=True)
            except Exception as exc:  # keep going; one failed call should not lose the batch
                log(f"{lesson.code} lần {k}: lỗi {type(exc).__name__}: {exc}")
                continue
            write_run(out, lesson, result, cross_check=True, max_rounds=max_rounds)
            log(f"{lesson.code} lần {k}: {' → '.join(result.log)}")


def generation_stats(runs: list[Run]) -> dict:
    first_items = final_items = first_pass = final_pass = 0
    sheets_first = sheets_final = 0
    failures = Counter()
    repaired = failed_first = 0
    calls = tokens_in = tokens_out = 0
    seconds = 0.0
    cost = 0.0
    cost_known = True
    for run in runs:
        rounds = run.record["rounds"]
        first, final = rounds[0], rounds[-1]
        first_items += len(first["items"])
        final_items += len(final["items"])
        first_pass += sum(i["status"] == "dat" for i in first["items"])
        final_pass += sum(i["status"] == "dat" for i in final["items"])
        sheets_first += bool(first.get("passed", _passed(first)))
        sheets_final += bool(final.get("passed", _passed(final)))
        final_status = {i["id"]: i["status"] for i in final["items"]}
        for item in first["items"]:
            if item["status"] != "dat":
                failures[item["status"]] += 1
                failed_first += 1
                repaired += final_status.get(item["id"]) == "dat"
        calls += run.record["calls"]
        tokens_in += run.record["input_tokens"]
        tokens_out += run.record["output_tokens"]
        seconds += run.record["seconds"]
        price = PRICES.get(run.record["model"])
        if price:
            cost += (run.record["input_tokens"] * price[0] + run.record["output_tokens"] * price[1]) / 1e6
        else:
            cost_known = False
    return {
        "worksheets": len(runs), "first_items": first_items, "final_items": final_items,
        "first_pass": first_pass, "final_pass": final_pass,
        "sheets_first": sheets_first, "sheets_final": sheets_final,
        "failures": failures, "failed_first": failed_first, "repaired": repaired,
        "calls": calls, "tokens_in": tokens_in, "tokens_out": tokens_out, "seconds": seconds,
        "cost": cost if cost_known else None,
        "unfinished": [
            (f"{r.lesson}/{r.path.name}", r.record["rounds"][-1]["summary"])
            for r in runs if not r.record["rounds"][-1].get("passed", _passed(r.record["rounds"][-1]))
        ],
        "models": sorted({r.record["model"] for r in runs}),
        "prompt_versions": sorted({r.record["prompt_version"] for r in runs}),
    }


def _passed(round_record: dict) -> bool:
    return (all(i["status"] == "dat" for i in round_record["items"])
            and not round_record.get("missing") and not round_record.get("structure_errors"))


# ---------------------------------------------------------------------------
# 2. Planted errors
# ---------------------------------------------------------------------------
def format_answer(kind: str, value: sp.Rational, original_answer: str) -> str | None:
    """Write `value` in the form an exercise of this kind requires, or None if impossible."""
    if kind == "so_nguyen":
        return str(value) if value.q == 1 else None
    if kind in ("gia_tri", "phan_so_toi_gian"):
        return str(value)                                   # sympy prints 7/12 or 5
    if kind == "mot_luy_thua":
        node = parse(original_answer)
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow)):
            return None
        base = evaluate(ast.unparse(node.left))
        if value.q != 1 or base.q != 1 or base < 2 or value < 1:
            return None
        for exponent in range(0, 65):
            if base ** exponent == value:
                return f"{base}**{exponent}"
            if base ** exponent > value:
                break
        return None
    if kind == "phan_tich_nguyen_to":
        if value.q != 1 or value < 2:
            return None
        return "*".join(f"{p}**{k}" if k > 1 else f"{p}" for p, k in sorted(sp.factorint(int(value)).items()))
    return None


def mutate_answer(ex: dict) -> dict | None:
    """Change the final answer; the expression stays correct. Check 3 should catch it."""
    kind, value = ex["kieu"], evaluate(ex["bieu_thuc"])
    if kind == "phan_so_toi_gian":
        p, q = int(value.p), int(value.q)
        k = 1
        while sp.gcd(p + k, q) != 1 or p + k == 0:
            k += 1
        new = f"{p + k}/{q}" if q != 1 else str(p + k)
    elif kind == "mot_luy_thua":
        node = parse(ex["dap_an"])
        new = f"{ast.unparse(node.left)}**{int(evaluate(ast.unparse(node.right))) + 1}"
    else:
        new = format_answer(kind, value * 2 if kind == "phan_tich_nguyen_to" else value + 1, ex["dap_an"])
    return None if new is None else {**ex, "dap_an": new}


def mutate_form(ex: dict) -> dict | None:
    """Same value, wrong form. Check 2 should catch it."""
    kind, value = ex["kieu"], evaluate(ex["bieu_thuc"])
    if kind == "mot_luy_thua" and value.q == 1:
        return {**ex, "dap_an": str(value)}
    if kind == "phan_so_toi_gian" and value.q != 1:
        return {**ex, "dap_an": f"{2 * value.p}/{2 * value.q}"}
    if kind == "phan_tich_nguyen_to" and value.q == 1 and not sp.isprime(int(value)):
        return {**ex, "dap_an": str(value)}
    if kind == "so_nguyen" and value.q == 1:
        return {**ex, "dap_an": f"{value}.0"}
    return None


def _int_literals(expression: str) -> list[ast.Constant]:
    return [n for n in ast.walk(parse(expression))
            if isinstance(n, ast.Constant) and type(n.value) is int and n.value >= 2]


def _replace_literal(expression: str, index: int, new_value: int) -> str:
    tree = parse(expression)
    literals = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and type(n.value) is int and n.value >= 2]
    literals[index].value = new_value
    return ast.unparse(tree)


def mutate_expression(ex: dict) -> dict | None:
    """Change a number in the expression and recompute the answer so checks 1–3 still pass.

    The problem text is untouched, so only the independent reading (check 4) can notice.
    """
    original = evaluate(ex["bieu_thuc"])
    for i, literal in enumerate(_int_literals(ex["bieu_thuc"])):
        try:
            new_expr = _replace_literal(ex["bieu_thuc"], i, literal.value + 1)
            new_value = evaluate(new_expr)
        except ExpressionError:
            continue
        if new_value == original:
            continue
        answer = format_answer(ex["kieu"], new_value, ex["dap_an"])
        if answer is None:
            continue
        mutated = {**ex, "bieu_thuc": new_expr, "dap_an": answer}
        if check_exercise(mutated).status == "dat":   # must pass checks 1–3 to be a fair test of check 4
            return mutated
    return None


def mutate_text_number(ex: dict) -> str | None:
    """Change one number in the problem text that also appears in the expression, if that changes the result."""
    original = evaluate(ex["bieu_thuc"])
    for i, literal in enumerate(_int_literals(ex["bieu_thuc"])):
        pattern = re.compile(rf"(?<![\d,.])(?<!\d\s){literal.value}(?![\d,.])(?!\s\d{{3}}(?!\d))")
        matches = list(pattern.finditer(ex["de_bai"]))
        # Only edit numbers that appear once: in "12 hộp … mua 12 hộp" changing the
        # first 12 does not change what is asked, so it would not be a real error.
        if len(matches) != 1:
            continue
        match = matches[0]
        try:
            if evaluate(_replace_literal(ex["bieu_thuc"], i, literal.value + 1)) == original:
                continue
        except ExpressionError:
            continue
        return ex["de_bai"][:match.start()] + str(literal.value + 1) + ex["de_bai"][match.end():]
    return None


OFFLINE_OPERATORS = {"sai_dap_an": mutate_answer, "sai_dang": mutate_form, "lech_bieu_thuc": mutate_expression}


def _eligible(run: Run):
    """Exercises that passed in the final round and have a stored independent reading."""
    final = {i["id"]: i["status"] for i in run.record["rounds"][-1]["items"]}
    readings = run.record.get("doc_lap", {})
    for ex in run.worksheet["bai_tap"]:
        if final.get(ex["id"]) == "dat" and ex["id"] in readings:
            yield ex, readings[ex["id"]]


def offline_mutants(runs: list[Run]) -> pd.DataFrame:
    rows = []
    for run in runs:
        for ex, reading in _eligible(run):
            for name, operator in OFFLINE_OPERATORS.items():
                mutated = operator(ex)
                if mutated is None:
                    continue
                with_check4 = check_exercise(mutated, reading, require_independent=True).status
                without = check_exercise(mutated).status
                rows.append({"lesson": run.lesson, "run": run.path.name, "id": ex["id"], "loai_loi": name,
                             "kieu": ex["kieu"], "trang_thai": with_check4, "trang_thai_khong_lop4": without})
    return pd.DataFrame(rows, columns=["lesson", "run", "id", "loai_loi", "kieu", "trang_thai", "trang_thai_khong_lop4"])


def online_mutants(runs: list[Run], model: Model, log: Callable[[str], None] = print) -> tuple[pd.DataFrame, dict]:
    rows, usage = [], {"calls": 0, "input_tokens": 0, "output_tokens": 0}
    for run in runs:
        batch, cases = [], []
        for ex, _ in _eligible(run):
            variants = {"goc": ex["de_bai"], "them_cau_hoi": ex["de_bai"] + SECOND_QUESTION}
            changed = mutate_text_number(ex)
            if changed:
                variants["doi_so_trong_de"] = changed
            for name, text in variants.items():
                key = f"{ex['id']}.{name}"
                batch.append({"id": key, "de_bai": text})
                cases.append((key, name, ex))
        if not batch:
            continue
        def call(system, user, schema, name):
            data, used = model.complete_json(system, user, schema, name)
            usage["calls"] += 1
            usage["input_tokens"] += used.get("input_tokens", 0)
            usage["output_tokens"] += used.get("output_tokens", 0)
            return data

        readings = read_problems(batch, call)
        for key, name, ex in cases:
            status = check_exercise(ex, readings.get(key), require_independent=True).status
            rows.append({"lesson": run.lesson, "run": run.path.name, "id": ex["id"], "loai_loi": name,
                         "kieu": ex["kieu"], "doc_lai": readings.get(key), "trang_thai": status})
        log(f"{run.lesson}/{run.path.name}: đọc lại {len(batch)} đề")
    return pd.DataFrame(rows, columns=["lesson", "run", "id", "loai_loi", "kieu", "doc_lai", "trang_thai"]), usage


# ---------------------------------------------------------------------------
# 3. Human review
# ---------------------------------------------------------------------------
def export_review_sheet(runs: list[Run], path: Path, n: int = 20, seed: int = 0) -> int:
    pool = []
    for run in runs:
        lesson = get_lesson(run.lesson)
        texts = {r.code: r.text for r in lesson.requirements}
        final = {i["id"]: i["status"] for i in run.record["rounds"][-1]["items"]}
        for ex in run.worksheet["bai_tap"]:
            pool.append({
                "ma_bai": run.lesson, "lan": run.path.name, "id": ex["id"],
                "yccd": "; ".join(f"{c}: {texts.get(c, '?')}" for c in ex.get("yccd", [])),
                "de_bai": clean_display(ex["de_bai"]), "loi_giai": clean_display(ex["loi_giai"]),
                "dap_an": pretty(ex["dap_an"]), "may_kiem_tra": STATUS_LABELS.get(final.get(ex["id"]), "?"),
                **{c: "" for c in CRITERIA}, "ghi_chu": "", "nguoi_duyet": "", "y_kien_nguoi_duyet": "",
            })
    sample = random.Random(seed).sample(pool, min(n, len(pool)))
    guide = pd.DataFrame({"cot": list(CRITERIA), "y_nghia": list(CRITERIA.values())})
    guide.loc[len(guide)] = ["cách điền", "Chọn trong danh sách: Đạt, Không đạt, Không áp dụng. "
                                          "Mỗi lần chọn Không đạt, ghi lí do ở cột ghi_chu."]
    guide.loc[len(guide)] = ["nguoi_duyet", "Tên người chấm. Nếu do mô hình AI chấm thì ghi rõ tên mô hình."]
    guide.loc[len(guide)] = ["y_kien_nguoi_duyet", "Khi duyệt lại điểm của người khác hoặc của AI: ghi "
                                                    "'đồng ý' hoặc 'không đồng ý: <lí do>'."]
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(sample)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="danh_gia", index=False)
        guide.to_excel(writer, sheet_name="huong_dan", index=False)
        _add_dropdowns(writer.book["danh_gia"], frame)
    return len(sample)


def _add_dropdowns(sheet, frame: pd.DataFrame) -> None:
    """Đạt / Không đạt / Không áp dụng lists instead of free 1/0, so a column cannot be misread."""
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    choice = DataValidation(type="list", formula1='"Đạt,Không đạt,Không áp dụng"', allow_blank=True)
    sheet.add_data_validation(choice)
    for name in CRITERIA:
        letter = get_column_letter(frame.columns.get_loc(name) + 1)
        choice.add(f"{letter}2:{letter}{len(frame) + 1}")


_MARKS = {"1": 1, "1.0": 1, "đạt": 1, "0": 0, "0.0": 0, "không đạt": 0}


def _mark(value):
    """1 / 0 / None from either 1-0 numbers or the dropdown words; 'Không áp dụng' and blanks are None."""
    if value is None or (isinstance(value, float) and value != value):
        return None
    return _MARKS.get(str(value).strip().lower())


def summarize_review(path: Path) -> pd.DataFrame | None:
    if not Path(path).exists():
        return None
    sheet = pd.read_excel(path, sheet_name="danh_gia")
    marks = pd.DataFrame({c: sheet[c].map(_mark) for c in CRITERIA}, dtype="float")
    rows = [{"tieu_chi": meaning, "dat": int((marks[c] == 1).sum()), "khong_dat": int((marks[c] == 0).sum())}
            for c, meaning in CRITERIA.items()]
    reviewed = marks.notna().any(axis=1)
    failed = (marks == 0).any(axis=1) & reviewed
    table = pd.DataFrame(rows)
    table.attrs["reviewed"] = int(reviewed.sum())
    table.attrs["any_fail"] = int(failed.sum())
    reviewers = sheet["nguoi_duyet"].dropna().astype(str).str.strip() if "nguoi_duyet" in sheet else pd.Series(dtype=str)
    table.attrs["reviewers"] = sorted({r for r in reviewers if r})
    opinions = (sheet["y_kien_nguoi_duyet"].dropna().astype(str).str.strip().str.lower()
                if "y_kien_nguoi_duyet" in sheet else pd.Series(dtype=str))
    disagree = opinions.str.startswith("không đồng ý")
    table.attrs["disagree"] = int(disagree.sum())
    table.attrs["disagreements"] = [
        (f"{sheet.loc[i, 'ma_bai']}/{sheet.loc[i, 'lan']}/{sheet.loc[i, 'id']}",
         str(sheet.loc[i, "y_kien_nguoi_duyet"]).strip())
        for i in opinions.index[disagree]
    ]
    table.attrs["agree"] = int((opinions.str.startswith("đồng ý") & ~disagree).sum())
    notes = sheet.get("ghi_chu", pd.Series([""] * len(sheet))).fillna("").astype(str)
    table.attrs["issues"] = [
        (f"{sheet.loc[i, 'ma_bai']}/{sheet.loc[i, 'lan']}/{sheet.loc[i, 'id']}", notes[i])
        for i in sheet.index[failed] if notes[i].strip()
    ]
    return table


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def _pct(a: int, b: int) -> str:
    return fmt_frac(a, b)


def write_report(root: Path) -> Path:
    root = Path(root)
    runs = load_runs(root / "sinh")
    lines = ["# Báo cáo đánh giá bộ sinh Phiếu Cầu", ""]

    lines += ["## 1. Sinh phiếu", ""]
    if runs:
        g = generation_stats(runs)
        lines += [
            f"{g['worksheets']} phiếu; mô hình: {', '.join(g['models'])}; phiên bản câu lệnh: {', '.join(g['prompt_versions'])}.",
            "Vòng 0 là kết quả soạn một lần; cột bên phải là sau tối đa 2 vòng sửa.", "",
            "| Chỉ số | Soạn một lần | Sau vòng sửa |", "|---|---|---|",
            f"| Bài tập đạt cả bốn lớp kiểm tra | {_pct(g['first_pass'], g['first_items'])} | {_pct(g['final_pass'], g['final_items'])} |",
            f"| Phiếu đạt hoàn toàn | {_pct(g['sheets_first'], g['worksheets'])} | {_pct(g['sheets_final'], g['worksheets'])} |",
            "",
        ]
        if g["failures"]:
            system = g["failures"].get("loi_doc_lai", 0)
            lines += ["Lỗi ở vòng 0:", "", "| Loại | Số bài |", "|---|---|"]
            lines += [f"| {STATUS_LABELS.get(k, k)} | {v} |" for k, v in g["failures"].most_common()]
            lines += ["", f"Trong {g['failed_first']} bài lỗi ở vòng 0, {system} là lỗi của bước đọc lại (hệ thống), "
                      f"{g['failed_first'] - system} là lỗi nội dung của bài. "
                      f"Sau vòng sửa, {_pct(g['repaired'], g['failed_first'])} bài này đạt.", ""]
        else:
            lines += ["Không có bài nào bị đánh lỗi ở vòng 0.", ""]
        if g["final_items"] != g["first_items"]:
            lines += [f"Vòng sửa thêm {g['final_items'] - g['first_items']} bài tập mới để phủ yêu cầu cần đạt còn thiếu.", ""]
        if g["unfinished"]:
            lines += ["Phiếu chưa đạt hoàn toàn sau vòng sửa:", ""]
            lines += [f"- {name}: {summary}" for name, summary in g["unfinished"]]
            lines.append("")
        cost = (f"khoảng {fmt_dec(g['cost'], 3)} USD tổng, {fmt_dec(g['cost'] / g['worksheets'] * 100, 2)} cent mỗi phiếu"
                if g["cost"] is not None else "không rõ giá của mô hình")
        lines += [f"Chi phí: {fmt_int(g['calls'])} lần gọi, {fmt_int(g['tokens_in'])} token vào, {fmt_int(g['tokens_out'])} token ra; "
                  f"{cost} theo giá niêm yết của OpenAI. Thời gian trung bình {fmt_int(g['seconds'] / g['worksheets'])} giây mỗi phiếu.", ""]
    else:
        lines += ["Chưa có dữ liệu. Chạy `python -m causach danhgia sinh`.", ""]

    lines += ["## 2. Thử bộ kiểm tra bằng lỗi cài sẵn", "",
              "Lấy các bài đã đạt, cài một lỗi đã biết, rồi xem bộ kiểm tra có bắt được không.", ""]
    offline_path, online_path = root / "gay_loi" / "offline.csv", root / "gay_loi" / "online.csv"
    if offline_path.exists() or online_path.exists():
        lines += ["| Loại lỗi cài | Số ca | Bắt được (đủ 4 lớp) | Bắt được (bỏ lớp 4) |", "|---|---|---|---|"]
        names = {"sai_dap_an": "Đổi đáp án", "sai_dang": "Đúng giá trị, sai dạng",
                 "lech_bieu_thuc": "Đổi số trong biểu thức, đáp án tính lại cho khớp",
                 "doi_so_trong_de": "Đổi số trong đề (mô hình đọc lại)",
                 "them_cau_hoi": "Thêm câu hỏi thứ hai vào đề (mô hình đọc lại)"}
        if offline_path.exists():
            off = pd.read_csv(offline_path)
            for name in ["sai_dap_an", "sai_dang", "lech_bieu_thuc"]:
                part = off[off["loai_loi"] == name]
                lines.append(f"| {names[name]} | {len(part)} | {_pct(int((part['trang_thai'] != 'dat').sum()), len(part))} | "
                             f"{_pct(int((part['trang_thai_khong_lop4'] != 'dat').sum()), len(part))} |")
        if online_path.exists():
            on = pd.read_csv(online_path)
            for name in ["doi_so_trong_de", "them_cau_hoi"]:
                part = on[on["loai_loi"] == name]
                lines.append(f"| {names[name]} | {len(part)} | {_pct(int((part['trang_thai'] != 'dat').sum()), len(part))} | — |")
            control = on[on["loai_loi"] == "goc"]
            added = on[on["loai_loi"] == "them_cau_hoi"]
            lines += ["", f"Báo nhầm khi đọc lại đề gốc (không cài lỗi): {_pct(int((control['trang_thai'] != 'dat').sum()), len(control))}.", "",
                      f"Với câu hỏi thêm vào: {int((added['trang_thai'] == 'nhieu_y').sum())} ca được nhận ra là đề hỏi nhiều ý; "
                      f"{int((added['trang_thai'] == 'khong_khop_de').sum())} ca bị bắt vì mô hình tính luôn câu hỏi thứ hai nên giá trị đổi."]
            usage_path = root / "gay_loi" / "online_usage.json"
            if usage_path.exists():
                import json as _json
                u = _json.loads(usage_path.read_text(encoding="utf-8"))
                lines.append(f"Phần đọc lại tốn {fmt_int(u['calls'])} lần gọi, {fmt_int(u['input_tokens'] + u['output_tokens'])} token.")
        lines += ["", "Ba hàng đầu không gọi mô hình. Hàng thứ ba dùng lần đọc lại đã lưu của đề gốc, nên nó cho thấy "
                  "lớp 4 là lớp duy nhất bắt được loại lỗi này, chứ không đo khả năng đọc của mô hình. "
                  "Hai hàng sau mới đo khả năng đó, vì mô hình phải đọc lại đề đã bị sửa.", ""]
    else:
        lines += ["Chưa có dữ liệu. Chạy `python -m causach danhgia gay-loi`.", ""]

    review = summarize_review(root / "thu_cong.xlsx")
    reviewers = review.attrs.get("reviewers", []) if review is not None else []
    by_ai = any(re.search(r"\b(ai|claude|gpt|mô hình)\b", r, re.IGNORECASE) for r in reviewers)
    checked = (review.attrs["agree"] + review.attrs["disagree"]) if review is not None else 0
    title = "## 3. Duyệt nội dung"
    if by_ai:
        title += " (AI chấm trước, người duyệt lại)" if checked else " (do AI chấm, chưa có người duyệt lại)"
    lines += [title, ""]
    if review is not None and review.attrs["reviewed"]:
        lines.append(f"Người chấm: {', '.join(reviewers) if reviewers else 'không ghi'}.")
        if by_ai and not checked:
            lines.append("Đây là đánh giá của một mô hình AI, **không phải duyệt thủ công**. Mô hình chấm bài do mô hình "
                         "khác viết có thể bỏ sót hoặc chấm lệch; mỗi nhận xét cần người duyệt lại.")
        if checked:
            lines.append(f"Người duyệt lại đã xem {checked} dòng và đồng ý với {review.attrs['agree']}. "
                         "Bảng dưới đây là điểm sau khi duyệt lại.")
            if review.attrs["disagreements"]:
                lines += ["", "Các dòng người duyệt không đồng ý:", ""]
                lines += [f"- {name}: {opinion}" for name, opinion in review.attrs["disagreements"]]
        lines += ["", f"{review.attrs['reviewed']} bài được chấm; {_pct(review.attrs['any_fail'], review.attrs['reviewed'])} "
                  "có ít nhất một tiêu chí không đạt.", "", "| Tiêu chí | Đạt | Không đạt |", "|---|---|---|"]
        lines += [f"| {r.tieu_chi} | {r.dat} | {r.khong_dat} |" for r in review.itertuples()]
        if review.attrs["issues"]:
            lines += ["", "Các vấn đề được ghi lại:", ""]
            lines += [f"- {name}: {note}" for name, note in review.attrs["issues"]]
        lines.append("")
    else:
        lines += ["Chưa có dữ liệu. Chạy `python -m causach danhgia mau-thu-cong`, điền tệp `thu_cong.xlsx`, rồi tổng hợp lại.", ""]

    lines += ["## Giới hạn", "",
              "- Số phiếu và số bài còn nhỏ; tỷ lệ chỉ nên đọc như ước lượng thô.",
              "- Lỗi cài sẵn là lỗi nhân tạo; lỗi thật của mô hình có thể khác.",
              "- Bước đọc lại đề dùng cùng mô hình với bước soạn, nên hai lần có thể sai giống nhau.",
              ("- Phần 3: AI chấm trước, một người duyệt lại; nên có thêm giáo viên duyệt độc lập." if by_ai and checked
               else "- Phần 3 do AI chấm; cần người, tốt nhất là giáo viên, duyệt lại từng nhận xét." if by_ai
               else "- Phần 3 do một người chấm; nên có thêm giáo viên duyệt độc lập."), ""]
    path = root / "bao_cao.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
