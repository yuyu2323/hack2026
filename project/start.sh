#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 scripts/local_runtime.py start
exec python3 scripts/services.py start "$@"
