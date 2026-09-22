"""마이그레이션과 선택한 합성 시드를 시작 전에 한 번 적용한다."""
import os
import subprocess
import sys

subprocess.run([sys.executable, '-m', 'alembic', '-c', 'server/alembic.ini', 'upgrade', 'head'], check=True)
if os.environ.get('SEED_DEMO', 'false').lower() == 'true':
    subprocess.run([sys.executable, '-m', 'server.seed'], check=True)
