"""검토된 StoreLoop 초기 스키마: 0002_content."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002_content'
down_revision = '0001_identity'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('guidelines',
    sa.Column('rule_key', sa.String(length=80), nullable=False),
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('level', sa.String(length=16), nullable=False),
    sa.Column('region_id', sa.Uuid(), nullable=True),
    sa.Column('store_id', sa.Uuid(), nullable=True),
    sa.Column('category_id', sa.Uuid(), nullable=True),
    sa.Column('scope_key', sa.String(length=180), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('current_version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("(level='HQ' AND region_id IS NULL AND store_id IS NULL) OR (level='REGION' AND region_id IS NOT NULL AND store_id IS NULL) OR (level='STORE' AND store_id IS NOT NULL AND region_id IS NULL) OR (level='CATEGORY' AND category_id IS NOT NULL AND region_id IS NULL)", name='ck_guideline_scope'),
    sa.CheckConstraint("level IN ('HQ','REGION','STORE','CATEGORY')", name='ck_level_values'),
    sa.CheckConstraint('current_version >= 1 AND version >= 1'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['created_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('scope_key', 'rule_key')
    )
    op.create_index('ix_guideline_scope', 'guidelines', ['level', 'region_id', 'store_id', 'category_id', 'is_active'], unique=False)
    op.create_table('media_assets',
    sa.Column('storage_key', sa.String(length=255), nullable=False),
    sa.Column('thumbnail_key', sa.String(length=255), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('mime_type', sa.String(length=32), nullable=False),
    sa.Column('byte_size', sa.Integer(), nullable=False),
    sa.Column('width', sa.Integer(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('uploaded_by_id', sa.Uuid(), nullable=False),
    sa.Column('source_kind', sa.String(length=32), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("mime_type IN ('image/jpeg','image/png')", name='ck_mime_type_values'),
    sa.CheckConstraint("source_kind IN ('user_upload','ai_generated_demo','seed_demo')", name='ck_source_kind_values'),
    sa.CheckConstraint('byte_size BETWEEN 1 AND 10485760'),
    sa.CheckConstraint('width BETWEEN 32 AND 8192 AND height BETWEEN 32 AND 8192 AND width * height <= 40000000'),
    sa.ForeignKeyConstraint(['uploaded_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('storage_key'),
    sa.UniqueConstraint('thumbnail_key')
    )
    op.create_index(op.f('ix_media_assets_sha256'), 'media_assets', ['sha256'], unique=False)
    op.create_table('guideline_versions',
    sa.Column('guideline_id', sa.Uuid(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('change_reason', sa.String(length=500), nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('length(text) BETWEEN 1 AND 10000'),
    sa.CheckConstraint('version >= 1'),
    sa.ForeignKeyConstraint(['created_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['guideline_id'], ['guidelines.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('guideline_id', 'version')
    )
    op.create_table('reference_photos',
    sa.Column('lineage_id', sa.Uuid(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('state_version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('photo_id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=False),
    sa.Column('store_id', sa.Uuid(), nullable=True),
    sa.Column('caption', sa.String(length=2000), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('version >= 1 AND state_version >= 1'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['created_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['photo_id'], ['media_assets.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lineage_id', 'version')
    )
    op.create_index('ix_reference_scope', 'reference_photos', ['category_id', 'store_id', 'is_active'], unique=False)
    op.create_index('uq_reference_active_lineage', 'reference_photos', ['lineage_id'], unique=True, postgresql_where=sa.text('is_active'), sqlite_where=sa.text('is_active = 1'))


def downgrade():
    raise RuntimeError("과거 업무 데이터 보존을 위해 자동 downgrade를 제공하지 않습니다.")
