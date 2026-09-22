"""URL에 안전한 서버 비밀을 생성하되 기존 설정은 덮어쓰지 않는다."""
import argparse
import os
from pathlib import Path
import secrets
from urllib.parse import urlsplit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', required=True, help='프론트의 최종 HTTPS origin')
    parser.add_argument('--backend-origin', help='분리 배포 시 Caddy의 공개 HTTPS origin')
    args = parser.parse_args()
    origin = urlsplit(args.origin)
    if origin.scheme != 'https' or not origin.hostname or origin.username or origin.password or origin.path not in ('', '/') or origin.query or origin.fragment:
        raise SystemExit('--origin에는 경로 없는 HTTPS 주소가 필요합니다.')
    backend = urlsplit(args.backend_origin) if args.backend_origin else origin
    if backend.scheme != 'https' or not backend.hostname or backend.username or backend.password or backend.path not in ('', '/') or backend.query or backend.fragment:
        raise SystemExit('--backend-origin에는 경로 없는 HTTPS 주소가 필요합니다.')
    root = Path(__file__).resolve().parents[1]
    local = root / '.local'
    local.mkdir(mode=0o700, exist_ok=True)
    values = {
        'POSTGRES_PASSWORD': secrets.token_hex(32),
        'AI_SERVICE_TOKEN': secrets.token_hex(48),
        'OPENAI_API_KEY': '',
        'OPENAI_MODEL': 'gpt-4.1-mini',
        'OPENAI_MAX_OUTPUT_TOKENS': '6000',
        'AI_REQUESTS_ENABLED': 'false',
        'PUBLIC_ORIGIN': f'https://{origin.netloc}',
        'SITE_ADDRESS': backend.netloc,
        'HTTP_PORT': '80', 'HTTPS_PORT': '443',
        'SESSION_COOKIE_SECURE': 'true', 'SEED_DEMO': 'true',
    }
    path = local / 'deploy.env'
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise SystemExit('기존 .local/deploy.env를 보존합니다. 필요 항목만 직접 수정하세요.') from None
    with os.fdopen(fd, 'w') as f:
        f.write('\n'.join(f'{key}={value}' for key, value in values.items()) + '\n')
    print('.local/deploy.env 생성 완료. API 키는 이 비공개 파일에 설정하세요. 모델 호출은 비활성화 상태입니다.')


if __name__ == '__main__':
    main()
