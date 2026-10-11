# Bản giáo viên · T6-06 · Bội chung. Bội chung nhỏ nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-06.1 | Xác định được bội chung, bội chung nhỏ nhất của hai hoặc ba số tự nhiên. | B1, B2, B3, B4, B5, B6 |
| T6-06.2 | Thực hiện được phép cộng, phép trừ phân số bằng cách quy đồng mẫu số với bội chung nhỏ nhất. | B4, B5 |

## Bài tập và đáp án

**Bài 1** (B1, T6-06.1) ✅ Đạt

- Đề: Tìm bội chung nhỏ nhất của 6 và 8.
- Lời giải: Phân tích: 6 = 2·3, 8 = 2³. Lấy 2³·3 = 8·3 = 24. Vậy BCNN = 24.
- Đáp án: **24**  (kiểm bằng `bcnn(6,8)`)

**Bài 2** (B2, T6-06.1) ✅ Đạt

- Đề: Có hộp đóng 6 quả và hộp đóng 8 quả. Hỏi cần ít nhất bao nhiêu quả để có thể xếp vừa đúng một số nguyên hộp của cả hai loại?
- Lời giải: Ta tìm số quả nhỏ nhất chia hết cho cả 6 và 8, tức là BCNN(6,8) = 24. Vậy cần 24 quả.
- Đáp án: **24**  (kiểm bằng `bcnn(6,8)`)

**Bài 3** (B3, T6-06.1) ✅ Đạt

- Đề: Tìm bội chung nhỏ nhất của 9 và 12.
- Lời giải: Phân tích: 9 = 3², 12 = 2²·3. Lấy 2²·3² = 4·9 = 36. Vậy BCNN = 36.
- Đáp án: **36**  (kiểm bằng `bcnn(9,12)`)

**Bài 4** (B4, T6-06.2, T6-06.1) ✅ Đạt

- Đề: Tính 3/8 + 1/6 bằng cách quy đồng mẫu số với BCNN.
- Lời giải: Mẫu số 8 và 6 có BCNN = 24. Quy đồng: 3/8 = 9/24, 1/6 = 4/24. Tổng = (9+4)/24 = 13/24. Phân số đã là tối giản.
- Đáp án: **13/24**  (kiểm bằng `3/8+1/6`)

**Bài 5** (B5, T6-06.2, T6-06.1) ✅ Đạt

- Đề: Tính 7/15 - 1/6 bằng cách quy đồng mẫu số với BCNN.
- Lời giải: Mẫu số 15 và 6 có BCNN = 30. Quy đồng: 7/15 = 14/30, 1/6 = 5/30. Hiệu = (14-5)/30 = 9/30 = 3/10 sau khi rút gọn.
- Đáp án: **3/10**  (kiểm bằng `7/15-1/6`)

**Bài 6** (B6, T6-06.1) ✅ Đạt

- Đề: Hai xe buýt khởi hành cùng lúc. Một xe lặp lại sau mỗi 12 phút, xe kia lặp lại sau mỗi 18 phút. Hỏi sau bao nhiêu phút hai xe sẽ cùng đứng lại cùng lúc lần tiếp theo?
- Lời giải: Ta cần BCNN(12,18). 12 = 2²·3, 18 = 2·3², nên BCNN = 2²·3² = 4·9 = 36. Vậy sau 36 phút.
- Đáp án: **36**  (kiểm bằng `bcnn(12,18)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
