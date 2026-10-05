# Checklist đề 36

Nguồn: mục Yêu cầu chung và Tiêu chí đánh giá, trang 1–2; Đề 36, trang 10, file De_Tai_Thuc_Hanh - TKQT HTPM K23.pdf. Các bài lab đã cung cấp dùng làm hướng dẫn thực hành.

Các ô chưa đánh dấu là công việc chưa được nghiệm thu. Danh sách minh chứng dưới đây là cách tổ chức báo cáo, không phải yêu cầu bổ sung của giảng viên.

| Tiêu chí | Điểm | Điều kiện nghiệm thu | Minh chứng người học tự chụp |
|---|---:|---|---|
| GitHub | 1,5 | Đủ mã nguồn và cấu hình; 3 commit có ý nghĩa; README hướng dẫn chạy | Repository và lịch sử commit |
| Web + DB | 1,5 | Web chạy ổn định, kết nối PostgreSQL; pgAdmin hoạt động | Web, kết quả thao tác được phép, pgAdmin |
| Nginx | 1,5 | Truy cập web qua reverse proxy; HTTPS hoặc security headers | Website qua Nginx và kết quả kiểm tra |
| Giám sát | 1,5 | Prometheus thu metrics; Grafana giám sát container, web, DB | Targets và dashboard có dữ liệu |
| Log | 1,5 | Loki + Promtail hoạt động; 2–3 query LogQL | Kết quả từng query với log thực tế |
| Hardening | 1,5 | Ít nhất 3–4 biện pháp bảo mật | Cấu hình và kết quả kiểm chứng từng biện pháp |
| Tổng thể | 1,0 | Compose chạy hoàn chỉnh; demo rõ, có minh chứng; hiểu bài | Trạng thái dịch vụ và phần giải thích |

## Nhiệm vụ

- [x] 01. Chuẩn bị checklist và khung báo cáo.
- [x] 02. Xác minh môi trường: Ubuntu WSL2, Docker Desktop theo lựa chọn người học; web Python; được phép dùng dữ liệu mẫu giả lập.
- [x] 03. Triển khai web đúng bốn nhóm chức năng, PostgreSQL và pgAdmin. Đã kiểm tra kết nối thật và CRUD cư dân; người học chưa chụp minh chứng.
- [x] 04. Triển khai Nginx reverse proxy và security headers (mốc commit 1 trong đề). Đã kiểm tra bốn trang chức năng, health endpoint và headers trên HTTP 404; người học tự chụp minh chứng.
- [ ] 05. Triển khai giám sát container, web, DB (mốc commit 2 trong đề).
- [ ] 06. Triển khai Loki + Promtail và 2–3 query LogQL (mốc commit 3 trong đề).
- [ ] 07. Kiểm chứng ít nhất 3–4 biện pháp hardening.
- [ ] 08. Hoàn thiện hướng dẫn chạy, báo cáo ít nhất 10 trang và demo.

Mỗi nhiệm vụ hoàn thành đều commit/push theo yêu cầu người học. Các commit chuẩn bị không thay thế ba mốc kỹ thuật Nginx, giám sát và log.

## Điều cần xác nhận

- Đã xác nhận Ubuntu WSL2 dùng Docker Desktop hiện có. Đây là lựa chọn người học cho phép, khác hướng dẫn cài Docker trực tiếp trong Ubuntu ở lab 3.
- Đã chọn web Python theo gợi ý đề 36.
- Đã được phép tạo dữ liệu mẫu giả lập; không thu thập dữ liệu người thật từ bên ngoài.
- Thông tin bìa còn thiếu: họ tên, lớp, giảng viên và thông tin trường/khoa theo mẫu người học sử dụng.
