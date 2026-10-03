import logging
import os
import secrets
from datetime import date
from decimal import Decimal, InvalidOperation

import psycopg
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from psycopg.rows import dict_row

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=16384)
logging.basicConfig(level=logging.INFO)

# Tên bảng/cột chỉ lấy từ cấu hình cố định; dữ liệu nhập luôn dùng tham số SQL.
MODULES = {
    'residents': {'title': 'Cư dân', 'fields': [('full_name', 'Họ tên', 'text'), ('apartment', 'Căn hộ', 'text'), ('phone', 'Điện thoại', 'text')]},
    'fees': {'title': 'Phí dịch vụ', 'fields': [('apartment', 'Căn hộ', 'text'), ('description', 'Nội dung phí', 'text'), ('amount', 'Số tiền (VND)', 'number'), ('due_date', 'Hạn thanh toán', 'date'), ('status', 'Trạng thái', 'fee_status')]},
    'announcements': {'title': 'Thông báo', 'fields': [('title', 'Tiêu đề', 'text'), ('content', 'Nội dung', 'textarea')]},
    'complaints': {'title': 'Khiếu nại', 'fields': [('apartment', 'Căn hộ', 'text'), ('content', 'Nội dung', 'textarea'), ('status', 'Trạng thái', 'complaint_status')]},
}


def connection():
    return psycopg.connect(host='db', dbname=os.environ['POSTGRES_DB'], user=os.environ['APP_DB_USER'], password=os.environ['APP_DB_PASSWORD'], row_factory=dict_row)


def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


app.jinja_env.globals['csrf_token'] = csrf_token


@app.before_request
def protect_forms():
    if request.method == 'POST' and not secrets.compare_digest(str(session.get('csrf_token', '')), str(request.form.get('csrf_token', ''))) :
        abort(400, 'Phiên biểu mẫu không hợp lệ. Hãy tải lại trang.')


@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.get('/health')
def health():
    try:
        with connection() as conn:
            conn.execute('SELECT 1')
        return {'status': 'ok'}
    except psycopg.Error:
        app.logger.exception('DATABASE_HEALTH_ERROR')
        return {'status': 'error'}, 503


@app.get('/')
def index():
    with connection() as conn:
        counts = {name: conn.execute(f'SELECT count(*) AS n FROM {name}').fetchone()['n'] for name in MODULES}
    return render_template('index.html', modules=MODULES, counts=counts)


@app.route('/<module>', methods=['GET', 'POST'])
def listing(module):
    if module not in MODULES:
        abort(404)
    config = MODULES[module]
    if request.method == 'POST':
        values = [request.form.get(key, '').strip() for key, _, _ in config['fields']]
        if any(not value or len(value) > 2000 for value in values):
            flash('Nhập đầy đủ các trường, mỗi trường không quá 2000 ký tự.')
            return redirect(url_for('listing', module=module))
        try:
            for i, (_, _, kind) in enumerate(config['fields']):
                if kind == 'number':
                    amount = Decimal(values[i])
                    if not amount.is_finite() or amount <= 0 or amount > Decimal('999999999999.99'):
                        raise ValueError()
                    values[i] = amount
                elif kind == 'date':
                    values[i] = date.fromisoformat(values[i])
                elif kind == 'fee_status' and values[i] not in ['Chưa thanh toán', 'Đã thanh toán']:
                    raise ValueError()
                elif kind == 'complaint_status' and values[i] not in ['Mới tiếp nhận', 'Đang xử lý', 'Đã giải quyết']:
                    raise ValueError()
            columns = ', '.join(field[0] for field in config['fields'])
            placeholders = ', '.join(['%s'] * len(values))
            with connection() as conn:
                record_id = request.form.get('record_id', '')
                if record_id:
                    record_id = int(record_id)
                    assignments = ', '.join(f'{field[0]}=%s' for field in config['fields'])
                    result = conn.execute(f'UPDATE {module} SET {assignments} WHERE id=%s', values + [record_id])
                    if result.rowcount == 0:
                        abort(404)
                    app.logger.info('UPDATE module=%s id=%s', module, record_id)
                    flash('Đã cập nhật bản ghi.')
                else:
                    conn.execute(f'INSERT INTO {module} ({columns}) VALUES ({placeholders})', values)
                    app.logger.info('CREATE module=%s', module)
                    flash('Đã thêm bản ghi.')
        except (ValueError, InvalidOperation):
            flash('Số tiền, ngày hoặc trạng thái không hợp lệ.')
        return redirect(url_for('listing', module=module))
    with connection() as conn:
        rows = conn.execute(f'SELECT * FROM {module} ORDER BY id DESC').fetchall()
        edit_id = request.args.get('edit', type=int)
        record = conn.execute(f'SELECT * FROM {module} WHERE id=%s', (edit_id,)).fetchone() if edit_id else None
        if edit_id and record is None:
            abort(404)
    return render_template('listing.html', modules=MODULES, module=module, config=config, rows=rows, record=record)


@app.post('/<module>/<int:record_id>/status')
def status(module, record_id):
    options = {'fees': ['Chưa thanh toán', 'Đã thanh toán'], 'complaints': ['Mới tiếp nhận', 'Đang xử lý', 'Đã giải quyết']}
    value = request.form.get('status')
    if module not in options or value not in options[module]:
        abort(400)
    with connection() as conn:
        result = conn.execute(f'UPDATE {module} SET status=%s WHERE id=%s', (value, record_id))
        if result.rowcount == 0:
            abort(404)
    app.logger.info('UPDATE_STATUS module=%s id=%s', module, record_id)
    flash('Đã cập nhật trạng thái.')
    return redirect(url_for('listing', module=module))


@app.post('/<module>/<int:record_id>/delete')
def delete(module, record_id):
    if module not in MODULES:
        abort(404)
    with connection() as conn:
        result = conn.execute(f'DELETE FROM {module} WHERE id=%s', (record_id,))
        if result.rowcount == 0:
            abort(404)
    app.logger.info('DELETE module=%s id=%s', module, record_id)
    flash('Đã xóa bản ghi.')
    return redirect(url_for('listing', module=module))
