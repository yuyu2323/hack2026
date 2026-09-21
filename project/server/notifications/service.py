from sqlalchemy import select
from server.core.db import utcnow
from server.core.errors import ApiError
from server.core.permissions import accessible_store_ids, require_business
from server.submissions.models import Submission
from server.notifications.models import Notification
from server.business_common import fields


def visible_notifications(db, account):
    require_business(account)
    ids = accessible_store_ids(db, account)
    return list(db.scalars(select(Notification).join(Submission, Submission.id == Notification.submission_id)
                           .where(Notification.recipient_id == account.id, Submission.store_id.in_(ids))
                           .order_by(Notification.created_at.desc(), Notification.id)))


def dto(row):
    result = fields(row, 'id kind title submission_id issue_id read_at created_at')
    result['target'] = {'type': 'issue' if row.issue_id else 'submission', 'id': str(row.issue_id or row.submission_id)}
    return result


def mark_read(db, account, ident):
    row = next((row for row in visible_notifications(db, account) if row.id == ident), None)
    if row is None:
        raise ApiError(404, 'NOT_FOUND', '알림을 찾을 수 없습니다.')
    if row.read_at is None:
        row.read_at = utcnow()
        db.commit()
    return dto(row)
