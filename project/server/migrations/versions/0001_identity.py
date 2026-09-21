"""검토된 StoreLoop 초기 스키마: 0001_identity."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_identity'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('categories',
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), server_default='', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('version >= 1'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('regions',
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('version >= 1'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('accounts',
    sa.Column('login_id', sa.String(length=80), nullable=False),
    sa.Column('display_name', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.Text(), nullable=False),
    sa.Column('role', sa.String(length=32), nullable=False),
    sa.Column('region_id', sa.Uuid(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("(role NOT IN ('ofc','regional') OR region_id IS NOT NULL) AND (role NOT IN ('hq','platform_operator') OR region_id IS NULL)", name='ck_account_region'),
    sa.CheckConstraint("role IN ('store_owner','ofc','regional','hq','platform_operator')", name='ck_role_values'),
    sa.CheckConstraint('version >= 1'),
    sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login_id')
    )
    op.create_index('ix_accounts_region', 'accounts', ['region_id'], unique=False)
    op.create_index('ix_accounts_role_active', 'accounts', ['role', 'is_active'], unique=False)
    op.create_table('stores',
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('region_id', sa.Uuid(), nullable=False),
    sa.Column('store_type', sa.String(length=80), nullable=False),
    sa.Column('address', sa.Text(), server_default='', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('version >= 1'),
    sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_index('ix_stores_region_active', 'stores', ['region_id', 'is_active'], unique=False)
    op.create_table('auth_sessions',
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('csrf_hash', sa.String(length=64), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('expires_at > created_at'),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index('ix_sessions_account', 'auth_sessions', ['account_id', 'revoked_at'], unique=False)
    op.create_index('ix_sessions_expiry', 'auth_sessions', ['expires_at'], unique=False)
    op.create_table('ofc_store_mappings',
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('changed_by_id', sa.Uuid(), nullable=False),
    sa.Column('reason', sa.String(length=500), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['changed_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ofc_account', 'ofc_store_mappings', ['account_id', 'ended_at'], unique=False)
    op.create_index('ix_ofc_store', 'ofc_store_mappings', ['store_id', 'ended_at'], unique=False)
    op.create_index('uq_ofc_active_pair', 'ofc_store_mappings', ['account_id', 'store_id'], unique=True, postgresql_where=sa.text('ended_at IS NULL'), sqlite_where=sa.text('ended_at IS NULL'))
    op.create_index('uq_ofc_active_store', 'ofc_store_mappings', ['store_id'], unique=True, postgresql_where=sa.text('ended_at IS NULL'), sqlite_where=sa.text('ended_at IS NULL'))
    op.create_table('store_owner_mappings',
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('changed_by_id', sa.Uuid(), nullable=False),
    sa.Column('reason', sa.String(length=500), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['changed_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_owner_account', 'store_owner_mappings', ['account_id', 'ended_at'], unique=False)
    op.create_index('ix_owner_store', 'store_owner_mappings', ['store_id', 'ended_at'], unique=False)
    op.create_index('uq_owner_active', 'store_owner_mappings', ['account_id', 'store_id'], unique=True, postgresql_where=sa.text('ended_at IS NULL'), sqlite_where=sa.text('ended_at IS NULL'))


def downgrade():
    raise RuntimeError("과거 업무 데이터 보존을 위해 자동 downgrade를 제공하지 않습니다.")
