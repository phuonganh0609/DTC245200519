"""Kiểm chứng kết nối thật; chỉ tạo và dọn bản ghi giả lập của phép thử."""
from app import app, connection, MODULES

client = app.test_client()
assert client.get('/health').json == {'status': 'ok'}
for name in MODULES:
    assert client.get('/' + name).status_code == 200, name
print('PASS: web kết nối DB; bốn trang chức năng trả HTTP 200.')

assert client.post('/residents', data={'full_name': 'Không có CSRF'}).status_code == 400
with client.session_transaction() as session:
    token = session['csrf_token']
marker = 'Bản ghi giả lập kiểm thử kết nối'
record_id = None
try:
    response = client.post('/residents', data={'csrf_token': token, 'full_name': marker, 'apartment': 'TEST', 'phone': 'Giả lập'})
    assert response.status_code == 302
    with connection() as conn:
        record = conn.execute('SELECT id FROM residents WHERE full_name=%s ORDER BY id DESC LIMIT 1', (marker,)).fetchone()
        assert record is not None
        record_id = record['id']
    assert client.get(f'/residents?edit={record_id}').status_code == 200
    assert client.post('/residents', data={'csrf_token': token, 'record_id': str(record_id), 'full_name': marker, 'apartment': 'TEST-UPDATED', 'phone': 'Giả lập'}).status_code == 302
    with connection() as conn:
        assert conn.execute('SELECT apartment FROM residents WHERE id=%s', (record_id,)).fetchone()['apartment'] == 'TEST-UPDATED'
    assert client.post(f'/residents/{record_id}/delete', data={'csrf_token': token}).status_code == 302
    with connection() as conn:
        assert conn.execute('SELECT id FROM residents WHERE id=%s', (record_id,)).fetchone() is None
    print('PASS: thêm, sửa, xóa bản ghi kiểm thử qua web; POST thiếu CSRF bị chặn.')
finally:
    if record_id is not None:
        with connection() as conn:
            conn.execute('DELETE FROM residents WHERE id=%s AND full_name=%s', (record_id, marker))

with connection() as conn:
    role = conn.execute('SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=current_user').fetchone()
    assert not any(role.values())
print('PASS: tài khoản web không có quyền superuser, tạo database hay tạo role.')
