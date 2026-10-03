# Khung báo cáo thực hành đề 36

Đây là khung để viết dần trong quá trình làm. Chưa phải báo cáo hoàn thành và chưa xác nhận đủ 10 trang. Chỉ ghi kết quả sau khi kiểm tra thực tế.

## Bìa

- Trường/khoa: [người học bổ sung]
- Môn: Triển khai và Quản trị Hệ thống Phần mềm
- Đề 36: Hệ thống Quản lý Chung cư / Căn hộ
- Sinh viên: [người học bổ sung]
- Mã số sinh viên: DTC245200519
- Lớp: [người học bổ sung]
- Giảng viên: [người học bổ sung]

Trình bày bìa theo mẫu báo cáo thực tập của người học. Không tự điền thông tin chưa được cung cấp.

## 1. Mục tiêu và phạm vi

Đoạn có thể dùng ngay:

“Đề tài thực hành triển khai website quản lý chung cư/căn hộ với các chức năng quản lý cư dân, phí dịch vụ, thông báo và khiếu nại. Hệ thống sử dụng PostgreSQL và pgAdmin, được triển khai bằng Docker Compose. Nội dung thực hành bao gồm quản lý mã nguồn trên GitHub, cấu hình Nginx reverse proxy, giám sát bằng Prometheus và Grafana, thu thập log bằng Loki và Promtail, và áp dụng các biện pháp củng cố bảo mật.”

## 2. Môi trường và kiến trúc

Sau khi xác minh môi trường, ghi hệ điều hành, tài nguyên máy, phiên bản Docker/Compose thực tế. Mô tả từng dịch vụ, các network và volume, luồng trình duyệt → Nginx → web → PostgreSQL.

[Ảnh người học tự chụp: phiên bản công cụ và trạng thái dịch vụ. Chưa đến bước chụp.]

## 3. Quản lý mã nguồn trên GitHub

Repository: https://github.com/phuonganh0609/DTC245200519

Giải thích mã nguồn và cấu hình nằm ở đâu; README dùng để làm gì; ghi commit thực tế theo từng nhiệm vụ. Không đưa mật khẩu, token hay khóa riêng vào báo cáo hoặc Git.

[Ảnh người học tự chụp: repository và lịch sử commit.]

## 4. Triển khai website, PostgreSQL và pgAdmin

Mô tả bốn nhóm chức năng theo đề; giải thích kết nối DB, lưu trữ bằng volume và vai trò pgAdmin. Ghi từng bước chạy, kết quả mong đợi, kết quả thực tế và lỗi đã xử lý. Dữ liệu sử dụng phải được người học cho phép.

[Ảnh người học tự chụp: website, pgAdmin và thao tác kiểm chứng được phép.]

## 5. Nginx reverse proxy

Giải thích reverse proxy; trình bày cấu hình đã triển khai, cách truy cập và HTTPS hoặc security headers. Ghi kết quả kiểm tra thực tế.

[Ảnh người học tự chụp: web qua Nginx và kiểm tra HTTPS/headers.]

## 6. Prometheus và Grafana

Giải thích metrics và vai trò thu thập/hiển thị. Trình bày cách giám sát container, web server và PostgreSQL, các target và dashboard thực tế. Giải thích ý nghĩa chỉ số hiển thị.

[Ảnh người học tự chụp: Prometheus Targets và dashboard đủ ba nhóm.]

## 7. Loki, Promtail và LogQL

Giải thích đường đi của log. Ghi 2–3 truy vấn phù hợp nhãn thực tế của hệ thống, kết quả và ý nghĩa từng truy vấn. Chỉ ghi truy vấn đã chạy thành công.

[Ảnh người học tự chụp: mỗi truy vấn và kết quả log.]

## 8. Hardening

Với ít nhất 3–4 biện pháp, ghi: vấn đề cần xử lý → cấu hình áp dụng → cách kiểm tra → kết quả. Các biện pháp trong đề gồm non-root container, network isolation, mật khẩu mạnh, security headers và hạn chế quyền DB.

[Ảnh người học tự chụp: cấu hình và kiểm chứng. Che thông tin bí mật khi tự chụp.]

## 9. Kiểm thử tổng thể và kết luận

Đối chiếu checklist; mô tả cách khởi động hệ thống bằng Compose, các thành phần demo và kết quả. Liệt kê trung thực phần chưa đạt nếu có.

## Phân bổ dung lượng gợi ý

Đề yêu cầu tối thiểu 10 trang nhưng không nêu cách tính bìa/mục lục. Nên chuẩn bị ít nhất 10 trang nội dung: mục tiêu 1 trang; môi trường/kiến trúc 1; GitHub 1; web/DB 2; Nginx 1; giám sát 1; log 1; hardening 1; kiểm thử/kết luận 1. Điều chỉnh theo nội dung và ảnh thực tế, không kéo dài bằng kết quả chưa thực hiện.
