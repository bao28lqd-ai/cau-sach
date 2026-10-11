# Bản giáo viên · T6-04 · Số nguyên tố. Phân tích một số ra thừa số nguyên tố

**Kiểm tra tự động:** 7/7 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 5/6 bài tập đạt → vòng 1: 6/7 bài tập đạt → vòng 2: 7/7 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-04.1 | Nhận biết được số nguyên tố, hợp số. | B1, B2, [B5] |
| T6-04.2 | Thực hiện được việc phân tích một số tự nhiên lớn hơn 1 thành tích các thừa số nguyên tố trong những trường hợp đơn giản. | B3, B4, B5, B6, [B5] |

## Bài tập và đáp án

**Bài 1** (B1, T6-04.1) ✅ Đạt

- Đề: Cho số 29. Ghi 1 nếu đó là số nguyên tố, ghi 0 nếu không.
- Lời giải: Ta kiểm tra các ước của 29: thử chia cho 2, 3, 5 (các số nguyên tố ≤ √29 ≈ 5,38). Không chia hết cho 2, 3, 5 nên 29 chỉ có 1 và chính nó là ước. Vậy 29 là số nguyên tố, ghi 1.
- Đáp án: **1**  (kiểm bằng `1`)

**Bài 2** (B2, T6-04.1) ✅ Đạt

- Đề: Cho số 45. Ghi 1 nếu đó là số nguyên tố, ghi 0 nếu không.
- Lời giải: 45 chia hết cho 3 (45 = 3 · 15), nên có 1, 3, 5, 9, 15, 45 là các ước. Vậy 45 là hợp số, ghi 0.
- Đáp án: **0**  (kiểm bằng `0`)

**Bài 3** (B3, T6-04.2) ✅ Đạt

- Đề: Phân tích số 60 ra thừa số nguyên tố và viết dưới dạng tích.
- Lời giải: 60 chia cho 2: 60 = 2 · 30; 30 = 2 · 15; 15 = 3 · 5. Các thừa số nguyên tố là 2, 2, 3, 5. Vậy 60 = 2 · 2 · 3 · 5 = 2² · 3 · 5.
- Đáp án: **2² · 3 · 5**  (kiểm bằng `60`)

**Bài 4** (B4, T6-04.2) ✅ Đạt

- Đề: Một gói kẹo có 72 viên. Viết phân tích thừa số nguyên tố của 72.
- Lời giải: 72 chia cho 2: 72 = 2 · 36; 36 = 2 · 18; 18 = 2 · 9; 9 = 3 · 3. Thừa số nguyên tố là 2, 2, 2, 3, 3. Vậy 72 = 2³ · 3².
- Đáp án: **2³ · 3²**  (kiểm bằng `72`)

**Bài 5** (B5, T6-04.2) ✅ Đạt

- Đề: Phân tích 36 thành tích các thừa số nguyên tố.
- Lời giải: 36 = 4·9 = 2²·3². Vậy 36 = 2²·3².
- Đáp án: **2² · 3²**  (kiểm bằng `36`)

**Bài 6** (B6, T6-04.2) ✅ Đạt

- Đề: Phân tích số 231 thành tích các thừa số nguyên tố.
- Lời giải: Thử chia 231 cho 3: 231 = 3 · 77. 77 = 7 · 11 và cả 7, 11 đều là số nguyên tố. Vậy 231 = 3 · 7 · 11.
- Đáp án: **3 · 7 · 11**  (kiểm bằng `231`)

**Bài 7** ([B5], T6-04.1, T6-04.2) ✅ Đạt

- Đề: Phân tích 36 thành thừa số nguyên tố.
- Lời giải: 36 chia hết cho 2 nên 36 = 2 · 18. 18 chia hết cho 2 nên 18 = 2 · 9. 9 chia hết cho 3 nên 9 = 3 · 3. Vậy 36 = 2² · 3².
- Đáp án: **2² · 3²**  (kiểm bằng `36`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
