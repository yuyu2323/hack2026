"""QA01 지정 운영 이력과 재처리 계약을 읽기 전용 메타데이터로 검증한다."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import (Account, AnalysisAttempt, AnalysisContext, AnalysisJob, AuditEvent, CriterionEvaluation,
                                MediaAsset, OFCStoreMapping, ReviewResult, StoreOwnerMapping, Submission, SubmissionPhoto)
from server.seed.__main__ import BASE, ident
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import validate_result, derive_metrics

OUT = ROOT / 'execute/workHitory/integration-concept-01'
ACCOUNT = UUID('988e8b9b-8ec4-45b3-afff-9937b45ac7c9')
JOB = UUID('c5d22c4e-7a26-5961-a04f-79ba8e12e745')
SUCCESS = UUID('6f336626-ae76-446a-84a7-024f8908ac5c')
FIRST_OFC_MAPPING = UUID('caffefaf-5fe3-462c-92de-e4edc2f86606')
checks = []
report = {'status': 'RUNNING', 'started_at': datetime.now(timezone.utc).isoformat(), 'checks': checks,
          'scope': 'READ ONLY 지정 메타데이터; DB/서비스 변경·HTTP·새 AI 호출·본문/비밀 출력 없음'}


def need(value):
    if value is None:
        raise ValueError('MISSING_TARGET')
    return value


def check(name, value):
    checks.append({'check': name, 'status': 'PASS' if bool(value) else 'FAIL'})


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def ms(start, end):
    return round((end-start).total_seconds()*1000) if start and end else None


def audit_meta(row):
    allowed = {'id', 'role', 'region_id', 'is_active', 'version', 'store_ids', 'ended_mapping_ids', 'ofc_id', 'status', 'current_attempt_id', 'enqueue_generation'}
    return {'id': str(row.id), 'action': row.action, 'target_type': row.target_type, 'target_id': str(row.target_id),
            'actor_id': str(row.actor_id), 'created_at': row.created_at.isoformat(), 'outcome': row.outcome,
            'reason_present': bool(row.reason.strip()), 'request_id_present': bool(row.request_id),
            'before': {k: v for k, v in row.before_data.items() if k in allowed},
            'after': {k: v for k, v in row.after_data.items() if k in allowed}}


def verify_retry(db):
    job = need(db.get(AnalysisJob, JOB))
    sub = need(db.get(Submission, job.submission_id))
    context = need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == sub.id)))
    review = need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id == sub.id)))
    attempts = list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id == JOB).order_by(AnalysisAttempt.attempt_number)))
    check('exact_two_attempts', len(attempts) == 2)
    first, second = attempts
    check('known_success_attempt_applied_once', second.id == SUCCESS and second.attempt_number == 2 and second.status == 'succeeded'
          and second.result_applied and not first.result_applied and review.attempt_id == second.id == job.current_attempt_id
          and job.status == 'succeeded' and job.error_code is None and review.source_kind == 'real_ai' and job.is_fixture)
    # 원래 시드의 식별자·시각·오류와 직접 대조한다. 새 실패를 일으키지 않는다.
    codes = ['spring-station', 'bank-road', 'green-hill', 'star-river', 'sunset-park', 'spring-road']
    matches = [(index, code+'-3') for index, code in enumerate(codes) if ident('analysis_jobs', code+'-3') == JOB]
    check('known_seed_job_identity', len(matches) == 1)
    index, code = matches[0]
    when = BASE - timedelta(days=(55 if index == 5 else 20) - 9 + index % 2)
    check('original_failure_preserved_exact_seed_fields', first.id == ident('analysis_attempts', code)
          and first.attempt_number == 1 and first.status == 'failed' and first.error_code == 'AI_UNAVAILABLE'
          and first.queued_at == when and first.started_at == when+timedelta(seconds=1)
          and first.finished_at == when+timedelta(seconds=12) and not first.result_applied
          and first.requested_by_id is None and first.worker_id is None)
    check('snapshot_sha256_matches_content', digest(context.snapshot) == context.snapshot_sha256)
    snap = context.snapshot
    payload = {'schema_version': context.schema_version, 'job_id': str(JOB), 'attempt_id': str(second.id), 'submission_id': str(sub.id),
               **{k: snap[k] for k in ('question', 'guidelines', 'references', 'previous_review')},
               'photos': [{k: row[k] for k in ('photo_id', 'position', 'mime_type', 'sha256')} for row in snap['photos']]}
    parsed = AnalysisInput.model_validate(payload)
    check('strict_ai_input_schema', True)
    result = validate_result(review.result, parsed)
    check('strict_output_and_exact_guideline_reference_contract', True)
    metrics = derive_metrics(result, parsed)
    check('derived_metrics_match_storage', all((float(getattr(review, k)) if isinstance(v, float) else getattr(review, k)) == v for k, v in metrics.items()))
    photos = list(db.scalars(select(SubmissionPhoto).where(SubmissionPhoto.submission_id == sub.id).order_by(SubmissionPhoto.position)))
    check('photo_links_and_hash_metadata', len(photos) == len(parsed.photos) and all(str(link.id) == meta.photo_id
          and link.position == meta.position and str(link.media_id) == snap['photos'][i]['media_id']
          and db.get(MediaAsset, link.media_id).sha256 == meta.sha256 for i, (link, meta) in enumerate(zip(photos, parsed.photos))))
    check('reference_media_hash_metadata', all(db.get(MediaAsset, UUID(meta.photo_id)).sha256 == meta.sha256 for meta in parsed.references))
    criteria = list(db.scalars(select(CriterionEvaluation).where(CriterionEvaluation.review_id == review.id)))
    expected = {(c.guideline_id, c.version_id, c.rule_key, c.verdict, digest(c.evidence), digest(c.actions)) for c in criteria}
    actual = {(UUID(c.guideline_id), UUID(c.version_id), c.rule_key, c.verdict,
               digest([item.model_dump() for item in c.evidence]), digest(c.actions)) for c in result.criteria}
    check('normalized_criteria_match_result', len(criteria) == len(result.criteria) and expected == actual)
    retry_audits = list(db.scalars(select(AuditEvent).where(AuditEvent.action == 'analysis_job.retry', AuditEvent.target_id == JOB)))
    check('retry_audit_failure_to_queued_attempt2', len(retry_audits) == 1 and retry_audits[0].before_data.get('status') == 'failed'
          and retry_audits[0].before_data.get('current_attempt_id') == str(first.id)
          and retry_audits[0].after_data.get('status') == 'queued'
          and retry_audits[0].after_data.get('current_attempt_id') == str(second.id))
    queue_ms, run_ms = ms(second.queued_at, second.started_at), ms(second.started_at, second.finished_at)
    check('nonnegative_times_and_acceptance_deadline', review.latency_ms >= 0 and queue_ms >= 0 and run_ms >= 0
          and second.finished_at <= second.deadline_at and second.finished_at <= second.lease_expires_at)
    check('review_job_attempt_status_consistency', job.started_at == second.started_at and job.finished_at == second.finished_at
          and review.created_at >= second.finished_at and second.error_code is None
          and db.scalar(select(func.count()).select_from(ReviewResult).where(ReviewResult.submission_id == sub.id)) == 1)
    report['retry'] = {'job_id': str(JOB), 'submission_id': str(sub.id), 'review_id': str(review.id),
                      'is_fixture': job.is_fixture, 'submission_source_kind': sub.source_kind, 'result_source_kind': review.source_kind,
                      'model': review.model_name, 'prompt_version': review.prompt_version, 'schema_version': review.schema_version,
                      'snapshot_sha256': context.snapshot_sha256, 'result_sha256': digest(review.result),
                      'input_count': {'photos': len(parsed.photos), 'guidelines': len(parsed.guidelines), 'references': len(parsed.references)},
                      'output_count': {'criteria': len(result.criteria), 'references': len(result.reference_comparisons)},
                      'review_created_at': review.created_at.isoformat(), 'model_ms': review.latency_ms,
                      'metrics': metrics, 'retry_audits': [audit_meta(a) for a in retry_audits],
                      'attempts': [{'id': str(a.id), 'number': a.attempt_number, 'status': a.status, 'error_code': a.error_code,
                                    'result_applied': a.result_applied, 'queued_at': a.queued_at.isoformat(),
                                    'started_at': a.started_at.isoformat() if a.started_at else None,
                                    'finished_at': a.finished_at.isoformat() if a.finished_at else None,
                                    'queue_ms': ms(a.queued_at, a.started_at), 'run_ms': ms(a.started_at, a.finished_at)} for a in attempts]}
    delta = run_ms-review.latency_ms
    report['timing'] = {'queue_ms': queue_ms, 'run_ms': run_ms, 'model_ms': review.latency_ms, 'run_minus_model_ms': delta,
                        'classification': 'CONSISTENT_ORDER' if delta >= 0 else 'CLOCK_BASIS_ANOMALY_UNRESOLVED',
                        'model_clock': 'adapter monotonic: 사진 준비/CLI/출력 검증', 'worker_clock': 'UTC wall-clock',
                        'excluded_from_normal_first_submission_latency': True, 'model_under_30_seconds': review.latency_ms < 30000}


def verify_account(db, expected_version):
    account = need(db.get(Account, ACCOUNT))
    owners = list(db.scalars(select(StoreOwnerMapping).where(StoreOwnerMapping.account_id == ACCOUNT)))
    ofcs = list(db.scalars(select(OFCStoreMapping).where(OFCStoreMapping.account_id == ACCOUNT)))
    audits = list(db.scalars(select(AuditEvent).where(AuditEvent.target_type == 'account', AuditEvent.target_id == ACCOUNT).order_by(AuditEvent.created_at)))
    claims = list(db.scalars(select(AuditEvent).where(AuditEvent.action == 'stores.claim', AuditEvent.actor_id == ACCOUNT).order_by(AuditEvent.created_at)))
    check('final_active_owner_expected_version_null_region_unmapped', account.version == expected_version and account.role == 'store_owner'
          and account.region_id is None and account.is_active and all(m.ended_at is not None for m in owners+ofcs))
    check('account_audit_versions_and_reason_request', audits[0].after_data.get('version') == 1
          and all(a.after_data.get('version') == a.before_data.get('version')+1 for a in audits[1:])
          and audits[-1].after_data.get('version') == expected_version
          and all(a.outcome == 'succeeded' and a.reason.strip() and a.request_id for a in audits+claims))
    latest = audits[-1].after_data
    check('final_audit_matches_current_account', latest.get('role') == account.role and latest.get('region_id') is None
          and latest.get('is_active') is True and latest.get('store_ids') == [])
    bank = [m for m in owners if m.store_id == ident('stores', 'bank-road')]
    check('bank_road_owner_mapping_ended_with_audit', bool(bank) and all(m.ended_at is not None and any(
        str(m.id) in a.after_data.get('ended_mapping_ids', []) and str(m.store_id) in a.before_data.get('store_ids', [])
        and str(m.store_id) not in a.after_data.get('store_ids', []) for a in audits) for m in bank))
    check('specified_first_ofc_mapping_preserved_ended', any(m.id == FIRST_OFC_MAPPING and m.ended_at is not None for m in ofcs))
    for mapping in ofcs:
        claim = [a for a in claims if a.target_id == mapping.store_id and a.after_data.get('ofc_id') == str(ACCOUNT)
                 and abs((mapping.created_at-a.created_at).total_seconds()) < 2]
        endings = [a for a in audits if str(mapping.id) in a.after_data.get('ended_mapping_ids', [])]
        check(str(mapping.id)+':claim_and_owner_restore_audit', mapping.store_id == ident('stores', 'green-hill')
              and mapping.ended_at is not None and len(claim) == 1 and len(endings) == 1
              and endings[0].before_data.get('role') == 'ofc' and endings[0].after_data.get('role') == 'store_owner'
              and claim[0].created_at < endings[0].created_at
              and abs((mapping.ended_at-endings[0].created_at).total_seconds()) < 2)
    report['account'] = {'id': str(account.id), 'version': account.version, 'role': account.role, 'region_id': None if account.region_id is None else str(account.region_id),
                         'is_active': account.is_active, 'active_owner_mapping_count': sum(m.ended_at is None for m in owners),
                         'active_ofc_mapping_count': sum(m.ended_at is None for m in ofcs),
                         'mapping_history': [{'kind': kind, 'id': str(m.id), 'store_id': str(m.store_id),
                                              'created_at': m.created_at.isoformat(), 'ended_at': m.ended_at.isoformat() if m.ended_at else None}
                                             for kind, group in [('owner', owners), ('ofc', ofcs)] for m in group],
                         'audits': [audit_meta(a) for a in audits], 'claims': [audit_meta(a) for a in claims]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--account-version', type=int)
    args = parser.parse_args()
    value = need(dotenv_values(ROOT / '.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL'))
    url = make_url(value)
    if url.host not in ('127.0.0.1', 'localhost') or url.port != 55432 or url.database != 'storeloop_test':
        raise ValueError('DB_TARGET_MISMATCH')
    engine = create_engine(value, hide_parameters=True, connect_args={'options': '-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('database_read_only', conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on')
        with Session(bind=conn, autoflush=False) as db:
            verify_retry(db)
            if args.account_version:
                verify_account(db, args.account_version)
            else:
                report['account_review'] = 'NOT_RUN: root 최종 복원 완료 대기'
    engine.dispose()
    report['status'] = ('PASS' if report['timing']['classification'] == 'CONSISTENT_ORDER' else 'FUNCTIONAL_PASS_WITH_TIMING_ANOMALY') if all(c['status'] == 'PASS' for c in checks) else 'FAIL'


if __name__ == '__main__':
    try:
        main()
    except Exception:
        report['status'] = 'FAIL'
        report['failure'] = '비밀과 업무 원문 보호를 위해 예외 원문은 출력하지 않았다.'
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    path = OUT / ('independent-operations-metadata-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n'); path.chmod(0o600)
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'failed': [c['check'] for c in checks if c['status'] == 'FAIL'],
                      'timing': report.get('timing'), 'account_version': report.get('account', {}).get('version'), 'evidence': str(path.relative_to(ROOT))}, ensure_ascii=False))
    if report['status'] == 'FAIL':
        raise SystemExit(1)
