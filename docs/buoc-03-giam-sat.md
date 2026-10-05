# Bước 3: Prometheus và Grafana

## 1. Mục tiêu và phạm vi

Thực hiện tiêu chí giám sát 1,5 điểm trong tài liệu đề tài: Prometheus thu metrics, Grafana có dashboard giám sát container, web server và database. Nguyên lý Pull, metrics, PromQL, exporter và dashboard theo chương 7 và bài lab 7 đã cung cấp.

Đề 36 sử dụng PostgreSQL nên dùng PostgreSQL exporter thay MySQL exporter trong lab. Nginx exporter đọc thống kê Nginx; cAdvisor đọc số liệu container. Dashboard do dự án tạo, không nhập dashboard từ bên ngoài. Không thêm bản ghi nghiệp vụ trong bước này.

## 2. Luồng dữ liệu

- cAdvisor → CPU và RAM từng container.
- Nginx `stub_status` → Nginx exporter → requests và connections.
- PostgreSQL → PostgreSQL exporter → thống kê kết nối và giao dịch.
- Prometheus kéo metrics từ exporters mỗi 15 giây và lưu lịch sử.
- Grafana truy vấn Prometheus bằng PromQL để hiển thị biểu đồ.

Các dịch vụ trao đổi metrics qua `monitor_net`. PostgreSQL exporter nối cả `db_net` và `monitor_net`; Prometheus không tham gia mạng DB. Nginx có endpoint `/stub_status` ở cổng nội bộ 8081, không publish cổng này ra host. Không mở cổng exporters ra host.

## 3. Thành phần và truy cập

| Thành phần | Vai trò | Truy cập |
|---|---|---|
| Prometheus | Thu thập và lưu metrics | http://localhost:9036 |
| Grafana | Dashboard | http://localhost:3036 |
| cAdvisor | Metrics container | Chỉ nội bộ, cổng 8080 |
| Nginx exporter | Metrics Nginx | Chỉ nội bộ, cổng 9113 |
| PostgreSQL exporter | Metrics DB | Chỉ nội bộ, cổng 9187 |

Toàn bộ dự án hiện có 9 dịch vụ gồm 4 dịch vụ trước và 5 dịch vụ giám sát mới. Grafana dùng username `admin`, password là `GRAFANA_PASSWORD` trong `.env`. Không chụp hoặc commit file mật khẩu.

Prometheus giữ dữ liệu tối đa 7 ngày và giới hạn dung lượng retention 1GB; dữ liệu Prometheus và Grafana nằm trong các volume riêng. Không dùng `down -v` khi cần giữ lại lịch sử.

## 4. Tài khoản PostgreSQL giám sát

Script `db/setup-monitoring.sh` tạo `monitor_user`, đặt mật khẩu ngẫu nhiên từ `.env`, cấp role `pg_monitor` và quyền CONNECT. Tài khoản này đọc thống kê vận hành, không được cấp quyền thao tác bảng cư dân/phí/thông báo/khiếu nại. Exporter không dùng mật khẩu của tài khoản quản trị hoặc ứng dụng.

Script chạy được nhiều lần mà không tạo tài khoản trùng. Các bản ghi nghiệp vụ và volume DB được giữ nguyên.

## 5. Cách chạy từng lệnh trong Ubuntu

```bash
cd '/mnt/d/Câu hỏi ôn tập/Câu hỏi ôn tập kì 7/Triển khai và quản trị hệ thống phần mềm/DTC245200519'
bash scripts/start-monitoring.sh
```

Script bổ sung biến môi trường còn thiếu, khởi động DB, cấu hình tài khoản giám sát và chạy các dịch vụ. Khi dùng Docker Desktop, script gọi CLI Windows (`docker.exe`) cho riêng cAdvisor để mount filesystem đúng.

Chờ khoảng 30–60 giây, sau đó:

```bash
docker compose ps
docker compose exec -T prometheus promtool check config /etc/prometheus/prometheus.yml
python3 scripts/verify-monitoring.py
```

- `ps`: các dịch vụ ở trạng thái Up.
- `promtool`: kiểm tra cú pháp file cấu hình Prometheus.
- `verify-monitoring.py`: kiểm tra 4 targets UP, `nginx_up=1`, `pg_up=1`, các metrics và tất cả biểu thức trong dashboard. Script chỉ đọc API, không sửa dữ liệu.

Nếu muốn hiện toàn bộ kết quả trong terminal để tự chụp:

```bash
bash scripts/minh-chung-giam-sat.sh
```

## 6. Dashboard và ý nghĩa chỉ số

Mở http://localhost:3036/d/de36-monitoring. Nếu thấy Login, đăng nhập bằng `admin` và mật khẩu `GRAFANA_PASSWORD` trong `.env`.

Dashboard **De36 - Container, Nginx va PostgreSQL** gồm:

1. **Container**: CPU từng dịch vụ và RAM working set. CPU tính theo % của một lõi nên có thể vượt 100% nếu dùng nhiều lõi. Working set phản ánh bộ nhớ đang được sử dụng, không bằng tổng giới hạn RAM.
2. **Web server Nginx**: số yêu cầu HTTP mỗi giây và số kết nối đang hoạt động.
3. **PostgreSQL**: số kết nối tới database `chungcu_dtc245200519` và số giao dịch commit mỗi giây.
4. **Kiểm tra thu thập**: `up` của các targets và trạng thái backend `nginx_up`, `pg_up`.

`up=1` chỉ chứng minh Prometheus scrape được exporter; `pg_up=1` và `nginx_up=1` mới kiểm tra thêm kết nối exporter tới dịch vụ tương ứng.

Biểu đồ lọc container bằng nhãn project `dtc245200519`; không trộn số liệu các bài lab khác. PostgreSQL được lọc bằng `datname` đúng tên database.

Giá trị 0 là bình thường nếu ít thao tác. `No data` là khác: phải kiểm tra targets/biểu thức. Các truy vấn `rate(...[2m])` cần ít nhất hai mẫu. Khoảng thời gian dashboard mặc định Last 15 minutes; không chỉnh về khoảng thời gian trước khi dịch vụ chạy.

## 7. Ví dụ PromQL dùng trong dashboard

```promql
sum by (container_label_com_docker_compose_service) (
  rate(container_cpu_usage_seconds_total{
    job="cadvisor",
    container_label_com_docker_compose_project="dtc245200519"
  }[2m])
) * 100
```

Đây là tốc độ tăng bộ đếm thời gian CPU, gom theo tên dịch vụ.

```promql
nginx_connections_active{job="nginx"}
```

Đây là số kết nối hiện tại, dạng gauge, không dùng `rate`.

```promql
pg_stat_database_numbackends{
  job="postgres",
  datname="chungcu_dtc245200519"
}
```

Đây là số backend đang kết nối tới database của đề tài.

## 8. Kết quả đã nghiệm thu

- Cấu hình Prometheus hợp lệ theo promtool.
- 4 targets: prometheus, cadvisor, nginx, postgres đều UP.
- `nginx_up` và `pg_up` đều bằng 1.
- Có metrics RAM container của dự án, requests Nginx và kết nối PostgreSQL.
- Grafana API xác nhận dashboard đã được provision từ JSON; mọi truy vấn panel đều trả dữ liệu.
- Script khởi động giám sát chạy lại thành công.
- Kiểm tra Nginx bước 2 vẫn đạt sau khi thêm giám sát.

## 9. Ảnh tự chụp và thứ tự đưa vào báo cáo

Không chụp lại trang tổng quan website hoặc cây bảng pgAdmin của bước 1.

### Ảnh 1: Trạng thái và kiểm tra cấu hình

Trong Ubuntu chạy `docker compose ps`, rồi lệnh `promtool` ở mục 5. Chụp các dịch vụ và dòng SUCCESS. Đặt sau phần giới thiệu các thành phần.

Chú thích: “Trạng thái các dịch vụ giám sát và kiểm tra cấu hình Prometheus”.

### Ảnh 2: Prometheus Targets

Mở http://localhost:9036/targets. Chụp bốn nhóm prometheus, cadvisor, nginx, postgres với trạng thái UP. Nếu các nhóm bị thu gọn, mở rộng để thấy endpoint và trạng thái. Có thể chia thành hai ảnh cho chữ rõ.

Chú thích: “Prometheus thu thập metrics thành công từ bốn targets”.

### Ảnh 3: Grafana giám sát container

Mở dashboard, chụp tiêu đề và nhóm **1. Container đề 36**, có biểu đồ CPU/RAM và chú giải tên dịch vụ.

Chú thích: “Dashboard theo dõi CPU và bộ nhớ của các container đề tài”.

### Ảnh 4: Grafana giám sát Nginx

Cuộn tới nhóm **2. Web server Nginx**. Chụp hai biểu đồ requests và connections. Có thể mở website trong tab khác và tải lại vài lần để quan sát lưu lượng thật; thao tác này không thêm bản ghi nghiệp vụ.

Chú thích: “Giám sát lưu lượng yêu cầu và kết nối của Nginx”.

### Ảnh 5: Grafana giám sát PostgreSQL

Cuộn tới nhóm **3. PostgreSQL**, chụp biểu đồ kết nối và giao dịch của database đề tài.

Chú thích: “Giám sát kết nối và giao dịch PostgreSQL của hệ thống quản lý chung cư”.

### Ảnh 6: Kết quả kiểm chứng

Trong Ubuntu, `clear`, rồi `python3 scripts/verify-monitoring.py`. Chụp các dòng PASS. Đặt sau phần mô tả kết quả kiểm tra.

Chú thích: “Kiểm chứng metrics thực tế và dữ liệu trên dashboard Grafana”.

## 10. Đoạn viết vào báo cáo

“Hệ thống giám sát được triển khai bằng Docker Compose, gồm Prometheus, Grafana, cAdvisor, Nginx exporter và PostgreSQL exporter. Prometheus sử dụng mô hình Pull, thu thập metrics mỗi 15 giây qua mạng giám sát riêng. PostgreSQL exporter sử dụng tài khoản riêng có quyền đọc thống kê vận hành.”

“Grafana được cấu hình nguồn dữ liệu Prometheus và dashboard từ các file trong repository. Dashboard có các nhóm chỉ số CPU/RAM container, lưu lượng và kết nối Nginx, kết nối và giao dịch PostgreSQL. Nhãn project và tên database được dùng để lọc số liệu đúng phạm vi đề tài.”

“Kết quả kiểm tra cho thấy bốn targets đều UP; Nginx exporter và PostgreSQL exporter kết nối được backend. Các truy vấn dashboard trả dữ liệu thực tế, không chỉ dừng ở việc cài đặt công cụ. Phần giám sát được quản lý trên GitHub cùng cấu hình triển khai.”

Chèn ảnh vào sau đoạn liên quan. Chưa ghi đã triển khai Loki hoặc LogQL ở bước này.

## 11. Khác biệt môi trường và lỗi đã xử lý

- **Credential helper WSL**: tải hai image exporter bằng Docker CLI Windows, rồi tiếp tục chạy từ Ubuntu. Nếu gặp lại, dùng PowerShell chạy `docker pull nginx/nginx-prometheus-exporter:1.4.0` và `docker pull prometheuscommunity/postgres-exporter:v0.16.0`.
- **cAdvisor trên Docker Desktop**: lần khởi động từ WSL không đọc được metadata container. Khi tạo riêng container cAdvisor qua CLI Windows, factory Docker đăng ký thành công và metrics xuất hiện. Script khởi động đã tích hợp cách xử lý này.
- cAdvisor cần đọc filesystem/cgroup Linux của Docker Desktop và chạy privileged để thu metrics như mô hình lab. Quyền này là ngoại lệ của dịch vụ giám sát, không có nghĩa tất cả container đều chạy non-root. Web và Nginx vẫn chạy non-root.
- Các image Prometheus/Grafana/cAdvisor dùng thẻ latest theo lab và image sẵn có trên máy; phiên bản có thể khác khi dựng lại ở thời điểm khác.
