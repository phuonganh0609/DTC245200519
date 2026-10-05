import json
import time
import base64
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

queries = [
    '{project="dtc245200519",container="nginx"}',
    '{project="dtc245200519",container="web"} |= "GET"',
    '{project="dtc245200519",container="nginx"} |= " 404 "',
]

# Chỉ kiểm tra log mới, không dùng log cũ để kết luận cấu hình mới hoạt động.
started = time.time_ns()
# Tạo yêu cầu HTTP thực tế, không thêm/sửa/xóa bản ghi nghiệp vụ.
with urlopen('http://localhost:8036/', timeout=10) as response:
    assert response.status == 200
try:
    urlopen('http://localhost:8036/minh-chung-log-404', timeout=10)
except HTTPError as error:
    assert error.code == 404

for query in queries:
    found = False
    for attempt in range(12):
        params = urlencode({'query': query, 'start': started, 'end': time.time_ns(), 'limit': 10})
        with urlopen('http://localhost:3136/loki/api/v1/query_range?' + params, timeout=10) as response:
            reply = json.load(response)
        assert reply['status'] == 'success'
        result = reply['data']['result']
        if result:
            print('PASS: ' + query)
            print('Dòng log mẫu: ' + result[0]['values'][-1][1][:250])
            found = True
            break
        time.sleep(3)
    assert found, 'Không tìm thấy log: ' + query
print('PASS: cả ba query LogQL trả log thật; không thay đổi dữ liệu nghiệp vụ.')
config = dict(line.split('=', 1) for line in (Path(__file__).resolve().parent.parent / '.env').read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))
auth = base64.b64encode(('admin:' + config['GRAFANA_PASSWORD']).encode()).decode()
request = Request('http://localhost:3036/api/datasources/uid/loki-de36/health', headers={'Authorization': 'Basic ' + auth})
with urlopen(request, timeout=15) as response:
    health = json.load(response)
assert health['status'] == 'OK', health
print('PASS: datasource Loki-De36 trong Grafana kết nối thành công.')
