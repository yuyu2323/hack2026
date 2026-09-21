from sqlalchemy import Column, String, Text, Boolean, Integer, Uuid, CheckConstraint, UniqueConstraint, Index, text
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices, VersionMixin

class Guideline(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'guidelines'
    rule_key = Column(String(80), nullable=False)
    title = Column(String(160), nullable=False)
    level = Column(String(16), nullable=False)
    region_id = fk('regions', nullable=True)
    store_id = fk('stores', nullable=True)
    category_id = fk('categories', nullable=True)
    scope_key = Column(String(180), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    current_version = Column(Integer, nullable=False, default=1, server_default='1')
    created_by_id = fk('accounts')
    __table_args__ = (choices('level',('HQ','REGION','STORE','CATEGORY')), UniqueConstraint('scope_key','rule_key'), CheckConstraint('current_version >= 1 AND version >= 1'),
        CheckConstraint("(level='HQ' AND region_id IS NULL AND store_id IS NULL) OR (level='REGION' AND region_id IS NOT NULL AND store_id IS NULL) OR (level='STORE' AND store_id IS NOT NULL AND region_id IS NULL) OR (level='CATEGORY' AND category_id IS NOT NULL AND region_id IS NULL)",name='ck_guideline_scope'),
        Index('ix_guideline_scope','level','region_id','store_id','category_id','is_active'))

class GuidelineVersion(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'guideline_versions'
    guideline_id = fk('guidelines')
    version = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    change_reason = Column(String(500), nullable=False)
    created_by_id = fk('accounts')
    __table_args__ = (UniqueConstraint('guideline_id','version'), CheckConstraint('version >= 1'), CheckConstraint('length(text) BETWEEN 1 AND 10000'))

class ReferencePhoto(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'reference_photos'
    lineage_id = Column(Uuid, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    state_version = Column(Integer, nullable=False, default=1, server_default='1')
    photo_id = fk('media_assets')
    category_id = fk('categories')
    store_id = fk('stores', nullable=True)
    caption = Column(String(2000), nullable=False, default='')
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    created_by_id = fk('accounts')
    __table_args__ = (UniqueConstraint('lineage_id','version'), CheckConstraint('version >= 1 AND state_version >= 1'),
        Index('uq_reference_active_lineage','lineage_id',unique=True,postgresql_where=text('is_active'),sqlite_where=text('is_active = 1')),
        Index('ix_reference_scope','category_id','store_id','is_active'))
