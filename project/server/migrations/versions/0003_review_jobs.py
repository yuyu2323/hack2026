"""검토된 StoreLoop 초기 스키마: 0003_review_jobs."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0003_review_jobs'
down_revision = '0002_content'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('idempotency_records',
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('operation', sa.String(length=80), nullable=False),
    sa.Column('key', sa.String(length=128), nullable=False),
    sa.Column('request_hash', sa.String(length=64), nullable=False),
    sa.Column('resource_id', sa.Uuid(), nullable=False),
    sa.Column('response_status', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_id', 'operation', 'key')
    )
    op.create_index('ix_idempotency_created', 'idempotency_records', ['created_at'], unique=False)
    op.create_table('submissions',
    sa.Column('store_id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=False),
    sa.Column('submitted_by_id', sa.Uuid(), nullable=False),
    sa.Column('question', sa.String(length=2000), server_default='', nullable=False),
    sa.Column('parent_submission_id', sa.Uuid(), nullable=True),
    sa.Column('source_kind', sa.String(length=32), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("source_kind IN ('user_upload','ai_generated_demo','seed_demo')", name='ck_source_kind_values'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['parent_submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['submitted_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_submission_author', 'submissions', ['submitted_by_id', 'created_at'], unique=False)
    op.create_index('ix_submission_parent', 'submissions', ['parent_submission_id'], unique=False)
    op.create_index('ix_submission_scope', 'submissions', ['store_id', 'category_id', 'created_at'], unique=False)
    op.create_table('analysis_contexts',
    sa.Column('submission_id', sa.Uuid(), nullable=False),
    sa.Column('schema_version', sa.String(length=16), nullable=False),
    sa.Column('snapshot', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('snapshot_sha256', sa.String(length=64), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('submission_id')
    )
    op.create_table('analysis_jobs',
    sa.Column('submission_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('current_attempt_id', sa.Uuid(), nullable=True),
    sa.Column('enqueue_generation', sa.Integer(), server_default='1', nullable=False),
    sa.Column('queued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('queue_deadline_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_code', sa.String(length=64), nullable=True),
    sa.Column('error_message', sa.String(length=240), nullable=True),
    sa.Column('is_fixture', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("status IN ('queued','running','succeeded','failed')", name='ck_status_values'),
    sa.CheckConstraint('enqueue_generation >= 1', name='ck_job_generation'),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('submission_id')
    )
    op.create_index('ix_jobs_deadline', 'analysis_jobs', ['status', 'queue_deadline_at'], unique=False)
    op.create_index('ix_jobs_queue', 'analysis_jobs', ['status', 'queued_at'], unique=False)
    op.create_table('submission_photos',
    sa.Column('submission_id', sa.Uuid(), nullable=False),
    sa.Column('media_id', sa.Uuid(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint('position BETWEEN 1 AND 5'),
    sa.ForeignKeyConstraint(['media_id'], ['media_assets.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('submission_id', 'media_id'),
    sa.UniqueConstraint('submission_id', 'position')
    )
    op.create_table('analysis_attempts',
    sa.Column('job_id', sa.Uuid(), nullable=False),
    sa.Column('attempt_number', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('requested_by_id', sa.Uuid(), nullable=True),
    sa.Column('worker_id', sa.String(length=120), nullable=True),
    sa.Column('queued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deadline_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('lease_expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_code', sa.String(length=64), nullable=True),
    sa.Column('error_message', sa.String(length=240), nullable=True),
    sa.Column('result_applied', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("status IN ('queued','running','succeeded','failed','expired')", name='ck_status_values'),
    sa.CheckConstraint('attempt_number >= 1'),
    sa.ForeignKeyConstraint(['job_id'], ['analysis_jobs.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['requested_by_id'], ['accounts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('job_id', 'attempt_number')
    )
    op.create_index('ix_attempt_lease', 'analysis_attempts', ['status', 'lease_expires_at'], unique=False)
    op.create_index('uq_attempt_active', 'analysis_attempts', ['job_id'], unique=True, postgresql_where=sa.text("status IN ('queued','running')"), sqlite_where=sa.text("status IN ('queued','running')"))
    op.create_table('review_results',
    sa.Column('submission_id', sa.Uuid(), nullable=False),
    sa.Column('attempt_id', sa.Uuid(), nullable=True),
    sa.Column('schema_version', sa.String(length=16), nullable=False),
    sa.Column('result', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('compliance_rate', sa.Numeric(precision=5, scale=1), nullable=True),
    sa.Column('assessable_rate', sa.Numeric(precision=5, scale=1), nullable=True),
    sa.Column('pass_count', sa.Integer(), nullable=False),
    sa.Column('fail_count', sa.Integer(), nullable=False),
    sa.Column('unknown_count', sa.Integer(), nullable=False),
    sa.Column('needs_ofc_review', sa.Boolean(), nullable=False),
    sa.Column('source_kind', sa.String(length=16), nullable=False),
    sa.Column('model_name', sa.String(length=120), nullable=True),
    sa.Column('prompt_version', sa.String(length=32), nullable=False),
    sa.Column('latency_ms', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("source_kind = 'mock' OR attempt_id IS NOT NULL"),
    sa.CheckConstraint("source_kind IN ('real_ai','mock')", name='ck_source_kind_values'),
    sa.CheckConstraint('assessable_rate BETWEEN 0 AND 100'),
    sa.CheckConstraint('compliance_rate BETWEEN 0 AND 100'),
    sa.CheckConstraint('pass_count >= 0 AND fail_count >= 0 AND unknown_count >= 0 AND latency_ms >= 0'),
    sa.ForeignKeyConstraint(['attempt_id'], ['analysis_attempts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('attempt_id'),
    sa.UniqueConstraint('submission_id')
    )
    op.create_index('ix_review_created', 'review_results', ['created_at'], unique=False)
    op.create_table('criterion_evaluations',
    sa.Column('review_id', sa.Uuid(), nullable=False),
    sa.Column('guideline_id', sa.Uuid(), nullable=False),
    sa.Column('version_id', sa.Uuid(), nullable=False),
    sa.Column('rule_key', sa.String(length=80), nullable=False),
    sa.Column('verdict', sa.String(length=16), nullable=False),
    sa.Column('evidence', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('actions', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.CheckConstraint("verdict IN ('pass','fail','unknown')", name='ck_verdict_values'),
    sa.ForeignKeyConstraint(['guideline_id'], ['guidelines.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['review_id'], ['review_results.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['version_id'], ['guideline_versions.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('review_id', 'version_id')
    )
    op.create_index('ix_criterion_verdict', 'criterion_evaluations', ['rule_key', 'verdict'], unique=False)

    with op.batch_alter_table("analysis_jobs") as batch:
        batch.create_foreign_key("fk_job_current_attempt", "analysis_attempts", ["current_attempt_id"], ["id"], ondelete="RESTRICT")


def downgrade():
    raise RuntimeError("과거 업무 데이터 보존을 위해 자동 downgrade를 제공하지 않습니다.")
