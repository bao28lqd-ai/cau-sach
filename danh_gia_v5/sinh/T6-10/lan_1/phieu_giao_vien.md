# Bản giáo viên · T6-10 · Số thập phân, làm tròn và tỉ số phần trăm

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 5/6 bài tập đạt → vòng 1: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-10.1 | Thực hiện được phép cộng, trừ, nhân, chia với số thập phân. | B1, B2, B3 |
| T6-10.2 | Làm tròn được số thập phân đến một hàng cho trước. | B4, B5, B6 |
| T6-10.3 | Tính được tỉ số và tỉ số phần trăm của hai số. | B5 |

## Bài tập và đáp án

**Bài 1** (B1, T6-10.1) ✅ Đạt

- Đề: Tính 7,25 + 3,6.
- Lời giải: Đặt thẳng cột chữ số sau dấu phẩy: 7,25 + 3,60 = 10,85. Kết quả là 10,85.
- Đáp án: **10,85**  (kiểm bằng `7.25+3.6`)

**Bài 2** (B2, T6-10.1) ✅ Đạt

- Đề: Tính 12,4 · 3.
- Lời giải: Nhân 12,4 với 3 cho 37,2. Kết quả là 37,2.
- Đáp án: **37,2**  (kiểm bằng `12.4*3`)

**Bài 3** (B3, T6-10.1) ✅ Đạt

- Đề: Tính 9,6 : 0,8.
- Lời giải: Chia 9,6 cho 0,8; 9,6 : 0,8 = 12. Kết quả là 12.
- Đáp án: **12**  (kiểm bằng `9.6/0.8`)

**Bài 4** (B4, T6-10.2) ✅ Đạt

- Đề: Làm tròn số 154,678 đến hàng phần mười.
- Lời giải: Xem chữ số ở hàng phần trăm là 8 (≥5) nên tăng chữ số phần mười 6 lên 7. Kết quả làm tròn là 154,7.
- Đáp án: **154,7**  (kiểm bằng `lam_tron(154.678,1)`)

**Bài 5** (B5, T6-10.2, T6-10.3) ✅ Đạt

- Đề: Một chiếc áo có giá 150 000 đồng. Hãng khuyến mãi giảm 12% trên giá bán. Hỏi số tiền được giảm là bao nhiêu đồng?
- Lời giải: Số tiền giảm = 150 000 · 12% = 150 000 · 12/100 = 18 000 đồng. Kết quả là 18 000.
- Đáp án: **18000**  (kiểm bằng `150000*12/100`)

**Bài 6** (B6, T6-10.2) ✅ Đạt

- Đề: Trong một lớp có 17 bạn nữ và 13 bạn nam. Tính phần trăm số bạn nữ trong lớp (làm tròn đến số nguyên phần trăm).
- Lời giải: Tổng số bạn trong lớp là 17 + 13 = 30. Phần trăm bạn nữ là 17:30 · 100 = 56,666...%. Làm tròn đến số nguyên phần trăm ta được 57%.
- Đáp án: **57**  (kiểm bằng `lam_tron(17/30*100,0)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
