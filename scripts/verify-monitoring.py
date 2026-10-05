"""Kiểm tra targets, dữ liệu thật và dashboard; không thay đổi dữ liệu nghiệp vụ."""
import base64
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def read_json(url, headers=None):
    with urlopen(Request(url, headers=headers or {}), timeout=15) as response:
        return json.load(response)

prom = 'http://localhost:9036'
targets = read_json(prom + '/api/v1/targets')['data']['activeTargets']
expected = {'prometheus', 'cadvisor', 'nginx', 'postgres'}
assert {target['labels']['job'] for target in targets} == expected
for target in sorted(targets, key=lambda item: item['labels']['job']):
    assert target['health'] == 'up', (target['labels']['job'], target['lastError'])
    print(f"PASS: target {target['labels']['job']} UP")

def query(expr):
    reply = read_json(prom + '/api/v1/query?' + urlencode({'query': expr}))
    assert reply['status'] == 'success'
    result = reply['data']['result']
    assert result, 'Chưa có dữ liệu: ' + expr
    return result

for metric in ['nginx_up', 'pg_up']:
    assert float(query(metric)[0]['value'][1]) == 1
    print(f'PASS: {metric} = 1 (exporter kết nối được dịch vụ)')

for metric in ['container_memory_working_set_bytes{job="cadvisor",container_label_com_docker_compose_project="dtc245200519"}', 'nginx_http_requests_total{job="nginx"}', 'pg_stat_database_numbackends{job="postgres",datname="chungcu_dtc245200519"}']:
    result = query(metric)
    print(f'PASS: có dữ liệu thật {metric.split("{")[0]} ({len(result)} chuỗi)')

config = dict(line.split('=', 1) for line in (Path(__file__).resolve().parent.parent / '.env').read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))
authorization = base64.b64encode(('admin:' + config['GRAFANA_PASSWORD']).encode()).decode()
reply = read_json('http://localhost:3036/api/dashboards/uid/de36-monitoring', {'Authorization': 'Basic ' + authorization})
dashboard = reply['dashboard']
for panel in dashboard['panels']:
    for target in panel.get('targets', []):
        query(target['expr'])
print('PASS: dashboard Grafana được provision; mọi panel có dữ liệu Prometheus.')
print('URL Prometheus: http://localhost:9036/targets')
print('URL Grafana: http://localhost:3036/d/de36-monitoring')
