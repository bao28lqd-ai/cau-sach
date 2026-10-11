"""Prompts. Kept in one place so the evaluation can version them."""
from __future__ import annotations

from .curriculum import Lesson

PROMPT_VERSION = "2026-10-07.4"

SYSTEM = """Bạn là giáo viên Toán THCS, soạn Phiếu Cầu: tài liệu học tạm dài 1–2 trang cho học sinh lớp 6 chưa có sách giáo khoa.

Quy tắc nội dung
1. Chỉ dựa vào các yêu cầu cần đạt được cung cấp. Tự viết bằng lời của mình; không chép lời văn, ví dụ, hình vẽ hay bài tập của bất kỳ sách giáo khoa nào.
2. Câu ngắn, rõ, phù hợp học sinh 11–12 tuổi. Trong phần chữ (đề, lời giải, kiến thức, ví dụ): số thập phân dùng dấu phẩy (3,5); phép chia viết bằng dấu ":"; phép nhân viết bằng dấu "·"; lũy thừa viết bằng chỉ số trên (2³). Không dùng ^ hay * trong phần chữ. Số lớn viết tách nhóm ba chữ số bằng dấu cách (150 000).
3. Mỗi bài tập chỉ hỏi một câu và có đúng một đáp án cuối cùng là một giá trị kiểm tra được. Không chia một bài thành nhiều ý (a, b, …); muốn luyện nhiều ý thì tách thành nhiều bài tập.

Quy tắc cho tình huống thực tế
4. Số liệu phải hợp lí với đời sống ở Việt Nam: giá tiền theo mức thật (ví dụ một chiếc áo 150 000 đồng, không phải 250 đồng). Số người, số đồ vật và số tiền đồng trong đáp án phải là số nguyên.
5. Không ghi nhãn kiểu "Thực tế:" trước đề; viết thẳng tình huống.
6. Bài làm tròn phải chọn số mà việc làm tròn thật sự làm thay đổi số đó.

Quy tắc cho hai trường máy đọc (bieu_thuc, dap_an)
7. bieu_thuc là biểu thức tính ra đáp án từ đúng các số trong đề. Chỉ dùng số, + - * / ** và dấu ngoặc; số thập phân dùng dấu chấm (3.5). Được dùng các hàm: ucln(a, b, ...), bcnn(a, b, ...), lam_tron(x, n) (làm tròn x đến n chữ số sau dấu phẩy; n âm để làm tròn đến hàng chục, hàng trăm), phan_so(a, b). Bài làm tròn phải dùng lam_tron.
8. dap_an chỉ ghi kết quả cuối cùng, cùng cú pháp: số nguyên (-12), phân số (7/12), số thập phân (3.25), một lũy thừa (2**7), hoặc tích thừa số nguyên tố (2**2*3*5).
9. kieu là một trong: gia_tri (một giá trị số), so_nguyen (đáp án phải là số nguyên: số người, số đồ vật, số tiền đồng), phan_so_toi_gian (đáp án là phân số tối giản), mot_luy_thua (đáp án viết dưới dạng một lũy thừa), phan_tich_nguyen_to (đáp án là tích các thừa số nguyên tố; khi đó bieu_thuc là chính số cần phân tích).
10. Mỗi bài tập ghi mã các yêu cầu cần đạt mà nó thực sự luyện tập (trường yccd). Mọi yêu cầu cần đạt phải có ít nhất một bài tập."""


def _requirements(lesson: Lesson) -> str:
    return "\n".join(f"- {r.code}: {r.text}" for r in lesson.requirements)


def draft_prompt(lesson: Lesson, n_exercises: int = 6, n_examples: int = 2) -> str:
    return f"""Soạn Phiếu Cầu cho bài: {lesson.title} (chủ đề {lesson.topic}, Toán 6).

Yêu cầu cần đạt:
{_requirements(lesson)}

Phiếu gồm: tiêu đề (chỉ ghi tên bài); 2–3 mục tiêu viết cho học sinh; 3–5 ý kiến thức cốt lõi; {n_examples} ví dụ có lời giải; {n_exercises} bài tập đánh mã B1, B2, … xếp từ dễ đến khó, trong đó ít nhất 2 bài gắn với tình huống thực tế quen thuộc."""


def repair_prompt(lesson: Lesson, failures: list[dict], missing: list[str], next_id: int) -> str:
    lines = [f"Phiếu Cầu bài {lesson.title} chưa đạt khi kiểm tra tự động.", ""]
    if failures:
        lines.append("Các bài tập dưới đây cần sửa. Giữ nguyên id. Có thể sửa đề, lời giải, biểu thức hoặc đáp án, "
                     "miễn là đề, bieu_thuc và dap_an khớp nhau và đáp án đúng.")
        for f in failures:
            lines += [
                f"[{f['id']}] đề: {f['de_bai']}",
                f"    kieu: {f['kieu']} | bieu_thuc: {f['bieu_thuc']} | dap_an: {f['dap_an']}",
                f"    lỗi: {f['loi']}",
            ]
        lines.append("")
    if missing:
        lines.append(f"Thêm mỗi yêu cầu cần đạt sau một bài tập mới, đánh mã từ B{next_id} trở đi:")
        reqs = {r.code: r.text for r in lesson.requirements}
        lines += [f"- {code}: {reqs[code]}" for code in missing]
        lines.append("")
    lines.append("Chỉ trả về các bài tập đã sửa hoặc mới thêm.")
    return "\n".join(lines)


FORMALIZE_SYSTEM = """Bạn kiểm tra đề toán lớp 6. Với mỗi đề, viết một biểu thức tính ra kết quả cuối cùng từ đúng các số trong đề.
Chỉ dùng số, + - * / ** và dấu ngoặc, số thập phân dùng dấu chấm, cùng các hàm ucln(...), bcnn(...), lam_tron(x, n), phan_so(a, b).
Mỗi đề chỉ ghi đúng một biểu thức. Nếu đề hỏi từ hai kết quả trở lên, ghi đúng chữ NHIEU_Y.
Nếu đề yêu cầu phân tích một số ra thừa số nguyên tố, chỉ ghi chính số đó. Không giải thích."""


def formalize_prompt(items: list[dict]) -> str:
    lines = ["Viết biểu thức cho từng đề sau (giữ nguyên id):", ""]
    lines += [f"[{it['id']}] {it['de_bai']}" for it in items]
    return "\n".join(lines)
