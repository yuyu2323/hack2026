from sqlalchemy import Column, String, Text, Boolean, DateTime, CheckConstraint, Index, text
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, VersionMixin

class Region(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'regions'
    code = Column(String(32), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    __table_args__ = (CheckConstraint('version >= 1'),)

class Category(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'categories'
    code = Column(String(32), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=False, default='', server_default='')
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    __table_args__ = (CheckConstraint('version >= 1'),)

class Store(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'stores'
    code = Column(String(32), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    region_id = fk('regions')
    store_type = Column(String(80), nullable=False)
    address = Column(Text, nullable=False, default='', server_default='')
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    __table_args__ = (CheckConstraint('version >= 1'), Index('ix_stores_region_active','region_id','is_active'))

class StoreOwnerMapping(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'store_owner_mappings'
    account_id = fk('accounts')
    store_id = fk('stores')
    ended_at = Column(DateTime(timezone=True))
    changed_by_id = fk('accounts')
    reason = Column(String(500), nullable=False)
    __table_args__ = (Index('uq_owner_active','account_id','store_id',unique=True,postgresql_where=text('ended_at IS NULL'),sqlite_where=text('ended_at IS NULL')),
                     Index('ix_owner_account','account_id','ended_at'), Index('ix_owner_store','store_id','ended_at'))

class OFCStoreMapping(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'ofc_store_mappings'
    account_id = fk('accounts')
    store_id = fk('stores')
    ended_at = Column(DateTime(timezone=True))
    changed_by_id = fk('accounts')
    reason = Column(String(500), nullable=False)
    __table_args__ = (Index('uq_ofc_active_store','store_id',unique=True,postgresql_where=text('ended_at IS NULL'),sqlite_where=text('ended_at IS NULL')),
                     Index('uq_ofc_active_pair','account_id','store_id',unique=True,postgresql_where=text('ended_at IS NULL'),sqlite_where=text('ended_at IS NULL')),
                     Index('ix_ofc_account','account_id','ended_at'), Index('ix_ofc_store','store_id','ended_at'))
