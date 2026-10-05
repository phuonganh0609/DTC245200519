from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
target = root / '.env'
if target.exists():
    current = target.read_text(encoding='utf-8')
    keys = {line.split('=', 1)[0] for line in current.splitlines() if '=' in line}
    added = []
    for line in (root / '.env.example').read_text(encoding='utf-8').splitlines():
        if '=' in line and line.split('=', 1)[0] not in keys:
            added.append(line.replace('REPLACE_WITH_GENERATED_SECRET', secrets.token_hex(24)))
    if added:
        target.write_text(current.rstrip() + '\n' + '\n'.join(added) + '\n', encoding='utf-8')
    print('Giữ nguyên cấu hình cũ; bổ sung biến còn thiếu, không in mật khẩu.')
else:
    content = (root / '.env.example').read_text(encoding='utf-8')
    while 'REPLACE_WITH_GENERATED_SECRET' in content:
        content = content.replace('REPLACE_WITH_GENERATED_SECRET', secrets.token_hex(24), 1)
    target.write_text(content, encoding='utf-8')
    target.chmod(0o600)
    print('Đã tạo .env cục bộ. Không đưa file này lên GitHub.')
