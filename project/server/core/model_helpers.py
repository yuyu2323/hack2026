"""스키마 공통 자료형과 제약 도우미."""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Uuid, CheckConstraint, JSON, func
from sqlalchemy.dialects.postgresql import JSONB
from server.core.base import utcnow

JSON_DATA = JSON().with_variant(JSONB, 'postgresql')


def fk(table: str, nullable=False, **kwargs):
    return Column(Uuid, ForeignKey(table + '.id', ondelete='RESTRICT'), nullable=nullable, **kwargs)


def choices(field: str, values: tuple[str, ...]):
    items = ','.join(repr(value) for value in values)
    return CheckConstraint(f'{field} IN ({items})', name=f'ck_{field}_values')

class VersionMixin:
    version = Column(Integer, nullable=False, default=1, server_default='1')
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow, server_default=func.now())
