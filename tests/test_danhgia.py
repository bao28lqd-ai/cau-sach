"""Run with `python -m pytest` or, without pytest, `python tests/test_danhgia.py`."""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from causach.phieu import get_lesson
from causach.phieu import danhgia as dg
from causach.phieu.demo import INDEPENDENT, LESSON, demo_model
from causach.phieu.llm import ScriptedModel
from causach.phieu.mathcheck import evaluate
from causach.phieu.render import clean_display
from causach.phieu.store import load_runs
from causach.phieu.verify import check_exercise

BASE = {"id": "B1", "yccd": [], "de_bai": "", "loi_giai": "", "kieu": "gia_tri", "bieu_thuc": "2**5", "dap_an": "32"}


# ---- new checks found by reviewing real worksheets -------------------------------
def test_counting_answers_must_be_whole_numbers():
    cakes = {**BASE, "kieu": "so_nguyen", "bieu_thuc": "(3/4)/(1/6)", "dap_an": "9/2"}   # the 4.5-cake problem
    assert check_exercise(cakes).status == "sai_dang"
    assert check_exercise({**BASE, "kieu": "so_nguyen", "bieu_thuc": "(3/4)/(1/8)", "dap_an": "6"}).status == "dat"


def test_rounding_that_changes_nothing_is_flagged():
    trivial = {**BASE, "bieu_thuc": "lam_tron((18/30)*100, 1)", "dap_an": "60"}           # 60 -> 60.0
    real = {**BASE, "bieu_thuc": "lam_tron(3.276, 2)", "dap_an": "3.28"}
    assert check_exercise(trivial).status == "lam_tron_vo_nghia"
    assert check_exercise(real).status == "dat"


def test_display_uses_school_notation():
    assert clean_display("3^4 = 3 * 3 * 3 * 3 = 81.") == "3⁴ = 3 · 3 · 3 · 3 = 81."
    assert clean_display("2^3 * 2^4 = 2^(3+4) = 2^7.") == "2³ · 2⁴ = 2³⁺⁴ = 2⁷."
    assert clean_display("có 120.000 đồng") == "có 120.000 đồng"        # Vietnamese thousands dot untouched
    assert clean_display("**đậm**") == "**đậm**"


# ---- mutation operators -------------------------------------------------------
def test_answer_mutations_change_the_value_and_keep_the_form():
    cases = [
        {**BASE},
        {**BASE, "kieu": "so_nguyen", "bieu_thuc": "4*16", "dap_an": "64"},
        {**BASE, "kieu": "phan_so_toi_gian", "bieu_thuc": "2/3+1/6", "dap_an": "5/6"},
        {**BASE, "kieu": "mot_luy_thua", "bieu_thuc": "2**3*2**4", "dap_an": "2**7"},
        {**BASE, "kieu": "phan_tich_nguyen_to", "bieu_thuc": "60", "dap_an": "2**2*3*5"},
    ]
    for ex in cases:
        mutated = dg.mutate_answer(ex)
        assert evaluate(mutated["dap_an"]) != evaluate(ex["dap_an"]), ex
        assert check_exercise(mutated).status == "sai_dap_an", (ex, mutated)


def test_form_mutations_keep_the_value():
    for ex, expected in [
        ({**BASE, "kieu": "mot_luy_thua", "bieu_thuc": "2**3*2**4", "dap_an": "2**7"}, "128"),
        ({**BASE, "kieu": "phan_so_toi_gian", "bieu_thuc": "2/3+1/6", "dap_an": "5/6"}, "10/12"),
        ({**BASE, "kieu": "phan_tich_nguyen_to", "bieu_thuc": "60", "dap_an": "2**2*3*5"}, "60"),
    ]:
        mutated = dg.mutate_form(ex)
        assert mutated["dap_an"] == expected
        assert check_exercise(mutated).status == "sai_dang"
    assert dg.mutate_form(BASE) is None                     # plain values have no form to break


def test_expression_mutation_passes_checks_1_to_3_and_only_check_4_catches_it():
    ex = {**BASE, "kieu": "mot_luy_thua", "de_bai": "Viết 2³ · 2⁴ dưới dạng một lũy thừa.",
          "bieu_thuc": "2**3*2**4", "dap_an": "2**7"}
    mutated = dg.mutate_expression(ex)
    assert mutated is not None and mutated["de_bai"] == ex["de_bai"]
    assert check_exercise(mutated).status == "dat"
    assert check_exercise(mutated, independent="2**3*2**4", require_independent=True).status == "khong_khop_de"


def test_text_mutation_changes_a_number_that_matters():
    ex = {**BASE, "de_bai": "Một hộp có 3 ngăn, mỗi ngăn 4 túi, mỗi túi 5 viên bi. Có bao nhiêu viên bi?",
          "bieu_thuc": "3*4*5", "dap_an": "60"}
    changed = dg.mutate_text_number(ex)
    assert changed == "Một hộp có 3 ngăn, mỗi ngăn 4 túi, mỗi túi 6 viên bi. Có bao nhiêu viên bi?"
    same_number = {**ex, "de_bai": "Một hộp có 4 ngăn, mỗi ngăn 4 túi, mỗi túi 4 viên bi. Có bao nhiêu viên bi?",
                   "bieu_thuc": "4*4*4", "dap_an": "64"}
    assert dg.mutate_text_number(same_number) is None
    repeated = {**BASE, "de_bai": "Một cửa hàng có 12 hộp bút, mỗi hộp giá 45 000 đồng. Hỏi tổng tiền mua 12 hộp?",
                "kieu": "so_nguyen", "bieu_thuc": "12*45000", "dap_an": "540000"}
    assert dg.mutate_text_number(repeated) is None         # editing one "12" would not change the question
    grouped = {**BASE, "de_bai": "Giá áo là 150 000 đồng, giảm 20 000 đồng. Giá còn lại?",
               "bieu_thuc": "150000-20000", "dap_an": "130000"}
    assert dg.mutate_text_number(grouped) is None            # never edits half of a grouped number


# ---- pipeline -----------------------------------------------------------------
def _perfect_reader() -> ScriptedModel:
    """Reads originals correctly, says NHIEU_Y to appended questions, and reads edited numbers as edited."""
    def read(prompt: str) -> dict:
        rows = []
        for key, text in re.findall(r"\[([^\]]+)\] (.*)", prompt):
            base, variant = key.split(".")
            reading = {"goc": INDEPENDENT[base], "them_cau_hoi": "NHIEU_Y"}.get(variant, "999999")
            rows.append({"id": key, "bieu_thuc": reading})
        return {"ket_qua": rows}
    return ScriptedModel({"bieu_thuc_doc_lap": read}, name="perfect reader")


def test_whole_evaluation_pipeline_offline():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dg.run_generation([get_lesson(LESSON)], 2, demo_model, root, log=lambda m: None)
        runs = load_runs(root / "sinh")
        assert len(runs) == 2

        stats = dg.generation_stats(runs)
        assert (stats["first_pass"], stats["final_pass"], stats["first_items"]) == (8, 12, 12)
        assert stats["repaired"] == stats["failed_first"] == 4

        offline = dg.offline_mutants(runs)
        caught = offline.assign(hit=offline["trang_thai"] != "dat").groupby("loai_loi")["hit"].mean()
        assert caught["sai_dap_an"] == 1 and caught["sai_dang"] == 1 and caught["lech_bieu_thuc"] == 1
        without = offline[offline["loai_loi"] == "lech_bieu_thuc"]["trang_thai_khong_lop4"]
        assert (without == "dat").all()                        # without check 4 none of these are caught
        offline.to_csv((root / "gay_loi").mkdir() or root / "gay_loi" / "offline.csv", index=False)

        online, usage = dg.online_mutants(runs, _perfect_reader(), log=lambda m: None)
        assert usage["calls"] == 2
        control = online[online["loai_loi"] == "goc"]
        assert (control["trang_thai"] == "dat").all()
        assert (online[online["loai_loi"] == "them_cau_hoi"]["trang_thai"] == "nhieu_y").all()
        online.to_csv(root / "gay_loi" / "online.csv", index=False)

        sheet = root / "thu_cong.xlsx"
        assert dg.export_review_sheet(runs, sheet, n=5) == 5
        filled = pd.read_excel(sheet, sheet_name="danh_gia")
        filled.loc[0, list(dg.CRITERIA)] = [1, 1, 0, 1, 1]
        filled.loc[1, list(dg.CRITERIA)] = [1, None, 1, 1, 1]
        guide = pd.read_excel(sheet, sheet_name="huong_dan")
        with pd.ExcelWriter(sheet, engine="openpyxl") as writer:
            filled.to_excel(writer, sheet_name="danh_gia", index=False)
            guide.to_excel(writer, sheet_name="huong_dan", index=False)
        review = dg.summarize_review(sheet)
        assert review.attrs["reviewed"] == 2 and review.attrs["any_fail"] == 1

        report = dg.write_report(root).read_text(encoding="utf-8")
        for heading in ("## 1. Sinh phiếu", "## 2. Thử bộ kiểm tra", "## 3. Duyệt nội dung", "Báo nhầm"):
            assert heading in report
        assert "không phải duyệt thủ công" not in report      # no AI reviewer named


def test_review_sheet_dropdowns_and_ai_label():
    from openpyxl import load_workbook
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dg.run_generation([get_lesson(LESSON)], 1, demo_model, root, log=lambda m: None)
        sheet = root / "thu_cong.xlsx"
        dg.export_review_sheet(load_runs(root / "sinh"), sheet, n=4)
        assert load_workbook(sheet)["danh_gia"].data_validations.dataValidation   # dropdowns present

        filled = pd.read_excel(sheet, sheet_name="danh_gia")
        filled[list(dg.CRITERIA)] = filled[list(dg.CRITERIA)].astype(object)
        filled[["ghi_chu", "nguoi_duyet", "y_kien_nguoi_duyet"]] = filled[["ghi_chu", "nguoi_duyet", "y_kien_nguoi_duyet"]].astype(object)
        filled.loc[0, list(dg.CRITERIA)] = ["Đạt", "Không áp dụng", "Không đạt", "Đạt", "Đạt"]
        filled.loc[0, "ghi_chu"] = "quá dễ"
        filled.loc[1, list(dg.CRITERIA)] = [1, None, 1, 1, 1]
        filled["nguoi_duyet"] = "Claude (AI)"
        with pd.ExcelWriter(sheet, engine="openpyxl") as writer:
            filled.to_excel(writer, sheet_name="danh_gia", index=False)
        review = dg.summarize_review(sheet)
        assert review.attrs["reviewed"] == 2 and review.attrs["any_fail"] == 1
        assert review.attrs["issues"][0][1] == "quá dễ"
        report = dg.write_report(root).read_text(encoding="utf-8")
        assert "do AI chấm, chưa có người duyệt lại" in report and "không phải duyệt thủ công" in report

        filled.loc[0, "y_kien_nguoi_duyet"] = "đồng ý"
        filled.loc[1, "y_kien_nguoi_duyet"] = "không đồng ý: bài này ổn"
        with pd.ExcelWriter(sheet, engine="openpyxl") as writer:
            filled.to_excel(writer, sheet_name="danh_gia", index=False)
        report = dg.write_report(root).read_text(encoding="utf-8")
        assert "đã xem 2 dòng và đồng ý với 1" in report
        assert "AI chấm trước, người duyệt lại" in report and "bài này ổn" in report
        assert "chưa có người duyệt lại" not in report


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print(f"ok  {name}")
    print(f"{len(tests)} tests passed")
