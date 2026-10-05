# Bước 2: Nginx Reverse Proxy và security headers

## 1. Mục tiêu và căn cứ

Thực hiện tiêu chí Nginx Reverse Proxy (1,5 điểm) theo trang 1–2 của file đề tài: truy cập website qua Nginx, có HTTPS **hoặc** security headers cơ bản. Nội dung reverse proxy, proxy_pass và forwarding headers dựa trên chương 1, chương 5 và các bài lab Nginx đã được cung cấp.

Bước này sử dụng HTTP kèm security headers. Không ghi trong báo cáo rằng hệ thống đã có HTTPS hoặc mã hóa TLS.

## 2. Luồng hoạt động

Trình duyệt → localhost:8036 → Nginx:8080 → web:8000 → PostgreSQL:5432.

1. Người dùng mở website tại http://localhost:8036.
2. Compose chuyển cổng 8036 của máy sang cổng 8080 trong container Nginx.
3. Nginx nhận yêu cầu, dùng `proxy_pass http://web:8000` chuyển tới ứng dụng. `web` là tên dịch vụ được Docker phân giải trong `web_net`.
4. Ứng dụng xử lý, kết nối PostgreSQL qua `db_net`, trả kết quả cho Nginx.
5. Nginx bổ sung security headers và gửi phản hồi về trình duyệt.

Nginx chỉ tham gia `web_net`, không tham gia mạng DB. Web không còn publish cổng 8000 ra host. pgAdmin vẫn mở ở localhost:8136 để quản trị DB. Dữ liệu nằm trong các volume cũ và được giữ nguyên.

## 3. Cấu hình đã triển khai

File `nginx/nginx.conf` chứa cấu hình Nginx, được mount read-only vào container. Dịch vụ `nginx` được khai báo trong `compose.yaml` và chờ web đạt healthcheck trước khi chạy.

```nginx
location / {
    proxy_pass http://web:8000;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

- `proxy_pass`: địa chỉ backend, dùng tên dịch vụ Docker; không dùng localhost vì localhost trong container Nginx là chính container đó.
- `Host`: giữ tên host và cổng mà trình duyệt sử dụng.
- `X-Real-IP`, `X-Forwarded-For`: truyền thông tin địa chỉ phía gửi tới backend. Trong môi trường WSL/Docker, địa chỉ quan sát được có thể là địa chỉ gateway.
- `X-Forwarded-Proto`: thông báo giao thức nhận được là HTTP.

## 4. Security headers

| Header | Giá trị | Mục đích |
|---|---|---|
| X-Content-Type-Options | nosniff | Ngăn trình duyệt tự đoán kiểu nội dung khác khai báo |
| X-Frame-Options | DENY | Không cho nhúng trang trong frame, giảm nguy cơ clickjacking |
| Referrer-Policy | strict-origin-when-cross-origin | Hạn chế thông tin URL được gửi qua Referer khi truy cập khác origin |

Các header được thêm với `always`, vì vậy vẫn có trên phản hồi lỗi như HTTP 404. Nginx ẩn hai header trùng từ web rồi bổ sung một bộ header thống nhất. `server_tokens off` không công bố số phiên bản Nginx trong header Server.

Security headers không thay thế mã hóa HTTPS. Đây là phương án đạt yêu cầu “HTTPS hoặc security headers” trong tài liệu đề tài.

## 5. Lệnh kiểm tra cho người mới

Mở Ubuntu WSL, chạy:

```bash
cd '/mnt/d/Câu hỏi ôn tập/Câu hỏi ôn tập kì 7/Triển khai và quản trị hệ thống phần mềm/DTC245200519'
docker compose ps
docker compose exec -T nginx nginx -t
curl -sS -D - -o /dev/null http://localhost:8036/
python3 scripts/verify-nginx.py
```

- `ps`: xem dịch vụ có chạy không; `nginx`, `web`, `db` phải healthy.
- `exec -T nginx nginx -t`: chạy công cụ kiểm tra cú pháp cấu hình trong container Nginx.
- `curl -sS -D - -o /dev/null`: gửi yêu cầu GET, in header phản hồi và bỏ phần HTML để kết quả dễ đọc.
- `verify-nginx.py`: kiểm tra trang tổng quan, bốn trang chức năng, `/health`, phản hồi HTTP 404 và ba headers. Phép kiểm tra này chỉ đọc, không sửa dữ liệu.

Hoặc dùng một lệnh mở toàn bộ kết quả, sau đó giữ terminal để tự chụp:

```bash
bash scripts/minh-chung-nginx.sh
```

## 6. Kết quả nghiệm thu ngày 06/10/2026

- `nginx -t`: syntax is ok; test is successful.
- Trang tổng quan, cư dân, phí, thông báo, khiếu nại và `/health`: HTTP 200, header `Server: nginx`, đủ ba security headers.
- `/health` trả `{"status":"ok"}`, chứng minh web vẫn kết nối PostgreSQL khi yêu cầu đi qua Nginx.
- URL không tồn tại trả HTTP 404 và vẫn có đủ security headers.
- Compose hiển thị Nginx publish `127.0.0.1:8036->8080`; web chỉ hiển thị `8000/tcp`, không còn publish cổng ra host.
- Nginx chạy user 101, filesystem read-only, `/tmp` là tmpfs, bỏ Linux capabilities và đặt no-new-privileges.

## 7. Ảnh người học tự chụp

1. **Website qua Nginx**: mở http://localhost:8036, giữ thanh địa chỉ trong ảnh. Chú thích: “Truy cập hệ thống quản lý chung cư thông qua Nginx Reverse Proxy”.
2. **Terminal: trạng thái và cấu hình**: chụp `docker compose ps` cùng kết quả `nginx -t`. Chú thích: “Dịch vụ Nginx hoạt động và cấu hình reverse proxy hợp lệ”.
3. **Terminal: HTTP headers**: chụp kết quả `curl`, thấy HTTP 200, Server nginx và ba security headers. Chú thích: “Security headers được bổ sung tại Nginx”.
4. **Terminal: phép kiểm tra**: chụp các dòng PASS từ `verify-nginx.py`. Chú thích: “Kiểm chứng truy cập các chức năng và security headers qua reverse proxy”.

Có thể tách ảnh terminal thành nhiều ảnh để chữ đọc được. Trợ lý không tự chụp ảnh.

## 8. Đoạn đưa vào báo cáo

Đặt sau phần triển khai web và DB:

“Nginx được triển khai dưới dạng một dịch vụ trong Docker Compose và đóng vai trò reverse proxy cho ứng dụng web. Người dùng truy cập localhost tại cổng 8036; yêu cầu được chuyển vào Nginx ở cổng 8080, rồi chuyển tiếp tới dịch vụ web ở cổng 8000 qua mạng Docker. Container web không publish cổng trực tiếp ra host. PostgreSQL tiếp tục nằm trong mạng nội bộ riêng.”

“Hệ thống sử dụng phương án HTTP kèm security headers theo yêu cầu đề tài. Tại Nginx, ba header X-Content-Type-Options, X-Frame-Options và Referrer-Policy được bổ sung vào phản hồi. Tùy chọn always giúp các header tồn tại cả trên phản hồi lỗi. Phương án này không cung cấp mã hóa HTTPS.”

“Kết quả kiểm tra cho thấy cấu hình Nginx hợp lệ, website và các trang chức năng trả HTTP 200 qua reverse proxy. Endpoint health trả trạng thái ok và URL không tồn tại trả HTTP 404. Các phản hồi có đủ security headers như cấu hình.”

Chèn ảnh tự chụp sau đoạn liên quan. Đây là mốc commit Nginx theo yêu cầu chung; không nhầm với commit chuẩn bị hoặc commit ứng dụng trước đó.
