#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose ps loki promtail grafana
python3 scripts/verify-logs.py
printf '\nBan tu chup ket qua. GET kiem thu khong sua du lieu nghiep vu.\n'
exec bash
