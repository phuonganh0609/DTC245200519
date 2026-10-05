#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 scripts/prepare-env.py
docker compose config --quiet
docker compose up -d --wait db
docker compose exec -T db sh /opt/setup-monitoring.sh
docker compose up -d nginx cadvisor nginx-exporter postgres-exporter prometheus grafana
# Docker Desktop: gọi CLI Windows cho riêng cAdvisor để bind /sys, /var/run
# vào filesystem Linux của daemon, thay vì filesystem của distro Ubuntu.
case "$(docker info --format '{{.OperatingSystem}}')" in
  *Docker\ Desktop*)
    if command -v docker.exe >/dev/null 2>&1; then
      docker.exe compose --project-directory "$(wslpath -w "$PWD")" \
        --file "$(wslpath -w "$PWD/compose.yaml")" \
        --env-file "$(wslpath -w "$PWD/.env")" \
        up -d --no-deps --force-recreate cadvisor
    fi
    ;;
esac
