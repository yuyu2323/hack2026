"""같은 범위·기간으로 관제 지표와 매장별 상세 이동 대상을 계산한다."""
from sqlalchemy import select
from server.business_common import encode, scoped_stores, period
from server.submissions.service import filtered_submissions, job_dto
from server.analysis_jobs.models import AnalysisJob
from server.reviews.models import ReviewResult
from server.issues.models import Issue

def rates(reviews):
    passes = sum(review.pass_count for review in reviews)
    fails = sum(review.fail_count for review in reviews)
    unknowns = sum(review.unknown_count for review in reviews)
    assessable = passes + fails
    total = assessable + unknowns
    return {'compliance_rate': round(passes / assessable * 100, 1) if assessable else None,
            'assessable_rate': round(assessable / total * 100, 1) if total else None}

def population(db, account, filters):
    stores = scoped_stores(db, account, filters)
    submissions = filtered_submissions(db, account, filters)
    ids = [row.id for row in submissions]
    jobs = {row.submission_id: row for row in db.scalars(select(AnalysisJob).where(AnalysisJob.submission_id.in_(ids)))}
    reviews = {row.submission_id: row for row in db.scalars(select(ReviewResult).where(ReviewResult.submission_id.in_(ids)))}
    issues = list(db.scalars(select(Issue).where(Issue.submission_id.in_(ids), Issue.status != 'resolved')))
    start, end = period(filters)
    applied = encode(filters.model_dump())
    from datetime import timedelta
    applied.update(date_from=start.date().isoformat(), date_to=(end - timedelta(days=1)).date().isoformat())
    return stores, submissions, jobs, reviews, issues, applied

def dashboard(db, account, filters):
    if filters.is_active is None:
        filters = filters.model_copy(update={'is_active': True})
    stores, submissions, jobs, reviews, issues, applied = population(db, account, filters)
    kpis = {'store_count': len(stores), 'submitted_store_count': len({row.store_id for row in submissions}),
            'submission_count': len(submissions), 'needs_ofc_review_count': sum(row.needs_ofc_review for row in reviews.values()),
            'open_issue_count': len(issues), **rates(list(reviews.values()))}
    for status in ('queued','running','succeeded','failed'):
        kpis[status + '_count'] = sum(row.status == status for row in jobs.values())
    rows = []
    for store in stores:
        owned = [row for row in submissions if row.store_id == store.id]
        ids = {row.id for row in owned}
        own_reviews = [row for sid, row in reviews.items() if sid in ids]
        latest = owned[0] if owned else None
        job = jobs.get(latest.id) if latest else None
        review = reviews.get(latest.id) if latest else None
        issue_count = sum(row.submission_id in ids for row in issues)
        status = 'not_submitted' if not latest else 'needs_attention' if issue_count else 'processing' if job.status in ('queued','running') else 'technical_failure' if job.status == 'failed' else 'unassessable' if not review or not review.assessable_rate or review.needs_ofc_review else 'evaluated'
        rows.append({'store_id': str(store.id), 'store_name': store.name, 'region_id': str(store.region_id),
                     'submission_count': len(owned), 'review_count': len(own_reviews), 'failed_count': sum(jobs[sid].status == 'failed' for sid in ids),
                     'open_issue_count': issue_count, **rates(own_reviews), 'status': status,
                     'latest_submission_id': str(latest.id) if latest else None, 'latest_job': job_dto(db, job) if job else None,
                     'needs_ofc_review_count': sum(row.needs_ofc_review for row in own_reviews),
                     'drilldown': {**applied, 'region_id': str(store.region_id), 'store_id': str(store.id)}})
    return {'filters': applied, 'kpis': kpis, 'stores': rows, 'sample_count': len(reviews),
            'mock_review_count': sum(row.source_kind == 'mock' for row in reviews.values())}
