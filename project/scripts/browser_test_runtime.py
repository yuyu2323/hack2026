"""브라우저 인수용 DB·미디어를 시연 서비스와 분리해 실행한다."""
import argparse
import os
from pathlib import Path
import subprocess
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','api','worker'])
    args = parser.parse_args()
    values = dotenv_values(ROOT / '.local/runtime.env')
    from sqlalchemy.engine import make_url
    url = values['STORELOOP_TEST_DATABASE_URL']
    if not make_url(url).database.endswith('_test'):
        raise SystemExit('브라우저 인수는 전용 _test DB만 허용합니다.')
    env = {**os.environ, 'DATABASE_URL':url, 'MEDIA_ROOT':str(ROOT / '.local/test-media')}
    python = str(ROOT / 'server/.venv/bin/python')
    if args.action == 'prepare':
        subprocess.run([str(ROOT/'server/.venv/bin/alembic'),'-c','server/alembic.ini','upgrade','head'],cwd=ROOT,env=env,check=True)
        subprocess.run([python,'-m','server.seed'],cwd=ROOT,env=env,check=True)
    else:
        command = [python,'-m','uvicorn','server.main:app','--host','127.0.0.1','--port','8101','--no-access-log'] if args.action == 'api' else [python,'-m','server.analysis_jobs.worker']
        os.chdir(ROOT); os.execve(python, command, env)

if __name__ == '__main__':
    main()
