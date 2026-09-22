"""운영 빌드에서 신규 DB만 초기화한다. 자격값을 빌드 산출물에 남기지 않는다."""
import json
import os
from pathlib import Path
import tempfile

# 세션 단위 마이그레이션 잠금은 transaction pooler를 거치지 않는다.
if os.environ.get('VERCEL_ENV') == 'production' and os.environ.get('DATABASE_URL_UNPOOLED'):
    os.environ['DATABASE_URL'] = os.environ['DATABASE_URL_UNPOOLED']

from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from server.core.config import PROJECT_ROOT
from server.core.db import engine
from sqlalchemy.orm import Session


def initialize():
    if os.environ.get('VERCEL_ENV') != 'production':
        return
    if not os.environ.get('DATABASE_URL'):
        raise RuntimeError('Production DATABASE_URL 설정이 필요합니다.')
    # 배포 재시도와 동시 빌드 사이의 초기화 경쟁을 방지한다.
    with engine.connect() as connection:
        postgres = connection.dialect.name == 'postgresql'
        if postgres:
            connection.execute(text('SELECT pg_advisory_lock(72602602)'))
            connection.commit()
        try:
            cfg = Config(str(PROJECT_ROOT / 'server/alembic.ini'))
            cfg.attributes['connection'] = connection
            command.upgrade(cfg, 'head')
            connection.commit()
            from server.core.models import Account
            with Session(bind=connection) as db:
                if db.scalar(select(Account.id).limit(1)) is not None:
                    print('기존 DB 스키마 갱신 완료: 계정과 데이터 보존')
                    return
                password = os.environ.get('DEMO_PASSWORD', '')
                if len(password) < 24:
                    raise RuntimeError('신규 DB 초기화에는 24자 이상의 DEMO_PASSWORD 비밀값이 필요합니다.')
                logins = [r + '.' + a for r in ('owner', 'ofc', 'regional') for a in ('north', 'south')]
                logins += ['hq.demo', 'operator.demo', 'owner.inactive', 'owner.unmapped']
                with tempfile.TemporaryDirectory(prefix='storeloop-seed-') as directory:
                    file = Path(directory) / 'credentials.json'
                    file.write_text(json.dumps({login: {'password': password} for login in logins}), encoding='utf-8')
                    os.chmod(file, 0o600)
                    os.environ['SEED_CREDENTIAL_FILE'] = str(file)
                    try:
                        from server.seed.__main__ import seed
                        seed(db)
                        db.commit()
                    finally:
                        os.environ.pop('SEED_CREDENTIAL_FILE', None)
                print('신규 시연 DB 초기화 완료: 자격값은 출력하지 않음')
        finally:
            if postgres:
                connection.rollback()
                connection.execute(text('SELECT pg_advisory_unlock(72602602)'))
                connection.commit()


if __name__ == '__main__':
    try:
        initialize()
    except Exception as error:
        # 연결 문자열·SQL 매개변수·자격 파일 내용은 빌드 로그에 남기지 않는다.
        print('DB 초기화 실패: ' + type(error).__name__)
        raise SystemExit(1) from None
