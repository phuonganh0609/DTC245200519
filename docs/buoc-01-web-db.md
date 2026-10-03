# Bước 1: Triển khai ứng dụng và cơ sở dữ liệu

## 1. Mục đích

Hoàn thành phần ứng dụng + PostgreSQL + pgAdmin trong đề 36, làm nền cho Nginx, giám sát và log. Chưa nghiệm thu toàn bộ đề tài.

## 2. Môi trường thực tế

Ngày thực hành: 04/10/2026 (giờ Việt Nam).

- Ubuntu 24.04.1 LTS trên WSL2.
- Docker Desktop; Docker Engine 29.7.2; Compose trong Ubuntu v5.4.0.
- Docker chạy qua Docker Desktop theo lựa chọn của người học. `systemctl is-active docker` trả `inactive` trong Ubuntu vì daemon đang do Docker Desktop quản lý; không dùng kết quả đó để kết luận container không chạy.
- Python 3.12 trong container; Flask, Gunicorn và psycopg.
- PostgreSQL 16; pgAdmin 4 image 8.14.

## 3. Cấu trúc và nguyên lý

| Dịch vụ | Vai trò | Địa chỉ |
|---|---|---|
| web | Giao diện và xử lý bốn nhóm chức năng | http://localhost:8036 |
| db | Lưu dữ liệu PostgreSQL | Chỉ trong network Docker, host `db`, port 5432 |
| pgadmin | Công cụ quản trị PostgreSQL | http://localhost:8136 |

Trình duyệt gửi yêu cầu tới web; web dùng psycopg kết nối PostgreSQL với tài khoản `app_user`. PostgreSQL lưu dữ liệu trên volume `db_data`. pgAdmin kết nối cùng database qua mạng nội bộ. Cổng riêng tránh trùng các bài lab đã có trên máy.

Tên dự án Compose là `dtc245200519`. Không dùng `container_name` cố định để tránh trùng tên với bài lab khác.

## 4. Hướng dẫn chạy cho người mới

Mở Ubuntu WSL, chuyển vào thư mục dự án:

```bash
cd '/mnt/d/Câu hỏi ôn tập/Câu hỏi ôn tập kì 7/Triển khai và quản trị hệ thống phần mềm/DTC245200519'
python3 scripts/prepare-env.py
docker compose up -d --build
bash scripts/verify.sh
```

- `cd`: chuyển thư mục, để Compose tìm được `compose.yaml`.
- `prepare-env.py`: tạo cấu hình và mật khẩu ngẫu nhiên trong `.env` nếu chưa có.
- `up -d --build`: build image web và chạy dịch vụ ở nền.
- `verify.sh`: kiểm tra cấu hình, trạng thái và kết nối thật giữa web và DB. Nó tạo một bản ghi giả lập tạm thời để thử thêm/sửa/xóa, sau đó dọn bản ghi đó.

Dữ liệu khởi tạo: 3 cư dân giả lập, 2 khoản phí, 1 thông báo, 1 khiếu nại. Tất cả đều phục vụ thực hành, không đại diện cho người thật. ID có thể không liên tiếp sau phép thử, vì PostgreSQL không thu hồi số đã cấp; đây không phải lỗi mất dữ liệu.

## 5. pgAdmin

Đã đăng nhập pgAdmin và đăng ký server `De36 - PostgreSQL` thành công trong lần thực hành này. Khi cần làm lại trên máy khác:

1. Mở http://localhost:8136.
2. Đăng nhập bằng giá trị `PGADMIN_EMAIL` và `PGADMIN_PASSWORD` trong `.env`.
3. Chọn **Add New Server**. Name: `De36 - PostgreSQL`.
4. Trong Connection: Host `db`, Port `5432`, Maintenance database `chungcu_dtc245200519`, Username theo `POSTGRES_USER`, Password theo `POSTGRES_PASSWORD`.
5. Save. Mở Databases → chungcu_dtc245200519 → Schemas → public → Tables.

Không chọn Save password khi chưa muốn lưu mật khẩu trong pgAdmin. Mật khẩu không đưa vào ảnh hay báo cáo.

## 6. Kết quả đã kiểm tra

- DB và web chạy, healthcheck đạt.
- `/health` trả `{"status":"ok"}` sau truy vấn `SELECT 1` tới DB thật.
- Bốn trang chức năng trả HTTP 200.
- Thêm/sửa/xóa cư dân kiểm thử thành công, bản ghi kiểm thử đã được dọn.
- POST thiếu CSRF trả HTTP 400.
- Container web chạy `uid=100(app)`, không phải root.
- Tài khoản web không có quyền superuser, tạo database hoặc tạo role.
- pgAdmin đăng nhập được, kết nối được server PostgreSQL.

## 7. Ảnh cần người học tự chụp

Không có ảnh nào do trợ lý tự chụp. Giữ ảnh ở nơi người học chọn; chưa thêm file ảnh vào Git.

1. **Trang tổng quan**: http://localhost:8036. Chú thích: “Giao diện tổng quan của hệ thống quản lý chung cư”.
2. **Bốn trang chức năng**: cư dân, phí dịch vụ, thông báo, khiếu nại. Có thể dùng ảnh riêng từng trang. Chú thích nêu đúng chức năng và dữ liệu giả lập.
3. **pgAdmin**: cây database `chungcu_dtc245200519`, schema `public`, bốn bảng `residents`, `fees`, `announcements`, `complaints`. Chú thích: “Cơ sở dữ liệu PostgreSQL được quản trị bằng pgAdmin”.
4. **Terminal Ubuntu**: kết quả `docker compose ps` và `bash scripts/verify.sh`. Chú thích: “Kiểm tra trạng thái dịch vụ và kết nối ứng dụng với cơ sở dữ liệu”.

## 8. Đoạn viết vào báo cáo

Đưa vào mục Môi trường:

“Hệ thống được thực hành trên Ubuntu 24.04.1 LTS chạy bằng WSL2. Docker Desktop cung cấp Docker Engine; các lệnh Docker Compose được thực hiện trong terminal Ubuntu. Người học lựa chọn sử dụng môi trường Docker Desktop hiện có.”

Đưa vào mục Triển khai ứng dụng và cơ sở dữ liệu:

“Ứng dụng web sử dụng Python, Flask và Gunicorn, gồm bốn nhóm chức năng: cư dân, phí dịch vụ, thông báo và khiếu nại. PostgreSQL lưu trữ dữ liệu và pgAdmin cung cấp giao diện quản trị. Ba dịch vụ được khai báo trong Compose. Dữ liệu PostgreSQL được lưu trên volume để giữ lại khi container khởi động lại. Ứng dụng sử dụng tài khoản database riêng có quyền thao tác dữ liệu, không sử dụng tài khoản quản trị.”

Đưa vào mục Kết quả:

“Sau khi triển khai, website truy cập được tại cổng 8036 và pgAdmin tại cổng 8136 trên localhost. Endpoint kiểm tra sức khỏe trả trạng thái ok sau khi truy vấn database. Bốn trang chức năng hoạt động; phép thử thêm, sửa và xóa cư dân thành công. Dữ liệu ban đầu là dữ liệu giả lập được người học cho phép sử dụng.”

Chèn ảnh mình tự chụp ngay sau đoạn liên quan. Không ghi đã có Nginx, giám sát hay log ở giai đoạn này.

## 9. Vấn đề gặp và cách xử lý

pgAdmin từ chối email mẫu có đuôi `.invalid`. Đã đổi thành địa chỉ minh họa `dtc245200519@example.com` dùng làm tên đăng nhập nội bộ, rồi tạo lại container pgAdmin. Địa chỉ này không dùng để gửi email.
