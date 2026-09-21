#!/usr/bin/env python3
"""공식 고정 배포본의 SHA-256을 확인한 뒤 로컬 검사기를 설치한다."""
import hashlib
import io
import os
from pathlib import Path
import platform
import ssl
import tarfile
import urllib.request
import certifi

ROOT = Path(__file__).resolve().parents[1]
VERSION = '8.30.1'
DIGESTS = {
    ('Darwin','arm64'): ('darwin_arm64','b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5'),
    ('Darwin','x86_64'): ('darwin_x64','dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709'),
    ('Linux','x86_64'): ('linux_x64','551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb'),
    ('Linux','aarch64'): ('linux_arm64','e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080'),
}
def main():
    target, digest = DIGESTS[(platform.system(), platform.machine())]
    url = f'https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/gitleaks_{VERSION}_{target}.tar.gz'
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=certifi.where())
    data = urllib.request.urlopen(url, timeout=60, context=context).read()
    if hashlib.sha256(data).hexdigest() != digest:
        raise SystemExit('Gitleaks 배포본 체크섬 불일치')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        content = archive.extractfile('gitleaks').read()
    binary = ROOT / '.local/bin/gitleaks'
    binary.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    binary.write_bytes(content); os.chmod(binary, 0o700)
    print('Gitleaks 8.30.1 공식 체크섬 확인·설치 완료')

if __name__ == '__main__':
    main()
