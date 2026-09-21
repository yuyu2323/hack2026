#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/security_guard.py files
server/.venv/bin/python -m unittest discover -s tests/security -p 'test_*.py'
python3 -m unittest discover -s tests/runtime -p 'test_*.py'
if [ "${1:-}" = '--postgres' ]; then
  server/.venv/bin/python -m pytest server/tests -q --tb=short -m 'not real_ai'
else
  server/.venv/bin/python -m pytest server/tests -q --tb=short -m 'not real_ai and not postgres'
fi
ai-service/.venv/bin/python -m pytest ai-service/tests -q --tb=short
npm run test:client
npm run test --workspaces --if-present
npm run test:ui --workspaces --if-present
npm run build
