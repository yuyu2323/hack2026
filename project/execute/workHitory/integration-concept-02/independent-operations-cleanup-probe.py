"""QA02 후속 기준·공지 비활성 정리를 독립 READ ONLY로 확인한다."""
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
from server.core.models import AnalysisContext, Announcement, AuditEvent, Guideline, GuidelineVersion, ReviewResult

OUT = ROOT / 'execute/workHitory/integration-concept-02'
UPPER = ['2d4ea8b1-116c-430e-8e06-e80ba477484b', '2089bf7c-3836-441c-9d00-7a32eb6a0436', 'd422d014-58d6-4d90-ae76-d4502709dad7']
CATEGORY = UUID('871e8d30-b380-4050-b81a-1594f4c1eac1')
NOTICE = UUID('8364b4a5-9704-4fa1-b5e7-300fad961aed')
checks = []
report = {'status':'RUNNING', 'checked_at':datetime.now(timezone.utc).isoformat(), 'checks':checks, 'scope':'후속 정리 READ ONLY; Browser 재실행 없음'}


def check(name, value):
    checks.append({'check':name,'status':'PASS' if value else 'FAIL'})


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def audit_meta(row):
    keys = {'version','is_active','starts_at','ends_at'}
    return {'id':str(row.id), 'action':row.action, 'created_at':row.created_at.isoformat(), 'outcome':row.outcome,
            'reason_present':bool(row.reason.strip()),'request_id_present':bool(row.request_id),
            'before':{k:v for k,v in row.before_data.items() if k in keys}, 'after':{k:v for k,v in row.after_data.items() if k in keys}}


def main():
    value = dotenv_values(ROOT/'.local/runtime.env')['STORELOOP_TEST_DATABASE_URL']
    url = make_url(value)
    if url.host not in ('127.0.0.1','localhost') or url.port != 55432 or url.database != 'storeloop_test':
        raise ValueError('TARGET_MISMATCH')
    engine = create_engine(value,hide_parameters=True,connect_args={'options':'-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('read_only',conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on')
        with Session(bind=conn,autoflush=False) as db:
            rules=[]
            for key in UPPER:
                row=db.get(Guideline,UUID(key))
                versions=list(db.scalars(select(GuidelineVersion).where(GuidelineVersion.guideline_id == row.id)))
                audit=list(db.scalars(select(AuditEvent).where(AuditEvent.target_type == 'guideline', AuditEvent.target_id == row.id).order_by(AuditEvent.created_at)))
                check(key+':inactive_without_content_revision',not row.is_active and row.current_version == 1 and len(versions) == 1)
                check(key+':deactivation_audit',any(a.before_data.get('is_active') is True and a.after_data.get('is_active') is False
                                                  and a.before_data.get('version') == a.after_data.get('version') == 1 for a in audit))
                rules.append({'id':key,'level':row.level,'is_active':row.is_active,'content_version':row.current_version,
                              'state_version':row.version,'audits':[audit_meta(a) for a in audit]})
            row=db.get(Guideline,CATEGORY)
            check('category_v2_remains_active',row.is_active and row.current_version == 2)
            report['rules']={'upper':rules,'category':{'id':str(row.id),'is_active':row.is_active,'content_version':row.current_version}}
            notice=db.get(Announcement,NOTICE)
            audits=list(db.scalars(select(AuditEvent).where(AuditEvent.target_type == 'announcement', AuditEvent.target_id == NOTICE).order_by(AuditEvent.created_at)))
            check('announcement_v2_inactive_expected_title',notice.version == 2 and not notice.is_active and notice.title == 'QA02 오늘 할 일 시연 안내')
            check('announcement_published_before_registration',notice.starts_at <= notice.created_at and (notice.ends_at is None or notice.ends_at > notice.created_at))
            check('announcement_creation_then_deactivation_audit',len(audits) == 2 and audits[0].action == 'announcements.create'
                  and audits[0].after_data.get('version') == 1 and audits[0].after_data.get('is_active') is True
                  and audits[1].before_data.get('version') == 1 and audits[1].before_data.get('is_active') is True
                  and audits[1].after_data.get('version') == 2 and audits[1].after_data.get('is_active') is False)
            report['announcement']={'id':str(notice.id),'version':notice.version,'is_active':notice.is_active,
                'starts_at':notice.starts_at.isoformat(),'ends_at':notice.ends_at.isoformat() if notice.ends_at else None,
                'created_at':notice.created_at.isoformat(),'audits':[audit_meta(a) for a in audits]}
            baseline=json.loads((OUT/'independent-ai-metadata-20260921T124410Z.json').read_text())
            preserved=[]
            for item in baseline['submissions']:
                sid=UUID(item['submission_id']);context=db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == sid))
                review=db.scalar(select(ReviewResult).where(ReviewResult.submission_id == sid))
                matches=context.snapshot_sha256 == item['snapshot_sha256'] == digest(context.snapshot) and digest(review.result) == item['result_sha256']
                check(str(sid)+':unchanged_after_cleanup',matches)
                preserved.append({'submission_id':str(sid),'snapshot_sha256':context.snapshot_sha256,'result_sha256':digest(review.result),'unchanged':matches})
            report['past_records']=preserved
    engine.dispose()
    report['status']='PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL'


if __name__ == '__main__':
    try:
        main()
    except Exception:
        report.update(status='FAIL',failure='민감 오류 원문 미기록')
    path=OUT/'independent-operations-cleanup-metadata.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c['check'] for c in checks if c['status']=='FAIL'],'evidence':str(path.relative_to(ROOT))},ensure_ascii=False))
    if report['status']=='FAIL':
        raise SystemExit(1)
