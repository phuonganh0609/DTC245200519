"""Read-only checks of running containers; never print secret values."""
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent

def run(*args, input_text=None):
    reply = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, input=input_text)
    if reply.returncode:
        raise RuntimeError('Command failed: ' + ' '.join(args[:3]) + '; check Docker/service availability')
    return reply.stdout.strip()

def inspect(service):
    identifier = run('docker', 'compose', 'ps', '-q', service)
    assert identifier, 'Service not running: ' + service
    return json.loads(run('docker', 'inspect', identifier))[0]

def passed(message):
    print('PASS: ' + message, flush=True)

containers = {name: inspect(name) for name in ('web', 'nginx', 'db', 'pgadmin')}
print('1. NON-ROOT AND CONTAINER RESTRICTIONS', flush=True)
for service in ('web', 'nginx'):
    uid = run('docker', 'compose', 'exec', '-T', service, 'id', '-u')
    assert int(uid) != 0, service + ' is root'
    host = containers[service]['HostConfig']
    assert host['ReadonlyRootfs'] and 'ALL' in host['CapDrop']
    assert any(option in ('no-new-privileges', 'no-new-privileges:true') for option in host['SecurityOpt'])
    passed(f'{service}: uid={uid}; read-only rootfs; drop ALL; no-new-privileges')

print('\n2. NETWORK ISOLATION AND LOCAL PORTS', flush=True)
assert not containers['db']['HostConfig']['PortBindings'], 'Database port published'
assert not containers['web']['HostConfig']['PortBindings'], 'Web bypass port published'
db_networks = containers['db']['NetworkSettings']['Networks']
assert len(db_networks) == 1
network_name = next(iter(db_networks))
assert json.loads(run('docker', 'network', 'inspect', network_name))[0]['Internal']
assert network_name not in containers['nginx']['NetworkSettings']['Networks']
passed('PostgreSQL: internal network; no published port; Nginx outside DB network')
passed('Web: no published port; access through Nginx')
for service in ('nginx', 'pgadmin', 'grafana', 'prometheus', 'loki'):
    bindings = inspect(service)['HostConfig']['PortBindings']
    assert bindings and all(binding['HostIp'] == '127.0.0.1' for entries in bindings.values() for binding in entries)
    passed(service + ': published only on 127.0.0.1')

print('\n3. SECRET CONFIGURATION (VALUES HIDDEN)', flush=True)
config = dict(line.split('=', 1) for line in (ROOT / '.env').read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))
keys = ('POSTGRES_PASSWORD', 'APP_DB_PASSWORD', 'MONITOR_DB_PASSWORD', 'PGADMIN_PASSWORD', 'GRAFANA_PASSWORD', 'APP_SECRET_KEY')
values = [config[key] for key in keys]
assert all(len(value) >= 32 and 'REPLACE' not in value for value in values)
assert len(set(values)) == len(values)
assert not run('git', 'ls-files', '--', '.env'), '.env tracked by Git'
run('git', 'check-ignore', '.env')
passed('Six distinct secret values, at least 32 characters; .env ignored and untracked')
print('Note: length/distinctness checks do not prove password randomness.', flush=True)

print('\n4. HTTP SECURITY HEADERS', flush=True)
expected = {'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY', 'Referrer-Policy': 'strict-origin-when-cross-origin'}
with urlopen('http://localhost:8036/', timeout=15) as response:
    assert response.status == 200
    for name, value in expected.items():
        assert response.headers.get(name) == value, name
        passed(name + ': ' + value)

print('\n5. DATABASE LEAST PRIVILEGE', flush=True)
sql = """SELECT rolname, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles
WHERE rolname IN (:'app_user', :'monitor_user') ORDER BY rolname;
SELECT tablename,
has_table_privilege(:'app_user', 'public.' || tablename, 'SELECT,INSERT,UPDATE,DELETE'),
has_table_privilege(:'monitor_user', 'public.' || tablename, 'SELECT')
FROM pg_tables WHERE schemaname='public' ORDER BY tablename;
SELECT has_schema_privilege(:'app_user', 'public', 'CREATE');
SELECT pg_has_role(:'monitor_user', 'pg_monitor', 'MEMBER');"""
command = 'psql -X -A -t -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" --set=app_user="$APP_DB_USER" --set=monitor_user="$MONITOR_DB_USER"'
rows = run('docker', 'compose', 'exec', '-T', 'db', 'sh', '-c', command, input_text=sql).splitlines()
assert len(rows) == 8, 'Unexpected database roles/tables'
assert {row.split('|')[0] for row in rows[:2]} == {config['APP_DB_USER'], config['MONITOR_DB_USER']}
assert all(row.endswith('|f|f|f') for row in rows[:2]), 'Excessive role privileges'
assert {row.split('|')[0] for row in rows[2:6]} == {'residents', 'fees', 'announcements', 'complaints'}
assert all(row.endswith('|t|f') for row in rows[2:6]), 'Unexpected table privileges'
assert rows[6:] == ['f', 't'], 'Unexpected schema/monitor privileges'
passed('app_user and monitor_user: no superuser / CREATEDB / CREATEROLE')
passed('app_user: CRUD on four tables; cannot CREATE in public schema')
passed('monitor_user: pg_monitor; cannot SELECT business tables')
print('\nAll five hardening groups passed. Local practice environment; HTTP is not encrypted.', flush=True)
print('Exceptions: cAdvisor is privileged; Promtail runs as root and accesses Docker socket.', flush=True)
