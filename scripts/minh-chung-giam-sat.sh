#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose ps
docker compose exec -T prometheus promtool check config /etc/prometheus/prometheus.yml
python3 scripts/verify-monitoring.py
printf '\nBan tu chup ket qua; script khong chup anh va khong sua du lieu nghiep vu.\n'
exec bash
