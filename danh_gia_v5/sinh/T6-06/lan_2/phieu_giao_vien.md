# Bản giáo viên · T6-06 · Bội chung. Bội chung nhỏ nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-06.1 | Xác định được bội chung, bội chung nhỏ nhất của hai hoặc ba số tự nhiên. | B1, B2, B3, B6 |
| T6-06.2 | Thực hiện được phép cộng, phép trừ phân số bằng cách quy đồng mẫu số với bội chung nhỏ nhất. | B4, B5 |

## Bài tập và đáp án

**Bài 1** (B1, T6-06.1) ✅ Đạt

- Đề: Bội chung nhỏ nhất của 6 và 8 là bao nhiêu?
- Lời giải: Phân tích: 6 = 2 · 3, 8 = 2³. Lấy 2³ · 3 = 24. Vậy BCNN(6, 8) = 24.
- Đáp án: **24**  (kiểm bằng `bcnn(6,8)`)

**Bài 2** (B2, T6-06.1) ✅ Đạt

- Đề: Bội chung nhỏ nhất của 9, 12 và 15 là bao nhiêu?
- Lời giải: 9 = 3², 12 = 2² · 3, 15 = 3 · 5. Lấy 2² · 3² · 5 = 180. Vậy BCNN là 180.
- Đáp án: **180**  (kiểm bằng `bcnn(9,12,15)`)

**Bài 3** (B3, T6-06.1) ✅ Đạt

- Đề: Ba nhóm sinh hoạt lần lượt sau 3 ngày, 4 ngày và 6 ngày. Hỏi sau bao nhiêu ngày kể từ hôm nay cả ba nhóm sẽ sinh hoạt cùng một ngày?
- Lời giải: Tìm BCNN của 3, 4, 6. BCNN(3,4,6) = 12. Vậy sau 12 ngày cả ba nhóm sẽ cùng sinh hoạt.
- Đáp án: **12**  (kiểm bằng `bcnn(3,4,6)`)

**Bài 4** (B4, T6-06.2) ✅ Đạt

- Đề: Tính 1/6 + 1/4 bằng cách quy đồng mẫu số với bội chung nhỏ nhất.
- Lời giải: BCNN của 6 và 4 là 12. Quy đồng: 1/6 = 2/12, 1/4 = 3/12. Cộng: 2/12 + 3/12 = 5/12. Kết quả tối giản là 5/12.
- Đáp án: **5/12**  (kiểm bằng `phan_so(1*2+1*3,12)`)

**Bài 5** (B5, T6-06.2) ✅ Đạt

- Đề: Tính 5/12 - 1/8 bằng cách quy đồng mẫu số với bội chung nhỏ nhất.
- Lời giải: BCNN của 12 và 8 là 24. Quy đồng: 5/12 = 10/24, 1/8 = 3/24. Trừ: 10/24 - 3/24 = 7/24. Kết quả tối giản là 7/24.
- Đáp án: **7/24**  (kiểm bằng `phan_so(5*2-1*3,24)`)

**Bài 6** (B6, T6-06.1) ✅ Đạt

- Đề: Hai chuyến xe buýt xuất phát cùng lúc. Một chuyến lặp lại sau mỗi 15 phút, chuyến kia lặp lại sau mỗi 20 phút. Hỏi sau bao nhiêu phút kể từ lúc xuất phát cả hai chuyến sẽ gặp nhau lại cùng lúc?
- Lời giải: Tìm BCNN của 15 và 20. BCNN(15,20) = 60. Vậy sau 60 phút cả hai sẽ cùng lúc gặp nhau.
- Đáp án: **60**  (kiểm bằng `bcnn(15,20)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
