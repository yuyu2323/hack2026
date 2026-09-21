from sqlalchemy import Column, String, Integer, Boolean, DateTime, Uuid, ForeignKey, CheckConstraint, UniqueConstraint, Index, text
from server.core.base import Base, IdentityMixin, CreatedMixin, utcnow
from server.core.model_helpers import fk, choices

class AnalysisJob(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'analysis_jobs'
    submission_id = fk('submissions', unique=True)
    status = Column(String(16), nullable=False, default='queued')
    current_attempt_id = Column(Uuid, ForeignKey('analysis_attempts.id', ondelete='RESTRICT',use_alter=True,name='fk_job_current_attempt'), nullable=True)
    enqueue_generation = Column(Integer, nullable=False, default=1, server_default='1')
    queued_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    queue_deadline_at = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    error_code = Column(String(64))
    error_message = Column(String(240))
    is_fixture = Column(Boolean, nullable=False, default=False, server_default='false')
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow,onupdate=utcnow)
    __table_args__ = (choices('status',('queued','running','succeeded','failed')),CheckConstraint('enqueue_generation >= 1',name='ck_job_generation'),Index('ix_jobs_queue','status','queued_at'),Index('ix_jobs_deadline','status','queue_deadline_at'))

class AnalysisAttempt(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'analysis_attempts'
    job_id = fk('analysis_jobs')
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(16), nullable=False)
    requested_by_id = fk('accounts', nullable=True)
    worker_id = Column(String(120))
    queued_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    started_at = Column(DateTime(timezone=True))
    deadline_at = Column(DateTime(timezone=True))
    lease_expires_at = Column(DateTime(timezone=True))
    heartbeat_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    error_code = Column(String(64))
    error_message = Column(String(240))
    result_applied = Column(Boolean, nullable=False, default=False, server_default='false')
    __table_args__ = (choices('status',('queued','running','succeeded','failed','expired')),UniqueConstraint('job_id','attempt_number'),CheckConstraint('attempt_number >= 1'),
        Index('uq_attempt_active','job_id',unique=True,postgresql_where=text("status IN ('queued','running')"),sqlite_where=text("status IN ('queued','running')")),Index('ix_attempt_lease','status','lease_expires_at'))

class IdempotencyRecord(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'idempotency_records'
    account_id = fk('accounts')
    operation = Column(String(80), nullable=False)
    key = Column(String(128), nullable=False)
    request_hash = Column(String(64), nullable=False)
    resource_id = Column(Uuid, nullable=False)
    response_status = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('account_id','operation','key'),Index('ix_idempotency_created','created_at'))
