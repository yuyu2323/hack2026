"""공개 시연 분석의 DB 전역 일별 한도."""
from alembic import op
import sqlalchemy as sa

revision = '0006_daily_analysis_usage'
down_revision = '0005_media_blobs'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('auth_sessions', sa.Column('is_public_demo', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table('daily_analysis_usage', sa.Column('day', sa.String(10), primary_key=True),
                    sa.Column('used', sa.Integer(), nullable=False),
                    sa.CheckConstraint('used BETWEEN 1 AND 20'))


def downgrade():
    raise RuntimeError('공개 시연 한도 기록 보존을 위해 자동 downgrade를 제공하지 않습니다.')
