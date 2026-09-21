"""QA02 현재 기준 우선순위·과거 스냅샷·운영 변경을 읽기 전용으로 검증한다."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from uuid import UUID
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import (Account, AnalysisContext, AuditEvent, Category, Guideline, GuidelineVersion,
                                OFCStoreMapping, ReviewResult, Store, StoreOwnerMapping, Submission)
from server.submissions.service import make_snapshot
from server.seed.__main__ import ident

OUT = ROOT / 'execute/workHitory/integration-concept-02'
ACCOUNT = UUID('22b4defd-15bf-478c-a23e-613fcf4134eb')
UPPER = {'HQ': UUID('2d4ea8b1-116c-430e-8e06-e80ba477484b'), 'REGION': UUID('2089bf7c-3836-441c-9d00-7a32eb6a0436'),
         'STORE': UUID('d422d014-58d6-4d90-ae76-d4502709dad7')}
BASELINE = OUT / 'independent-ai-metadata-20260921T124410Z.json'
checks = []
report = {'status': 'RUNNING', 'started_at': datetime.now(timezone.utc).isoformat(), 'checks': checks,
          'scope': '현재 시점 READ ONLY resolve 및 기존 기록 비교; DB/API/AI/Browser 변경 없음'}


def check(name, value):
    checks.append({'check': name, 'status': 'PASS' if bool(value) else 'FAIL'})


def need(value):
    if value is None:
        raise ValueError('TARGET_MISSING')
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def audit_meta(row):
    allowed = {'id', 'version', 'role', 'region_id', 'is_active', 'store_ids', 'ended_mapping_ids', 'ofc_id', 'code'}
    return {'id': str(row.id), 'action': row.action, 'target_id': str(row.target_id), 'actor_id': str(row.actor_id),
            'created_at': row.created_at.isoformat(), 'outcome': row.outcome, 'reason_present': bool(row.reason.strip()),
            'request_id_present': bool(row.request_id), 'before': {k:v for k,v in row.before_data.items() if k in allowed},
            'after': {k:v for k,v in row.after_data.items() if k in allowed}}


def main():
    baseline = json.loads(BASELINE.read_text())
    check('baseline_three_real_ai_records', len(baseline['submissions']) == 3)
    report['baseline'] = {'path': str(BASELINE.relative_to(ROOT)), 'sha256': hashlib.sha256(BASELINE.read_bytes()).hexdigest()}
    value = need(dotenv_values(ROOT / '.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL'))
    url = make_url(value)
    if url.host not in ('127.0.0.1', 'localhost') or url.port != 55432 or url.database != 'storeloop_test':
        raise ValueError('DB_TARGET_MISMATCH')
    engine = create_engine(value, hide_parameters=True, connect_args={'options': '-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('database_read_only', conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on')
        with Session(bind=conn, autoflush=False) as db:
            upper = [need(db.get(Guideline, row_id)) for row_id in UPPER.values()]
            check('three_requested_upper_rules_active', all(g.is_active and g.rule_key == 'qa02_labels' and UPPER[g.level] == g.id for g in upper))
            latest = need(db.get(Submission, UUID(baseline['submissions'][-1]['submission_id'])))
            context = need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == latest.id)))
            current = make_snapshot(db, db.get(Store, latest.store_id), db.get(Category, latest.category_id),
                                    latest.question, context.snapshot['photos'], None)
            candidates = [r for r in current['candidate_guidelines'] if r['rule_key'] == 'qa02_labels']
            effective = [r for r in current['guidelines'] if r['rule_key'] == 'qa02_labels']
            category = [r for r in candidates if r['level'] == 'CATEGORY']
            check('current_four_levels_present_once', len(candidates) == 4 and {r['level'] for r in candidates} == {'HQ','REGION','STORE','CATEGORY'})
            check('current_category_v2_is_only_winner', len(category) == len(effective) == 1 and category[0]['version'] == 2
                  and effective[0]['guideline_id'] == category[0]['guideline_id']
                  and sum(r['selected'] for r in candidates) == 1 and category[0]['selected'])
            report['current_resolution'] = {'ephemeral_only': True, 'store_id': str(latest.store_id), 'category_id': str(latest.category_id),
                'created_at': datetime.now(timezone.utc).isoformat(), 'persisted': False,
                'candidates': [{k:r[k] for k in ('guideline_id','version_id','version','level','rule_key','selected','selection_reason')} for r in candidates],
                'effective': [{k:r[k] for k in ('guideline_id','version_id','version','level','rule_key')} for r in effective],
                'upper_created_at': {g.level:g.created_at.isoformat() for g in upper}}
            records = []
            for original in baseline['submissions']:
                sub = need(db.get(Submission, UUID(original['submission_id'])))
                saved = need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == sub.id)))
                result = need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id == sub.id)))
                check(str(sub.id)+':snapshot_unchanged_from_baseline', saved.snapshot_sha256 == original['snapshot_sha256'] == digest(saved.snapshot))
                check(str(sub.id)+':result_unchanged_from_baseline', digest(result.result) == original['result_sha256'] and result.source_kind == 'real_ai')
                check(str(sub.id)+':upper_rules_created_after_real_ai', all(g.created_at > result.created_at > sub.created_at for g in upper))
                check(str(sub.id)+':new_upper_rules_absent_from_old_snapshot', not any(r['guideline_id'] in {str(x) for x in UPPER.values()} for r in saved.snapshot['candidate_guidelines']))
                records.append({'submission_id': str(sub.id), 'submitted_at': sub.created_at.isoformat(), 'review_created_at': result.created_at.isoformat(),
                    'snapshot_sha256': saved.snapshot_sha256, 'result_sha256': digest(result.result),
                    'qa02_saved_candidates': [{k:r[k] for k in ('guideline_id','level','version','selected')} for r in saved.snapshot['candidate_guidelines'] if r['rule_key'] == 'qa02_labels'],
                    'unchanged': saved.snapshot_sha256 == original['snapshot_sha256'] and digest(result.result) == original['result_sha256']})
            report['past_records'] = records
            account = need(db.get(Account, ACCOUNT))
            owners = list(db.scalars(select(StoreOwnerMapping).where(StoreOwnerMapping.account_id == ACCOUNT)))
            ofcs = list(db.scalars(select(OFCStoreMapping).where(OFCStoreMapping.account_id == ACCOUNT)))
            audits = list(db.scalars(select(AuditEvent).where(AuditEvent.target_type == 'account', AuditEvent.target_id == ACCOUNT).order_by(AuditEvent.created_at)))
            claims = list(db.scalars(select(AuditEvent).where(AuditEvent.action == 'stores.claim', AuditEvent.actor_id == ACCOUNT).order_by(AuditEvent.created_at)))
            check('account_active_owner_null_region_unmapped', account.role == 'store_owner' and account.is_active and account.region_id is None
                  and all(m.ended_at is not None for m in owners+ofcs))
            check('account_audit_latest_matches_version_and_current_state', audits[-1].after_data.get('version') == account.version
                  and audits[-1].after_data.get('role') == 'store_owner' and audits[-1].after_data.get('region_id') is None
                  and audits[-1].after_data.get('is_active') is True and audits[-1].after_data.get('store_ids') == [])
            check('ofc_claim_once_then_owner_restore_ends_mapping', len(ofcs) == len(claims) == 1
                  and ofcs[0].store_id == ident('stores','green-hill') and ofcs[0].ended_at is not None
                  and claims[0].target_id == ofcs[0].store_id and claims[0].after_data.get('ofc_id') == str(ACCOUNT)
                  and any(a.before_data.get('role') == 'ofc' and a.after_data.get('role') == 'store_owner'
                          and str(ofcs[0].id) in a.after_data.get('ended_mapping_ids', []) for a in audits))
            check('all_account_mapping_ends_have_audit', bool(owners) and all(any(str(m.id) in a.after_data.get('ended_mapping_ids', []) for a in audits) for m in owners+ofcs))
            check('account_and_claim_audit_reason_request', all(a.outcome == 'succeeded' and a.reason.strip() and a.request_id for a in audits+claims))
            report['account'] = {'id': str(account.id), 'version': account.version, 'role': account.role, 'is_active': account.is_active,
                'region_id': str(account.region_id) if account.region_id else None, 'active_owner_mapping_count': sum(m.ended_at is None for m in owners),
                'active_ofc_mapping_count': sum(m.ended_at is None for m in ofcs),
                'mapping_history': [{'kind': kind, 'id': str(m.id), 'store_id': str(m.store_id), 'created_at': m.created_at.isoformat(),
                                     'ended_at': m.ended_at.isoformat() if m.ended_at else None} for kind, rows in [('owner', owners), ('ofc', ofcs)] for m in rows],
                'audits': [audit_meta(a) for a in audits], 'claims': [audit_meta(a) for a in claims]}
            cat = need(db.scalar(select(Category).where(Category.code == 'qa02_test_category')))
            cat_audits = list(db.scalars(select(AuditEvent).where(AuditEvent.target_type == 'category', AuditEvent.target_id == cat.id).order_by(AuditEvent.created_at)))
            check('category_v2_renamed_inactive', cat.version == 2 and not cat.is_active and ''.join(cat.name.split()) == 'QA02검증완료분류')
            check('category_create_v1_update_v2_audit', len(cat_audits) == 2 and cat_audits[0].action == 'categories.create'
                  and cat_audits[0].after_data.get('version') == 1 and cat_audits[0].after_data.get('is_active') is True
                  and cat_audits[1].before_data.get('version') == 1 and cat_audits[1].after_data.get('version') == 2
                  and cat_audits[1].before_data.get('name') != cat_audits[1].after_data.get('name')
                  and cat_audits[1].after_data.get('is_active') is False)
            report['category'] = {'id': str(cat.id), 'code': cat.code, 'version': cat.version, 'is_active': cat.is_active,
                                  'expected_name_matches_ignoring_whitespace': ''.join(cat.name.split()) == 'QA02검증완료분류', 'audits': [audit_meta(a) for a in cat_audits]}
            check('no_pending_orm_writes', not db.new and not db.dirty and not db.deleted)
    engine.dispose()
    report['status'] = 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL'


if __name__ == '__main__':
    try:
        main()
    except Exception:
        report.update(status='FAIL', failure='비밀·본문 보호를 위해 예외 원문은 기록하지 않았다.')
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    path = OUT / ('independent-operations-metadata-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n'); path.chmod(0o600)
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'failed': [c['check'] for c in checks if c['status'] == 'FAIL'],
                      'account_version': report.get('account',{}).get('version'), 'evidence': str(path.relative_to(ROOT))}, ensure_ascii=False))
    if report['status'] == 'FAIL':
        raise SystemExit(1)
