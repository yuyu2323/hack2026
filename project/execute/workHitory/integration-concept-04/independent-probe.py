"""시안04의 지정 이력과 별도 HTTP 세션만 읽어 보조 증거를 남긴다."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
import httpx
from dotenv import dotenv_values
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import (Account, AnalysisAttempt, AnalysisContext, AnalysisJob,
    GuidelineVersion, MediaAsset, ReferencePhoto, ReviewResult, Store, StoreOwnerMapping,
    Submission, SubmissionPhoto)
from packages.review_contract.validation import derive_metrics, validate_result

OUT = ROOT / 'execute/workHitory/integration-concept-04'
FIRST = UUID('e447d4e9-54c0-4c85-a0d6-20597b92d0ba')
CHILD = UUID('80d35004-ef2b-4d18-8618-f2199b6878a2')
RETRY = UUID('667d69ab-2eca-565b-b5d7-7b2736b2b57c')
BASE = 'http://127.0.0.1:5176'
checks = []
report = {'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'RUNNING',
          'scope': '독립 READ ONLY DB 메타데이터·Vite 경유 HTTP; 브라우저 E04와 별도',
          'checks': checks, 'submissions': [], 'http': [], 'sessions': []}
stage = 'prepare'

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def check(name, condition):
    checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL'})
    return bool(condition)

def need(value):
    if not value:
        raise ValueError('필수 대상이 없습니다.')
    return value

def submission_metadata(db, ident):
    submission = need(db.get(Submission, ident))
    context = need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == ident)))
    job = need(db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == ident)))
    review = need(db.scalar(select(ReviewResult).where(ReviewResult.submission_id == ident)))
    attempts = list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id == job.id).order_by(AnalysisAttempt.attempt_number)))
    snapshot = context.snapshot
    check(f'{ident}:snapshot_digest', digest(snapshot) == context.snapshot_sha256)
    check(f'{ident}:success_and_real_ai', job.status == 'succeeded' and review.source_kind == 'real_ai')
    check(f'{ident}:applied_attempt', review.attempt_id == job.current_attempt_id
          and sum(a.result_applied for a in attempts) == 1
          and any(a.id == review.attempt_id and a.status == 'succeeded' and a.result_applied for a in attempts))
    try:
        validated = validate_result(review.result, snapshot)
        metrics = derive_metrics(validated, snapshot)
        check(f'{ident}:result_schema_references', True)
        check(f'{ident}:derived_metrics', all((float(getattr(review, k)) if isinstance(v,float) else getattr(review,k)) == v for k, v in metrics.items()))
    except Exception:
        check(f'{ident}:result_schema_references', False)
    references = []
    for ref in snapshot['references']:
        row = need(db.get(ReferencePhoto, UUID(ref['reference_id'])))
        media = need(db.get(MediaAsset, row.photo_id))
        check(f'{ident}:reference:{row.id}:snapshot_media_hash',
              str(row.photo_id) == ref['photo_id'] and media.sha256 == ref['sha256'])
        references.append({'reference_id': str(row.id), 'lineage_id': str(row.lineage_id),
            'version': row.version, 'active_now': row.is_active, 'photo_id': str(media.id),
            'snapshot_sha256': ref['sha256'], 'media_sha256': media.sha256})
    for guideline in snapshot['guidelines']:
        row = need(db.get(GuidelineVersion, UUID(guideline['version_id'])))
        check(f'{ident}:guideline:{row.id}:immutable_version',
              str(row.guideline_id) == guideline['guideline_id'] and row.version == guideline['version']
              and row.text == guideline['text'] and row.created_at <= submission.created_at)
    meta = {'submission_id': str(ident), 'parent_submission_id': str(submission.parent_submission_id) if submission.parent_submission_id else None,
            'job_id': str(job.id), 'review_id': str(review.id), 'job_status': job.status,
            'current_attempt_id': str(job.current_attempt_id), 'review_attempt_id': str(review.attempt_id),
            'review_source_kind': review.source_kind, 'snapshot_sha256': context.snapshot_sha256,
            'result_sha256': digest(review.result), 'submitted_at': submission.created_at.isoformat(),
            'counts': {'photos': len(snapshot['photos']), 'guidelines': len(snapshot['guidelines']), 'references': len(references)},
            'guidelines': [{k:g[k] for k in ('guideline_id','version_id','version','rule_key','level')} for g in snapshot['guidelines']],
            'qa04_candidates': [{k:g[k] for k in ('guideline_id','version_id','version','rule_key','level','selected')} for g in snapshot['candidate_guidelines'] if g['rule_key'] == 'qa04_labels'],
            'photos': [{**{k:p[k] for k in ('photo_id','position','sha256')},'media_id':p.get('media_id',p['photo_id'])} for p in snapshot['photos']],
            'references': references, 'is_fixture': job.is_fixture,
            'attempts': [{'attempt_id':str(a.id),'number':a.attempt_number,'status':a.status,'error_code':a.error_code,'result_applied':a.result_applied} for a in attempts]}
    return meta, submission, context, review

def request_check(client, role, path, expected, expected_hash=None):
    response = client.get(path)
    item = {'role':role,'method':'GET','path':path,'status':response.status_code,'expected':expected}
    valid = response.status_code == expected
    if expected in (403,404):
        try:
            body = response.json()
            item['error_code'] = body.get('error',{}).get('code')
            item['business_body_absent'] = set(body) <= {'error','request_id'} and item['error_code'] == ('FORBIDDEN' if expected == 403 else 'NOT_FOUND')
        except Exception:
            item['business_body_absent'] = False
        valid = valid and item['business_body_absent']
    elif expected == 200 and path.startswith('/api/media/'):
        item['content_type'] = response.headers.get('content-type','')
        valid = valid and item['content_type'].startswith('image/') and bool(response.content)
        if expected_hash:
            item['sha256'] = hashlib.sha256(response.content).hexdigest()
            valid = valid and item['sha256'] == expected_hash
    item['result'] = 'PASS' if valid else 'FAIL'
    report['http'].append(item)
    check(f'http:{role}:{path}', valid)
    return response

def main():
    global stage
    stage = 'read_only_metadata'
    values = dotenv_values(ROOT / '.local/runtime.env')
    url = need(values.get('STORELOOP_TEST_DATABASE_URL'))
    parsed = make_url(url)
    need(parsed.host in ('127.0.0.1','localhost') and parsed.port == 55432 and parsed.database == 'storeloop_test')
    engine = create_engine(url, hide_parameters=True, connect_args={'options':'-c default_transaction_read_only=on -c statement_timeout=10000'})
    private = {}
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('database_transaction_read_only', conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on')
        with Session(bind=conn, autoflush=False) as db:
            retry = need(db.get(AnalysisJob, RETRY))
            report['retry_job_submission_id'] = str(retry.submission_id)
            for ident in (FIRST, CHILD, retry.submission_id):
                meta, submission, context, review = submission_metadata(db, ident)
                report['submissions'].append(meta)
                private[ident] = (submission, context, review, meta)
            first, first_context, first_review, first_meta = private[FIRST]
            child, child_context, child_review, child_meta = private[CHILD]
            check('child_parent_submission', child.parent_submission_id == FIRST and first.parent_submission_id is None)
            previous = child_context.snapshot.get('previous_review')
            check('previous_review_exact_parent', bool(previous) and previous['submission_id'] == str(FIRST)
                  and previous['review_id'] == str(first_review.id) and previous['criteria'] == first_review.result['criteria'])
            old_rule = [g for g in first_context.snapshot['guidelines'] if g['rule_key']=='qa04_labels']
            new_rule = [g for g in child_context.snapshot['guidelines'] if g['rule_key']=='qa04_labels']
            check('qa04_labels_v1_to_v2', len(old_rule)==len(new_rule)==1 and old_rule[0]['version']==1
                  and new_rule[0]['version']==2 and old_rule[0]['guideline_id']==new_rule[0]['guideline_id'])
            check('qa04_category_precedence', all(len(meta['qa04_candidates'])==4
                  and len([g for g in meta['qa04_candidates'] if g['selected'] and g['level']=='CATEGORY'])==1
                  and sum(g['selected'] for g in meta['qa04_candidates'])==1 for meta in (first_meta,child_meta)))
            changed = []
            for before in first_meta['references']:
                for after in child_meta['references']:
                    if before['lineage_id'] == after['lineage_id'] and before['version'] != after['version']:
                        changed.append({'lineage_id':before['lineage_id'],'before':before,'after':after})
            report['reference_changes'] = changed
            check('reference_v1_v2_hash_replacement', len(changed)==1 and changed[0]['before']['version']==1
                  and changed[0]['after']['version']==2 and changed[0]['before']['snapshot_sha256'] != changed[0]['after']['snapshot_sha256']
                  and not changed[0]['before']['active_now'] and changed[0]['after']['active_now'])
            retried = private[retry.submission_id][3]
            check('retry_first_failure_preserved_second_applied', len(retried['attempts'])==2
                  and retried['attempts'][0]['number']==1 and retried['attempts'][0]['status'] in ('failed','expired')
                  and retried['attempts'][0]['error_code'] is not None and not retried['attempts'][0]['result_applied']
                  and retried['attempts'][1]['number']==2 and retried['attempts'][1]['status']=='succeeded'
                  and retried['attempts'][1]['result_applied'])
            root_evidence = json.loads((OUT/'actual-ai.json').read_text())
            for meta in (first_meta,child_meta):
                old = next((r for r in root_evidence if r['submission_id']==meta['submission_id']),None)
                check(meta['submission_id']+':matches_recorded_snapshot_hash', old is not None and old['snapshot_sha256']==meta['snapshot_sha256'])
            owner = need(db.scalar(select(Account).where(Account.login_id=='owner.north')))
            southern = need(db.scalar(select(Account).where(Account.login_id=='regional.south')))
            owner_stores = set(db.scalars(select(StoreOwnerMapping.store_id).where(StoreOwnerMapping.account_id==owner.id,StoreOwnerMapping.ended_at.is_(None))))
            north_store = need(db.get(Store,first.store_id))
            check('live_scope_setup', first.store_id in owner_stores and north_store.region_id != southern.region_id)
            south_submission = need(db.scalar(select(Submission).join(Store).where(Store.region_id==southern.region_id,Submission.source_kind=='seed_demo').order_by(Submission.created_at,Submission.id).limit(1)))
            south_photo = need(db.scalar(select(SubmissionPhoto).where(SubmissionPhoto.submission_id==south_submission.id).order_by(SubmissionPhoto.position).limit(1)))
            # 합성 제출은 같은 MediaAsset을 여러 지역에서 재사용할 수 있다.
            # 북부에도 연결된 사진의 200을 권한 결함으로 오인하지 않는다.
            south_media_has_north_link = db.scalar(select(SubmissionPhoto.id).join(Submission).where(
                Submission.store_id.in_(owner_stores), SubmissionPhoto.media_id==south_photo.media_id).limit(1)) is not None
            north_photo = first_meta['photos'][0]['media_id']
            north_media = need(db.get(MediaAsset,UUID(north_photo)))
            check('north_media_target_is_real_snapshot_asset',north_media.sha256==first_meta['photos'][0]['sha256'])
            targets={'north_submission':str(FIRST),'north_photo':north_photo,'south_submission':str(south_submission.id),'south_photo':str(south_photo.media_id)}
            report['scope_target_ids']=targets
            report['southern_seed_photo_shared_with_north'] = south_media_has_north_link
    engine.dispose()
    print(json.dumps({'retry_job_id':str(RETRY),'submission_id':report['retry_job_submission_id'],'metadata_checks':len(checks)},ensure_ascii=False),flush=True)

    stage = 'own_http_sessions'
    credentials = json.loads((ROOT/'.local/demo-credentials').read_text())
    for role in ('operator.demo','owner.north','regional.south'):
        session_record={'login_id':role,'csrf_status':None,'login_status':None,'logout_status':None}
        report['sessions'].append(session_record)
        with httpx.Client(base_url=BASE,trust_env=False,timeout=20) as client:
            csrf=None
            try:
                response=client.get('/api/auth/csrf');session_record['csrf_status']=response.status_code
                need(response.status_code==200);csrf=response.json()['csrf_token']
                response=client.post('/api/auth/login',json={'login_id':role,'password':credentials[role]['password']},
                    headers={'Origin':BASE,'X-CSRF-Token':csrf})
                session_record['login_status']=response.status_code
                need(response.status_code==200);csrf=response.json()['csrf_token']
                if role=='operator.demo':
                    for path in (f"/api/submissions/{FIRST}",f"/api/media/{north_photo}",f"/api/media/{north_photo}?variant=thumbnail",'/api/notifications'):
                        request_check(client,role,path,403)
                elif role=='owner.north':
                    request_check(client,role,f'/api/submissions/{FIRST}',200)
                    request_check(client,role,f'/api/submissions/{CHILD}',200)
                    request_check(client,role,f'/api/media/{north_photo}',200,first_meta['photos'][0]['sha256'])
                    request_check(client,role,f'/api/media/{north_photo}?variant=thumbnail',200)
                    request_check(client,role,f"/api/submissions/{targets['south_submission']}",404)
                    if not report['southern_seed_photo_shared_with_north']:
                        for path in (f"/api/media/{targets['south_photo']}",f"/api/media/{targets['south_photo']}?variant=thumbnail"):
                            request_check(client,role,path,404)
                    for side in ('before','after'):
                        ref=report['reference_changes'][0][side]
                        request_check(client,role,f"/api/media/{ref['photo_id']}",200,ref['snapshot_sha256'])
                    response=request_check(client,role,f'/api/submissions/{CHILD}/comparison',200)
                    body=response.json()
                    changed_rule=next((c for c in body.get('criteria',[]) if c['rule_key']=='qa04_labels'),None)
                    check('http_comparison_changed_rule_unavailable', bool(changed_rule) and changed_rule['criterion_changed'] and changed_rule['change']=='unavailable')
                else:
                    request_check(client,role,f"/api/submissions/{targets['south_submission']}",200)
                    for path in (f'/api/submissions/{FIRST}',f'/api/media/{north_photo}',f'/api/media/{north_photo}?variant=thumbnail'):
                        request_check(client,role,path,404)
            finally:
                if csrf is not None:
                    response=client.post('/api/auth/logout',json={},headers={'Origin':BASE,'X-CSRF-Token':csrf})
                    session_record['logout_status']=response.status_code
                    check('logout:'+role,response.status_code==204)
    report['status']='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL'

try:
    main()
except Exception:
    report['status']='FAIL'
    report['failure_stage']=stage
    report['failure_detail']='본문·자격값 보호를 위해 예외 원문은 저장하지 않음'
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    path=OUT/'independent-metadata-http.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    path.chmod(0o600)
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed_checks':[c['check'] for c in checks if c['status']=='FAIL'],'http_checks':len(report['http']),'evidence':str(path.relative_to(ROOT))},ensure_ascii=False))
    if report['status'] != 'PASS':
        raise SystemExit(1)
