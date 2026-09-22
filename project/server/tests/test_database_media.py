"""SQLite 검증: DB 사진 저장·용량 제한·롤백·변조 탐지."""
import hashlib
from io import BytesIO
from types import SimpleNamespace
import pytest
from PIL import Image
from fastapi import UploadFile
from starlette.datastructures import Headers
from sqlalchemy import select, func
from server.core.errors import ApiError
from server.submissions import storage
from server.submissions.models import MediaBlob, MediaAsset


@pytest.fixture
def media_settings(monkeypatch, tmp_path):
    settings = SimpleNamespace(media_storage='database', media_database_max_bytes=200*1024*1024, media_root=tmp_path/'media')
    monkeypatch.setattr(storage, 'get_settings', lambda: settings)
    return settings


def test_database_upload_survives_session_expiry_without_files(db, account_factory, media_settings):
    account = account_factory()
    output = BytesIO()
    Image.new('RGB', (64, 64), 'blue').save(output, format='PNG')
    row = storage.store_media(db, account, UploadFile(file=BytesIO(output.getvalue()), filename='image.png', headers=Headers({'content-type':'image/png'})), [])
    ident = row.id
    db.commit(); db.expire_all()
    row = db.get(MediaAsset, ident)
    assert hashlib.sha256(storage.read_media(db, row)).hexdigest() == row.sha256
    assert storage.read_media(db, row, True).startswith(bytes.fromhex('ffd8'))
    assert not media_settings.media_root.exists()
    assert db.scalar(select(func.count()).select_from(MediaBlob)) == 2


def test_database_capacity_is_atomic_and_replay_does_not_consume_space(db, media_settings):
    media_settings.media_database_max_bytes = 6
    storage.write_media(db, [('original', b'abc'), ('thumb', b'de')], [])
    db.commit()
    storage.write_media(db, [('original', b'abc'), ('thumb', b'de')], [], allow_existing=True)
    with pytest.raises(ApiError) as error:
        storage.write_media(db, [('new-original', b'ab'), ('new-thumb', b'cd')], [])
    assert error.value.status_code == 507
    db.rollback()
    assert db.get(MediaBlob, 'new-original') is None
    assert db.scalar(select(func.sum(MediaBlob.byte_size))) == 5
    with pytest.raises(ValueError):
        storage.write_media(db, [('original', b'xyz')], [], allow_existing=True)


def test_database_media_rollback_and_hash_validation(db, media_settings):
    storage.write_media(db, [('original', b'abc'), ('thumb', b'de')], [])
    db.rollback()
    assert db.get(MediaBlob, 'original') is None
    storage.write_media(db, [('original', b'abc')], [])
    media = SimpleNamespace(storage_key='original', byte_size=3, sha256=hashlib.sha256(b'xyz').hexdigest())
    with pytest.raises(ApiError):
        storage.read_media(db, media)


def test_filesystem_storage_remains_available(db, media_settings):
    media_settings.media_storage = 'filesystem'
    paths = []
    storage.write_media(db, [('original', b'abc')], paths)
    media = SimpleNamespace(storage_key='original', byte_size=3, sha256=hashlib.sha256(b'abc').hexdigest())
    assert storage.read_media(db, media) == b'abc'
    assert len(paths) == 1
    storage.cleanup(paths)
    assert not paths[0].exists()


def test_seed_media_is_durable_and_replay_safe(db, media_settings, monkeypatch, tmp_path):
    from server.seed import __main__ as seeder
    monkeypatch.setenv('SEED_CREDENTIAL_FILE', str(tmp_path/'credentials'))
    seeder.seed(db)
    count = db.scalar(select(func.count()).select_from(MediaBlob))
    assert count == 20
    for media in db.scalars(select(MediaAsset)):
        assert hashlib.sha256(storage.read_media(db, media)).hexdigest() == media.sha256
    seeder.seed(db)
    assert db.scalar(select(func.count()).select_from(MediaBlob)) == count
    assert not media_settings.media_root.exists()
