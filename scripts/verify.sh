#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose config --quiet
docker compose ps
docker compose exec -T web id
cat scripts/smoke.py | docker compose exec -T web python -
curl -fsS http://localhost:8036/health
printf '\n'
