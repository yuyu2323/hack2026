from sqlalchemy import Column, String, Integer, Boolean, DateTime, Uuid, CheckConstraint, Index
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices, VersionMixin, JSON_DATA

class AuditEvent(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'audit_events'
    actor_id = fk('accounts')
    action = Column(String(80), nullable=False)
    target_type = Column(String(80), nullable=False)
    target_id = Column(Uuid, nullable=False)
    reason = Column(String(500), nullable=False)
    before_data = Column(JSON_DATA, nullable=False)
    after_data = Column(JSON_DATA, nullable=False)
    outcome = Column(String(16), nullable=False)
    request_id = Column(Uuid, nullable=False)
    __table_args__ = (choices('outcome',('succeeded','rejected')),Index('ix_audit_created','created_at'),Index('ix_audit_target','target_type','target_id','created_at'),Index('ix_audit_actor','actor_id','created_at'))

class ServiceStatus(IdentityMixin, Base):
    __tablename__ = 'service_status'
    service_name = Column(String(80), nullable=False, unique=True)
    status = Column(String(16), nullable=False)
    checked_at = Column(DateTime(timezone=True), nullable=False)
    heartbeat_at = Column(DateTime(timezone=True))
    last_success_at = Column(DateTime(timezone=True))
    last_failure_at = Column(DateTime(timezone=True))
    error_code = Column(String(64))
    is_fixture = Column(Boolean, nullable=False, default=False, server_default='false')
    details = Column(JSON_DATA, nullable=False, default=dict)
    __table_args__ = (choices('status',('up','down','unknown')),)

class Announcement(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'announcements'
    title = Column(String(160), nullable=False)
    body = Column(String(4000), nullable=False)
    severity = Column(String(16), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    created_by_id = fk('accounts')
    __table_args__ = (choices('severity',('info','maintenance')),CheckConstraint('ends_at IS NULL OR ends_at > starts_at'),CheckConstraint('version >= 1'),Index('ix_announcement_active','is_active','starts_at','ends_at'))
