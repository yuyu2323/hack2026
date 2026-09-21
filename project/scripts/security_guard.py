#!/usr/bin/env python3
"""커밋할 내용과 전송할 전체 이력을 비밀 원문 출력 없이 검사한다."""
import argparse
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
PINNED_VERSION = '8.30.1'


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise RuntimeError('Git 검사 범위를 읽지 못했습니다.')
    return result.stdout


def forbidden(path):
    p = PurePosixPath(path)
    name = p.name.lower()
    if name == '.env.example':
        return False
    return (name == '.env' or name.startswith('.env.') or '.local' in p.parts
            or '.venv' in p.parts or name in {'auth.json', 'id_rsa', 'id_ed25519'}
            or name.startswith(('storage-state', 'storagestate', 'credentials'))
            or p.suffix.lower() in {'.pem', '.key', '.p12', '.pfx', '.db', '.sqlite', '.sqlite3', '.dump', '.log'})


def check_paths(paths):
    bad = [p for p in paths if p and forbidden(p)]
    if bad:
        raise RuntimeError(f'추적 금지 파일 {len(bad)}개를 발견했습니다. 파일 내용은 출력하지 않습니다.')


def scanner():
    binary = Path(os.environ.get('GITLEAKS_BIN', PROJECT / '.local/bin/gitleaks'))
    result = subprocess.run([str(binary), 'version'], capture_output=True, text=True)
    if result.returncode or result.stdout.strip() != PINNED_VERSION:
        raise RuntimeError('고정 버전 Gitleaks 설치를 확인해 주세요.')
    return str(binary)


def scan(binary, args, content=None):
    command = [binary, *args, '--config', str(PROJECT / '.gitleaks.toml'), '--redact=100',
               '--no-banner', '--no-color', '--ignore-gitleaks-allow', '--gitleaks-ignore-path', '/dev/null']
    env = {k: v for k, v in os.environ.items() if k not in {'GITLEAKS_CONFIG', 'GITLEAKS_CONFIG_TOML'}}
    result = subprocess.run(command, input=content, capture_output=True, env=env)
    if result.returncode:
        # 검사기의 내부 로그나 발견 원문을 다시 출력하지 않는다.
        raise RuntimeError('비밀 후보 발견 또는 검사 오류로 작업을 차단했습니다. 비밀 없는 파일 위치 검토가 필요합니다.')


def staged(repo, binary):
    paths = git(repo, 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z').decode().split('\0')
    check_paths(paths)
    for path in filter(None, paths):
        scan(binary, ['stdin'], git(repo, 'show', ':' + path))


def pushing(repo, binary, lines):
    if not lines.strip():
        raise RuntimeError('전송할 ref 검사 입력이 없습니다.')
    for line in lines.splitlines():
        parts = line.split()
        if len(parts) != 4:
            raise RuntimeError('잘못된 pre-push ref 입력입니다.')
        _, local, _, remote = parts
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', local) or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', remote):
            raise RuntimeError('유효하지 않은 Git object ID입니다.')
        if not local.strip('0'):
            continue
        known = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', remote + '^{commit}'], capture_output=True).returncode == 0
        revision = remote + '..' + local if known and remote.strip('0') else local
        commits = git(repo, 'rev-list', revision).decode().splitlines()
        for commit in commits:
            paths = git(repo, 'diff-tree', '--root', '-m', '--no-commit-id', '--name-only', '-r', '-z', commit).decode().split('\0')
            check_paths(paths)
        if commits:
            scan(binary, ['git', str(repo), '--log-opts=-m ' + revision])


def files(repo, binary):
    # Git이 추적하거나 새 추적 후보로 보는 파일만 검사한다. 로컬 비밀 저장소는 제외된다.
    paths = git(repo, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')
    check_paths(paths)
    for path in filter(None, paths):
        file = repo / path
        if file.is_file():
            scan(binary, ['stdin'], file.read_bytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['staged', 'push', 'files'])
    parser.add_argument('--repo', type=Path, default=PROJECT.parent)
    args = parser.parse_args()
    try:
        binary = scanner()
        if args.mode == 'staged':
            staged(args.repo, binary)
        elif args.mode == 'push':
            pushing(args.repo, binary, sys.stdin.read())
        else:
            files(args.repo, binary)
        print('StoreLoop 비밀·금지 파일 검사 통과')
        return 0
    except (OSError, RuntimeError) as exc:
        print('StoreLoop 보안 검사 차단: ' + (str(exc) if isinstance(exc, RuntimeError) else '검사 도구를 실행하지 못했습니다.'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
