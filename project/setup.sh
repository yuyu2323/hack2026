#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/preflight.py
python3 scripts/local_runtime.py prepare
python3 -m venv server/.venv
python3 -m venv ai-service/.venv
server/.venv/bin/python -m pip install -r server/requirements.lock
ai-service/.venv/bin/python -m pip install -r ai-service/requirements.lock
npm ci --cache .local/npm-cache --no-audit --no-fund
server/.venv/bin/python scripts/install_security.py
git -C .. config core.hooksPath project/.githooks
python3 scripts/local_runtime.py start
server/.venv/bin/alembic -c server/alembic.ini upgrade head
server/.venv/bin/python -m server.seed
printf '%s\n' '설정 완료. .local/demo-credentials에서 시연 계정을 확인하고 ./start.sh를 실행하세요.'
