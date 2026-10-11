# Bản giáo viên · T6-06 · Bội chung. Bội chung nhỏ nhất

**Kiểm tra tự động:** 6/6 bài tập đạt. Mô hình: `gpt-5-mini`.

Các vòng sửa: vòng 0: 6/6 bài tập đạt

## Yêu cầu cần đạt

| Mã | Nội dung | Bài tập |
|---|---|---|
| T6-06.1 | Xác định được bội chung, bội chung nhỏ nhất của hai hoặc ba số tự nhiên. | B1, B2, B5 |
| T6-06.2 | Thực hiện được phép cộng, phép trừ phân số bằng cách quy đồng mẫu số với bội chung nhỏ nhất. | B3, B4, B6 |

## Bài tập và đáp án

**Bài 1** (B1, T6-06.1) ✅ Đạt

- Đề: Tìm bội chung nhỏ nhất của 4 và 10.
- Lời giải: Phân tích: 4 = 2², 10 = 2·5. Lấy các lũy thừa lớn nhất: 2² và 5. BCNN = 2²·5 = 20.
- Đáp án: **20**  (kiểm bằng `bcnn(4,10)`)

**Bài 2** (B2, T6-06.1) ✅ Đạt

- Đề: Tìm bội chung nhỏ nhất của 8, 12 và 15.
- Lời giải: Phân tích: 8 = 2³, 12 = 2²·3, 15 = 3·5. Lấy các lũy thừa lớn nhất: 2³, 3, 5. BCNN = 2³·3·5 = 120.
- Đáp án: **120**  (kiểm bằng `bcnn(8,12,15)`)

**Bài 3** (B3, T6-06.2) ✅ Đạt

- Đề: Tính 3/4 + 5/6 bằng cách quy đồng mẫu số với BCNN.
- Lời giải: Mẫu số 4 và 6 có BCNN = 12. Quy đồng: 3/4 = 9/12, 5/6 = 10/12. Tổng = 9/12 + 10/12 = 19/12. Kết quả tối giản 19/12.
- Đáp án: **19/12**  (kiểm bằng `phan_so(3*3+5*2,12)`)

**Bài 4** (B4, T6-06.2) ✅ Đạt

- Đề: Tính 7/8 - 1/3 bằng cách quy đồng mẫu số với BCNN.
- Lời giải: Mẫu số 8 và 3 có BCNN = 24. Quy đồng: 7/8 = 21/24, 1/3 = 8/24. Hiệu = 21/24 - 8/24 = 13/24.
- Đáp án: **13/24**  (kiểm bằng `phan_so(7*3-1*8,24)`)

**Bài 5** (B5, T6-06.1) ✅ Đạt

- Đề: Hai xe buýt cùng khởi hành từ bến. Xe A lặp lại sau mỗi 12 phút, xe B lặp lại sau mỗi 18 phút. Sau bao nhiêu phút lần đầu tiên cả hai cùng có mặt ở bến đồng thời?
- Lời giải: Ta cần BCNN của 12 và 18. BCNN = 36. Vậy sau 36 phút cả hai cùng có mặt.
- Đáp án: **36**  (kiểm bằng `bcnn(12,18)`)

**Bài 6** (B6, T6-06.2) ✅ Đạt

- Đề: Cần 2/3 lít sữa và 1/4 lít nước cho một món. Hỏi tổng thể tích chất lỏng cần cho món là bao nhiêu lít?
- Lời giải: Mẫu số 3 và 4 có BCNN = 12. Quy đồng: 2/3 = 8/12, 1/4 = 3/12. Tổng = 8/12 + 3/12 = 11/12 lít.
- Đáp án: **11/12**  (kiểm bằng `phan_so(2*4+1*3,12)`)

## Việc giáo viên cần xem

- Lời văn có phù hợp học sinh lớp 6 không; tình huống thực tế có hợp lí không.
- Lời giải có đúng cách trình bày của lớp không (máy chỉ kiểm đáp án cuối).
- Không có câu chữ, hình hay bài tập nào giống sách giáo khoa.
- Điền trang đối chiếu SGK và tên người duyệt trước khi in.
