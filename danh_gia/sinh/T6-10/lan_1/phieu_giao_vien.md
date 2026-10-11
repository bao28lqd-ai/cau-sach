# Bản giáo viên · T6-10 · Số thập phân, làm tròn và tỉ số phần trăm

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-10.1 | Thực hiện được phép cộng, trừ, nhân, chia với số thập phân. | B1, B2, B4, B6 |
| T6-10.2 | Làm tròn được số thập phân đến một hàng cho trước. | B3, B6 |
| T6-10.3 | Tính được tỉ số và tỉ số phần trăm của hai số. | B4, B5 |

## Bài tập và đáp án

**Bài 1** (B1, T6-10.1) ✅ Đạt

- Đề: Tính 8,25 + 1,4.
- Lời giải: Đặt dọc theo dấu phẩy: 8,25 + 1,40 = 9,65. Kết quả là 9,65.
- Đáp án: **9,65**  (kiểm bằng `8.25+1.4`)

**Bài 2** (B2, T6-10.1) ✅ Đạt

- Đề: Tính 7,5 : 2,5.
- Lời giải: 7,5 : 2,5 = 3 vì 7,5 = 2,5 · 3. Kết quả là 3.
- Đáp án: **3**  (kiểm bằng `7.5/2.5`)

**Bài 3** (B3, T6-10.2) ✅ Đạt

- Đề: Làm tròn 3,276 đến một chữ số thập phân.
- Lời giải: Chữ số thứ hai sau dấu phẩy là 7 nên làm tròn 3,276 thành 3,3 khi làm tròn đến một chữ số thập phân.
- Đáp án: **3,3**  (kiểm bằng `lam_tron(3.276,1)`)

**Bài 4** (B4, T6-10.1, T6-10.3) ✅ Đạt

- Đề: Một áo giá 150 000 đồng giảm 20%. Tính số tiền giảm (đồng).
- Lời giải: Số tiền giảm = 150 000 · 20 : 100 = 30 000 đồng.
- Đáp án: **30000**  (kiểm bằng `150000*20/100`)

**Bài 5** (B5, T6-10.3) ✅ Đạt

- Đề: Trong lớp có 12 bạn nam và 8 bạn nữ. Tính phần trăm số bạn nam trên cả lớp.
- Lời giải: Tổng số học sinh = 12 + 8 = 20. Phần trăm nam = 12 : 20 · 100 = 60%. Kết quả là 60.
- Đáp án: **60**  (kiểm bằng `12/(12+8)*100`)

**Bài 6** (B6, T6-10.1, T6-10.2) ✅ Đạt

- Đề: Chuối giá 28 750 đồng mỗi kg. Mua 2,6 kg, tính tổng tiền sau đó làm tròn số tiền đến hàng nghìn gần nhất (đồng).
- Lời giải: Tổng tiền chưa làm tròn = 28 750 · 2,6 = 74 750 đồng. Làm tròn đến hàng nghìn gần nhất cho 74 750 → 75 000 đồng.
- Đáp án: **75000**  (kiểm bằng `lam_tron(28750*2.6,-3)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
