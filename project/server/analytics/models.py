from sqlalchemy import Column, String, Integer, Date, Numeric, UniqueConstraint, CheckConstraint, Index
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk

class SalesMock(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'sales_mock'
    store_id = fk('stores')
    category_id = fk('categories')
    week_start = Column(Date, nullable=False)
    amount = Column(Numeric(14,2), nullable=False)
    source_kind = Column(String(16), nullable=False, default='mock')
    __table_args__ = (UniqueConstraint('store_id','category_id','week_start'),CheckConstraint('amount >= 0'),CheckConstraint("source_kind='mock'"),Index('ix_sales_period','week_start','store_id','category_id'))

class InventoryMock(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'inventory_mock'
    store_id = fk('stores')
    category_id = fk('categories')
    sku = Column(String(80), nullable=False)
    name = Column(String(120), nullable=False)
    quantity = Column(Integer, nullable=False)
    observed_on = Column(Date, nullable=False)
    source_kind = Column(String(16), nullable=False, default='mock')
    __table_args__ = (UniqueConstraint('store_id','sku','observed_on'),CheckConstraint('quantity >= 0'),CheckConstraint("source_kind='mock'"),Index('ix_inventory_scope','store_id','category_id','observed_on'))
