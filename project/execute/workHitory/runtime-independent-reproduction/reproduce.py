"""현재 QA를 건드리지 않는 임시 구성/서비스 수명주기 검증 harness."""
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

import httpx

SOURCE = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
TEMP = Path(tempfile.mkdtemp(prefix='storeloop-runtime-repro-', dir='/private/tmp')).resolve()
TEMP.chmod(0o700)
REPORT = {'temp_root': str(TEMP), 'checks': [], 'not_run': [
    '문서 setup/start 전체: 고정 포트와 현재 QA가 충돌',
    'pip/npm/Gitleaks 신규 설치: 외부 전송 금지, 기존 의존성 읽기 재사용',
    'Git 훅 설치: Git 변경 범위 제외',
    '실제 모델 분석/브라우저 클릭: 이번 검증 범위 제외',
]}
PRIVATE = []
PG_STARTED = False
SERVICES = None
OUTSIDER = None
OWNED = []


def record(name, **details):
    REPORT['checks'].append({'name': name, 'status': 'PASS', **details})
    print(name + ': PASS', flush=True)


def scrub(value):
    for secret in PRIVATE:
        value = value.replace(secret, '[REDACTED]')
    return value


def private_text(path, text):
    with os.fdopen(os.open(path, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600), 'w') as file:
        file.write(text)


ENV = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'TMPDIR', 'SYSTEMROOT') if key in os.environ}
ENV.update(PIP_NO_INDEX='1', npm_config_offline='true', PYTHONDONTWRITEBYTECODE='1',
           HTTP_PROXY='', HTTPS_PROXY='', ALL_PROXY='', NO_PROXY='127.0.0.1,localhost')


def run(label, command, env=None, timeout=45):
    output = subprocess.run(command, cwd=TEMP, env=env or ENV, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    private_text(TEMP / (label + '.log'), scrub(output.stdout))
    if output.returncode:
        raise RuntimeError(label + ': exit=' + str(output.returncode))
    return output.stdout


def reserve_ports():
    sockets = []
    try:
        for _ in range(4):
            item = socket.socket()
            item.bind(('127.0.0.1', 0))
            sockets.append(item)
        ports = [item.getsockname()[1] for item in sockets]
        assert len(set(ports)) == 4
        assert not set(ports) & {8000, 8010, 55432, 5173, 5174, 5175, 5176, 5177}
        return ports
    finally:
        for item in sockets:
            item.close()


def pid_alive(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True)
    return result.returncode == 0 and not result.stdout.lstrip().startswith('Z')


def wait_url(port, path='/health'):
    deadline = time.monotonic() + 15
    with httpx.Client(trust_env=False, timeout=1) as client:
        while time.monotonic() < deadline:
            try:
                response = client.get(f'http://127.0.0.1:{port}{path}')
                if response.status_code == 200:
                    return response
            except httpx.HTTPError:
                pass
            time.sleep(0.15)
    raise RuntimeError('local readiness timeout')


try:
    # 비밀/캐시/설치 환경을 복제하지 않고 제품 소스와 합성 공개 자산만 복사한다.
    ignore = shutil.ignore_patterns('.venv', '.local', 'node_modules', '__pycache__',
                                    '.pytest_cache', '.env*', 'dist', '*.pyc')
    for name in ('server', 'ai-service', 'packages', 'scripts', 'web-concepts-01'):
        shutil.copytree(SOURCE / name, TEMP / name, ignore=ignore)
    for name in ('setup.sh', 'start.sh', 'stop.sh', 'package.json', 'package-lock.json'):
        shutil.copy2(SOURCE / name, TEMP / name)
    assert not (TEMP / '.local').exists() and not (TEMP / '.git').exists()
    REPORT['source_hashes'] = {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
                             for name in ('setup.sh', 'start.sh', 'stop.sh', 'scripts/local_runtime.py', 'scripts/services.py')}
    record('source_copy_without_secrets')
    preflight = run('preflight', [sys.executable, str(TEMP / 'scripts/preflight.py')])
    record('documented_preflight', versions=preflight.strip().splitlines())
    run('prepare_first', [sys.executable, str(TEMP / 'scripts/local_runtime.py'), 'prepare'])
    env_path = TEMP / '.local/runtime.env'
    password_path = TEMP / '.local/postgres-password'
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in (env_path, password_path)]
    run('prepare_replay', [sys.executable, str(TEMP / 'scripts/local_runtime.py'), 'prepare'])
    assert hashes == [hashlib.sha256(path.read_bytes()).hexdigest() for path in (env_path, password_path)]
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in (env_path, password_path))
    record('prepare_private_files_and_replay_preservation')
    for domain in ('server', 'ai-service'):
        run(domain + '_venv', [shutil.which('python3'), '-m', 'venv', str(TEMP / domain / '.venv')])
        site = next((TEMP / domain / '.venv/lib').glob('python*/site-packages'))
        existing = next((SOURCE / domain / '.venv/lib').glob('python*/site-packages'))
        private_text(site / 'reused_readonly_dependencies.pth', str(existing) + '\n')
    (TEMP / 'node_modules').symlink_to(SOURCE / 'node_modules', target_is_directory=True)
    record('new_separate_venvs_with_reused_dependencies')
    pg_port, api_port, ai_port, vite_port = reserve_ports()
    REPORT['ports'] = {'postgres': pg_port, 'api': api_port, 'ai': ai_port, 'vite': vite_port}
    from dotenv import dotenv_values
    values = dict(dotenv_values(env_path))
    password = password_path.read_text().strip()
    PRIVATE.extend([password, values['AI_SERVICE_TOKEN']])
    database_url = f'postgresql+psycopg://storeloop:{password}@127.0.0.1:{pg_port}/storeloop_repro'
    test_url = database_url + '_test'
    PRIVATE.extend([database_url, test_url])
    values.update(DATABASE_URL=database_url, STORELOOP_TEST_DATABASE_URL=test_url,
                  AI_SERVICE_URL=f'http://127.0.0.1:{ai_port}',
                  ALLOWED_ORIGINS=json.dumps([f'http://127.0.0.1:{vite_port}']))
    # 임시 설정만 재작성하며 제품 스크립트의 포트 지원으로 오인하지 않는다.
    import shlex
    private_text(env_path, '\n'.join(f'{key}={shlex.quote(value)}' for key, value in values.items()) + '\n')
    ENV.update(values, PYTHONPATH=str(TEMP))
    sys.path.insert(0, str(TEMP / 'scripts'))
    import local_runtime
    import services
    SERVICES = services
    assert services.ROOT == TEMP and local_runtime.LOCAL == TEMP / '.local'
    ctl = local_runtime.pg_binary('pg_ctl')
    data, sockets = TEMP / '.local/postgres', TEMP / '.local/socket'
    sockets.mkdir(mode=0o700)
    run('initdb', [local_runtime.pg_binary('initdb'), '-D', str(data), '--username=storeloop',
                  '--auth-local=scram-sha-256', '--auth-host=scram-sha-256', '--pwfile=' + str(password_path),
                  '--encoding=UTF8', '--locale=C'])
    run('postgres_start', [ctl, '-D', str(data), '-l', str(TEMP / '.local/logs/postgres.log'),
                          '-o', f'-h 127.0.0.1 -p {pg_port} -k {sockets}', '-w', 'start'])
    PG_STARTED = True
    pg_env = dict(ENV, PGPASSWORD=password)
    for name in ('storeloop_repro', 'storeloop_repro_test'):
        run('create_' + name, [local_runtime.pg_binary('createdb'), '-h', '127.0.0.1', '-p', str(pg_port),
                              '-U', 'storeloop', name], pg_env)
    record('new_postgres_cluster_and_databases')
    python = str(TEMP / 'server/.venv/bin/python')
    run('migration', [python, '-m', 'alembic', '-c', 'server/alembic.ini', 'upgrade', 'head'])
    first = json.loads(run('seed_first', [python, '-m', 'server.seed']).strip())
    replay = json.loads(run('seed_replay', [python, '-m', 'server.seed']).strip())
    assert first['created'] > 500 and replay.get('created', 0) == 0
    credentials_path = TEMP / '.local/demo-credentials'
    assert credentials_path.stat().st_mode & 0o777 == 0o600
    record('migration_seed_and_idempotent_replay', first_created=first['created'], replay_created=replay.get('created', 0))
    # 외부 모델을 호출하지 않으며 seed fixture만 있는 DB를 worker에 연결한다.
    os.environ.clear()
    os.environ.update(ENV)
    captured = {}
    def capture(name, command, marker, port=None, cwd=None):
        captured[name] = (list(command), marker, port)
    with patch.object(services, 'prepare'), patch.object(services, 'require_available_port'), \
            patch.object(services, 'healthy', return_value=True), patch.object(services, 'launch', side_effect=capture):
        services.start([1], False)
    commands = []
    for name, assigned_port in [('ai', ai_port), ('api', api_port), ('worker', None)]:
        command, marker, _ = captured[name]
        if assigned_port:
            command[command.index('--port') + 1] = str(assigned_port)
        commands.append((name, command, marker, assigned_port))
    for name, command, marker, port in commands:
        services.launch(name, command, marker, port)
        info = json.loads((TEMP / '.local/pids' / (name + '.json')).read_text())
        OWNED.append(info['pid'])
        command_text = subprocess.run(['ps', '-p', str(info['pid']), '-o', 'command='], capture_output=True, text=True).stdout.strip()
        REPORT.setdefault('owned_process_checks', []).append({'name': name, 'command': command_text,
                                                              'recognized': services.alive(info['pid'], marker)})
        assert services.alive(info['pid'], marker), name + ': own process not recognized'
        if port:
            wait_url(port)
    record('isolated_ai_api_worker_started')
    api_pid = OWNED[1]
    services.launch(*commands[1])
    assert json.loads((TEMP / '.local/pids/api.json').read_text())['pid'] == api_pid
    record('owned_start_replay_reuses_same_pid')
    vite_driver = TEMP / 'isolated-vite.mjs'
    private_text(vite_driver, "import {createServer} from 'vite';\nimport react from '@vitejs/plugin-react';\n" +
                 'const server=await createServer(' + json.dumps({'configFile': False, 'root': str(TEMP / 'web-concepts-01'),
                 'cacheDir': str(TEMP / '.local/vite-cache'), 'server': {'host': '127.0.0.1', 'port': vite_port,
                 'strictPort': True, 'proxy': {'/api': f'http://127.0.0.1:{api_port}'},
                 'fs': {'allow': [str(TEMP), str(SOURCE / 'node_modules'), str(SOURCE / 'packages')]}}})[:-1] +
                 ',plugins:[react()]});\nawait server.listen();\n')
    services.launch('concept-01', [shutil.which('node'), str(vite_driver)], str(vite_driver), vite_port)
    OWNED.append(json.loads((TEMP / '.local/pids/concept-01.json').read_text())['pid'])
    page = wait_url(vite_port, '/store-owner/submissions')
    assert '<html' in page.text.lower()
    credentials = json.loads(credentials_path.read_text())
    for item in credentials.values():
        PRIVATE.append(item['password'])
    status_summary = {}
    with httpx.Client(base_url=f'http://127.0.0.1:{vite_port}', trust_env=False, timeout=5) as client:
        entry = client.get('/src/main.tsx')
        assert entry.status_code == 200
        for login, path in [('owner.north', '/api/submissions'), ('ofc.north', '/api/dashboard'),
                            ('regional.north', '/api/dashboard'), ('hq.demo', '/api/references?include_inactive=true'),
                            ('operator.demo', '/api/operations/accounts')]:
            client.cookies.clear()
            csrf = client.get('/api/auth/csrf').json()['csrf_token']
            response = client.post('/api/auth/login', json={'login_id': login, 'password': credentials[login]['password']},
                                   headers={'Origin': f'http://127.0.0.1:{vite_port}', 'X-CSRF-Token': csrf})
            assert response.status_code == 200
            result = client.get(path)
            assert result.status_code == 200
            status_summary[credentials[login]['role']] = result.status_code
        assert client.get('/api/submissions').status_code == 403
    record('vite_spa_proxy_and_five_roles_http', statuses=status_summary)
    with httpx.Client(trust_env=False, timeout=2) as client:
        health = client.get(f'http://127.0.0.1:{ai_port}/health').json()
        assert health['last_success_at'] is None and health['last_failure_at'] is None
    record('no_real_ai_request')
    OUTSIDER = subprocess.Popen(['sleep', '60'], start_new_session=True)
    private_text(TEMP / '.local/pids/unrelated.json', json.dumps({'pid': OUTSIDER.pid, 'marker': 'sleep', 'name': 'unrelated'}))
    assert not services.alive(OUTSIDER.pid, 'sleep')
    with redirect_stdout(StringIO()) as stopped:
        services.stop()
    deadline = time.monotonic() + 10
    while any(pid_alive(pid) for pid in OWNED) and time.monotonic() < deadline:
        time.sleep(0.15)
    assert not any(pid_alive(pid) for pid in OWNED)
    assert OUTSIDER.poll() is None
    assert not list((TEMP / '.local/pids').glob('*.json'))
    record('owned_stop_preserves_unrelated_process', owned_count=len(OWNED))
    services.stop()
    record('stop_replay')
except BaseException as error:
    REPORT['failure'] = {'type': type(error).__name__, 'message': scrub(str(error))}
    REPORT['failure']['locations'] = [{'file': Path(frame.filename).name, 'line': frame.lineno}
                                      for frame in traceback.extract_tb(error.__traceback__)]
    print('reproduction: FAIL (' + type(error).__name__ + ')', flush=True)
finally:
    if SERVICES is not None:
        try:
            SERVICES.stop()
        except BaseException:
            REPORT['cleanup_service_error'] = True
    for pid in OWNED:
        if pid_alive(pid):
            os.killpg(pid, signal.SIGTERM)
    if OUTSIDER is not None and OUTSIDER.poll() is None:
        OUTSIDER.terminate()
        OUTSIDER.wait(timeout=5)
    if PG_STARTED:
        try:
            run('postgres_stop', [ctl, '-D', str(data), '-m', 'fast', '-w', 'stop'])
            status = subprocess.run([ctl, '-D', str(data), 'status'], capture_output=True)
            assert status.returncode != 0
            record('temporary_postgres_stopped')
        except BaseException:
            REPORT['cleanup_database_error'] = True
    REPORT['status'] = 'FAIL' if REPORT.get('failure') or REPORT.get('cleanup_service_error') or REPORT.get('cleanup_database_error') else 'PASS_WITH_NOT_RUN'
    private_text(EVIDENCE / 'result.json', json.dumps(REPORT, ensure_ascii=False, indent=2))
    print('result: ' + REPORT['status'], flush=True)
    print('evidence: ' + str(EVIDENCE / 'result.json'), flush=True)
sys.exit(1 if REPORT['status'] == 'FAIL' else 0)
