import json
from urllib.request import urlopen
from urllib.error import HTTPError

base = 'http://localhost:8036'
expected = {'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY', 'Referrer-Policy': 'strict-origin-when-cross-origin'}
for path in ['/', '/residents', '/fees', '/announcements', '/complaints', '/health']:
    with urlopen(base + path, timeout=10) as response:
        assert response.status == 200
        assert response.headers.get('Server') == 'nginx', 'Yêu cầu chưa đi qua Nginx'
        for name, value in expected.items():
            assert response.headers.get(name) == value, name
        body = response.read()
        if path == '/health':
            assert json.loads(body) == {'status': 'ok'}
        print(f'PASS: {path} -> HTTP 200 qua Nginx, đủ security headers')
try:
    urlopen(base + '/khong-ton-tai', timeout=10)
except HTTPError as error:
    assert error.code == 404
    for name, value in expected.items():
        assert error.headers.get(name) == value
    print('PASS: HTTP 404 vẫn có security headers (always).')
else:
    raise AssertionError('URL không tồn tại phải trả 404')
for name, value in expected.items():
    print(f'{name}: {value}')
