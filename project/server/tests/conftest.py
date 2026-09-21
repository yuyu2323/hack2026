"""마이그레이션으로 구성한 격리 DB와 실제 로그인 테스트 도구."""
import importlib
import os
from pathlib import Path
import uuid
import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from server.core.config import PROJECT_ROOT,get_settings
from server.core.db import get_db,make_engine
from server.core.errors import install_error_handlers
from server.core.models import Account,Region,Store
from server.core.security import hash_password

TEST_PASSWORD='only-test-invalid-password-2026'


def migrate(engine):
    config=Config(str(PROJECT_ROOT/'server/alembic.ini'))
    with engine.begin() as connection:
        config.attributes['connection']=connection
        command.upgrade(config,'head')

@pytest.fixture
def db(tmp_path):
    engine=make_engine('sqlite:///'+str(tmp_path/'test.sqlite'))
    migrate(engine)
    with Session(engine,expire_on_commit=False) as session:
        yield session
    engine.dispose()

@pytest.fixture
def make_client(db,monkeypatch):
    clients=[]
    monkeypatch.setattr(get_settings(),'allowed_origins_value','http://testserver')
    monkeypatch.setattr(get_settings(),'session_cookie_secure',False)
    def create(app=None):
        if app is None:
            app=FastAPI(); install_error_handlers(app)
            for name in ('accounts','stores','operations'):
                if (PROJECT_ROOT/'server'/name/'router.py').exists():
                    app.include_router(importlib.import_module('server.'+name+'.router').router)
        def override_db(): yield db
        app.dependency_overrides[get_db]=override_db
        client=TestClient(app); client.__enter__(); clients.append(client)
        return client
    yield create
    for client in clients: client.__exit__(None,None,None)

@pytest.fixture
def client(make_client): return make_client()

@pytest.fixture
def region_factory(db):
    def create(**values):
        defaults={'code':'r-'+uuid.uuid4().hex[:12],'name':'테스트 지역'};defaults.update(values)
        region=Region(**defaults);db.add(region);db.commit();return region
    return create

@pytest.fixture
def store_factory(db,region_factory):
    def create(region=None,**values):
        region=region or region_factory()
        defaults={'code':'s-'+uuid.uuid4().hex[:12],'name':'테스트 매장','region_id':region.id,'store_type':'도심형','address':''};defaults.update(values)
        store=Store(**defaults);db.add(store);db.commit();return store
    return create

@pytest.fixture
def account_factory(db,region_factory):
    def create(role='store_owner',region_id=None,is_active=True,**values):
        if role in ('ofc','regional') and region_id is None: region_id=region_factory().id
        defaults={'login_id':'test.'+uuid.uuid4().hex[:12],'display_name':'테스트 계정','role':role,'region_id':region_id,'is_active':is_active,'password_hash':hash_password(TEST_PASSWORD)};defaults.update(values)
        account=Account(**defaults);db.add(account);db.commit();return account
    return create

@pytest.fixture
def login_as(client):
    def login(account,target_client=None):
        target=target_client or client
        csrf=target.get('/api/auth/csrf').json()['csrf_token']
        response=target.post('/api/auth/login',json={'login_id':account.login_id,'password':TEST_PASSWORD},headers={'Origin':'http://testserver','X-CSRF-Token':csrf})
        assert response.status_code==200,response.text
        return {'Origin':'http://testserver','X-CSRF-Token':response.json()['csrf_token']}
    return login

@pytest.fixture
def postgres_db():
    from dotenv import dotenv_values
    url=os.environ.get('STORELOOP_TEST_DATABASE_URL') or dotenv_values(PROJECT_ROOT/'.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL')
    if not url: pytest.skip('STORELOOP_TEST_DATABASE_URL 설정 없음: PostgreSQL 인수 NOT_RUN')
    parsed=make_url(url)
    if not parsed.database or not parsed.database.endswith('_test'):
        pytest.fail('전용 _test 데이터베이스만 허용합니다.')
    schema='test_'+uuid.uuid4().hex
    admin=make_engine(url)
    try:
        with admin.begin() as connection: connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    except OperationalError:
        pytest.fail('PostgreSQL 연결에 실패했습니다. 전용 서버·샌드박스 네트워크 권한을 확인해 주세요.',pytrace=False)
    engine=make_engine(url,connect_args={'options':f'-csearch_path={schema}'})
    try:
        migrate(engine)
        with Session(engine,expire_on_commit=False) as session: yield session
    finally:
        engine.dispose()
        with admin.begin() as connection: connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def pytest_configure(config):
    config.addinivalue_line('markers','postgres: 전용 PostgreSQL에서 실행하는 제약·동시성 검증')
    config.addinivalue_line('markers','real_ai: 실제 로컬 AI 서버와 Codex 모델 호출 검증')
