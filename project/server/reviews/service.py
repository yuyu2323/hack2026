"""기준 버전 변경과 관찰 불가를 구별해 개선 전후를 비교한다."""
from sqlalchemy import select
from server.business_common import fields
from server.reviews.models import ReviewResult
from server.submissions.models import SubmissionPhoto
from server.submissions.service import get_submission
from server.submissions.storage import photo_dto

def compare(db, account, ident):
    current = get_submission(db, account, ident)
    parent = get_submission(db, account, current.parent_submission_id) if current.parent_submission_id else None
    def side(item):
        if item is None:
            return None, None
        review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == item.id))
        photos = db.scalars(select(SubmissionPhoto).where(SubmissionPhoto.submission_id == item.id).order_by(SubmissionPhoto.position)).all()
        return {'submission_id': str(item.id), 'review_id': str(review.id) if review else None,
                'compliance_rate': float(review.compliance_rate) if review and review.compliance_rate is not None else None,
                'assessable_rate': float(review.assessable_rate) if review and review.assessable_rate is not None else None,
                'photos': [photo_dto(db, photo.media_id, photo.position, photo.id) for photo in photos]}, review
    before, old_review = side(parent)
    after, new_review = side(current)
    old = {row['rule_key']: row for row in old_review.result['criteria']} if old_review else {}
    new = {row['rule_key']: row for row in new_review.result['criteria']} if new_review else {}
    criteria = []
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        changed = not a or not b or a['version_id'] != b['version_id']
        verdicts = (a['verdict'] if a else None, b['verdict'] if b else None)
        change = 'unavailable' if changed or 'unknown' in verdicts else 'resolved' if verdicts == ('fail','pass') else 'regressed' if verdicts == ('pass','fail') else 'unchanged'
        criteria.append({'rule_key': key, 'before': verdicts[0], 'after': verdicts[1], 'criterion_changed': bool(changed), 'change': change})
    return {'parent': before, 'current': after, 'criteria': criteria,
            'narrative': new_review.result.get('follow_up_comparison') if new_review else None}
