#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose ps
docker compose exec -T nginx nginx -t
curl -sS -D - -o /dev/null http://localhost:8036/
python3 scripts/verify-nginx.py
printf '\nBan tu chup ket qua trong terminal nay. Khong co anh tu dong.\n'
exec bash
