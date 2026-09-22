"""무료 서버리스 배포용 보호 사진 저장소."""
from alembic import op
import sqlalchemy as sa

revision = '0005_media_blobs'
down_revision = '0004_workflow_operations'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('media_blobs',
        sa.Column('storage_key', sa.String(255), primary_key=True),
        sa.Column('content', sa.LargeBinary(), nullable=False),
        sa.Column('byte_size', sa.Integer(), nullable=False),
        sa.CheckConstraint('byte_size BETWEEN 1 AND 10485760'))


def downgrade():
    raise RuntimeError('보호 사진 보존을 위해 자동 downgrade를 제공하지 않습니다.')
