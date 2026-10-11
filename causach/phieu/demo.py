"""Offline demo for lesson T6-02 (Lũy thừa), driven by a scripted model.

The draft below is HAND-WRITTEN, not model output. Two errors are planted
on purpose so the loop has something to catch:

    B3  answer is wrong: 2³ · 2⁴ written as 2¹² (exponents multiplied, not added)
    B6  answer matches its own expression, but that expression does not match
        the problem text (6² · 6 : 6³ computed as 6² · 6 : 6²). Only the
        independent re-derivation can catch this one.
"""
from __future__ import annotations

from .llm import ScriptedModel, ids_in_prompt

LESSON = "T6-02"

DRAFT = {
    "tieu_de": "Lũy thừa với số mũ tự nhiên",
    "muc_tieu": [
        "Tính được giá trị của một lũy thừa.",
        "Nhân, chia được hai lũy thừa cùng cơ số.",
    ],
    "kien_thuc_cot_loi": [
        "aⁿ là tích của n thừa số bằng a (n ≥ 1); a là cơ số, n là số mũ.",
        "Quy ước: a¹ = a; a⁰ = 1 với a khác 0.",
        "Nhân hai lũy thừa cùng cơ số: giữ cơ số, cộng các số mũ: aᵐ · aⁿ = aᵐ⁺ⁿ.",
        "Chia hai lũy thừa cùng cơ số (a khác 0, m ≥ n): giữ cơ số, trừ các số mũ: aᵐ : aⁿ = aᵐ⁻ⁿ.",
    ],
    "vi_du": [
        {"de_bai": "Tính 3⁴.", "loi_giai": "3⁴ = 3 · 3 · 3 · 3 = 81."},
        {"de_bai": "Viết 7⁵ · 7² dưới dạng một lũy thừa.", "loi_giai": "Giữ cơ số 7, cộng số mũ: 7⁵ · 7² = 7⁷."},
    ],
    "bai_tap": [
        {"id": "B1", "yccd": ["T6-02.1"], "de_bai": "Tính 2⁵.",
         "loi_giai": "2⁵ = 2 · 2 · 2 · 2 · 2 = 32.", "kieu": "gia_tri", "bieu_thuc": "2**5", "dap_an": "32"},
        {"id": "B2", "yccd": ["T6-02.1"],
         "de_bai": "Một hộp có 4 ngăn, mỗi ngăn có 4 túi, mỗi túi có 4 viên bi. Hộp có tất cả bao nhiêu viên bi?",
         "loi_giai": "Số viên bi là 4 · 4 · 4 = 4³ = 64.", "kieu": "gia_tri", "bieu_thuc": "4**3", "dap_an": "64"},
        {"id": "B3", "yccd": ["T6-02.2"], "de_bai": "Viết 2³ · 2⁴ dưới dạng một lũy thừa.",
         "loi_giai": "2³ · 2⁴ = 2¹².", "kieu": "mot_luy_thua", "bieu_thuc": "2**3*2**4", "dap_an": "2**12"},
        {"id": "B4", "yccd": ["T6-02.2"], "de_bai": "Viết 5⁶ : 5² dưới dạng một lũy thừa.",
         "loi_giai": "Giữ cơ số 5, trừ số mũ: 5⁶ : 5² = 5⁴.", "kieu": "mot_luy_thua",
         "bieu_thuc": "5**6/5**2", "dap_an": "5**4"},
        {"id": "B5", "yccd": ["T6-02.1"], "de_bai": "Tính 10³ + 10².",
         "loi_giai": "10³ + 10² = 1000 + 100 = 1100.", "kieu": "gia_tri",
         "bieu_thuc": "10**3 + 10**2", "dap_an": "1100"},
        {"id": "B6", "yccd": ["T6-02.2"], "de_bai": "Tính 6² · 6 : 6³.",
         "loi_giai": "6² · 6 = 6³, rồi 6³ : 6² = 6.", "kieu": "gia_tri",
         "bieu_thuc": "6**2*6/6**2", "dap_an": "6"},
    ],
}

FIXES = {
    "B3": {"id": "B3", "yccd": ["T6-02.2"], "de_bai": "Viết 2³ · 2⁴ dưới dạng một lũy thừa.",
           "loi_giai": "Giữ cơ số 2, cộng số mũ: 2³ · 2⁴ = 2³⁺⁴ = 2⁷.", "kieu": "mot_luy_thua",
           "bieu_thuc": "2**3*2**4", "dap_an": "2**7"},
    "B6": {"id": "B6", "yccd": ["T6-02.2"], "de_bai": "Tính 6² · 6 : 6³.",
           "loi_giai": "6² · 6 = 6³, rồi 6³ : 6³ = 6⁰ = 1.", "kieu": "gia_tri",
           "bieu_thuc": "6**2*6/6**3", "dap_an": "1"},
}

# What an independent reader writes from each problem text alone.
INDEPENDENT = {
    "B1": "2**5", "B2": "4*4*4", "B3": "2**3*2**4", "B4": "5**6/5**2",
    "B5": "10**3 + 10**2", "B6": "6**2*6/6**3",
}


def demo_model() -> ScriptedModel:
    return ScriptedModel(
        {
            "phieu_cau": lambda prompt: DRAFT,
            "sua_bai_tap": lambda prompt: {"bai_tap": [FIXES[i] for i in ids_in_prompt(prompt) if i in FIXES]},
            "bieu_thuc_doc_lap": lambda prompt: {
                "ket_qua": [{"id": i, "bieu_thuc": INDEPENDENT[i]} for i in ids_in_prompt(prompt) if i in INDEPENDENT]
            },
        },
        name="demo (mô hình giả lập)",
    )
