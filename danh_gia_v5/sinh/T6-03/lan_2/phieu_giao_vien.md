# Bản giáo viên · T6-03 · Thứ tự thực hiện các phép tính

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-03.1 | Nhận biết được thứ tự thực hiện các phép tính. | B1, B3, B5, B6 |
| T6-03.2 | Vận dụng được các tính chất của phép tính, kể cả phép tính lũy thừa, để tính giá trị biểu thức. | B2, B3, B4, B5, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-03.1) ✅ Đạt

- Đề: Tính giá trị của biểu thức 3 + 5·2.
- Lời giải: Thực hiện nhân trước: 5·2 = 10. Rồi cộng: 3 + 10 = 13.
- Đáp án: **13**  (kiểm bằng `3+5*2`)

**Bài 2** (B2, T6-03.2) ✅ Đạt

- Đề: Tính giá trị của (2 + 3)·2³.
- Lời giải: Trong ngoặc 2 + 3 = 5. Tính lũy thừa 2³ = 8. Nhân: 5·8 = 40.
- Đáp án: **40**  (kiểm bằng `(2+3)*2**3`)

**Bài 3** (B3, T6-03.1, T6-03.2) ✅ Đạt

- Đề: Tính giá trị của 18 : 3 + 4·2.
- Lời giải: Thực hiện chia: 18 : 3 = 6. Thực hiện nhân: 4·2 = 8. Rồi cộng: 6 + 8 = 14.
- Đáp án: **14**  (kiểm bằng `18/3+4*2`)

**Bài 4** (B4, T6-03.2) ✅ Đạt

- Đề: Rút gọn và tính 2³·2², rồi viết kết quả dưới dạng một lũy thừa.
- Lời giải: Dùng tính chất lũy thừa: 2³·2² = 2³⁺² = 2⁵. Giá trị là 2⁵.
- Đáp án: **2⁵**  (kiểm bằng `2**3*2**2`)

**Bài 5** (B5, T6-03.1, T6-03.2) ✅ Đạt

- Đề: Ba chiếc áo mỗi chiếc giá 150 000 đồng. Tổng tiền được giảm 10%. Hỏi phải trả bao nhiêu đồng?
- Lời giải: Tổng tiền trước giảm: 3·150 000 = 450 000. Giảm 10% nghĩa là nhân 0,9: 450 000·0,9 = 405 000 đồng.
- Đáp án: **405000**  (kiểm bằng `3*150000*(1-0.1)`)

**Bài 6** (B6, T6-03.1, T6-03.2) ✅ Đạt

- Đề: Một quyển sách nặng 0,75 kg. Bảy quyển như vậy. Làm tròn tổng khối lượng đến kg gần nhất.
- Lời giải: Tổng khối lượng thực: 0,75·7 = 5,25 kg. Làm tròn đến kg gần nhất: 5,25 ≈ 5 kg.
- Đáp án: **5**  (kiểm bằng `lam_tron(0.75*7,0)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
