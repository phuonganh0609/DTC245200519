# Đề 36: Hệ thống Quản lý Chung cư / Căn hộ

Mã số sinh viên: DTC245200519.

Dự án thực hành môn Triển khai và Quản trị Hệ thống Phần mềm, căn cứ vào đề 36 và yêu cầu chung trong tài liệu được cung cấp.

## Phạm vi

Website quản lý cư dân, phí dịch vụ, thông báo và khiếu nại. Cơ sở dữ liệu PostgreSQL, công cụ quản trị pgAdmin. Tất cả dịch vụ triển khai bằng Docker Compose; tích hợp Nginx, Prometheus, Grafana, Loki và Promtail.

## Trạng thái thực hành

Đã triển khai web Python, PostgreSQL và pgAdmin bằng Compose, chạy trên Ubuntu WSL2 với Docker Desktop theo lựa chọn của người học. Website có xem/thêm/sửa/xóa trong bốn nhóm chức năng; phí và khiếu nại có cập nhật trạng thái. Dữ liệu mẫu giả lập đã được người học cho phép.

Đã kiểm chứng kết nối DB, bốn trang chức năng, thao tác thêm/sửa/xóa cư dân, bảo vệ CSRF, user non-root và quyền DB hạn chế. Đã đăng nhập và kết nối pgAdmin với PostgreSQL.

Đã triển khai Nginx reverse proxy và kiểm tra ba security headers trên các trang chức năng và phản hồi lỗi 404. Website tại cổng 8036 đi qua Nginx; container web chỉ truy cập trong mạng Docker. Phần này dùng HTTP với security headers theo lựa chọn được đề tài cho phép, chưa có HTTPS.

Đã tích hợp Prometheus và Grafana: bốn targets UP, metrics container/Nginx/PostgreSQL có dữ liệu thật. Dashboard riêng của đề 36 được provision từ file JSON trong repository.

Chưa hoàn thành Loki/Promtail và nghiệm thu hardening tổng thể; chưa đạt toàn bộ tiêu chí.

## Chạy trong Ubuntu WSL2

Điều kiện: Docker Desktop đang chạy và Ubuntu đã được tích hợp với Docker Desktop. Chạy các lệnh trong thư mục dự án:

```bash
python3 scripts/prepare-env.py
docker compose up -d --build
bash scripts/start-monitoring.sh
bash scripts/verify.sh
python3 scripts/verify-nginx.py
python3 scripts/verify-monitoring.py
```

- Website qua Nginx: http://localhost:8036
- pgAdmin: http://localhost:8136
- Prometheus Targets: http://localhost:9036/targets
- Dashboard Grafana: http://localhost:3036/d/de36-monitoring
- Grafana: tài khoản `admin`, mật khẩu từ `GRAFANA_PASSWORD` trong `.env`.
- Thông tin đăng nhập pgAdmin nằm trong `.env`: `PGADMIN_EMAIL`, `PGADMIN_PASSWORD`.
- Đăng ký server trong pgAdmin: host `db`, port `5432`, database `chungcu_dtc245200519`, username từ `POSTGRES_USER`, password từ `POSTGRES_PASSWORD`.

Lệnh `prepare-env.py` tạo `.env` hoặc bổ sung biến còn thiếu, không ghi đè giá trị đã có. `.env` không được commit. Các giao diện chỉ mở trên localhost. PostgreSQL và exporters không publish cổng ra máy host.

`start-monitoring.sh` tạo tài khoản DB đọc thống kê và khởi động stack giám sát. Khi dùng Docker Desktop từ WSL, script gọi `docker.exe` cho riêng cAdvisor để mount đúng filesystem Linux của Docker Desktop. Sau khi thay cấu hình hay dựng lại bằng `docker compose up`, chạy lại script này nếu metrics container chưa xuất hiện. Chờ khoảng 30–60 giây để có đủ mẫu cho các biểu đồ `rate`.

```bash
docker compose ps                  # Xem trạng thái
docker compose logs --tail 30 web  # Xem log web
docker compose stop               # Dừng dịch vụ, giữ dữ liệu
docker compose start              # Chạy lại
```

Volume `db_data` và `pgadmin_data` giữ dữ liệu. Script `db/init.sh` chỉ chạy lúc volume PostgreSQL còn trống; không dùng `docker compose down -v` khi cần giữ dữ liệu.

## Tài liệu dự án

- [Checklist tiêu chí và tiến độ](docs/checklist.md)
- [Khung báo cáo thực hành](docs/bao-cao-thuc-hanh.md)
- [Bước 1: web, database và hướng dẫn chụp minh chứng](docs/buoc-01-web-db.md)
- [Bước 2: Nginx reverse proxy và security headers](docs/buoc-02-nginx.md)
- [Bước 3: Giám sát bằng Prometheus và Grafana](docs/buoc-03-giam-sat.md)

## Quy tắc thực hiện

- Chỉ thực hiện theo các tài liệu người học đã cung cấp.
- Không tự chụp ảnh. Mở phần cần minh chứng để người học tự chụp.
- Không thêm dữ liệu ngoài hoặc dữ liệu mẫu khi chưa được cho phép.
- Báo rõ yêu cầu phát sinh; hướng dẫn viết báo cáo theo từng nhiệm vụ.
- Commit và push sau mỗi nhiệm vụ hoàn thành.

