#!/bin/bash
set -eu
cd "$(dirname "$0")/.."
python3 scripts/verify-hardening.py
exec bash
