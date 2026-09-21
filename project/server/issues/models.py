from sqlalchemy import Column, String, DateTime, Index, CheckConstraint, text
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices, VersionMixin

class Issue(IdentityMixin, CreatedMixin, VersionMixin, Base):
    __tablename__ = 'issues'
    submission_id = fk('submissions')
    review_id = fk('review_results', nullable=True)
    type = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False, default='open')
    priority = Column(String(16), nullable=False, default='normal')
    title = Column(String(160), nullable=False)
    description = Column(String(2000), nullable=False)
    assignee_id = fk('accounts', nullable=True)
    created_by_id = fk('accounts', nullable=True)
    resolution = Column(String(2000))
    next_check_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint('version >= 1',name='ck_issue_version'), choices('type',('owner_question','ai_review_required')), choices('status',('open','in_progress','resolved')),choices('priority',('normal','high')),
        Index('uq_ai_issue','submission_id',unique=True,postgresql_where=text("type='ai_review_required'"),sqlite_where=text("type='ai_review_required'")),Index('ix_issue_work','status','assignee_id','updated_at'))

class IssueAction(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'issue_actions'
    issue_id = fk('issues')
    actor_id = fk('accounts')
    action_type = Column(String(32), nullable=False)
    body = Column(String(2000), nullable=False)
    from_status = Column(String(32))
    to_status = Column(String(32))
    __table_args__ = (choices('action_type',('comment','status_change','assignment')),Index('ix_actions_issue','issue_id','created_at'))
