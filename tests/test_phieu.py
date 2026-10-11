"""Run with `python -m pytest` or, without pytest, `python tests/test_phieu.py`."""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sympy as sp

from causach.phieu import ScriptedModel, generate, get_lesson, load_lessons, verify
from causach.phieu.demo import DRAFT, INDEPENDENT, LESSON, demo_model
from causach.phieu.mathcheck import (ExpressionError, check_prime_factorization, check_reduced_fraction,
                                     check_single_power, evaluate)
from causach.phieu.render import pretty, student_markdown, teacher_markdown
from causach.phieu.verify import check_exercise


def _raises(fn, *args) -> bool:
    try:
        fn(*args)
    except ExpressionError:
        return True
    return False


def test_arithmetic_is_exact():
    assert evaluate("1/3 + 1/6") == sp.Rational(1, 2)
    assert evaluate("0.1 + 0.2") == sp.Rational(3, 10)
    assert evaluate("2^3 · 3") == 24                     # common non-Python spellings are accepted
    assert evaluate("12 : 4") == 3
    assert evaluate("ucln(18, 24, 30)") == 6 and evaluate("bcnn(4, 6)") == 12
    assert evaluate("phan_so(3, 4) * 8") == 6


def test_rounding_is_half_away_from_zero():
    assert evaluate("lam_tron(2.345, 2)") == sp.Rational(235, 100)
    assert evaluate("lam_tron(2.5, 0)") == 3
    assert evaluate("lam_tron(-2.5, 0)") == -3
    assert evaluate("lam_tron(1234, -2)") == 1200


def test_model_output_cannot_run_code():
    for bad in ["__import__('os').system('echo hi')", "open('x')", "(1).__class__", "x + 1",
                "2**1000", "10**30 * 10**30", "1/0", "lam_tron(x=1)", ""]:
        assert _raises(evaluate, bad), bad


def test_answer_form_checks():
    assert check_prime_factorization("2**2*3*5") is None
    assert check_prime_factorization("4*15") is not None
    assert check_prime_factorization("60") is not None
    assert check_single_power("2**7") is None
    assert check_single_power("128") is not None
    assert check_single_power("2**3*2**4") is not None
    assert check_reduced_fraction("7/12") is None and check_reduced_fraction("-3/4") is None
    assert check_reduced_fraction("14/24") is not None


def test_exercise_statuses():
    base = {"id": "B1", "yccd": [], "de_bai": "", "loi_giai": "", "kieu": "gia_tri", "bieu_thuc": "2**5", "dap_an": "32"}
    assert check_exercise(base).status == "dat"
    assert check_exercise({**base, "dap_an": "31"}).status == "sai_dap_an"
    assert check_exercise({**base, "bieu_thuc": "2***5"}).status == "loi_bieu_thuc"
    assert check_exercise({**base, "kieu": "mot_luy_thua"}).status == "sai_dang"
    assert check_exercise(base, independent="2**4").status == "khong_khop_de"
    assert check_exercise(base, independent="2*2*2*2*2").status == "dat"


def test_unchecked_exercises_never_pass_silently():
    # Found in the first real run: a two-part problem ("Tính 4³ và 7²") came back from
    # the independent reader as "4**3;7**2" and used to pass with only a note.
    base = {"id": "B1", "yccd": [], "de_bai": "", "loi_giai": "", "kieu": "gia_tri", "bieu_thuc": "4**3", "dap_an": "64"}
    assert check_exercise(base, independent="4**3;7**2").status == "nhieu_y"
    assert check_exercise(base, independent="NHIEU_Y").status == "nhieu_y"
    assert check_exercise(base, independent="bốn mũ ba").status == "chua_doi_chieu"
    assert check_exercise(base, independent=None, require_independent=True).status == "loi_doc_lai"
    assert check_exercise(base, independent=None, require_independent=False).status == "dat"


def test_missing_independent_reading_fails_the_worksheet():
    report = verify(DRAFT, get_lesson(LESSON), {})          # check 4 on, but no readings came back
    assert report.n_passed == 0 and not report.passed


def test_verifier_finds_the_planted_errors():
    report = verify(DRAFT, get_lesson(LESSON), INDEPENDENT)
    statuses = {c.id: c.status for c in report.items}
    assert statuses["B3"] == "sai_dap_an"
    assert statuses["B6"] == "khong_khop_de"
    assert sum(c.passed for c in report.items) == 4
    assert not report.passed


def test_missing_requirement_is_reported():
    draft = copy.deepcopy(DRAFT)
    draft["bai_tap"] = [ex for ex in draft["bai_tap"] if "T6-02.2" not in ex["yccd"]]
    report = verify(draft, get_lesson(LESSON))
    assert report.missing_requirements == ["T6-02.2"]


def test_repair_loop_fixes_what_one_shot_leaves():
    lesson = get_lesson(LESSON)
    one_shot = generate(lesson, demo_model(), max_rounds=0)
    looped = generate(lesson, demo_model(), max_rounds=2)
    assert one_shot.final.n_passed == 4 and not one_shot.final.passed
    assert looped.final.passed and looped.rounds_used == 1
    # Unchanged problem texts are not re-derived again: draft, check, repair = 3 calls.
    assert looped.calls == 3


def test_without_cross_check_the_mismatch_slips_through():
    result = generate(get_lesson(LESSON), demo_model(), max_rounds=2, cross_check=False)
    b6 = next(ex for ex in result.worksheet["bai_tap"] if ex["id"] == "B6")
    assert result.final.passed and b6["dap_an"] == "6"   # passes, yet the answer is wrong for the problem


def test_rendering():
    lesson = get_lesson(LESSON)
    result = generate(lesson, demo_model(), max_rounds=2)
    student = student_markdown(result.worksheet, lesson)
    teacher = teacher_markdown(result.worksheet, lesson, result.final, result.log)
    assert "Đáp án" not in student and "2**" not in student
    assert "2⁷" in teacher and "CC BY 4.0" in student
    assert pretty("2**2*3*5") == "2² · 3 · 5" and pretty("3.25") == "3,25"


def test_curriculum_file():
    lessons = load_lessons()
    assert len(lessons) == 10
    assert all(len(lesson.requirements) >= 2 for lesson in lessons.values())


# ---- found in the first full evaluation (20 worksheets, gpt-5-mini) ----------------
def test_requirement_codes_are_restricted_to_the_lesson():
    from causach.phieu.curriculum import WORKSHEET_SCHEMA, repair_schema, worksheet_schema
    lesson = get_lesson("T6-09")
    for schema in (worksheet_schema(lesson), repair_schema(lesson)):
        codes = schema["properties"]["bai_tap"]["items"]["properties"]["yccd"]["items"]["enum"]
        assert codes == ["T6-09.1", "T6-09.2"]
    assert "enum" not in WORKSHEET_SCHEMA["properties"]["bai_tap"]["items"]["properties"]["yccd"]["items"]


def test_reader_ids_are_matched_leniently_or_by_position():
    from causach.phieu.generate import read_problems
    items = [{"id": "B1", "de_bai": "Tính 2⁵."}, {"id": "B2", "de_bai": "Tính 3²."}]

    def reply(rows):
        return lambda system, user, schema, name: {"ket_qua": rows}

    bracketed = read_problems(items, reply([{"id": "[B1]", "bieu_thuc": "2**5"}, {"id": "b2.", "bieu_thuc": "3**2"}]))
    assert bracketed == {"B1": "2**5", "B2": "3**2"}
    numbered = read_problems(items, reply([{"id": "1", "bieu_thuc": "2**5"}, {"id": "2", "bieu_thuc": "3**2"}]))
    assert numbered == {"B1": "2**5", "B2": "3**2"}
    assert read_problems(items, reply([])) == {}


def test_a_failed_reading_is_retried_not_rewritten():
    # The reading call returns nothing twice (first attempt and its retry), then works.
    replies = iter([{"ket_qua": []}, {"ket_qua": []}])

    def reader(prompt):
        try:
            return next(replies)
        except StopIteration:
            return {"ket_qua": [{"id": i, "bieu_thuc": INDEPENDENT_OK[i]} for i in re.findall(r"\[(B\d+)\]", prompt)]}

    from causach.phieu.demo import FIXES
    clean = copy.deepcopy(DRAFT)
    clean["bai_tap"] = [FIXES.get(ex["id"], ex) for ex in clean["bai_tap"]]
    model = ScriptedModel({"phieu_cau": lambda p: clean, "bieu_thuc_doc_lap": reader,
                           "sua_bai_tap": lambda p: {"bai_tap": []}})
    result = generate(get_lesson(LESSON), model, max_rounds=2)
    assert result.final.passed and result.rounds_used == 1
    assert "sua_bai_tap" not in model.calls                       # nothing was rewritten
    assert result.reports[0].items[0].status == "loi_doc_lai"
    assert len(result.reader_log) == 3                            # read, retry, read again


INDEPENDENT_OK = {"B1": "2**5", "B2": "4*4*4", "B3": "2**3*2**4", "B4": "5**6/5**2",
                  "B5": "10**3 + 10**2", "B6": "6**2*6/6**3"}


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print(f"ok  {name}")
    print(f"{len(tests)} tests passed")
