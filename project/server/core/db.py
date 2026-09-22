"""요청과 작업별 DB 세션을 제공한다."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from server.core.config import get_settings
from server.core.base import Base, IdentityMixin, CreatedMixin, utcnow, as_utc


def make_engine(url: str, **kwargs):
    if url.startswith('sqlite'):
        kwargs.setdefault('connect_args', {'check_same_thread': False})
    kwargs.setdefault('hide_parameters', True)
    result = create_engine(url, **kwargs)
    if url.startswith('sqlite'):
        @event.listens_for(result, 'connect')
        def _foreign_keys(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')
    return result

engine = make_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as session:
        yield session
