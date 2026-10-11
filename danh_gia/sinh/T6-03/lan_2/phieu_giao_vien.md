# Bản giáo viên · T6-03 · Thứ tự thực hiện các phép tính

**Kiểm tra tự động:** 8/8 bài tập đạt; mã yêu cầu cần đạt không tồn tại: Nhận dạng một lũy thừa từ kết quả phép tính, Thực hiện phép tính theo thứ tự, Tính khối lượng còn lại sau khi bốc, dỡ, Tính tiền phải trả sau khi giảm giá. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 0/6 bài tập đạt; thiếu bài cho T6-03.1, T6-03.2 → vòng 1: 6/6 bài tập đạt; thiếu bài cho T6-03.1, T6-03.2; mã yêu cầu cần đạt không tồn tại: Nhận dạng một lũy thừa từ kết quả phép tính, Thực hiện phép tính theo thứ tự, Tính khối lượng còn lại sau khi bốc, dỡ, Tính tiền phải trả sau khi giảm giá → vòng 2: 8/8 bài tập đạt; mã yêu cầu cần đạt không tồn tại: Nhận dạng một lũy thừa từ kết quả phép tính, Thực hiện phép tính theo thứ tự, Tính khối lượng còn lại sau khi bốc, dỡ, Tính tiền phải trả sau khi giảm giá

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-03.1 | Nhận biết được thứ tự thực hiện các phép tính. | B7 |
| T6-03.2 | Vận dụng được các tính chất của phép tính, kể cả phép tính lũy thừa, để tính giá trị biểu thức. | B8 |

## Bài tập và đáp án

**Bài 1** (B1, Thực hiện phép tính theo thứ tự) ✅ Đạt

- Đề: Tính giá trị biểu thức 5 + 4·3.
- Lời giải: Thực hiện phép nhân trước: 4·3 = 12; rồi cộng: 5 + 12 = 17.
- Đáp án: **17**  (kiểm bằng `5 + 4*3`)

**Bài 2** (B2, Thực hiện phép tính theo thứ tự) ✅ Đạt

- Đề: Tính giá trị biểu thức 3·(2 + 5) - 4.
- Lời giải: Tính trong ngoặc trước: 2 + 5 = 7; nhân: 3·7 = 21; rồi trừ: 21 - 4 = 17.
- Đáp án: **17**  (kiểm bằng `3*(2 + 5) - 4`)

**Bài 3** (B3, Thực hiện phép tính theo thứ tự) ✅ Đạt

- Đề: Tính giá trị biểu thức 2³·3 + 4 : 2.
- Lời giải: Tính lũy thừa trước: 2³ = 8; nhân: 8·3 = 24; phép chia 4 : 2 = 2; rồi cộng: 24 + 2 = 26.
- Đáp án: **26**  (kiểm bằng `2**3*3 + 4/2`)

**Bài 4** (B4, Nhận dạng một lũy thừa từ kết quả phép tính) ✅ Đạt

- Đề: Tính giá trị biểu thức (2²)³ : 2⁴ và viết kết quả dưới dạng một lũy thừa của 2.
- Lời giải: Tính: (2²)³ = 4³ = 64 và 2⁴ = 16; chia: 64 : 16 = 4 = 2².
- Đáp án: **2²**  (kiểm bằng `(2**2)**3 / 2**4`)

**Bài 5** (B5, Tính tiền phải trả sau khi giảm giá) ✅ Đạt

- Đề: Một chiếc áo giá 150 000 đồng. Người ta mua 3 chiếc và được giảm 20 000 đồng cho cả đơn hàng. Hỏi người đó phải trả bao nhiêu đồng?
- Lời giải: Tiền trước giảm: 150 000·3 = 450 000 đồng; trừ giảm giá: 450 000 - 20 000 = 430 000 đồng.
- Đáp án: **430000**  (kiểm bằng `150000*3 - 20000`)

**Bài 6** (B6, Tính khối lượng còn lại sau khi bốc, dỡ) ✅ Đạt

- Đề: Một thùng nước nặng 12 kg. Người ta xếp 5 thùng lên xe rồi bỏ xuống 2 thùng. Hỏi khối lượng nước còn trên xe theo kg?
- Lời giải: Số thùng còn trên xe: 5 - 2 = 3 thùng; khối lượng: 12·3 = 36 kg.
- Đáp án: **36**  (kiểm bằng `12*5 - 12*2`)

**Bài 7** (B7, T6-03.1) ✅ Đạt

- Đề: Tính giá trị biểu thức 5 + 3 · 2².
- Lời giải: Thứ tự: tính lũy thừa trước, rồi nhân, sau cùng cộng. 2² = 4; 3 · 4 = 12; 5 + 12 = 17.
- Đáp án: **17**  (kiểm bằng `5+3*2**2`)

**Bài 8** (B8, T6-03.2) ✅ Đạt

- Đề: Dùng tính chất của lũy thừa để tính nhanh 12² · 12³.
- Lời giải: Khi nhân hai lũy thừa cùng cơ số thì cộng số mũ: 12² · 12³ = 12²⁺³ = 12⁵. Tính 12⁵ = 248 832.
- Đáp án: **248832**  (kiểm bằng `12**2*12**3`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
