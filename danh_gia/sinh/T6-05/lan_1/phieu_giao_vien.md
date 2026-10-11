# Bản giáo viên · T6-05 · Ước chung. Ước chung lớn nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-05.1 | Xác định được ước chung, ước chung lớn nhất của hai hoặc ba số tự nhiên. | B1, B2, B3, B5, B6 |
| T6-05.2 | Nhận biết được phân số tối giản; dùng ước chung lớn nhất để rút gọn phân số về phân số tối giản. | B4, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-05.1) ✅ Đạt

- Đề: Tìm ước chung lớn nhất của 12 và 18.
- Lời giải: Phân tích: 12 = 2²·3, 18 = 2·3² nên ƯCLN = 2·3 = 6.
- Đáp án: **6**  (kiểm bằng `ucln(12,18)`)

**Bài 2** (B2, T6-05.1) ✅ Đạt

- Đề: Tìm ước chung lớn nhất của 18, 24 và 30.
- Lời giải: ƯCLN(18,24,30) = 6 vì 18 = 2·3², 24 = 2³·3, 30 = 2·3·5 nên lấy các thừa số chung nhỏ nhất: 2·3 = 6.
- Đáp án: **6**  (kiểm bằng `ucln(18,24,30)`)

**Bài 3** (B3, T6-05.1) ✅ Đạt

- Đề: Tìm ƯCLN của 14 và 49.
- Lời giải: 49 = 7², 14 = 2·7 nên ƯCLN = 7.
- Đáp án: **7**  (kiểm bằng `ucln(14,49)`)

**Bài 4** (B4, T6-05.2) ✅ Đạt

- Đề: Rút gọn phân số 18/24 về phân số tối giản.
- Lời giải: ƯCLN(18,24) = 6. Chia cả tử và mẫu cho 6: 18:6 = 3, 24:6 = 4. Phân số tối giản là 3/4.
- Đáp án: **3/4**  (kiểm bằng `phan_so(18,24)`)

**Bài 5** (B5, T6-05.1) ✅ Đạt

- Đề: Có hai sợi dây dài 150 cm và 210 cm. Cắt chúng thành các đoạn dài bằng nhau (độ dài nguyên cm) sao cho mỗi đoạn dài nhất có thể. Hỏi mỗi đoạn dài bao nhiêu cm?
- Lời giải: Độ dài lớn nhất chia hết cả cho 150 và 210 là ƯCLN(150,210) = 30 cm. Vậy mỗi đoạn dài 30 cm.
- Đáp án: **30**  (kiểm bằng `ucln(150,210)`)

**Bài 6** (B6, T6-05.1, T6-05.2) ✅ Đạt

- Đề: Bạn và bạn thân có 150 000 đồng và 90 000 đồng. Muốn chia thành các phần bằng nhau, mỗi phần có giá trị lớn nhất có thể (số nguyên đồng). Hỏi mỗi phần bằng bao nhiêu đồng?
- Lời giải: Số tiền tối đa cho mỗi phần là ƯCLN(150000,90000) = 30000 đồng. Vậy mỗi phần 30 000 đồng.
- Đáp án: **30000**  (kiểm bằng `ucln(150000,90000)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
