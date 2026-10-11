# Bản giáo viên · T6-05 · Ước chung. Ước chung lớn nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-05.1 | Xác định được ước chung, ước chung lớn nhất của hai hoặc ba số tự nhiên. | B1, B2, B4, B5 |
| T6-05.2 | Nhận biết được phân số tối giản; dùng ước chung lớn nhất để rút gọn phân số về phân số tối giản. | B3, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-05.1) ✅ Đạt

- Đề: Tìm ƯCLN của 12 và 30.
- Lời giải: ƯCLN(12, 30) = 6 vì các ước chung là 1, 2, 3, 6. Lớn nhất là 6.
- Đáp án: **6**  (kiểm bằng `ucln(12, 30)`)

**Bài 2** (B2, T6-05.1) ✅ Đạt

- Đề: Tìm ƯCLN của 12, 30 và 18.
- Lời giải: ƯCLN(12, 30, 18) = 6 vì 6 chia hết cho cả ba số và không có ước chung lớn hơn.
- Đáp án: **6**  (kiểm bằng `ucln(12, 30, 18)`)

**Bài 3** (B3, T6-05.2) ✅ Đạt

- Đề: Rút gọn phân số 14/21 xuống phân số tối giản.
- Lời giải: ƯCLN(14, 21) = 7. Chia cả tử và mẫu cho 7 được 2/3, phân số tối giản là 2/3.
- Đáp án: **2/3**  (kiểm bằng `phan_so(14, 21)`)

**Bài 4** (B4, T6-05.1) ✅ Đạt

- Đề: Hai đoạn dây dài 150 cm và 210 cm. Cắt thành các đoạn có cùng độ dài lớn nhất là bao nhiêu xăngti mét, sao cho không còn dây thừa?
- Lời giải: Độ dài mỗi đoạn là ƯCLN(150, 210) = 30 cm. Ta có thể chia đều và không còn dây thừa.
- Đáp án: **30**  (kiểm bằng `ucln(150, 210)`)

**Bài 5** (B5, T6-05.1) ✅ Đạt

- Đề: Một cửa hàng có hộp kẹo 45 viên và 60 viên. Muốn chia đều thành các gói có cùng số viên và số viên trong mỗi gói lớn nhất là bao nhiêu?
- Lời giải: Số viên mỗi gói lớn nhất là ƯCLN(45, 60) = 15 viên.
- Đáp án: **15**  (kiểm bằng `ucln(45, 60)`)

**Bài 6** (B6, T6-05.2) ✅ Đạt

- Đề: Rút gọn phân số 462/770 về phân số tối giản.
- Lời giải: ƯCLN(462, 770) = 154. Chia cả tử và mẫu cho 154 được 3/5. Phân số tối giản là 3/5.
- Đáp án: **3/5**  (kiểm bằng `phan_so(462, 770)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
