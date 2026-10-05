#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=monitor_user="$MONITOR_DB_USER" --set=monitor_password="$MONITOR_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN', :'monitor_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname=:'monitor_user') \gexec
ALTER ROLE :"monitor_user" PASSWORD :'monitor_password';
GRANT pg_monitor TO :"monitor_user";
GRANT CONNECT ON DATABASE :"DBNAME" TO :"monitor_user";
SQL
