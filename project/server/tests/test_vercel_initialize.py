"""배포 초기화의 자격정보 삭제와 기존 계정 보존 검증."""
from pathlib import Path
import os
import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from deploy.vercel import initialize as deployment
from server.core.config import get_settings
from server.core.db import make_engine
from server.core.models import Account
from server.submissions.models import MediaBlob

@pytest.fixture
def production(monkeypatch, tmp_path):
    url = 'sqlite:///' + str(tmp_path / 'deployment.sqlite')
    engine = make_engine(url)
    monkeypatch.setattr(deployment, 'engine', engine)
    monkeypatch.setenv('VERCEL_ENV', 'production')
    monkeypatch.setenv('DATABASE_URL', url)
    monkeypatch.setenv('DEMO_PASSWORD', 'test-only-deployment-password-2026')
    monkeypatch.setattr(get_settings(), 'media_storage', 'database')
    yield engine
    engine.dispose()

def test_initialize_once_preserves_accounts_erases_credentials(production, monkeypatch, capsys):
    from server.seed import __main__ as seeder
    original, files = seeder.seed, []
    def capture_seed(db):
        file = Path(os.environ['SEED_CREDENTIAL_FILE'])
        assert file.is_file() and not file.is_relative_to(deployment.PROJECT_ROOT)
        files.append(file)
        return original(db)
    monkeypatch.setattr(seeder, 'seed', capture_seed)
    deployment.initialize()
    assert len(files) == 1 and not files[0].exists()
    assert 'SEED_CREDENTIAL_FILE' not in os.environ
    with Session(production) as db:
        owner = db.scalar(select(Account).where(Account.login_id == 'owner.north'))
        ident, original_hash = owner.id, owner.password_hash
        owner.display_name = '사용자 변경 보존'
        db.commit()
        assert db.scalar(select(func.count()).select_from(MediaBlob)) == 20
    monkeypatch.setenv('DEMO_PASSWORD', 'different-password-should-not-replace')
    deployment.initialize()
    with Session(production) as db:
        owner = db.get(Account, ident)
        assert owner.display_name == '사용자 변경 보존' and owner.password_hash == original_hash
    assert len(files) == 1
    assert 'test-only-deployment-password-2026' not in capsys.readouterr().out

def test_preview_never_opens_database(monkeypatch):
    class Forbidden:
        def connect(self):
            raise AssertionError('preview must not initialize production')
    monkeypatch.setattr(deployment, 'engine', Forbidden())
    monkeypatch.setenv('VERCEL_ENV', 'preview')
    deployment.initialize()

def test_missing_database_fails_before_connect(monkeypatch):
    monkeypatch.setenv('VERCEL_ENV', 'production')
    monkeypatch.delenv('DATABASE_URL', raising=False)
    with pytest.raises(RuntimeError, match='DATABASE_URL'):
        deployment.initialize()

def test_new_database_rejects_short_password(production, monkeypatch):
    monkeypatch.setenv('DEMO_PASSWORD', 'short')
    with pytest.raises(RuntimeError, match='24'):
        deployment.initialize()
    with Session(production) as db:
        assert db.scalar(select(func.count()).select_from(Account)) == 0

def test_seed_failure_cleans_credentials_and_rolls_back(production, monkeypatch):
    from server.seed import __main__ as seeder
    paths = []
    def fail(db):
        paths.append(Path(os.environ['SEED_CREDENTIAL_FILE']))
        raise RuntimeError('controlled test failure')
    monkeypatch.setattr(seeder, 'seed', fail)
    with pytest.raises(RuntimeError, match='controlled'):
        deployment.initialize()
    assert paths and not paths[0].exists()
    assert 'SEED_CREDENTIAL_FILE' not in os.environ
    with Session(production) as db:
        assert db.scalar(select(func.count()).select_from(Account)) == 0
