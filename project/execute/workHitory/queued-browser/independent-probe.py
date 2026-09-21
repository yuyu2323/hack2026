"""root가 실행한 대기 fixture 복원과 비교 가능한 기존 기록을 읽기 전용 확인한다."""
from datetime import datetime, timezone
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
from server.core.models import AnalysisAttempt, AnalysisContext, AnalysisJob, AuditEvent, ReviewResult, Submission

OUT = ROOT / 'execute/workHitory/queued-browser'
SUBMISSION = UUID('2f9b333f-8a43-5df0-841d-f1c66b213ab3')
JOB = UUID('0d50701f-c61b-5c48-80ea-1df7ca4d2cb4')
AUDIT = UUID('48dbbd19-8225-5e78-9615-aa72653ce8c3')
EXPECTED_SHA = '7a09aa3f289e307a825a20921522ed3d030004c01e7a5289e9efc4d0cf7ee7e8'
checks = []
report = {'status':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),'checks':checks,
          'scope':'READ ONLY; 원문·비밀·이미지 출력 없음, API/AI/Browser/서비스/DB 쓰기 없음'}


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def check(name, value):
    checks.append({'check':name,'status':'PASS' if bool(value) else 'FAIL'})


def need(value):
    if value is None:
        raise ValueError('TARGET_MISSING')
    return value


def baselines():
    paths = [
        'integration-concept-01/independent-ai-metadata-20260921T124354Z.json',
        'integration-concept-01/independent-operations-metadata-20260921T125136Z.json',
        'integration-concept-02/independent-ai-metadata-20260921T124410Z.json',
        'integration-concept-03/actual-ai.json',
        'integration-concept-04/independent-metadata-http.json',
        'integration-concept-05/independent-pair-metadata.json',
        'integration-concept-05/independent-operations-metadata.json',
    ]
    rows = {}
    files = []
    for relative in paths:
        path = ROOT/'execute/workHitory'/relative
        data = path.read_bytes(); document = json.loads(data)
        files.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest()})
        items = document if isinstance(document,list) else document.get('submissions',[])
        if isinstance(document,dict) and 'retry' in document:
            items = [*items,document['retry']]
        for item in items:
            if item.get('snapshot_sha256'):
                rows[item['submission_id']] = {'submission_id':item['submission_id'],'snapshot_sha256':item['snapshot_sha256'],
                    'result_sha256':item.get('result_sha256'),'source':str(path.relative_to(ROOT))}
    return list(rows.values()), files


def main():
    existing = json.loads((OUT/'existing-metadata.json').read_text())['existing_boundary']
    prior, source_files = baselines()
    report['baseline_files'] = source_files
    report['new_snapshot_baseline'] = {'sha256':EXPECTED_SHA,'source':'execute/workHitory/queued-browser/browser.md root 실제 apply 기록 + 생성 감사 after_data',
                                      'browser_record_sha256':hashlib.sha256((OUT/'browser.md').read_bytes()).hexdigest()}
    value = dotenv_values(ROOT/'.local/runtime.env')['STORELOOP_TEST_DATABASE_URL']
    url = make_url(value)
    if url.host not in ('127.0.0.1','localhost') or url.port != 55432 or url.database != 'storeloop_test':
        raise ValueError('TARGET_MISMATCH')
    engine = create_engine(value,hide_parameters=True,connect_args={'options':'-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('database_read_only',conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on')
        with Session(bind=conn,autoflush=False) as db:
            sub=need(db.get(Submission,SUBMISSION));job=need(db.get(AnalysisJob,JOB))
            context=need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == SUBMISSION)))
            audit=need(db.get(AuditEvent,AUDIT))
            attempts=list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id == JOB)))
            count=db.scalar(select(func.count()).select_from(ReviewResult).where(ReviewResult.submission_id == SUBMISSION))
            check('mock_fixture_identity_and_queue_timeout',job.submission_id == SUBMISSION and job.is_fixture
                  and sub.source_kind == 'seed_demo' and sub.question.startswith('[Mock 장기 대기 UI 검수]')
                  and job.status == 'failed' and job.error_code == 'QUEUE_TIMEOUT' and job.enqueue_generation == 1)
            check('exactly_one_initial_expired_attempt',len(attempts) == 1 and attempts[0].attempt_number == 1
                  and attempts[0].status == 'expired' and attempts[0].error_code == 'QUEUE_TIMEOUT'
                  and attempts[0].id == job.current_attempt_id)
            a=attempts[0]
            check('attempt_was_not_started_or_claimed',a.started_at is None and a.worker_id is None
                  and a.deadline_at is None and a.lease_expires_at is None and a.heartbeat_at is None
                  and a.requested_by_id is None and job.started_at is None)
            check('no_result_applied_or_created',not a.result_applied and count == 0)
            check('timeout_happened_after_queue_deadline',a.finished_at == job.finished_at and job.finished_at >= job.queue_deadline_at
                  and a.queued_at == job.queued_at and job.queue_deadline_at > job.queued_at)
            check('snapshot_same_as_apply_and_creation_audit',digest(context.snapshot) == context.snapshot_sha256 == EXPECTED_SHA
                  and audit.after_data.get('snapshot_sha256') == EXPECTED_SHA
                  and audit.action == 'qa.queued_fixture.create' and audit.target_id == SUBMISSION)
            check('creation_audit_still_mock',audit.after_data.get('is_fixture') is True and audit.after_data.get('source_kind') == 'seed_demo'
                  and audit.after_data.get('job_id') == str(JOB) and audit.outcome == 'succeeded')
            report['fixture']={'submission_id':str(SUBMISSION),'job_id':str(JOB),'status':job.status,'error_code':job.error_code,
                'is_fixture':job.is_fixture,'source_kind':sub.source_kind,'snapshot_sha256':context.snapshot_sha256,
                'created_at':sub.created_at.isoformat(),'queued_at':job.queued_at.isoformat(),'queue_deadline_at':job.queue_deadline_at.isoformat(),
                'finished_at':job.finished_at.isoformat(),'review_count':count,'attempt_count':len(attempts),
                'attempt':{'id':str(a.id),'number':a.attempt_number,'status':a.status,'error_code':a.error_code,
                           'started_at':None,'worker_id':None,'result_applied':a.result_applied,'finished_at':a.finished_at.isoformat()},
                'ai_input_counts':{k:len(context.snapshot[k]) for k in ('photos','guidelines','references')},
                'new_ai_call_evidence':'점유/시작/worker/lease/heartbeat 없음 + QUEUE_TIMEOUT expired; 결과0. 외부 모델 서버 로그 직접 계수는 수행하지 않음'}
            old=need(db.get(AnalysisJob,UUID(existing['job_id'])))
            old_context=need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == old.submission_id)))
            old_attempts=db.scalar(select(func.count()).select_from(AnalysisAttempt).where(AnalysisAttempt.job_id == old.id))
            old_reviews=db.scalar(select(func.count()).select_from(ReviewResult).where(ReviewResult.submission_id == old.submission_id))
            check('original_boundary_status_counts_snapshot_preserved',old.status == existing['status'] and old.error_code == existing['error_code']
                  and old_attempts == existing['attempt_count'] and old_reviews == existing['review_count']
                  and old_context.snapshot_sha256 == existing['snapshot_sha256'] == digest(old_context.snapshot))
            report['original_boundary']={'submission_id':str(old.submission_id),'job_id':str(old.id),'status':old.status,
                'attempt_count':old_attempts,'review_count':old_reviews,'snapshot_sha256':old_context.snapshot_sha256}
            preserved=[]
            for item in prior:
                sid=UUID(item['submission_id']);c=need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == sid)))
                r=need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id == sid)))
                j=need(db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == sid)))
                snapshot_ok=c.snapshot_sha256 == item['snapshot_sha256'] == digest(c.snapshot)
                result_ok=digest(r.result) == item['result_sha256'] if item['result_sha256'] else None
                check(str(sid)+':existing_ai_record_preserved',snapshot_ok and result_ok is not False and j.status == 'succeeded' and r.source_kind == 'real_ai')
                preserved.append({**item,'snapshot_preserved':snapshot_ok,'result_preserved':result_ok,'job_status':j.status,'source_kind':r.source_kind})
            report['preserved_ai_records']=preserved
            check('no_pending_orm_writes',not db.new and not db.dirty and not db.deleted)
    engine.dispose()
    report['status']='PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL'


if __name__ == '__main__':
    try:
        main()
    except Exception:
        report.update(status='FAIL',failure='비밀·본문 보호를 위해 예외 원문 미기록')
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    path=OUT/'independent-metadata.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c['check'] for c in checks if c['status']=='FAIL'],
                      'preserved_ai_records':len(report.get('preserved_ai_records',[])),'evidence':str(path.relative_to(ROOT))},ensure_ascii=False))
    if report['status']=='FAIL':
        raise SystemExit(1)
