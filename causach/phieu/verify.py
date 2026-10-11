"""Automatic checks for a worksheet.

Per exercise, in order:
    1. bieu_thuc and dap_an parse as permitted expressions      -> loi_bieu_thuc
    2. dap_an has the form the exercise type requires            -> sai_dang
       (a so_nguyen exercise whose expression is not a whole
       number, e.g. 4.5 cakes, also lands here)
    3. dap_an equals the exact value of bieu_thuc                -> sai_dap_an
       a rounding step that changes nothing (60 -> 60.0)         -> lam_tron_vo_nghia
    4. an expression written independently from the problem
       text alone (second model call) has the same value         -> khong_khop_de
       the independent reader finds several questions in one     -> nhieu_y
       the independent reader's answer is not a usable expression -> chua_doi_chieu
       the reading step returned nothing for this exercise       -> loi_doc_lai
       (a failure of the pipeline, not of the exercise; the loop
       retries the reading instead of asking for a rewrite)

Check 4 matters because checks 1–3 only prove the answer matches the model's
own expression; they cannot tell whether that expression matches the problem.
When check 4 is enabled, an exercise it could not check does NOT pass: an
unchecked exercise is reported as unchecked, never as correct.

For the whole worksheet: every learning requirement (YCCĐ) has at least one
exercise, exercise ids are unique, and the number of exercises is in range.

What is NOT checked automatically: whether explanations are pedagogically
good, whether the wording suits 11-year-olds, whether word problems are
realistic. That is the teacher's review.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import Lesson
from .mathcheck import FORM_CHECKS, ExpressionError, evaluate, noop_roundings

STATUS_LABELS = {
    "dat": "Đạt",
    "loi_bieu_thuc": "Lỗi biểu thức",
    "sai_dang": "Sai dạng đáp án",
    "sai_dap_an": "Sai đáp án",
    "khong_khop_de": "Biểu thức không khớp đề",
    "nhieu_y": "Đề hỏi nhiều ý",
    "lam_tron_vo_nghia": "Làm tròn không thay đổi số",
    "chua_doi_chieu": "Chưa đối chiếu được với đề",
    "loi_doc_lai": "Bước đọc lại không trả kết quả (lỗi hệ thống)",
}

MULTI_PART_MESSAGE = ("đề hỏi nhiều kết quả nhưng chỉ một đáp án được kiểm tra; "
                      "viết lại thành một câu hỏi có đúng một đáp án")


@dataclass
class ItemCheck:
    id: str
    status: str
    message: str = ""
    note: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "dat"


@dataclass
class Report:
    items: list[ItemCheck]
    structure_errors: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(i.passed for i in self.items) and not self.structure_errors and not self.missing_requirements

    @property
    def n_passed(self) -> int:
        return sum(i.passed for i in self.items)

    def by_id(self) -> dict[str, ItemCheck]:
        return {i.id: i for i in self.items}

    def summary(self) -> str:
        text = f"{self.n_passed}/{len(self.items)} bài tập đạt"
        if self.missing_requirements:
            text += f"; thiếu bài cho {', '.join(self.missing_requirements)}"
        if self.structure_errors:
            text += f"; {'; '.join(self.structure_errors)}"
        return text


def check_exercise(item: dict, independent: str | None = None, require_independent: bool = False) -> ItemCheck:
    item_id = item.get("id", "?")
    try:
        value = evaluate(item["bieu_thuc"])
    except (ExpressionError, KeyError) as exc:
        return ItemCheck(item_id, "loi_bieu_thuc", f"bieu_thuc: {exc}")
    try:
        answer = evaluate(item["dap_an"])
    except (ExpressionError, KeyError) as exc:
        return ItemCheck(item_id, "loi_bieu_thuc", f"dap_an: {exc}")

    if item.get("kieu") == "so_nguyen" and value.q != 1:
        return ItemCheck(item_id, "sai_dang",
                         f"kết quả của đề là {value}, không phải số nguyên; chọn lại số liệu để kết quả là số nguyên")
    form_error = FORM_CHECKS.get(item.get("kieu"), lambda a: f"kiểu không hợp lệ: {item.get('kieu')}")(item["dap_an"])
    if form_error:
        return ItemCheck(item_id, "sai_dang", form_error)
    if answer != value:
        return ItemCheck(item_id, "sai_dap_an", f"đáp án {item['dap_an']} nhưng biểu thức cho {value}")
    noop = noop_roundings(item["bieu_thuc"])
    if noop:
        return ItemCheck(item_id, "lam_tron_vo_nghia",
                         f"{', '.join(noop)} không làm thay đổi số; chọn số mà việc làm tròn thật sự thay đổi nó")

    if independent is None:
        if require_independent:
            return ItemCheck(item_id, "loi_doc_lai", "bước đọc lại đề không trả kết quả cho bài này")
        return ItemCheck(item_id, "dat")
    if independent.strip().upper() == "NHIEU_Y" or ";" in independent:
        return ItemCheck(item_id, "nhieu_y", MULTI_PART_MESSAGE, note=f"đọc lại đề được: {independent}")
    try:
        other = evaluate(independent)
    except ExpressionError as exc:
        return ItemCheck(item_id, "chua_doi_chieu",
                         f"không đọc lại được đề thành một biểu thức ({exc}); viết đề rõ hơn, chỉ hỏi một kết quả")
    if other != value:
        return ItemCheck(item_id, "khong_khop_de",
                         f"đọc lại đề được {independent} = {other}, khác với {item['bieu_thuc']} = {value}")
    return ItemCheck(item_id, "dat")


def verify(worksheet: dict, lesson: Lesson, independent: dict[str, str] | None = None,
           min_exercises: int = 4, max_exercises: int = 10) -> Report:
    """`independent=None` skips check 4; a dict (even empty) makes it required."""
    required = independent is not None
    independent = independent or {}
    exercises = worksheet.get("bai_tap", [])
    items = [check_exercise(ex, independent.get(ex.get("id")), required) for ex in exercises]

    errors = []
    ids = [ex.get("id") for ex in exercises]
    if len(ids) != len(set(ids)):
        errors.append("trùng mã bài tập")
    if not min_exercises <= len(exercises) <= max_exercises:
        errors.append(f"số bài tập {len(exercises)} ngoài khoảng {min_exercises}–{max_exercises}")
    unknown = sorted({c for ex in exercises for c in ex.get("yccd", [])} - lesson.requirement_codes)
    if unknown:
        errors.append(f"mã yêu cầu cần đạt không tồn tại: {', '.join(unknown)}")
    for key in ("tieu_de", "muc_tieu", "kien_thuc_cot_loi", "vi_du"):
        if not worksheet.get(key):
            errors.append(f"thiếu {key}")

    # A requirement counts as covered only by an exercise that passed.
    passed = {i.id for i in items if i.passed}
    covered = {c for ex in exercises if ex.get("id") in passed for c in ex.get("yccd", [])}
    missing = sorted(lesson.requirement_codes - covered)
    return Report(items, errors, missing)
