"""시안05 운영 변경·재처리의 상태와 계측 메타데이터만 읽는다."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
ROOT=Path.cwd()
sys.path.insert(0,str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine,or_,select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import (Account,AnalysisAttempt,AnalysisContext,AnalysisJob,AuditEvent,Category,
    OFCStoreMapping,ReviewResult,Store,StoreOwnerMapping)
from packages.review_contract.validation import validate_result,derive_metrics

OUT=ROOT/'execute/workHitory/integration-concept-05'
ACCOUNT=UUID('b979fd3d-661c-45eb-8c4d-f3c1dd155aa9')
JOB=UUID('aa73ad7e-9d08-5a5b-b035-96941a217621')
SUBMISSION=UUID('96165c7c-53c9-5ded-9f99-f9ee67ec2c86')
checks=[]
report={'status':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),'checks':checks,
        'scope':'READ ONLY metadata; 업무 본문/비밀/사진 및 새 HTTP/AI 호출 없음'}
def need(v):
    if not v: raise ValueError('지정 자료 없음')
    return v
def check(name,value):
    checks.append({'check':name,'status':'PASS' if value else 'FAIL'})
def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ms(start,end):
    return round((end-start).total_seconds()*1000) if start and end else None
def audit_meta(row):
    allowed={'id','role','region_id','is_active','version','store_ids','ended_mapping_ids','ofc_id'}
    return {'id':str(row.id),'action':row.action,'target_type':row.target_type,'target_id':str(row.target_id),
            'actor_id':str(row.actor_id),'created_at':row.created_at.isoformat(),'outcome':row.outcome,
            'reason_present':bool(row.reason.strip()),'request_id_present':bool(row.request_id),
            'before':{k:v for k,v in row.before_data.items() if k in allowed},
            'after':{k:v for k,v in row.after_data.items() if k in allowed}}
def main():
    url=need(dotenv_values(ROOT/'.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL'))
    parsed=make_url(url);need(parsed.host in ('127.0.0.1','localhost') and parsed.port==55432 and parsed.database=='storeloop_test')
    engine=create_engine(url,hide_parameters=True,connect_args={'options':'-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn,conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('database_read_only',conn.exec_driver_sql('SHOW transaction_read_only').scalar()=='on')
        with Session(bind=conn,autoflush=False) as db:
            account=need(db.get(Account,ACCOUNT))
            owners=list(db.scalars(select(StoreOwnerMapping).where(StoreOwnerMapping.account_id==ACCOUNT)))
            ofcs=list(db.scalars(select(OFCStoreMapping).where(OFCStoreMapping.account_id==ACCOUNT)))
            audit=list(db.scalars(select(AuditEvent).where(AuditEvent.target_type=='account',AuditEvent.target_id==ACCOUNT).order_by(AuditEvent.created_at)))
            claim=list(db.scalars(select(AuditEvent).where(AuditEvent.action=='stores.claim',AuditEvent.actor_id==ACCOUNT).order_by(AuditEvent.created_at)))
            report['account']={'id':str(account.id),'version':account.version,'role':account.role,'region_id':str(account.region_id) if account.region_id else None,
                'is_active':account.is_active,'owner_mapping_count':len(owners),'active_owner_mapping_count':sum(m.ended_at is None for m in owners),
                'ofc_mapping_count':len(ofcs),'active_ofc_mapping_count':sum(m.ended_at is None for m in ofcs),
                'ofc_mappings':[{'id':str(m.id),'store_id':str(m.store_id),'created_at':m.created_at.isoformat(),'ended_at':m.ended_at.isoformat() if m.ended_at else None} for m in ofcs]}
            check('current_v8_active_owner_null_region_unmapped',account.version==8 and account.role=='store_owner'
                  and account.region_id is None and account.is_active and all(m.ended_at is not None for m in owners+ofcs))
            v6=next((a for a in audit if a.after_data.get('version')==6),None)
            v7=next((a for a in audit if a.after_data.get('version')==7),None)
            check('v6_ofc_audit',v6 is not None and v6.after_data.get('role')=='ofc' and v6.after_data.get('region_id') is not None)
            check('v7_owner_ends_exactly_one_mapping',v7 is not None and v7.before_data.get('role')=='ofc'
                  and v7.after_data.get('role')=='store_owner' and len(v7.after_data.get('ended_mapping_ids',[]))==1)
            target=[m for m in ofcs if db.get(Store,m.store_id).name=='새봄로점']
            check('new_ofc_claim_then_ended',len(target)==1 and target[0].ended_at is not None and any(a.target_id==target[0].store_id
                  and a.after_data.get('ofc_id')==str(ACCOUNT) and v6.created_at<=a.created_at<=v7.created_at for a in claim)
                  and str(target[0].id) in v7.after_data['ended_mapping_ids'])
            report['account_audits']=[audit_meta(a) for a in audit]
            report['claim_audits']=[audit_meta(a) for a in claim]
            check('account_audit_integrity',bool(audit) and all(a.outcome=='succeeded' and a.reason.strip() and a.request_id for a in audit+claim))
            category=need(db.scalar(select(Category).where(Category.code=='qa05_test_category')))
            category_audits=list(db.scalars(select(AuditEvent).where(AuditEvent.target_type=='category',AuditEvent.target_id==category.id).order_by(AuditEvent.created_at)))
            report['category']={'id':str(category.id),'code':category.code,'version':category.version,'is_active':category.is_active,
                'name_contains_completed_marker':'검증완료' in category.name.replace(' ',''),'audits':[audit_meta(a) for a in category_audits]}
            check('category_created_renamed_inactive',not category.is_active and report['category']['name_contains_completed_marker']
                  and any(a.action=='categories.create' for a in category_audits)
                  and any(a.action=='categories.update' and a.before_data.get('name')!=a.after_data.get('name') for a in category_audits)
                  and any(a.after_data.get('is_active') is False for a in category_audits))
            job=need(db.get(AnalysisJob,JOB));check('retry_job_submission',job.submission_id==SUBMISSION)
            attempts=list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id==JOB).order_by(AnalysisAttempt.attempt_number)))
            review=need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id==SUBMISSION)))
            context=need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id==SUBMISSION)))
            check('failed_attempt_preserved_11_seconds',len(attempts)==2 and attempts[0].attempt_number==1
                  and attempts[0].status=='failed' and attempts[0].error_code=='AI_UNAVAILABLE'
                  and not attempts[0].result_applied and ms(attempts[0].started_at,attempts[0].finished_at)==11000)
            check('second_success_is_only_applied_result',len(attempts)==2 and attempts[1].attempt_number==2
                  and attempts[1].status=='succeeded' and attempts[1].error_code is None and attempts[1].result_applied
                  and review.attempt_id==attempts[1].id==job.current_attempt_id and job.status=='succeeded'
                  and review.source_kind=='real_ai' and job.is_fixture)
            check('retry_snapshot_digest',digest(context.snapshot)==context.snapshot_sha256)
            try:
                result=validate_result(review.result,context.snapshot);metrics=derive_metrics(result,context.snapshot)
                check('retry_result_contract_and_metrics',all((float(getattr(review,k)) if isinstance(v,float) else getattr(review,k))==v for k,v in metrics.items()))
            except Exception:
                check('retry_result_contract_and_metrics',False)
            report['retry']={'job_id':str(job.id),'submission_id':str(SUBMISSION),'review_id':str(review.id),'is_fixture':job.is_fixture,
                'source_kind':review.source_kind,'status':job.status,'model_ms':review.latency_ms,'snapshot_sha256':context.snapshot_sha256,
                'result_sha256':digest(review.result),'review_created_at':review.created_at.isoformat(),
                'attempts':[{'number':a.attempt_number,'id':str(a.id),'status':a.status,'error_code':a.error_code,'result_applied':a.result_applied,
                    'queued_at':a.queued_at.isoformat(),'started_at':a.started_at.isoformat() if a.started_at else None,
                    'finished_at':a.finished_at.isoformat() if a.finished_at else None,'heartbeat_at':a.heartbeat_at.isoformat() if a.heartbeat_at else None,
                    'deadline_at':a.deadline_at.isoformat() if a.deadline_at else None,'queue_ms':ms(a.queued_at,a.started_at),'run_ms':ms(a.started_at,a.finished_at)} for a in attempts]}
            delta=ms(attempts[1].started_at,attempts[1].finished_at)-review.latency_ms
            report['timing']={'model_clock':'time.monotonic in AI adapter','attempt_clock':'datetime.now(UTC) in worker',
                'run_minus_model_ms':delta,'nested_elapsed_relation_observed':delta>=0,
                'classification':'CONSISTENT_ORDER' if delta>=0 else 'CLOCK_BASIS_ANOMALY_UNRESOLVED',
                'cause_proven':False,'excluded_from_new_submission_latency':True}
            check('retry_times_match_root_export',review.latency_ms==50635 and ms(attempts[1].queued_at,attempts[1].started_at)==520
                  and ms(attempts[1].started_at,attempts[1].finished_at)==48786)
            baseline=json.loads((OUT/'independent-pair-metadata.json').read_text())
            preserved=[]
            for item in baseline['submissions']:
                ident=UUID(item['submission_id'])
                c=need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id==ident)))
                r=need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id==ident)))
                valid=c.snapshot_sha256==item['snapshot_sha256'] and digest(c.snapshot)==item['snapshot_sha256'] and digest(r.result)==item['result_sha256']
                check(item['submission_id']+':first_child_hash_preserved',valid)
                preserved.append({'submission_id':item['submission_id'],'snapshot_sha256':c.snapshot_sha256,'result_sha256':digest(r.result),'preserved':valid})
            report['first_child_preserved']=preserved
    engine.dispose()
    report['status']='FUNCTIONAL_PASS_WITH_TIMING_ANOMALY' if all(c['status']=='PASS' for c in checks) else 'FAIL'
try:
    main()
except Exception:
    report['status']='FAIL'
    report['failure_detail']='본문·자격값 보호를 위해 예외 원문 미기록'
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    path=OUT/'independent-operations-metadata.json'
    if path.exists():path=path.with_name(path.stem+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed_checks':[c['check'] for c in checks if c['status']=='FAIL'],
        'account':report.get('account'),'timing':report.get('timing'),'evidence':str(path.relative_to(ROOT))},ensure_ascii=False))
    if report['status']=='FAIL':raise SystemExit(1)
