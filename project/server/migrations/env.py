"""애플리케이션 시작과 분리된 스키마 마이그레이션."""
from alembic import context
from server.core.models import Base
from server.core.db import make_engine
from server.core.config import get_settings

config = context.config
target_metadata = Base.metadata


def migrate(connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True,
                      render_as_batch=connection.dialect.name == 'sqlite')
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    context.configure(url=config.get_main_option('sqlalchemy.url') or get_settings().database_url,
                      target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
elif config.attributes.get('connection') is not None:
    migrate(config.attributes['connection'])
else:
    engine = make_engine(config.get_main_option('sqlalchemy.url') or get_settings().database_url)
    with engine.connect() as connection:
        migrate(connection)
