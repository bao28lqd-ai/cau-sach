"""Markdown output: a student copy (no answers) and a teacher copy for review."""
from __future__ import annotations

import re

from .curriculum import Lesson
from .verify import STATUS_LABELS, Report

SUPERSCRIPT = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
FOOTER = ("Phiếu Cầu, soạn theo yêu cầu cần đạt của Chương trình giáo dục phổ thông môn Toán 2018; "
          "không chép từ sách giáo khoa. Giấy phép CC BY 4.0. Người biên soạn và duyệt: ____________")


_SUP_CHARS = "0123456789+-()nm"
_SUP_TABLE = str.maketrans(_SUP_CHARS, "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ⁿᵐ")
_POWER = re.compile(r"([\w)])\s*(?:\*\*|\^)\s*(?:\(([^()]*)\)|(\d+|[nm]))")


def clean_display(text: str) -> str:
    """School notation for model-written text: 3^4 -> 3⁴, 2^(3+4) -> 2³⁺⁴, 3 * 3 -> 3 · 3.

    Decimal points are left alone on purpose: in Vietnamese text "120.000" means
    one hundred and twenty thousand, so rewriting dots would change numbers.
    """
    def power(match: re.Match) -> str:
        exponent = (match.group(2) if match.group(2) is not None else match.group(3)).replace(" ", "")
        if exponent and all(c in _SUP_CHARS for c in exponent):
            return match.group(1) + exponent.translate(_SUP_TABLE)
        return match.group(0)

    text = _POWER.sub(power, text)
    return re.sub(r"(?<!\*)\s*\*\s*(?!\*)", " · ", text)


def pretty(expr: str) -> str:
    """Display form of a machine expression: 2**2*3*5 -> 2² · 3 · 5, 3.25 -> 3,25."""
    text = re.sub(r"\*\*\s*\(?(-?\d+)\)?", lambda m: m.group(1).translate(SUPERSCRIPT), expr)
    text = text.replace("*", " · ").replace("/", "/")
    text = re.sub(r"(\d)\.(\d)", r"\1,\2", text)
    return re.sub(r"\s+", " ", text).strip()


def student_markdown(worksheet: dict, lesson: Lesson) -> str:
    c = clean_display
    lines = [f"# Phiếu Cầu · Toán 6 · {lesson.title}", "",
             "*Đối chiếu SGK: trang ……*", "", "## Mục tiêu", ""]
    lines += [f"- {c(m)}" for m in worksheet["muc_tieu"]]
    lines += ["", "## Kiến thức cốt lõi", ""]
    lines += [f"- {c(k)}" for k in worksheet["kien_thuc_cot_loi"]]
    lines += ["", "## Ví dụ", ""]
    for n, ex in enumerate(worksheet["vi_du"], 1):
        lines += [f"**Ví dụ {n}.** {c(ex['de_bai'])}", "", f"*Lời giải.* {c(ex['loi_giai'])}", ""]
    lines += ["## Bài tập", ""]
    for n, ex in enumerate(worksheet["bai_tap"], 1):
        lines += [f"**Bài {n}.** {c(ex['de_bai'])}", ""]
    lines += ["---", "", f"*{FOOTER}*", ""]
    return "\n".join(lines)


def teacher_markdown(worksheet: dict, lesson: Lesson, report: Report, log: list[str] | None = None,
                     model: str = "") -> str:
    c = clean_display
    checks = report.by_id()
    lines = [f"# Bản giáo viên · {lesson.code} · {lesson.title}", ""]
    lines.append(f"**Kiểm tra tự động:** {report.summary()}." + (f" Mô hình: `{model}`." if model else ""))
    if log:
        lines += ["", "Các vòng sửa: " + " → ".join(log)]
    lines += ["", "## Yêu cầu cần đạt", "", "| Mã | Nội dung | Bài tập |", "|---|---|---|"]
    for req in lesson.requirements:
        used = [ex["id"] for ex in worksheet["bai_tap"] if req.code in ex.get("yccd", [])]
        lines.append(f"| {req.code} | {req.text} | {', '.join(used) or '**chưa có**'} |")
    lines += ["", "## Bài tập và đáp án", ""]
    for n, ex in enumerate(worksheet["bai_tap"], 1):
        check = checks.get(ex["id"])
        status = STATUS_LABELS.get(check.status, check.status) if check else "chưa kiểm tra"
        mark = "✅" if check and check.passed else "❌"
        lines += [
            f"**Bài {n}** ({ex['id']}, {', '.join(ex.get('yccd', []))}) {mark} {status}",
            "",
            f"- Đề: {c(ex['de_bai'])}",
            f"- Lời giải: {c(ex['loi_giai'])}",
            f"- Đáp án: **{pretty(ex['dap_an'])}**  (kiểm bằng `{ex['bieu_thuc']}`)",
        ]
        if check and check.message:
            lines.append(f"- Lỗi: {check.message}")
        if check and check.note:
            lines.append(f"- Ghi chú: {check.note}")
        lines.append("")
    lines += ["## Việc giáo viên cần xem", "",
              "- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.",
              "- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).",
              "- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.",
              "- Điền trang đối chiếu SGK và tên người duyệt trước khi in.", ""]
    return "\n".join(lines)
