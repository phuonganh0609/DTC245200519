# Bước 4: Loki + Promtail và LogQL

## 1. Mục tiêu

Thực hiện tiêu chí log tập trung 1,5 điểm của đề tài: Loki + Promtail hoạt động và ít nhất 2–3 query LogQL trả kết quả. Dựa vào chương 8 và bài lab 8 được cung cấp. Bước này chưa triển khai cảnh báo Alertmanager vì yêu cầu chung chỉ quy định log tập trung và truy vấn LogQL.

## 2. Luồng log và cấu hình

Ứng dụng/Nginx/PostgreSQL/pgAdmin → stdout/stderr container → Docker API → Promtail → Loki → Grafana Explore.

- `monitoring/promtail.yml`: khám phá container bằng Docker socket, chỉ giữ project `dtc245200519` và bốn service `web`, `nginx`, `db`, `pgadmin`.
- Nhãn `project` xác định đề tài; nhãn `container` là tên service Compose, không phải ID ngẫu nhiên.
- Promtail không thu log các bài lab khác và không thu log của chính Loki/Promtail để tránh vòng lặp.
- `monitoring/loki.yml`: Loki dùng TSDB/schema v13, lưu filesystem trên volume `loki_data`, retention 72 giờ. Việc xóa dữ liệu hết hạn diễn ra qua compactor, không nhất thiết đúng ngay tại mốc 72 giờ.
- Vị trí đọc log của Promtail lưu trên volume `promtail_positions`, giúp tiếp tục đọc khi khởi động lại.
- `monitoring/grafana/provisioning/datasources/loki.yml`: khai báo datasource `Loki-De36`, địa chỉ nội bộ `http://loki:3100`.

Loki chỉ publish `127.0.0.1:3136`. Promtail không publish cổng. Loki không bật xác thực trong mạng lab này; không phơi cổng ra Internet. Promtail cần quyền đọc Docker socket. Mount `:ro` không biến Docker API thành API chỉ đọc; cấu hình được giới hạn trong môi trường thực hành cục bộ.

## 3. Khởi động và kiểm tra

Trong Ubuntu WSL:

```bash
cd '/mnt/d/Câu hỏi ôn tập/Câu hỏi ôn tập kì 7/Triển khai và quản trị hệ thống phần mềm/DTC245200519'
bash scripts/start-logs.sh
```

Chờ dịch vụ khởi động, rồi chạy:

```bash
docker compose ps loki promtail grafana
python3 scripts/verify-logs.py
```

Script gửi GET trang chủ và GET `/minh-chung-log-404` để tạo log HTTP thật (200 và 404). Không thêm/sửa/xóa bản ghi nghiệp vụ. Script chỉ chấp nhận log mới từ thời điểm chạy, nên không dùng log cũ để kết luận cấu hình đang hoạt động. Sau đó kiểm tra datasource Loki trong Grafana.

Kết quả cần có ba dòng PASS cho ba query, log mẫu, dòng xác nhận không đổi dữ liệu nghiệp vụ và dòng datasource kết nối thành công.

Muốn hiện kết quả trong terminal để tự chụp:

```bash
bash scripts/minh-chung-log.sh
```

## 4. Mở Grafana Explore cho người mới

1. Mở http://localhost:3036/explore.
2. Đăng nhập `admin`, password là `GRAFANA_PASSWORD` trong `.env` nếu được yêu cầu.
3. Trong danh sách nguồn dữ liệu, chọn **Loki-De36**. Không dùng nguồn Prometheus cho LogQL.
4. Chọn **Code** thay cho Builder trong khung truy vấn.
5. Chọn thời gian **Last 15 minutes** hoặc **Last 1 hour** bao gồm thời điểm vừa chạy kiểm tra.
6. Dán từng query dưới đây, nhấn **Run query**.

Sau mỗi query, nhìn thấy dòng log thật rồi tự chụp, giữ câu query trong ảnh. Không chụp màn hình chỉ có No logs found.

## 5. Ba query và ý nghĩa

### Query 1: Toàn bộ log Nginx của đề tài

```logql
{project="dtc245200519",container="nginx"}
```

Phần `{...}` chọn luồng theo nhãn. Có thể thấy GET, trạng thái HTTP, thời gian, đường dẫn và User-Agent. IP có thể là gateway Docker, không nhất thiết là IP Windows.

### Query 2: Các yêu cầu GET trong log ứng dụng

```logql
{project="dtc245200519",container="web"} |= "GET"
```

`|=` giữ dòng có chứa chuỗi GET. Cùng một yêu cầu có thể được ghi ở Nginx và Gunicorn, giúp đối chiếu hoạt động proxy và backend.

### Query 3: Các phản hồi 404 tại Nginx

```logql
{project="dtc245200519",container="nginx"} |= " 404 "
```

Khoảng trắng hai bên 404 giúp lọc mã trạng thái trong access log. Dòng kiểm thử có đường dẫn `/minh-chung-log-404`; đây là đường dẫn cố ý không tồn tại để minh chứng truy vấn lỗi, không phải website hỏng.

## 6. Kết quả nghiệm thu

- Loki và Promtail chạy trong Compose.
- Cả ba query trả log HTTP mới thực tế, gồm 200 và 404.
- Grafana API xác nhận datasource `Loki-De36` có trạng thái OK.
- Kiểm tra giám sát bước 3 vẫn đạt sau khi thêm hệ thống log.
- Dữ liệu nghiệp vụ và lịch sử metrics trước đó được giữ nguyên.

## 7. Thứ tự ảnh đưa vào báo cáo

1. **Terminal: trạng thái dịch vụ** — `docker compose ps loki promtail grafana`. Chú thích: “Các dịch vụ Loki, Promtail và Grafana hoạt động trong Docker Compose”. Đặt sau đoạn mô tả thành phần.
2. **Grafana Explore: query 1** — thấy datasource Loki-De36, câu query, khoảng thời gian và kết quả. Chú thích: “Truy vấn log Nginx của hệ thống bằng LogQL”.
3. **Grafana Explore: query 2** — thay query, Run query, chụp cả câu lệnh và log GET. Chú thích: “Lọc các yêu cầu GET trong log ứng dụng web”.
4. **Grafana Explore: query 3** — chụp câu query và dòng 404. Chú thích: “Truy vấn các phản hồi HTTP 404 tại Nginx”.
5. **Terminal: kiểm chứng** — `clear`, rồi `python3 scripts/verify-logs.py`; chụp các dòng PASS và log mẫu. Chú thích: “Kiểm chứng log mới và kết nối Grafana với Loki”. Đặt cuối phần kết quả.

Không cần chụp lại dashboard metrics hoặc trang chủ website. Không có ảnh nào do trợ lý tự chụp.

## 8. Đoạn viết vào báo cáo

“Hệ thống sử dụng Promtail thu log từ các container web, Nginx, PostgreSQL và pgAdmin của đề tài, sau đó gửi về Loki qua mạng Docker. Các nhãn project và container giúp xác định nguồn log. Dữ liệu Loki và vị trí đọc Promtail được lưu bằng volume để giữ lại khi container khởi động lại.”

“Nguồn dữ liệu Loki-De36 được cấu hình trong Grafana. Người học sử dụng Explore và LogQL để xem log Nginx, lọc yêu cầu GET trong ứng dụng và tìm phản hồi HTTP 404. Mỗi truy vấn có kết quả log thực tế làm minh chứng.”

“Kiểm tra bằng các yêu cầu HTTP mới xác nhận Promtail thu được log hiện tại, không chỉ truy vấn dữ liệu cũ. Các yêu cầu kiểm thử không làm thay đổi dữ liệu nghiệp vụ. Hệ thống giám sát metrics ở bước trước vẫn hoạt động sau khi tích hợp log.”

Chèn ba ảnh query ngay sau phần trình bày truy vấn tương ứng, đánh số hình tiếp nối bước 3.

## 9. Sự cố đã xử lý và lưu ý

Lần đầu thu tất cả dịch vụ của project tạo nhiều log từ hệ giám sát và log thu thập, có phản hồi 429/400 khi nạp lịch sử. Đã giới hạn Promtail ở bốn dịch vụ nghiệp vụ để tránh vòng lặp tự thu log và giảm lưu lượng. Kiểm tra sau điều chỉnh xác nhận các log mới vẫn được thu thành công; không xóa lịch sử để che lỗi.

Nếu không có log, kiểm tra datasource, nhãn, khoảng thời gian, rồi chạy lại `verify-logs.py`. Không dùng `down -v` để xử lý vì có thể xóa dữ liệu.

Promtail được dùng theo tài liệu bài lab đã cung cấp. Bước này không tự chuyển sang công cụ khác ngoài phạm vi đã thống nhất.
