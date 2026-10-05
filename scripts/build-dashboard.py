"""Tạo dashboard từ các truy vấn của dự án, không tải dashboard ngoài."""
import json
from pathlib import Path

panels = []
source = {'type': 'prometheus', 'uid': 'prometheus-de36'}

def row(title, y):
    panels.append({'id': len(panels)+1, 'title': title, 'type': 'row', 'collapsed': False, 'panels': [], 'gridPos': {'x': 0, 'y': y, 'w': 24, 'h': 1}})

def panel(title, expr, x, y, unit='short', kind='timeseries', legend=''):
    panels.append({
        'id': len(panels)+1, 'title': title, 'type': kind, 'datasource': source,
        'gridPos': {'x': x, 'y': y, 'w': 12, 'h': 7},
        'targets': [{'refId': 'A', 'expr': expr, 'legendFormat': legend, 'instant': kind == 'stat'}],
        'fieldConfig': {'defaults': {'unit': unit, 'min': 0, 'color': {'mode': 'palette-classic'}, 'custom': {'lineWidth': 2, 'fillOpacity': 10}}, 'overrides': []},
        'options': {'legend': {'displayMode': 'list', 'placement': 'bottom'}, 'tooltip': {'mode': 'multi'}, 'reduceOptions': {'calcs': ['lastNotNull'], 'values': False}, 'colorMode': 'value', 'graphMode': 'none'},
    })

row('1. Container đề 36', 0)
panel('CPU từng container (% của 1 lõi)', 'sum by (container_label_com_docker_compose_service) (rate(container_cpu_usage_seconds_total{job="cadvisor",container_label_com_docker_compose_project="dtc245200519"}[2m])) * 100', 0, 1, 'percent', legend='{{container_label_com_docker_compose_service}}')
panel('RAM working set từng container', 'sum by (container_label_com_docker_compose_service) (container_memory_working_set_bytes{job="cadvisor",container_label_com_docker_compose_project="dtc245200519"})', 12, 1, 'bytes', legend='{{container_label_com_docker_compose_service}}')
row('2. Web server Nginx', 8)
panel('Yêu cầu HTTP mỗi giây', 'rate(nginx_http_requests_total{job="nginx"}[2m])', 0, 9, 'reqps', legend='Nginx requests/s')
panel('Kết nối Nginx đang hoạt động', 'nginx_connections_active{job="nginx"}', 12, 9, legend='Kết nối active')
row('3. PostgreSQL', 16)
panel('Kết nối tới database đề 36', 'pg_stat_database_numbackends{job="postgres",datname="chungcu_dtc245200519"}', 0, 17, legend='Kết nối database')
panel('Giao dịch commit mỗi giây', 'rate(pg_stat_database_xact_commit{job="postgres",datname="chungcu_dtc245200519"}[2m])', 12, 17, 'ops', legend='Commit/s')
row('4. Kiểm tra thu thập', 24)
panel('Trạng thái scrape targets (1 = UP)', 'up', 0, 25, kind='stat', legend='{{job}}')
panel('Trạng thái dịch vụ (1 = hoạt động)', '{__name__=~"nginx_up|pg_up"}', 12, 25, kind='stat', legend='{{job}}')

dashboard = {'uid': 'de36-monitoring', 'title': 'De36 - Container, Nginx va PostgreSQL', 'tags': ['de36'], 'schemaVersion': 39, 'version': 1, 'refresh': '15s', 'timezone': 'browser', 'time': {'from': 'now-15m', 'to': 'now'}, 'panels': panels}
target = Path(__file__).resolve().parent.parent / 'monitoring/grafana/dashboards/de36.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Đã tạo dashboard De36 trong repository.')
