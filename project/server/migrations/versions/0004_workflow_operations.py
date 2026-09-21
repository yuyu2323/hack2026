"""검토된 StoreLoop 초기 스키마: 0004_workflow_operations."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0004_workflow_operations'
down_revision = '0003_review_jobs'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('service_status',
    sa.Column('service_name', sa.String(length=80), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('checked_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_code', sa.String(length=64), nullable=True),
    sa.Column('is_fixture', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('details', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint("status IN ('up','down','unknown')", name='ck_status_values'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('service_name')
    )
    op.create_table('announcements',
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('body', sa.String(length=4000), nullable=False),
    sa.Column('severity', sa.String(length=16), nullable=False),
    sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("severity IN ('info','maintenance')", name='ck_severity_values'),
    sa.CheckConstraint('ends_at IS NULL OR ends_at > starts_at'),
    sa.CheckConstraint('version >= 1'),
    sa.ForeignKeyConstraint(['created_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_announcement_active', 'announcements', ['is_active', 'starts_at', 'ends_at'], unique=False)
    op.create_table('audit_events',
    sa.Column('actor_id', sa.Uuid(), nullable=False),
    sa.Column('action', sa.String(length=80), nullable=False),
    sa.Column('target_type', sa.String(length=80), nullable=False),
    sa.Column('target_id', sa.Uuid(), nullable=False),
    sa.Column('reason', sa.String(length=500), nullable=False),
    sa.Column('before_data', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('after_data', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('outcome', sa.String(length=16), nullable=False),
    sa.Column('request_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("outcome IN ('succeeded','rejected')", name='ck_outcome_values'),
    sa.ForeignKeyConstraint(['actor_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_actor', 'audit_events', ['actor_id', 'created_at'], unique=False)
    op.create_index('ix_audit_created', 'audit_events', ['created_at'], unique=False)
    op.create_index('ix_audit_target', 'audit_events', ['target_type', 'target_id', 'created_at'], unique=False)
    op.create_table('inventory_mock',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=False),
    sa.Column('sku', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('observed_on', sa.Date(), nullable=False),
    sa.Column('source_kind', sa.String(length=16), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("source_kind='mock'"),
    sa.CheckConstraint('quantity >= 0'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('store_id', 'sku', 'observed_on')
    )
    op.create_index('ix_inventory_scope', 'inventory_mock', ['store_id', 'category_id', 'observed_on'], unique=False)
    op.create_table('sales_mock',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=False),
    sa.Column('week_start', sa.Date(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('source_kind', sa.String(length=16), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("source_kind='mock'"),
    sa.CheckConstraint('amount >= 0'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('store_id', 'category_id', 'week_start')
    )
    op.create_index('ix_sales_period', 'sales_mock', ['week_start', 'store_id', 'category_id'], unique=False)
    op.create_table('issues',
    sa.Column('submission_id', sa.Uuid(), nullable=False),
    sa.Column('review_id', sa.Uuid(), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('priority', sa.String(length=16), nullable=False),
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('description', sa.String(length=2000), nullable=False),
    sa.Column('assignee_id', sa.Uuid(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('resolution', sa.String(length=2000), nullable=True),
    sa.Column('next_check_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("priority IN ('normal','high')", name='ck_priority_values'),
    sa.CheckConstraint("status IN ('open','in_progress','resolved')", name='ck_status_values'),
    sa.CheckConstraint("type IN ('owner_question','ai_review_required')", name='ck_type_values'),
    sa.CheckConstraint('version >= 1', name='ck_issue_version'),
    sa.ForeignKeyConstraint(['assignee_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['created_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['review_id'], ['review_results.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_issue_work', 'issues', ['status', 'assignee_id', 'updated_at'], unique=False)
    op.create_index('uq_ai_issue', 'issues', ['submission_id'], unique=True, postgresql_where=sa.text("type='ai_review_required'"), sqlite_where=sa.text("type='ai_review_required'"))
    op.create_table('issue_actions',
    sa.Column('issue_id', sa.Uuid(), nullable=False),
    sa.Column('actor_id', sa.Uuid(), nullable=False),
    sa.Column('action_type', sa.String(length=32), nullable=False),
    sa.Column('body', sa.String(length=2000), nullable=False),
    sa.Column('from_status', sa.String(length=32), nullable=True),
    sa.Column('to_status', sa.String(length=32), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("action_type IN ('comment','status_change','assignment')", name='ck_action_type_values'),
    sa.ForeignKeyConstraint(['actor_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_actions_issue', 'issue_actions', ['issue_id', 'created_at'], unique=False)
    op.create_table('notifications',
    sa.Column('recipient_id', sa.Uuid(), nullable=False),
    sa.Column('kind', sa.String(length=32), nullable=False),
    sa.Column('submission_id', sa.Uuid(), nullable=True),
    sa.Column('issue_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('dedupe_key', sa.String(length=180), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("kind IN ('review_ready','issue_created','issue_updated')", name='ck_kind_values'),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['recipient_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('dedupe_key')
    )
    op.create_index('ix_notification_inbox', 'notifications', ['recipient_id', 'read_at', 'created_at'], unique=False)


def downgrade():
    raise RuntimeError("과거 업무 데이터 보존을 위해 자동 downgrade를 제공하지 않습니다.")
