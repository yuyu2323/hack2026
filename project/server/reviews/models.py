from sqlalchemy import Column, String, Integer, Boolean, Numeric, UniqueConstraint, CheckConstraint, Index
from server.core.base import Base, IdentityMixin, CreatedMixin
from server.core.model_helpers import fk, choices, JSON_DATA

class ReviewResult(IdentityMixin, CreatedMixin, Base):
    __tablename__ = 'review_results'
    submission_id = fk('submissions', unique=True)
    attempt_id = fk('analysis_attempts', nullable=True, unique=True)
    schema_version = Column(String(16), nullable=False, default='1.0')
    result = Column(JSON_DATA, nullable=False)
    compliance_rate = Column(Numeric(5,1))
    assessable_rate = Column(Numeric(5,1))
    pass_count = Column(Integer, nullable=False)
    fail_count = Column(Integer, nullable=False)
    unknown_count = Column(Integer, nullable=False)
    needs_ofc_review = Column(Boolean, nullable=False)
    source_kind = Column(String(16), nullable=False)
    model_name = Column(String(120))
    prompt_version = Column(String(32), nullable=False)
    latency_ms = Column(Integer, nullable=False)
    __table_args__ = (choices('source_kind',('real_ai','mock')),CheckConstraint("source_kind = 'mock' OR attempt_id IS NOT NULL"),CheckConstraint('compliance_rate BETWEEN 0 AND 100'),CheckConstraint('assessable_rate BETWEEN 0 AND 100'),CheckConstraint('pass_count >= 0 AND fail_count >= 0 AND unknown_count >= 0 AND latency_ms >= 0'),Index('ix_review_created','created_at'))

class CriterionEvaluation(IdentityMixin, Base):
    __tablename__ = 'criterion_evaluations'
    review_id = fk('review_results')
    guideline_id = fk('guidelines')
    version_id = fk('guideline_versions')
    rule_key = Column(String(80), nullable=False)
    verdict = Column(String(16), nullable=False)
    evidence = Column(JSON_DATA, nullable=False)
    actions = Column(JSON_DATA, nullable=False)
    __table_args__ = (UniqueConstraint('review_id','version_id'),choices('verdict',('pass','fail','unknown')),Index('ix_criterion_verdict','rule_key','verdict'))
