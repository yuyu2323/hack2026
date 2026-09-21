"""Mock 매출을 명시한 주차 추이·상관·기간 집계를 제공한다."""
from collections import defaultdict
from datetime import timedelta
from sqlalchemy import select
from server.core.db import as_utc, utcnow
from server.business_common import encode, period
from server.dashboard.service import population, rates
from server.analytics.models import SalesMock
from server.analytics.statistics import correlation
from server.stores.models import Category, Region

def week_start(value):
    day = as_utc(value).date() if hasattr(value, 'hour') else value
    return day - timedelta(days=day.weekday())

def trends(db, account, filters):
    stores, submissions, jobs, reviews, issues, applied = population(db, account, filters)
    groups = defaultdict(list)
    for row in submissions:
        groups[week_start(row.created_at)].append(row)
    points = []
    for week, rows in sorted(groups.items()):
        found = [reviews[row.id] for row in rows if row.id in reviews]
        points.append({'week_start': week.isoformat(), 'submission_count': len(rows), 'review_count': len(found),
                       **rates(found), 'unknown_count': sum(row.unknown_count for row in found),
                       'mock_review_count': sum(row.source_kind == 'mock' for row in found)})
    return {'filters': applied, 'points': points}

def sales_query(db, stores, filters):
    start, end = period(filters)
    query = select(SalesMock).where(SalesMock.store_id.in_([row.id for row in stores]), SalesMock.week_start >= week_start(start), SalesMock.week_start <= week_start(end - timedelta(days=1)))
    if filters.category_id:
        query = query.where(SalesMock.category_id == filters.category_id)
    return list(db.scalars(query))

def correlate(db, account, filters):
    stores, submissions, jobs, reviews, issues, applied = population(db, account, filters)
    groups = defaultdict(list)
    for row in submissions:
        if row.id in reviews:
            groups[(row.store_id, row.category_id, week_start(row.created_at))].append(reviews[row.id])
    sales = {(row.store_id, row.category_id, row.week_start): row for row in sales_query(db, stores, filters)}
    points = []
    missing = unassessable = 0
    for key, rows in sorted(groups.items(), key=lambda item: (item[0][2], str(item[0][0]), str(item[0][1]))):
        valid = [float(row.compliance_rate) for row in rows if row.compliance_rate is not None]
        if not valid:
            unassessable += 1
            continue
        if key not in sales:
            missing += 1
            continue
        points.append({'store_id': str(key[0]), 'category_id': str(key[1]), 'week_start': key[2].isoformat(),
                       'compliance_rate': round(sum(valid) / len(valid), 1), 'sales_amount': float(sales[key].amount),
                       'review_count': len(rows), 'assessable_rate': rates(rows)['assessable_rate']})
    return {'filters': applied, 'mock': True, 'method': 'pearson', **correlation(points),
            'excluded_missing_count': missing, 'excluded_unassessable_count': unassessable, 'points': points}

def report(db, account, filters, group_by):
    stores, submissions, jobs, reviews, issues, applied = population(db, account, filters)
    store_map = {row.id: row for row in stores}
    categories = list(db.scalars(select(Category).order_by(Category.name, Category.id)))
    if filters.category_id:
        categories = [row for row in categories if row.id == filters.category_id]
    if group_by == 'store':
        targets = [(row.id, row.name) for row in stores]
    elif group_by == 'region':
        targets = [(row.id, row.name) for row in db.scalars(select(Region).where(Region.id.in_({row.region_id for row in stores})).order_by(Region.name, Region.id))]
    else:
        targets = [(row.id, row.name) for row in categories] if stores else []
    def group(row):
        return row.store_id if group_by == 'store' else row.category_id if group_by == 'category' else store_map[row.store_id].region_id
    sales = sales_query(db, stores, filters)
    results = []
    for ident, name in targets:
        owned = [row for row in submissions if group(row) == ident]
        ids = {row.id for row in owned}
        found = [reviews[sid] for sid in ids if sid in reviews]
        amounts = [row.amount for row in sales if group(row) == ident]
        results.append({'id': str(ident), 'name': name, 'submission_count': len(owned), 'review_count': len(found),
                        'failed_count': sum(jobs[sid].status == 'failed' for sid in ids),
                        'open_issue_count': sum(row.submission_id in ids for row in issues), **rates(found),
                        'mock_sales_amount': float(sum(amounts)) if amounts else None, 'mock': True})
    return {'filters': applied, 'group_by': group_by, 'rows': results, 'generated_at': encode(utcnow())}
