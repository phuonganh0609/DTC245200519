from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
target = root / '.env'
if target.exists():
    print('.env đã có; giữ nguyên các giá trị hiện tại.')
else:
    content = (root / '.env.example').read_text(encoding='utf-8')
    while 'REPLACE_WITH_GENERATED_SECRET' in content:
        content = content.replace('REPLACE_WITH_GENERATED_SECRET', secrets.token_hex(24), 1)
    target.write_text(content, encoding='utf-8')
    target.chmod(0o600)
    print('Đã tạo .env cục bộ. Không đưa file này lên GitHub.')
