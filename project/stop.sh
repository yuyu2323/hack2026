#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/services.py stop
printf '%s\n' 'PostgreSQL을 함께 종료하려면 ./scripts/db.sh stop을 실행하세요.'
