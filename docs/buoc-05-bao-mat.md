# Bước 5: Kiểm chứng bảo mật

Phạm vi theo tiêu chí hardening trong tài liệu đề tài: ít nhất 3–4 biện pháp. Dự án kiểm chứng năm nhóm dưới đây, không bổ sung dữ liệu nghiệp vụ. Người học tự chụp ảnh; không chụp `.env` hoặc kết quả `docker inspect`/`docker compose config` đầy đủ vì có thể chứa mật khẩu.

## 1. Chạy kiểm tra

Mở Docker Desktop, chờ Engine chạy. Trong Ubuntu WSL, chuyển vào thư mục dự án:

```bash
cd '/mnt/d/Câu hỏi ôn tập/Câu hỏi ôn tập kì 7/Triển khai và quản trị hệ thống phần mềm/DTC245200519'
python3 scripts/verify-hardening.py
```

Script đọc cấu hình container đang chạy, kiểm tra HTTP, truy vấn quyền PostgreSQL và kiểm tra Git. Không in giá trị bí mật, không thêm/sửa/xóa bản ghi. Chỉ ghi kết quả đạt sau khi script chạy thành công; lỗi kết nối Docker không có nghĩa cấu hình bảo mật sai.

Trong lần kiểm tra ngày 14/10/2026, sau khi bật Docker Desktop, Grafana không đọc được thư mục bind mount dashboard từ phiên WSL trước đó. Đã khôi phục bằng lệnh dưới đây trong PowerShell tại thư mục dự án, giữ nguyên volume. Sau đó bốn targets UP, các panel có dữ liệu và ba truy vấn log mới đều được kiểm tra thành công:

```powershell
docker compose up -d --no-deps --force-recreate grafana
```

## 2. Chụp ảnh theo thứ tự

Có thể chạy `bash scripts/minh-chung-bao-mat.sh` để giữ terminal sau khi kiểm tra. Kéo terminal lên xem từng nhóm; phóng to chữ vừa đủ đọc. Mỗi ảnh cần thấy tên nhóm và các dòng PASS tương ứng. Không cần chụp lại ảnh Nginx nếu ảnh cũ đã thấy ba headers.

| Ảnh | Nội dung cần thấy | Chú thích trong báo cáo |
|---|---|---|
| 1 | Nhóm 1: web/nginx uid khác 0, read-only, drop ALL, no-new-privileges | Kiểm chứng web và Nginx chạy bằng người dùng không phải root và bị hạn chế quyền container. |
| 2 | Nhóm 2: PostgreSQL internal, không publish DB/web, các cổng chỉ 127.0.0.1 | Kiểm chứng cô lập mạng cơ sở dữ liệu và giới hạn truy cập dịch vụ trên máy thực hành. |
| 3 | Nhóm 3: sáu giá trị bí mật khác nhau, độ dài tối thiểu, .env không được Git theo dõi | Kiểm tra cấu hình bí mật mà không hiển thị mật khẩu. |
| 4 | Nhóm 4: ba HTTP headers; dùng lại ảnh bước Nginx được | Kiểm chứng ba security headers của Nginx. |
| 5 | Nhóm 5 và dòng All five hardening groups passed | Kiểm chứng tài khoản ứng dụng và tài khoản giám sát có quyền PostgreSQL hạn chế. |

Đặt ảnh trong mục **8. Hardening** của khung báo cáo, theo thứ tự bảng trên. Đây là cách tổ chức minh chứng, không phải yêu cầu thêm của giảng viên.

## 3. Giải thích cho người mới học

**Non-root và hạn chế container:** web chạy bằng user `app`, Nginx bằng UID 101. `read_only` hạn chế ghi vào filesystem container; `/tmp` vẫn được ghi bằng tmpfs. `cap_drop: ALL` bỏ Linux capabilities và `no-new-privileges` ngăn tiến trình nhận quyền bổ sung qua exec. Không kết luận mọi container đều non-root: cAdvisor cần privileged để giám sát, Promtail dùng root và Docker socket để đọc log.

**Cô lập mạng:** PostgreSQL chỉ thuộc `db_net` có `internal: true`, không publish cổng 5432. Web không publish cổng 8000; trình duyệt truy cập qua Nginx tại 8036. Nginx không thuộc mạng DB. Web, pgAdmin và postgres-exporter vẫn kết nối DB trong mạng Docker theo đúng chức năng. Các giao diện được bind 127.0.0.1 để dùng trên máy học.

**Mật khẩu:** script chuẩn bị môi trường tạo các giá trị ngẫu nhiên riêng biệt bằng bộ sinh của Python; lưu trong `.env` bị Git bỏ qua. Kiểm tra độ dài và tính khác nhau chỉ chứng minh điều kiện cấu hình, không tự chứng minh độ ngẫu nhiên hay mật khẩu đang được dịch vụ dùng nếu người học đã sửa `.env` sau khởi tạo volume. Không tự thay mật khẩu DB/Grafana khi volume đã có dữ liệu.

**Security headers:** `nosniff` ngăn trình duyệt đoán kiểu nội dung; `DENY` hạn chế nhúng trang vào frame; Referrer-Policy giới hạn thông tin URL gửi đến trang khác. Phần thực hành dùng HTTP với headers theo lựa chọn được yêu cầu cho phép; headers không mã hóa đường truyền.

**Quyền DB:** `app_user` có CRUD trên bốn bảng, quyền dùng sequence cho ID, không phải superuser, không tạo database/role hoặc đối tượng trong schema public. `monitor_user` thuộc pg_monitor để đọc thống kê nhưng không SELECT bảng nghiệp vụ. Script kiểm tra quyền thực tế bằng các hàm PostgreSQL, không thử tạo/xóa đối tượng.

## 4. Đoạn viết báo cáo

Chỉ sử dụng đoạn sau khi chạy kiểm tra thành công:

“Hệ thống được kiểm chứng theo năm nhóm biện pháp bảo mật. Container web và Nginx chạy bằng tài khoản không phải root, filesystem chỉ đọc và bị hạn chế quyền. PostgreSQL được đặt trong mạng nội bộ, không công bố cổng ra máy host; ứng dụng được truy cập qua Nginx. Các giao diện thực hành chỉ mở trên localhost. Giá trị bí mật được lưu riêng trong .env và không đưa lên GitHub. Nginx cung cấp ba security headers. Tài khoản ứng dụng và giám sát PostgreSQL có quyền phù hợp với chức năng, không có quyền quản trị cao. Script verify-hardening.py kiểm tra trạng thái thực tế mà không thay đổi dữ liệu nghiệp vụ.”

Ghi giới hạn: môi trường thực hành cục bộ dùng HTTP, chưa có đăng nhập ứng dụng; cAdvisor có privileged và Promtail truy cập Docker socket. Mount socket với `:ro` không biến Docker API thành API chỉ đọc. Không mô tả dự án đã đủ bảo mật cho triển khai Internet.
