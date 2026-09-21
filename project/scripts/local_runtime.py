#!/usr/bin/env python3
"""프로젝트 전용 로컬 설정과 PostgreSQL만 구성한다."""
import argparse
import os
from pathlib import Path
import secrets
import shlex
import shutil
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'


def private_write(path, content):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(content)


def prepare():
    LOCAL.mkdir(exist_ok=True, mode=0o700)
    os.chmod(LOCAL, 0o700)
    for name in ['media', 'test-media', 'logs', 'pids']:
        (LOCAL / name).mkdir(exist_ok=True, mode=0o700)
    password_file = LOCAL / 'postgres-password'
    if not password_file.exists():
        private_write(password_file, secrets.token_urlsafe(32))
    password = password_file.read_text().strip()
    runtime_file = LOCAL / 'runtime.env'
    if not runtime_file.exists():
        origins = [f'http://{host}:{port}' for host in ['127.0.0.1', 'localhost'] for port in [5183]]
        values = {
            'DATABASE_URL': f'postgresql+psycopg://storeloop:{password}@127.0.0.1:55443/storeloop',
            'STORELOOP_TEST_DATABASE_URL': f'postgresql+psycopg://storeloop:{password}@127.0.0.1:55443/storeloop_test',
            'MEDIA_ROOT': str(LOCAL / 'media'),
            'AI_SERVICE_URL': 'http://127.0.0.1:8203',
            'AI_SERVICE_TOKEN': secrets.token_urlsafe(48),
            'SESSION_COOKIE_SECURE': 'false',
            'SESSION_COOKIE_NAME': 'storeloop_concept_03_session',
            'ALLOWED_ORIGINS': json.dumps(origins),
            'CODEX_BIN': shutil.which('codex') or 'codex',
            'CODEX_MODEL': 'gpt-6-astra',
            'CODEX_REASONING_EFFORT': 'low',
            'QUEUE_TIMEOUT_SECONDS': '180',
            'MODEL_TIMEOUT_SECONDS': '120',
            'AI_HTTP_TIMEOUT_SECONDS': '130',
            'LEASE_TIMEOUT_SECONDS': '140',
            'HEARTBEAT_INTERVAL_SECONDS': '10',
        }
        private_write(runtime_file, '\n'.join(f'{key}={shlex.quote(value)}' for key, value in values.items()) + '\n')
    print('로컬 설정 준비 완료: .local/runtime.env (기존 값 보존, 비밀 무출력)')


def pg_binary(name):
    candidates = [os.environ.get('PG_BIN_DIR', ''), '/opt/homebrew/opt/postgresql@16/bin', '/opt/homebrew/opt/postgresql@14/bin']
    for folder in candidates:
        candidate = Path(folder) / name
        if folder and candidate.is_file():
            return str(candidate)
    found = shutil.which(name)
    if found:
        return found
    raise SystemExit(f'PostgreSQL 실행 파일을 찾지 못했습니다: {name}. PG_BIN_DIR을 지정해 주세요.')


def database(action):
    prepare()
    data = LOCAL / 'postgres'
    ctl = pg_binary('pg_ctl')
    if action == 'stop':
        if (data / 'PG_VERSION').exists():
            subprocess.run([ctl, '-D', str(data), '-m', 'fast', '-w', 'stop'], check=True)
        return
    if not (data / 'PG_VERSION').exists():
        subprocess.run([pg_binary('initdb'), '-D', str(data), '--username=storeloop',
                        '--auth-local=scram-sha-256', '--auth-host=scram-sha-256',
                        '--pwfile=' + str(LOCAL / 'postgres-password'), '--encoding=UTF8', '--locale=C'], check=True)
    status = subprocess.run([ctl, '-D', str(data), 'status'], capture_output=True)
    if status.returncode:
        # 긴 한글 프로젝트 경로가 UNIX 소켓 경로 한도를 넘지 않게 한다.
        subprocess.run([ctl, '-D', str(data), '-l', str(LOCAL / 'logs/postgres.log'),
                        '-o', '-h 127.0.0.1 -p 55443 -k /tmp', '-w', 'start'], check=True)
    env = dict(os.environ, PGPASSWORD=(LOCAL / 'postgres-password').read_text().strip())
    command = [pg_binary('psql'), '-h', '127.0.0.1', '-p', '55443', '-U', 'storeloop', '-d', 'postgres', '-At']
    present = subprocess.check_output(command + ['-c', 'SELECT datname FROM pg_database'], env=env, text=True).splitlines()
    for name in ['storeloop', 'storeloop_test']:
        if name not in present:
            subprocess.run(command + ['-c', f'CREATE DATABASE {name}'], env=env, check=True)
    print('전용 PostgreSQL 준비 완료: 127.0.0.1:55443 / storeloop, storeloop_test')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'start', 'stop'])
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else database(args.action)
