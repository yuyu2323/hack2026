from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, CheckConstraint, Index
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices, VersionMixin

ROLES = ('store_owner','ofc','regional','hq','platform_operator')

class Account(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'accounts'
    login_id = Column(String(80), nullable=False, unique=True)
    display_name = Column(String(120), nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(32), nullable=False)
    region_id = fk('regions', nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    __table_args__ = (choices('role', ROLES), CheckConstraint('version >= 1'),
                     CheckConstraint("(role NOT IN ('ofc','regional') OR region_id IS NOT NULL) AND (role NOT IN ('hq','platform_operator') OR region_id IS NULL)", name='ck_account_region'),
                     Index('ix_accounts_role_active','role','is_active'), Index('ix_accounts_region','region_id'))

class AuthSession(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'auth_sessions'
    token_hash = Column(String(64), nullable=False, unique=True)
    csrf_hash = Column(String(64), nullable=False)
    account_id = fk('accounts', nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    is_public_demo = Column(Boolean, nullable=False, default=False, server_default='false')
    __table_args__ = (CheckConstraint('expires_at > created_at'), Index('ix_sessions_expiry','expires_at'), Index('ix_sessions_account','account_id','revoked_at'))
