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

- Đề: Tìm ước chung lớn nhất của 12 và 18.
- Lời giải: Các ước của 12: 1, 2, 3, 4, 6, 12. Các ước của 18: 1, 2, 3, 6, 9, 18. Ước chung lớn nhất là 6.
- Đáp án: **6**  (kiểm bằng `ucln(12,18)`)

**Bài 2** (B2, T6-05.1) ✅ Đạt

- Đề: Tìm ước chung lớn nhất của 24, 36 và 60.
- Lời giải: ƯCLN của 24, 36, 60 là 12.
- Đáp án: **12**  (kiểm bằng `ucln(24,36,60)`)

**Bài 3** (B3, T6-05.2) ✅ Đạt

- Đề: Rút gọn phân số 18/24 về phân số tối giản.
- Lời giải: ƯCLN(18,24)=6. Chia tử và mẫu cho 6, được 3/4.
- Đáp án: **3/4**  (kiểm bằng `phan_so(18,24)`)

**Bài 4** (B4, T6-05.1) ✅ Đạt

- Đề: Có hai dây dài 150 cm và 210 cm. Cắt đều hai dây thành các đoạn có cùng độ dài là số nguyên cm và dùng hết. Độ dài lớn nhất mỗi đoạn là bao nhiêu?
- Lời giải: Độ dài lớn nhất là ƯCLN(150,210)=30 cm.
- Đáp án: **30**  (kiểm bằng `ucln(150,210)`)

**Bài 5** (B5, T6-05.1) ✅ Đạt

- Đề: Có 96 cây viết và 160 thước kẻ. Chia đều vào các phần quà sao cho mỗi phần có cùng số đồ vật và dùng hết. Tối đa mỗi phần có bao nhiêu đồ vật?
- Lời giải: Số đồ vật tối đa mỗi phần là ƯCLN(96,160)=32.
- Đáp án: **32**  (kiểm bằng `ucln(96,160)`)

**Bài 6** (B6, T6-05.2) ✅ Đạt

- Đề: Rút gọn phân số 210/462 về phân số tối giản.
- Lời giải: ƯCLN(210,462)=42. Chia tử và mẫu cho 42: 210:42 = 5, 462:42 = 11. Phân số tối giản là 5/11.
- Đáp án: **5/11**  (kiểm bằng `phan_so(210,462)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
