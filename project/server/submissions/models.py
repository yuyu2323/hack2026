from sqlalchemy import Column, String, Integer, UniqueConstraint, CheckConstraint, Index
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices, JSON_DATA

class MediaAsset(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'media_assets'
    storage_key = Column(String(255), nullable=False, unique=True)
    thumbnail_key = Column(String(255), nullable=False, unique=True)
    sha256 = Column(String(64), nullable=False, index=True)
    mime_type = Column(String(32), nullable=False)
    byte_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    uploaded_by_id = fk('accounts')
    source_kind = Column(String(32), nullable=False, default='user_upload')
    __table_args__ = (choices('mime_type',('image/jpeg','image/png')),choices('source_kind',('user_upload','ai_generated_demo','seed_demo')),
        CheckConstraint('byte_size BETWEEN 1 AND 10485760'),CheckConstraint('width BETWEEN 32 AND 8192 AND height BETWEEN 32 AND 8192 AND width * height <= 40000000'))

class Submission(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'submissions'
    store_id = fk('stores')
    category_id = fk('categories')
    submitted_by_id = fk('accounts')
    question = Column(String(2000), nullable=False, default='', server_default='')
    parent_submission_id = fk('submissions', nullable=True)
    source_kind = Column(String(32), nullable=False, default='user_upload')
    __table_args__ = (choices('source_kind',('user_upload','ai_generated_demo','seed_demo')),
        Index('ix_submission_scope','store_id','category_id','created_at'),Index('ix_submission_author','submitted_by_id','created_at'),Index('ix_submission_parent','parent_submission_id'))

class SubmissionPhoto(IdentityMixin, Base):
    __tablename__ = 'submission_photos'
    submission_id = fk('submissions')
    media_id = fk('media_assets')
    position = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('submission_id','position'),UniqueConstraint('submission_id','media_id'),CheckConstraint('position BETWEEN 1 AND 5'))

class AnalysisContext(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'analysis_contexts'
    submission_id = fk('submissions', unique=True)
    schema_version = Column(String(16), nullable=False, default='1.0')
    snapshot = Column(JSON_DATA, nullable=False)
    snapshot_sha256 = Column(String(64), nullable=False)
