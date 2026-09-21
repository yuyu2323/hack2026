"""Alembic과 작업자가 공유하는 모델 등록부."""
from server.core.base import Base
from server.accounts.models import Account, AuthSession
from server.stores.models import Region, Store, Category, StoreOwnerMapping, OFCStoreMapping
from server.guidelines.models import Guideline, GuidelineVersion, ReferencePhoto
from server.submissions.models import MediaAsset, Submission, SubmissionPhoto, AnalysisContext
from server.analysis_jobs.models import AnalysisJob, AnalysisAttempt, IdempotencyRecord
from server.reviews.models import ReviewResult, CriterionEvaluation
from server.issues.models import Issue, IssueAction
from server.notifications.models import Notification
from server.analytics.models import SalesMock, InventoryMock
from server.operations.models import AuditEvent, ServiceStatus, Announcement
