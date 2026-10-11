# Bản giáo viên · T6-05 · Ước chung. Ước chung lớn nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-05.1 | Xác định được ước chung, ước chung lớn nhất của hai hoặc ba số tự nhiên. | B1, B2, B3, B4, B6 |
| T6-05.2 | Nhận biết được phân số tối giản; dùng ước chung lớn nhất để rút gọn phân số về phân số tối giản. | B3, B5, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-05.1) ✅ Đạt

- Đề: Ước chung lớn nhất của 12 và 18 bằng bao nhiêu?
- Lời giải: Các ước của 12: 1, 2, 3, 4, 6, 12. Các ước của 18: 1, 2, 3, 6, 9, 18. Các ước chung: 1, 2, 3, 6. ƯCLN = 6.
- Đáp án: **6**  (kiểm bằng `ucln(12,18)`)

**Bài 2** (B2, T6-05.1) ✅ Đạt

- Đề: Ước chung lớn nhất của ba số 8, 12 và 20 là bao nhiêu?
- Lời giải: Các ước chung của 8, 12, 20 là 1, 2, 4. ƯCLN = 4.
- Đáp án: **4**  (kiểm bằng `ucln(8,12,20)`)

**Bài 3** (B3, T6-05.2, T6-05.1) ✅ Đạt

- Đề: Rút gọn phân số 18/24 về phân số tối giản.
- Lời giải: Tìm ƯCLN của 18 và 24 là 6. Chia tử và mẫu cho 6: 18:6 = 3, 24:6 = 4. Kết quả 3/4 là tối giản.
- Đáp án: **3/4**  (kiểm bằng `phan_so(18,24)`)

**Bài 4** (B4, T6-05.1) ✅ Đạt

- Đề: Một nhóm tình nguyện có 18 cờ đỏ và 30 cờ xanh. Họ muốn chia số cờ thành các gói giống nhau sao cho mỗi gói có cùng số cờ đỏ và cùng số cờ xanh, và số gói là lớn nhất. Hỏi có thể chia thành bao nhiêu gói?
- Lời giải: Số gói là ƯCLN của 18 và 30, ƯCLN = 6. Vậy chia được 6 gói.
- Đáp án: **6**  (kiểm bằng `ucln(18,30)`)

**Bài 5** (B5, T6-05.2) ✅ Đạt

- Đề: Một chiếc áo giá 150 000 đồng, một chiếc quần giá 45 000 đồng. Viết tỉ số giá áo so với giá quần dưới dạng phân số rồi rút gọn phân số đó.
- Lời giải: Tỉ số ban đầu là 150 000/45 000. ƯCLN của 150 000 và 45 000 là 15 000. Chia cả hai cho 15 000 được 10/3. Phân số tối giản là 10/3.
- Đáp án: **10/3**  (kiểm bằng `phan_so(150000,45000)`)

**Bài 6** (B6, T6-05.2, T6-05.1) ✅ Đạt

- Đề: Rút gọn phân số 84/126 về phân số tối giản.
- Lời giải: ƯCLN của 84 và 126 là 42. Chia tử và mẫu cho 42: 84:42 = 2, 126:42 = 3. Phân số tối giản là 2/3.
- Đáp án: **2/3**  (kiểm bằng `phan_so(84,126)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
