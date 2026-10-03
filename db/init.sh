#!/bin/sh
set -eu
# Dùng biến môi trường qua psql, không ghép mật khẩu trực tiếp vào chuỗi SQL.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=app_user="$APP_DB_USER" --set=app_password="$APP_DB_PASSWORD" <<'SQL'
CREATE USER :"app_user" PASSWORD :'app_password';
CREATE TABLE residents (id SERIAL PRIMARY KEY, full_name TEXT NOT NULL, apartment TEXT NOT NULL, phone TEXT NOT NULL);
CREATE TABLE fees (id SERIAL PRIMARY KEY, apartment TEXT NOT NULL, description TEXT NOT NULL, amount NUMERIC(14,2) NOT NULL CHECK(amount>0), due_date DATE NOT NULL, status TEXT NOT NULL CHECK(status IN ('Chưa thanh toán','Đã thanh toán')));
CREATE TABLE announcements (id SERIAL PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL);
CREATE TABLE complaints (id SERIAL PRIMARY KEY, apartment TEXT NOT NULL, content TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('Mới tiếp nhận','Đang xử lý','Đã giải quyết')));
GRANT CONNECT ON DATABASE :"DBNAME" TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO :"app_user";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO :"app_user";
INSERT INTO residents(full_name,apartment,phone) VALUES ('Cư dân mẫu 01','A101','SĐT giả lập 01'),('Cư dân mẫu 02','A102','SĐT giả lập 02'),('Cư dân mẫu 03','B201','SĐT giả lập 03');
INSERT INTO fees(apartment,description,amount,due_date,status) VALUES ('A101','Phí dịch vụ mẫu kỳ 10/2026',350000,'2026-10-31','Chưa thanh toán'),('A102','Phí dịch vụ mẫu kỳ 10/2026',350000,'2026-10-31','Đã thanh toán');
INSERT INTO announcements(title,content) VALUES ('Thông báo mẫu: vệ sinh khu vực chung','Dữ liệu giả lập phục vụ bài thực hành đề 36.');
INSERT INTO complaints(apartment,content,status) VALUES ('B201','Khiếu nại mẫu: đèn hành lang cần kiểm tra.','Mới tiếp nhận');
SQL
