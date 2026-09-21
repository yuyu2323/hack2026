"""시안05 지정 제출의 DB 메타데이터만 READ ONLY로 검증한다."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

ROOT=Path.cwd()
sys.path.insert(0,str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine,select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import AnalysisAttempt,AnalysisContext,AnalysisJob,GuidelineVersion,MediaAsset,ReferencePhoto,ReviewResult,Submission
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import validate_result,derive_metrics

OUT=ROOT/'execute/workHitory/integration-concept-05'
FIRST=UUID('3fdb0cf3-61da-4008-84c1-79e2a58cde05')
ids=[FIRST]+[UUID(value) for value in sys.argv[1:]]
checks=[]
report={'status':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'submissions':[],
        'scope':'읽기 전용 DB 관찰; 브라우저/HTTP 세션/업무 쓰기/신규 실제 AI 호출 없음'}
def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check(name,value):
    checks.append({'check':name,'status':'PASS' if value else 'FAIL'})
def need(value):
    if not value: raise ValueError('필수 대상 없음')
    return value
def main():
    url=need(dotenv_values(ROOT/'.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL'))
    parsed=make_url(url)
    need(parsed.host in ('127.0.0.1','localhost') and parsed.port==55432 and parsed.database=='storeloop_test')
    engine=create_engine(url,hide_parameters=True,connect_args={'options':'-c default_transaction_read_only=on -c statement_timeout=10000'})
    private={}
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn,conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('read_only_transaction',conn.exec_driver_sql('SHOW transaction_read_only').scalar()=='on')
        with Session(bind=conn,autoflush=False) as db:
            for ident in ids:
                sub=need(db.get(Submission,ident))
                context=need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id==ident)))
                job=need(db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id==ident)))
                review=need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id==ident)))
                attempts=list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id==job.id).order_by(AnalysisAttempt.attempt_number)))
                snap=context.snapshot
                check(f'{ident}:snapshot_sha256',digest(snap)==context.snapshot_sha256)
                check(f'{ident}:succeeded_real_ai',job.status=='succeeded' and review.source_kind=='real_ai' and not job.is_fixture)
                check(f'{ident}:current_applied_attempt',job.current_attempt_id==review.attempt_id
                      and sum(a.result_applied for a in attempts)==1
                      and any(a.id==review.attempt_id and a.status=='succeeded' and a.result_applied for a in attempts))
                ai_input={'schema_version':context.schema_version,'job_id':str(job.id),'attempt_id':str(review.attempt_id),
                          'submission_id':str(ident),**{k:snap[k] for k in ('question','guidelines','photos','references','previous_review')}}
                # DB 연결용 media_id는 실제 worker도 AI strict 입력에서 제외한다.
                ai_input['photos']=[{key:p[key] for key in ('photo_id','position','mime_type','sha256')} for p in snap['photos']]
                try:
                    parsed_input=AnalysisInput.model_validate(ai_input)
                    result=validate_result(review.result,parsed_input)
                    metrics=derive_metrics(result,parsed_input)
                    check(f'{ident}:input_result_schema_and_references',True)
                    check(f'{ident}:stored_metrics',all((float(getattr(review,k)) if isinstance(v,float) else getattr(review,k))==v for k,v in metrics.items()))
                except Exception:
                    check(f'{ident}:input_result_schema_and_references',False)
                photos=[]
                for p in snap['photos']:
                    media=need(db.get(MediaAsset,UUID(p.get('media_id',p['photo_id']))))
                    check(f'{ident}:photo:{p["position"]}:hash',media.sha256==p['sha256'])
                    photos.append({**{k:p[k] for k in ('photo_id','position','sha256')},'media_id':str(media.id)})
                references=[]
                for r in snap['references']:
                    row=need(db.get(ReferencePhoto,UUID(r['reference_id'])))
                    media=need(db.get(MediaAsset,row.photo_id))
                    check(f'{ident}:reference:{row.id}:hash',str(row.photo_id)==r['photo_id'] and media.sha256==r['sha256'])
                    references.append({'reference_id':str(row.id),'lineage_id':str(row.lineage_id),'version':row.version,'active_now':row.is_active,
                                       'photo_id':str(row.photo_id),'sha256':r['sha256']})
                for g in snap['guidelines']:
                    version=need(db.get(GuidelineVersion,UUID(g['version_id'])))
                    check(f'{ident}:guideline:{version.id}:immutable',version.version==g['version'] and str(version.guideline_id)==g['guideline_id']
                          and version.text==g['text'] and version.created_at<=sub.created_at)
                row={'submission_id':str(ident),'parent_submission_id':str(sub.parent_submission_id) if sub.parent_submission_id else None,
                     'job_id':str(job.id),'review_id':str(review.id),'source_kind':review.source_kind,'is_fixture':job.is_fixture,'status':job.status,
                     'model':review.model_name,'prompt_version':review.prompt_version,'schema_version':context.schema_version,
                     'submitted_at':sub.created_at.isoformat(),'model_ms':review.latency_ms,
                     'submit_to_db_ms':round((job.finished_at-sub.created_at).total_seconds()*1000),
                     'snapshot_sha256':context.snapshot_sha256,'result_sha256':digest(review.result),'ai_input_sha256':digest(ai_input),
                     'question_length':len(snap['question']),'question_sha256':hashlib.sha256(snap['question'].encode()).hexdigest(),
                     'counts':{k:len(snap[k]) for k in ('photos','guidelines','references')},
                     'guidelines':[{k:g[k] for k in ('guideline_id','version_id','version','rule_key','level')} for g in snap['guidelines']],
                     'qa05_candidates':[{k:g[k] for k in ('guideline_id','version_id','version','rule_key','level','selected')} for g in snap['candidate_guidelines'] if g['rule_key'].startswith('qa05')],
                     'photos':photos,'references':references,'attempts':[{'number':a.attempt_number,'status':a.status,'error_code':a.error_code,'result_applied':a.result_applied,'attempt_id':str(a.id)} for a in attempts]}
                report['submissions'].append(row)
                private[ident]=(sub,context,review)
            first,first_context,first_review=private[FIRST]
            check('first_has_no_parent',first.parent_submission_id is None and first_context.snapshot['previous_review'] is None)
            root_evidence=OUT/'actual-ai.json'
            if root_evidence.exists():
                exported=json.loads(root_evidence.read_text())
                for row in report['submissions']:
                    matching=next((r for r in exported if r['submission_id']==row['submission_id']),None)
                    if matching is not None:
                        check(row['submission_id']+':matches_root_export',all(matching[k]==row[k] for k in ('job_id','review_id','snapshot_sha256','model_ms'))
                              and matching['photos']==row['counts']['photos'] and matching['criteria']==row['counts']['guidelines']
                              and matching['references']==row['counts']['references'])
            baseline=OUT/'independent-first-metadata.json'
            if len(ids)>1:
                previous=json.loads(baseline.read_text())['submissions'][0]
                current=report['submissions'][0]
                check('first_snapshot_and_result_preserved',all(previous[k]==current[k] for k in ('snapshot_sha256','result_sha256','review_id','job_id')))
                for ident in ids[1:]:
                    child,context,review=private[ident]
                    parent=context.snapshot.get('previous_review')
                    check(f'{ident}:parent_link',child.parent_submission_id==FIRST and bool(parent) and parent['submission_id']==str(FIRST)
                          and parent['review_id']==str(first_review.id) and parent['criteria']==first_review.result['criteria'])
                    old_rule=[g for g in first_context.snapshot['guidelines'] if g['rule_key']=='qa05_labels']
                    new_rule=[g for g in context.snapshot['guidelines'] if g['rule_key']=='qa05_labels']
                    check(f'{ident}:qa05_labels_v1_to_v2',len(old_rule)==len(new_rule)==1 and old_rule[0]['version']==1
                          and new_rule[0]['version']==2 and old_rule[0]['guideline_id']==new_rule[0]['guideline_id'])
                    first_meta=report['submissions'][0]
                    child_meta=next(r for r in report['submissions'] if r['submission_id']==str(ident))
                    check(f'{ident}:category_precedence',all(len(r['qa05_candidates'])==4
                          and sum(g['selected'] for g in r['qa05_candidates'])==1
                          and any(g['selected'] and g['level']=='CATEGORY' for g in r['qa05_candidates']) for r in (first_meta,child_meta)))
                    changed=[{'before':a,'after':b} for a in first_meta['references'] for b in child_meta['references']
                             if a['lineage_id']==b['lineage_id'] and a['version']!=b['version']]
                    report['reference_changes']=changed
                    check(f'{ident}:reference_v1_v2_hash_changed',len(changed)==1 and changed[0]['before']['version']==1
                          and changed[0]['after']['version']==2 and changed[0]['after']['reference_id']=='881d5e08-0690-41c4-8f6d-cf67a5d744fc'
                          and changed[0]['before']['sha256']!=changed[0]['after']['sha256']
                          and not changed[0]['before']['active_now'] and changed[0]['after']['active_now'])
    engine.dispose()
    report['status']='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL'
try:
    main()
except Exception:
    report['status']='FAIL'
    report['failure_detail']='본문·자격값 보호를 위해 예외 원문 미기록'
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    report['exporter_sha256']=hashlib.sha256((ROOT/'scripts/export_acceptance_evidence.py').read_bytes()).hexdigest()
    path=OUT/('independent-pair-metadata.json' if len(ids)>1 else 'independent-first-metadata.json')
    if path.exists():
        path=path.with_name(path.stem+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed_checks':[c['check'] for c in checks if c['status']=='FAIL'],
                      'submissions':[{k:r[k] for k in ('submission_id','job_id','review_id','counts','model_ms','submit_to_db_ms')} for r in report['submissions']],
                      'evidence':str(path.relative_to(ROOT))},ensure_ascii=False))
    if report['status']!='PASS': raise SystemExit(1)
