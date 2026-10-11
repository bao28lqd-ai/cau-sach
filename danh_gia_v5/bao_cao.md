# Báo cáo đánh giá bộ sinh Phiếu Cầu

## 1. Sinh phiếu

20 phiếu; mô hình: gpt-5-mini; phiên bản câu lệnh: 2026-10-07.4.
Vòng 0 là kết quả soạn một lần; cột bên phải là sau tối đa 2 vòng sửa.

| Chỉ số | Soạn một lần | Sau vòng sửa |
|---|---|---|
| Bài tập đạt cả bốn lớp kiểm tra | 116/120 (97%) | 121/121 (100%) |
| Phiếu đạt hoàn toàn | 16/20 (80%) | 20/20 (100%) |

Lỗi ở vòng 0:

| Loại | Số bài |
|---|---|
| Lỗi biểu thức | 1 |
| Đề hỏi nhiều ý | 1 |
| Biểu thức không khớp đề | 1 |
| Làm tròn không thay đổi số | 1 |

Trong 4 bài lỗi ở vòng 0, 0 là lỗi của bước đọc lại (hệ thống), 4 là lỗi nội dung của bài. Sau vòng sửa, 4/4 (100%) bài này đạt.

Vòng sửa thêm 1 bài tập mới để phủ yêu cầu cần đạt còn thiếu.

Chi phí: 49 lần gọi, 36.477 token vào, 53.772 token ra; khoảng 0,117 USD tổng, 0,58 cent mỗi phiếu theo giá niêm yết của OpenAI. Thời gian trung bình 23 giây mỗi phiếu.

## 2. Thử bộ kiểm tra bằng lỗi cài sẵn

Lấy các bài đã đạt, cài một lỗi đã biết, rồi xem bộ kiểm tra có bắt được không.

| Loại lỗi cài | Số ca | Bắt được (đủ 4 lớp) | Bắt được (bỏ lớp 4) |
|---|---|---|---|
| Đổi đáp án | 121 | 121/121 (100%) | 121/121 (100%) |
| Đúng giá trị, sai dạng | 100 | 100/100 (100%) | 100/100 (100%) |
| Đổi số trong biểu thức, đáp án tính lại cho khớp | 103 | 103/103 (100%) | 0/103 (0%) |
| Đổi số trong đề (mô hình đọc lại) | 94 | 93/94 (99%) | — |
| Thêm câu hỏi thứ hai vào đề (mô hình đọc lại) | 121 | 121/121 (100%) | — |

Báo nhầm khi đọc lại đề gốc (không cài lỗi): 2/121 (2%).

Với câu hỏi thêm vào: 18 ca được nhận ra là đề hỏi nhiều ý; 102 ca bị bắt vì mô hình tính luôn câu hỏi thứ hai nên giá trị đổi.
Phần đọc lại tốn 20 lần gọi, 35.152 token.

Ba hàng đầu không gọi mô hình. Hàng thứ ba dùng lần đọc lại đã lưu của đề gốc, nên nó cho thấy lớp 4 là lớp duy nhất bắt được loại lỗi này, chứ không đo khả năng đọc của mô hình. Hai hàng sau mới đo khả năng đó, vì mô hình phải đọc lại đề đã bị sửa.

## 3. Duyệt nội dung

Người chấm: không ghi.

20 bài được chấm; 0/20 (0%) có ít nhất một tiêu chí không đạt.

| Tiêu chí | Đạt | Không đạt |
|---|---|---|
| Câu chữ tự nhiên, đúng tiếng Việt, hợp với học sinh lớp 6 | 20 | 0 |
| Tình huống và số liệu hợp lí (để trống nếu không phải bài có tình huống) | 0 | 0 |
| Bài có giá trị luyện tập, không hiển nhiên đến mức vô nghĩa | 20 | 0 |
| Bài thực sự luyện đúng các yêu cầu cần đạt được gắn | 20 | 0 |
| Lời giải đúng và trình bày phù hợp lớp 6 | 20 | 0 |

## Giới hạn

- Số phiếu và số bài còn nhỏ; tỷ lệ chỉ nên đọc như ước lượng thô.
- Lỗi cài sẵn là lỗi nhân tạo; lỗi thật của mô hình có thể khác.
- Bước đọc lại đề dùng cùng mô hình với bước soạn, nên hai lần có thể sai giống nhau.
- Phần 3 do một người chấm; nên có thêm giáo viên duyệt độc lập.
