from sqlalchemy import Column, String, DateTime, Index
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices

class Notification(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'notifications'
    recipient_id = fk('accounts')
    kind = Column(String(32), nullable=False)
    submission_id = fk('submissions', nullable=True)
    issue_id = fk('issues', nullable=True)
    title = Column(String(160), nullable=False)
    read_at = Column(DateTime(timezone=True))
    dedupe_key = Column(String(180), nullable=False, unique=True)
    __table_args__ = (choices('kind',('review_ready','issue_created','issue_updated')),Index('ix_notification_inbox','recipient_id','read_at','created_at'))
