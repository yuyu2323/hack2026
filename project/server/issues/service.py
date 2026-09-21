"""평가 원본을 보존하면서 담당자 조치와 앱 알림을 연결한다."""
from uuid import uuid4
from sqlalchemy import select, or_
from server.core.db import utcnow
from server.core.errors import ApiError
from server.core.permissions import require_store_access, accessible_store_ids, require_business
from server.business_common import fields, encode, lock_idempotency, save_idempotency, request_hash, MANAGER_ROLES
from server.accounts.models import Account
from server.stores.models import Store, Category, OFCStoreMapping
from server.submissions.models import Submission
from server.reviews.models import ReviewResult
from server.issues.models import Issue, IssueAction
from server.notifications.models import Notification


def assignees(db, store_id):
    store = db.get(Store, store_id)
    ofc_ids = list(db.scalars(select(OFCStoreMapping.account_id).where(OFCStoreMapping.store_id == store_id, OFCStoreMapping.ended_at.is_(None))))
    accounts = db.scalars(select(Account).where(Account.is_active == True).order_by(Account.display_name, Account.id))
    return [item for item in accounts if item.role == 'hq' or (item.role == 'regional' and item.region_id == store.region_id)
            or (item.role == 'ofc' and item.id in ofc_ids and item.region_id == store.region_id)]


def default_assignee(db, store_id):
    return next((item.id for item in assignees(db, store_id) if item.role == 'ofc'), None)


def notify(db, recipient_id, kind, submission_id, issue_id, title, key):
    if recipient_id and not db.scalar(select(Notification.id).where(Notification.dedupe_key == key)):
        db.add(Notification(id=uuid4(), recipient_id=recipient_id, kind=kind, submission_id=submission_id,
                            issue_id=issue_id, title=title, dedupe_key=key))


def on_review_ready(db, submission, review):
    # 작업자는 이 함수를 결과 저장과 같은 트랜잭션에서 호출한다. 여기서 commit하지 않는다.
    notify(db, submission.submitted_by_id, 'review_ready', submission.id, None, '사진 분석 결과가 도착했습니다.',
           f'review:{review.id}:{submission.submitted_by_id}')
    if review.needs_ofc_review and not db.scalar(select(Issue.id).where(Issue.submission_id == submission.id, Issue.type == 'ai_review_required')):
        issue = Issue(id=uuid4(), submission_id=submission.id, review_id=review.id, type='ai_review_required',
                      status='open', priority='normal', title='AI 판단에 대한 OFC 확인',
                      description=review.result['summary'][:2000], assignee_id=default_assignee(db, submission.store_id))
        db.add(issue)
        db.flush()
        notify(db, issue.assignee_id, 'issue_created', submission.id, issue.id, '확인이 필요한 평가가 있습니다.',
               f'issue:{issue.id}:created:{issue.assignee_id}')


def get_issue(db, account, ident, lock=False):
    require_business(account)
    query = select(Issue).where(Issue.id == ident)
    issue = db.scalar(query.with_for_update().execution_options(populate_existing=True) if lock else query)
    if issue is None:
        raise ApiError(404, 'NOT_FOUND', '문의 또는 조치를 찾을 수 없습니다.')
    submission = db.get(Submission, issue.submission_id)
    require_store_access(db, account, submission.store_id)
    return issue


def issue_summary(db, issue):
    submission = db.get(Submission, issue.submission_id)
    store, category = db.get(Store, submission.store_id), db.get(Category, submission.category_id)
    assigned = db.get(Account, issue.assignee_id) if issue.assignee_id else None
    result = fields(issue, 'id submission_id review_id type status priority title assignee_id next_check_at created_at updated_at version')
    result.update(store_id=str(store.id), store_name=store.name, category_id=str(category.id), category_name=category.name,
                  assignee_name=assigned.display_name if assigned else None)
    return result


def action_dto(db, action):
    actor = db.get(Account, action.actor_id)
    return dict(**fields(action, 'id actor_id action_type body from_status to_status created_at'), actor_name=actor.display_name)


def issue_detail(db, issue):
    actions = db.scalars(select(IssueAction).where(IssueAction.issue_id == issue.id).order_by(IssueAction.created_at, IssueAction.id)).all()
    return dict(**issue_summary(db, issue), **fields(issue, 'description resolution resolved_at'), actions=[action_dto(db, action) for action in actions])


def create_issue(db, account, data, key):
    from server.submissions.service import get_submission
    submission = get_submission(db, account, data.submission_id)
    if account.role == 'store_owner' and submission.submitted_by_id != account.id:
        raise ApiError(403, 'FORBIDDEN', '본인이 제출한 사진에 확인을 요청할 수 있습니다.')
    digest = request_hash('POST', '/issues', data.model_dump(mode='json'))
    existing = lock_idempotency(db, account, 'issues.create', key, digest)
    if existing:
        return issue_detail(db, get_issue(db, account, existing.resource_id)), True
    review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == submission.id))
    issue = Issue(id=uuid4(), submission_id=submission.id, review_id=review.id if review else None,
                  type='owner_question', status='open', priority=data.priority, title=data.title, description=data.description,
                  assignee_id=default_assignee(db, submission.store_id), created_by_id=account.id)
    db.add(issue)
    db.flush()
    notify(db, issue.assignee_id, 'issue_created', submission.id, issue.id, '매장 사진에 대한 확인 요청이 있습니다.', f'issue:{issue.id}:created:{issue.assignee_id}')
    save_idempotency(db, account, 'issues.create', key, digest, issue.id, 201)
    db.commit()
    return issue_detail(db, issue), False


def notify_update(db, issue, event_id):
    submission = db.get(Submission, issue.submission_id)
    for recipient in {submission.submitted_by_id, issue.assignee_id} - {None}:
        notify(db, recipient, 'issue_updated', submission.id, issue.id, '확인 요청에 새로운 조치가 등록되었습니다.', f'issue:{issue.id}:{event_id}:{recipient}')


def update_issue(db, account, ident, data):
    if account.role not in MANAGER_ROLES:
        raise ApiError(403, 'FORBIDDEN', '영업 관리자만 조치를 변경할 수 있습니다.')
    issue = get_issue(db, account, ident, lock=True)
    if issue.version != data.version:
        raise ApiError(409, 'VERSION_CONFLICT', '다른 담당자가 변경했습니다. 최신 내용을 확인해 주세요.')
    submission = db.get(Submission, issue.submission_id)
    if data.assignee_id and data.assignee_id not in {item.id for item in assignees(db, submission.store_id)}:
        raise ApiError(422, 'VALIDATION_ERROR', '이 매장을 담당할 수 있는 사용자를 선택해 주세요.')
    changed = data.model_dump(exclude_unset=True, exclude={'version'})
    before = issue.status
    target_status = changed.get('status', issue.status)
    target_resolution = changed.get('resolution', issue.resolution)
    if target_status == 'resolved' and not (target_resolution or '').strip():
        raise ApiError(422, 'VALIDATION_ERROR', '해결 내용을 입력해 주세요.')
    if all(getattr(issue, key) == value for key, value in changed.items()):
        return issue_detail(db, issue)
    for key, value in changed.items():
        setattr(issue, key, value)
    issue.version += 1
    issue.resolved_at = utcnow() if issue.status == 'resolved' else None
    action = IssueAction(id=uuid4(), issue_id=issue.id, actor_id=account.id,
                         action_type='status_change' if before != issue.status else 'assignment',
                         body=data.resolution or ('조치 상태 변경' if before != issue.status else '담당 또는 확인 일정 변경'),
                         from_status=before, to_status=issue.status)
    db.add(action)
    notify_update(db, issue, action.id)
    db.commit()
    return issue_detail(db, issue)


def add_action(db, account, ident, body):
    if account.role not in MANAGER_ROLES:
        raise ApiError(403, 'FORBIDDEN', '영업 관리자만 조치를 등록할 수 있습니다.')
    issue = get_issue(db, account, ident, lock=True)
    action = IssueAction(id=uuid4(), issue_id=issue.id, actor_id=account.id, action_type='comment', body=body)
    db.add(action)
    issue.updated_at = utcnow()
    issue.version += 1
    notify_update(db, issue, action.id)
    db.commit()
    return action_dto(db, action)
