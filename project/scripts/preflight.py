#!/usr/bin/env python3
"""구성 파일을 만들기 전에 필수 로컬 도구 버전을 확인한다."""
import re
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from local_runtime import pg_binary


def version(command, minimum, name):
    try:
        value = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit(f'{name}을 실행할 수 없습니다. 설치와 PATH를 확인해 주세요.') from None
    found = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', value)
    actual = tuple(int(part or 0) for part in found.groups()) if found else ()
    if actual < minimum:
        raise SystemExit(f'{name} 버전이 부족합니다. 최소 {".".join(map(str, minimum))}이 필요합니다.')
    print(f'{name}: {".".join(map(str, actual))}')


def main():
    version([sys.executable, '--version'], (3, 11, 0), 'Python')
    version([shutil.which('node') or 'node', '--version'], (22, 12, 0), 'Node')
    version([shutil.which('npm') or 'npm', '--version'], (10, 0, 0), 'npm')
    version([pg_binary('pg_ctl'), '--version'], (14, 0, 0), 'PostgreSQL')
    provider = os.environ.get('AI_PROVIDER')
    if provider is None:
        runtime = Path(__file__).resolve().parents[1] / '.local/runtime.env'
        if runtime.exists():
            for line in runtime.read_text().splitlines():
                if line.startswith('AI_PROVIDER='):
                    values = shlex.split(line.split('=', 1)[1])
                    provider = values[0] if values else 'codex'
    if (provider or 'codex') == 'codex':
        version([shutil.which('codex') or 'codex', '--version'], (0, 0, 0), 'Codex CLI')

if __name__ == '__main__':
    main()
