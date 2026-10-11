# Báo cáo đánh giá bộ sinh Phiếu Cầu

## 1. Sinh phiếu

20 phiếu; mô hình: gpt-5-mini; phiên bản câu lệnh: 2026-10-07.3.
Vòng 0 là kết quả soạn một lần; cột bên phải là sau tối đa 2 vòng sửa.

| Chỉ số | Soạn một lần | Sau vòng sửa |
|---|---|---|
| Bài tập đạt cả bốn lớp kiểm tra | 94/120 (78%) | 128/128 (100%) |
| Phiếu đạt hoàn toàn | 15/20 (75%) | 16/20 (80%) |

Lỗi ở vòng 0:

| Loại | Số bài |
|---|---|
| Chưa đối chiếu được với đề | 24 |
| Đề hỏi nhiều ý | 2 |

Vòng sửa làm đạt 26/26 (100%) bài lỗi ở vòng 0.

Chi phí: 58 lần gọi, 43,284 token vào, 63,702 token ra; khoảng 0.138 USD tổng, 0.69 cent mỗi phiếu (theo giá niêm yết trong `PRICES`). Thời gian trung bình 28 giây mỗi phiếu.

## 2. Thử bộ kiểm tra bằng lỗi cài sẵn

Lấy các bài đã đạt, cài một lỗi đã biết, rồi xem bộ kiểm tra có bắt được không.

| Loại lỗi cài | Số ca | Bắt được (đủ 4 lớp) | Bắt được (bỏ lớp 4) |
|---|---|---|---|
| Đổi đáp án | 128 | 128/128 (100%) | 128/128 (100%) |
| Đúng giá trị, sai dạng | 112 | 112/112 (100%) | 112/112 (100%) |
| Đổi số trong biểu thức, đáp án tính lại cho khớp | 113 | 113/113 (100%) | 0/113 (0%) |
| Đổi số trong đề (mô hình đọc lại) | 103 | 101/103 (98%) | — |
| Thêm câu hỏi thứ hai vào đề (mô hình đọc lại) | 128 | 128/128 (100%) | — |

Báo nhầm khi đọc lại đề gốc (không cài lỗi): 0/128 (0%).

## 3. Duyệt thủ công

Chưa có dữ liệu. Chạy `python -m causach danhgia mau-thu-cong`, điền tệp `thu_cong.xlsx`, rồi tổng hợp lại.

## Giới hạn

- Số phiếu và số bài còn nhỏ; tỷ lệ chỉ nên đọc như ước lượng thô.
- Lỗi cài sẵn là lỗi nhân tạo; lỗi thật của mô hình có thể khác.
- Bước đọc lại đề dùng cùng mô hình với bước soạn, nên hai lần có thể sai giống nhau.
- Duyệt thủ công do một người làm; nên có thêm giáo viên duyệt độc lập.
