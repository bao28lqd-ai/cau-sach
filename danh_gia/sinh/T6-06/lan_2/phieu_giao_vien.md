# Bản giáo viên · T6-06 · Bội chung. Bội chung nhỏ nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-06.1 | Xác định được bội chung, bội chung nhỏ nhất của hai hoặc ba số tự nhiên. | B1, B2, B5, B6 |
| T6-06.2 | Thực hiện được phép cộng, phép trừ phân số bằng cách quy đồng mẫu số với bội chung nhỏ nhất. | B3, B4, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-06.1) ✅ Đạt

- Đề: Tìm bội chung nhỏ nhất của 4 và 6.
- Lời giải: Phân tích: 4 = 2², 6 = 2·3. Lấy 2²·3 = 4·3 = 12. Vậy BCNN(4, 6) = 12.
- Đáp án: **12**  (kiểm bằng `bcnn(4,6)`)

**Bài 2** (B2, T6-06.1) ✅ Đạt

- Đề: Tìm bội chung nhỏ nhất của 6, 8 và 15.
- Lời giải: Phân tích: 6 = 2·3, 8 = 2³, 15 = 3·5. Lấy 2³·3·5 = 8·3·5 = 120. Vậy BCNN(6,8,15) = 120.
- Đáp án: **120**  (kiểm bằng `bcnn(6,8,15)`)

**Bài 3** (B3, T6-06.2) ✅ Đạt

- Đề: Tính 1/3 + 1/6 bằng cách quy đồng mẫu số với BCNN.
- Lời giải: Mẫu số chung nhỏ nhất của 3 và 6 là 6. Viết 1/3 = 2/6, nên 2/6 + 1/6 = 3/6 = 1/2 sau khi rút gọn.
- Đáp án: **1/2**  (kiểm bằng `phan_so(1,3)+phan_so(1,6)`)

**Bài 4** (B4, T6-06.2) ✅ Đạt

- Đề: Tính 5/12 − 1/3 bằng cách quy đồng mẫu số với BCNN.
- Lời giải: Mẫu số chung nhỏ nhất của 12 và 3 là 12. Viết 1/3 = 4/12, nên 5/12 − 4/12 = 1/12.
- Đáp án: **1/12**  (kiểm bằng `phan_so(5,12)-phan_so(1,3)`)

**Bài 5** (B5, T6-06.1) ✅ Đạt

- Đề: Hai loại hộp bút bán theo hộp có 12 cây và 15 cây. Hỏi phải mua ít nhất bao nhiêu cây bút để số cây chia đều cho cả hai loại hộp?
- Lời giải: Số cây cần mua là BCNN(12, 15). Ta có BCNN = 60, nên phải mua ít nhất 60 cây.
- Đáp án: **60**  (kiểm bằng `bcnn(12,15)`)

**Bài 6** (B6, T6-06.2, T6-06.1) ✅ Đạt

- Đề: Một cái bánh. Bạn A ăn 1/3 chiếc, bạn B ăn 1/4 chiếc. Hỏi phần bánh còn lại là bao nhiêu phần (tối giản)?
- Lời giải: Tổng phần đã ăn là 1/3 + 1/4 = 7/12, nên phần còn lại là 1 − 7/12 = 5/12.
- Đáp án: **5/12**  (kiểm bằng `phan_so(1,1)-(phan_so(1,3)+phan_so(1,4))`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
