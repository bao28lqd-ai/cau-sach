# Bản giáo viên · T6-10 · Số thập phân, làm tròn và tỉ số phần trăm

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-10.1 | Thực hiện được phép cộng, trừ, nhân, chia với số thập phân. | B1, B2, B5 |
| T6-10.2 | Làm tròn được số thập phân đến một hàng cho trước. | B3, B6 |
| T6-10.3 | Tính được tỉ số và tỉ số phần trăm của hai số. | B4, B5, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-10.1) ✅ Đạt

- Đề: Tính 4,25 + 3,6.
- Lời giải: Đặt thẳng dấu phẩy rồi cộng: 4,25 + 3,60 = 7,85.
- Đáp án: **7,85**  (kiểm bằng `4.25+3.6`)

**Bài 2** (B2, T6-10.1) ✅ Đạt

- Đề: Tính 5,4 · 0,8.
- Lời giải: 5,4 · 0,8 = 4,32 bằng cách nhân như số nguyên rồi đặt dấu phẩy.
- Đáp án: **4,32**  (kiểm bằng `5.4*0.8`)

**Bài 3** (B3, T6-10.2) ✅ Đạt

- Đề: Làm tròn số 7,386 đến 1 chữ số thập phân.
- Lời giải: Xem chữ số ở hàng 2 là 8 nên làm tròn hàng 1: 7,386 ≈ 7,4.
- Đáp án: **7,4**  (kiểm bằng `lam_tron(7.386,1)`)

**Bài 4** (B4, T6-10.3) ✅ Đạt

- Đề: Cho hai số 15 và 60. Tính tỉ số phần trăm của 15 so với 60.
- Lời giải: Tỉ số 15 : 60 = 0,25. Nhân 100% được 25%.
- Đáp án: **25**  (kiểm bằng `15/60*100`)

**Bài 5** (B5, T6-10.3, T6-10.1) ✅ Đạt

- Đề: Một chiếc áo giá 150 000 đồng được giảm 20%. Hỏi người mua phải trả bao nhiêu đồng sau khi giảm (làm tròn tới đồng)?
- Lời giải: Số tiền giảm là 150 000·20% = 150 000·0,20 = 30 000. Số phải trả = 150 000 - 30 000 = 120 000 đồng.
- Đáp án: **120000**  (kiểm bằng `150000-150000*0.20`)

**Bài 6** (B6, T6-10.3, T6-10.2) ✅ Đạt

- Đề: Trong một lớp 28 học sinh có 11 bạn đọc sách mỗi tuần. Tính tỉ số phần trăm học sinh đọc sách trong lớp, làm tròn kết quả đến 1 chữ số thập phân.
- Lời giải: Tỉ số = 11 : 28 ≈ 0,392857...; nhân 100% được 39,2857...%. Làm tròn đến 1 chữ số thập phân: 39,3%.
- Đáp án: **39,3**  (kiểm bằng `lam_tron(11/28*100,1)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
