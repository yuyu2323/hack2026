#!/usr/bin/env python3
"""이 프로젝트가 직접 띄운 프로세스만 시작·종료한다."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import shutil
import subprocess
import time
import urllib.request
from local_runtime import ROOT, LOCAL, prepare

def healthy(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def alive(pid, marker):
    result = subprocess.run(['ps','-p',str(pid),'-o','command='], capture_output=True, text=True)
    return result.returncode == 0 and marker in result.stdout and str(ROOT) in result.stdout

def require_available_port(name, port):
    path = LOCAL / 'pids' / (name + '.json')
    if path.exists():
        info = json.loads(path.read_text())
        if alive(info['pid'], info['marker']):
            return
    occupied = healthy(port)
    if not occupied:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.3):
                occupied = True
        except OSError:
            pass
    if occupied:
        raise SystemExit(f'{name}: 포트 {port}에 이 실행 명령이 관리하지 않는 프로세스가 있습니다. 해당 실행 창에서 종료한 뒤 다시 시작하세요.')

def launch(name, command, marker, port=None, cwd=ROOT):
    path = LOCAL / 'pids' / (name + '.json')
    if path.exists():
        info = json.loads(path.read_text())
        if alive(info['pid'], info['marker']):
            print(name + ': 이미 실행 중'); return
    if port:
        require_available_port(name, port)
    log_path = LOCAL / 'logs' / (name + '.log')
    descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, 'ab') as log:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    path.write_text(json.dumps({'pid':process.pid,'marker':marker,'name':name})); path.chmod(0o600)
    time.sleep(0.3)
    if process.poll() is not None:
        raise SystemExit(name + ': 시작 실패. .local/logs의 해당 로그를 확인해 주세요.')
    print(name + ': 시작 완료')

def start(concepts, without_worker):
    prepare()
    # 하나라도 충돌하면 일부 서비스가 먼저 시작되어 서로 다른 DB가 섞이지 않게 한다.
    for name, port in [('ai', 8010), ('api', 8000)] + [(f'concept-{number:02d}', 5172+number) for number in concepts]:
        require_available_port(name, port)
    launch('ai',[str(ROOT/'ai-service/.venv/bin/python'),'-m','uvicorn','app.main:app','--app-dir',str(ROOT/'ai-service'),'--host','127.0.0.1','--port','8010','--no-access-log'],'app.main:app',8010)
    launch('api',[str(ROOT/'server/.venv/bin/python'),'-m','uvicorn','server.main:app','--app-dir',str(ROOT),'--host','127.0.0.1','--port','8000','--no-access-log'],'server.main:app',8000)
    for port in (8010, 8000):
        deadline = time.monotonic() + 15
        while not healthy(port) and time.monotonic() < deadline:
            time.sleep(0.2)
        if not healthy(port):
            raise SystemExit(f'서비스 준비 실패: 포트 {port}')
    if not without_worker:
        launch('worker',[str(ROOT/'server/.venv/bin/python'),str(ROOT/'scripts/worker_entry.py')],'worker_entry.py')
    for number in concepts:
        package = ROOT / f'web-concepts-{number:02d}'
        launch(f'concept-{number:02d}',[shutil.which('node'),str(ROOT/'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port',str(5172+number),'--strictPort'],f'--port {5172+number}',port=5172+number,cwd=package)
        print(f'시안 {number:02d}: http://127.0.0.1:{5172+number}')

def stop():
    for path in sorted((LOCAL/'pids').glob('*.json')):
        info = json.loads(path.read_text())
        if alive(info['pid'], info['marker']):
            os.killpg(info['pid'], signal.SIGTERM)
            print(info['name'] + ': 정상 종료 요청')
        path.unlink()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start','stop'])
    parser.add_argument('--concept', type=int, choices=range(1,6), action='append')
    parser.add_argument('--without-worker', action='store_true')
    args = parser.parse_args()
    start(args.concept or [1], args.without_worker) if args.action == 'start' else stop()
