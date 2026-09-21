"""원래 합성 fixture만 dry-run/명시적 apply로 정정한다. 일반 seed와 분리한다."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID, uuid4, uuid5

from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from dotenv import dotenv_values

from server.business_common import encode
from server.core.config import PROJECT_ROOT
from server.core.db import as_utc, make_engine
from server.core.models import (
    Submission, SubmissionPhoto, AnalysisContext, AnalysisJob, AnalysisAttempt,
    GuidelineVersion, ReviewResult, CriterionEvaluation, ReferencePhoto, MediaAsset,
)
from server.guidelines.resolution import resolve_guidelines
from packages.review_contract.validation import validate_result, derive_metrics

REPAIR_VERSION = 'seed-chronology-20260921-v1'
BASE = datetime(2026,9,21,tzinfo=timezone.utc)
NAMESPACE = UUID('e3359552-691b-5b94-9a80-a46d7a8e12d7')

def ident(kind, code):
    return uuid5(NAMESPACE, kind+':'+str(code))
STORES = [('north','spring-station','봄빛역점'), ('north','bank-road','은행길점'),
          ('north','green-hill','푸른언덕점'), ('south','star-river','별하천점'),
          ('south','sunset-park','노을공원점'), ('south','spring-road','새봄로점')]
QUESTION = '앞줄 정렬과 빈 간격을 어떻게 개선하면 좋을까요?'
V1_TEXT = '음료 앞줄 상품의 앞면을 일정하게 정렬한다.'
V2_TEXT = '병과 캔의 앞면을 정렬하고 앞줄의 간격을 일정하게 유지한다.'
# 최초 시드에서 실제 정규화한 이미지의 고정 지문이다. 변경된 자산은 허용하지 않는다.
MEDIA = {
    'beverage-before-01': ('86d21c85c15d0328e6942a82c7fe0d797d1dbc4584bb320fab4bd80e7e7f4329',2298957),
    'beverage-after-01': ('26f62fc402a8ae76e160b7c63d24432c14534e3a3656bc6e317ad8fe7b9d155f',2117298),
    'beverage-reference-01': ('63c02dac9d0410a8e2b6a03b6668d5b3070baebd76f452cefecbef47964bb5aa',2288160),
    'beverage-reference-02': ('283ab88714aef8521bdb47b1dd79a2afed388fd38b3f9bd1712575271802ea2a',2121384),
    'snack-reference-01': ('8458f5510458ede7ef6e2173e5584a182a77dea321f3e9d83eb96e35a1954c8f',2158105),
    'snack-reference-02': ('15708f4baec41748dc579a017cd2479b044f2a45efc88ee9578b69dd744b63fa',2051568),
}


class RepairConflict(ValueError):
    """원문을 포함하지 않는 정정 거부 사유."""


def digest(value):
    return hashlib.sha256(json.dumps(encode(value), ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def reject(code, row_id):
    raise RepairConflict(f'{code}:{row_id}')


def locked(db, model, row_id):
    row = db.scalar(select(model).where(model.id == row_id).with_for_update().execution_options(populate_existing=True))
    if row is None:
        reject('MISSING_ORIGINAL', row_id)
    return row


def check(row, expected):
    if any(encode(getattr(row, name)) != encode(value) for name, value in expected.items()):
        reject('ORIGINAL_MISMATCH', row.id)


def serialized(row):
    return {column.name:encode(getattr(row, column.name)) for column in row.__table__.columns}


def expected_snapshot(index, sequence, version):
    area, store_code, store_name = STORES[index]
    code = f'{store_code}-{sequence}'
    store_id, category_id = ident('stores',store_code), ident('categories','beverage')
    rules = [('hq-label','label_visibility','HQ','사진에 보이는 선반 라벨이 상품에 가려지지 않아야 한다.',None,None),
             ('hq-facing','facing','HQ','동일 상품의 앞줄이 선반 앞선에 맞게 정렬되어야 한다.',None,None),
             (area+'-facing','facing','REGION','앞줄 상품의 앞면 방향과 간격을 일정하게 맞춘다.',None,None),
             (store_code+'-gap','shelf_gap','STORE','넓은 빈 간격이 보이면 보충하거나 간격을 고르게 조정한다.',str(store_id),None),
             ('beverage-group','category_grouping','CATEGORY','같은 상품군을 묶고 다른 상품군과 구분해 배치한다.',None,str(category_id)),
             ('beverage-facing','facing','CATEGORY',V1_TEXT if version == 1 else V2_TEXT,None,str(category_id))]
    candidates = []
    for rule_code, key, level, text, target_store, target_category in rules:
        revision = version if rule_code == 'beverage-facing' else 1
        candidates.append(dict(guideline_id=str(ident('guidelines',rule_code)),
            version_id=str(ident('guideline_versions',f'{rule_code}-{revision}')), version=revision,
            level=level, rule_key=key, text=text, store_id=target_store, category_id=target_category))
    effective, history = resolve_guidelines(candidates)
    keys = ('guideline_id','version_id','version','level','rule_key','text')
    effective = [{key:item[key] for key in keys} for item in effective]
    history = [{key:item[key] for key in (*keys,'selected','selection_reason')} for item in history]
    photo_code = 'beverage-after-01' if sequence == 1 else 'beverage-before-01'
    references = []
    for position, reference_code in enumerate((['beverage-reference-02'] if index == 0 else [])+['beverage-reference-01'],1):
        references.append(dict(reference_id=str(ident('reference_photos',reference_code)),
            photo_id=str(ident('media_assets',reference_code)), position=position,
            caption='AI 생성 시연 Reference · beverage', mime_type='image/png', sha256=MEDIA[reference_code][0]))
    previous = None
    if sequence == 1:
        parent = f'{store_code}-0'
        parent_snapshot = expected_snapshot(index, 0, 1)
        previous = dict(submission_id=str(ident('submissions',parent)), review_id=str(ident('review_results',parent)),
                        criteria=expected_result(index, 0, parent_snapshot)['criteria'])
    return dict(store={'id':str(store_id),'region_id':str(ident('regions',area)),'name':store_name},
        category={'id':str(category_id),'name':'음료'}, question=QUESTION,
        photos=[dict(photo_id=str(ident('submission_photos',code)),media_id=str(ident('media_assets',photo_code)),
                     position=1,mime_type='image/png',sha256=MEDIA[photo_code][0])],
        candidate_guidelines=history,guidelines=effective,references=references,previous_review=previous)


def expected_result(index, sequence, snapshot):
    criteria = []
    for number, guideline in enumerate(snapshot['guidelines']):
        verdict = 'pass' if sequence == 1 or (number+index+sequence)%3 else 'fail'
        criteria.append({**{key:guideline[key] for key in ['guideline_id','version_id','version','rule_key']},
            'verdict':verdict,'reason':'합성 과거 평가: 진열 기준과 사진을 비교한 시연 결과입니다.',
            'evidence':[{'photo_position':1,'observation':'시연 사진의 앞줄과 선반 간격을 확인했습니다.'}],
            'actions':['앞줄 간격을 고르게 조정해 주세요.'] if verdict == 'fail' else []})
    return dict(schema_version='1.0',question_answer='Mock 과거 평가입니다. 앞줄 간격과 상품군을 기준에 맞춰 정리해 주세요.',
        summary='합성 데이터로 구성한 과거 진열 평가입니다. 실제 AI 분석 결과가 아닙니다.',overall_confidence='medium',criteria=criteria,
        reference_comparisons=[dict(reference_id=ref['reference_id'],verdict='similar' if sequence == 1 else 'different',
                                   photo_positions=[1],observation='합성 시연 비교입니다.') for ref in snapshot['references']],
        limitations=[],ofc_review_required=False,follow_up_comparison='합성 이전 평가와 비교한 개선 시연입니다.' if sequence == 1 else None)


def add_change(changes, row, values):
    if all(encode(getattr(row,key)) == encode(value) for key,value in values.items()):
        return
    before = serialized(row)
    after = dict(before, **encode(values))
    changes.append({'row':row,'values':values,'before':before,
        'report':{'table':row.__tablename__,'id':str(row.id),'before_sha256':digest(before),'after_sha256':digest(after)}})


def build_plan(db):
    changes, changed_submissions = [], 0
    hq_id = ident('accounts','hq.demo')
    for code, (sha, size) in MEDIA.items():
        media = locked(db,MediaAsset,ident('media_assets',code))
        check(media,dict(sha256=sha,byte_size=size,width=1254,height=1254,mime_type='image/png',
            source_kind='ai_generated_demo',uploaded_by_id=hq_id,storage_key=f'{media.id}.png',
            thumbnail_key=f'{media.id}-thumbnail.jpg',created_at=BASE-timedelta(days=70)))
    for revision, text in [(1,V1_TEXT),(2,V2_TEXT)]:
        version = locked(db,GuidelineVersion,ident('guideline_versions',f'beverage-facing-{revision}'))
        check(version,dict(guideline_id=ident('guidelines','beverage-facing'),version=revision,text=text,
            change_reason='합성 시연 기준 '+str(revision),created_by_id=hq_id,
            created_at=BASE-timedelta(days=65 if revision == 1 else 7)))
    for code in [name for name in MEDIA if 'reference' in name]:
        reference = locked(db,ReferencePhoto,ident('reference_photos',code))
        category = code.split('-')[0]
        check(reference,dict(lineage_id=reference.id,version=1,state_version=1,photo_id=ident('media_assets',code),
            category_id=ident('categories',category),store_id=ident('stores','spring-station') if code.endswith('02') else None,
            caption='AI 생성 시연 Reference · '+category,is_active=True,created_by_id=hq_id))
        if as_utc(reference.created_at) not in [BASE-timedelta(days=70),BASE-timedelta(days=65)]:
            reject('REFERENCE_DATE_CHANGED',reference.id)
        if len(list(db.scalars(select(ReferencePhoto.id).where(ReferencePhoto.lineage_id == reference.id)))) != 1:
            reject('REFERENCE_REVISED',reference.id)
        add_change(changes,reference,{'created_at':BASE-timedelta(days=65)})
    for index, (area, store_code, _) in enumerate(STORES):
        for sequence in [1,4]:
            code = f'{store_code}-{sequence}'
            when = BASE-timedelta(days=(55 if index == 5 else 20)-sequence*3+index%2)
            submission = locked(db,Submission,ident('submissions',code))
            check(submission,dict(store_id=ident('stores',store_code),category_id=ident('categories','beverage'),
                submitted_by_id=ident('accounts','owner.'+area),question=QUESTION,source_kind='seed_demo',created_at=when,
                parent_submission_id=ident('submissions',f'{store_code}-0') if sequence == 1 else None))
            if db.scalar(select(Submission.id).where(Submission.parent_submission_id == submission.id).limit(1)):
                reject('EXTERNAL_DEPENDENCY',submission.id)
            context = locked(db,AnalysisContext,ident('analysis_contexts',code))
            check(context,dict(submission_id=submission.id,schema_version='1.0',created_at=when))
            if digest(context.snapshot) != context.snapshot_sha256:
                reject('SNAPSHOT_HASH_MISMATCH',context.id)
            legacy, corrected = expected_snapshot(index,sequence,2), expected_snapshot(index,sequence,1)
            if context.snapshot == legacy:
                original = legacy
            elif context.snapshot == corrected:
                original = corrected
            else:
                reject('SNAPSHOT_ORIGINAL_MISMATCH',context.id)
            photos = list(db.scalars(select(SubmissionPhoto).where(SubmissionPhoto.submission_id == submission.id)))
            if len(photos) != 1:
                reject('PHOTO_LINK_CHANGED',submission.id)
            check(photos[0],dict(id=ident('submission_photos',code),media_id=UUID(original['photos'][0]['media_id']),position=1))
            job = locked(db,AnalysisJob,ident('analysis_jobs',code))
            attempt_id = ident('analysis_attempts',code)
            check(job,dict(submission_id=submission.id,status='succeeded',is_fixture=True,current_attempt_id=attempt_id,
                queued_at=when,queue_deadline_at=when+timedelta(seconds=180),started_at=when+timedelta(seconds=1),
                finished_at=when+timedelta(seconds=12),error_code=None,error_message=None))
            attempt = locked(db,AnalysisAttempt,attempt_id)
            check(attempt,dict(job_id=job.id,attempt_number=2 if sequence == 4 else 1,status='succeeded',result_applied=True,
                queued_at=when+timedelta(seconds=4 if sequence == 4 else 0),started_at=when+timedelta(seconds=5 if sequence == 4 else 1),
                finished_at=when+timedelta(seconds=12),error_code=None,error_message=None,created_at=when))
            old_result, fixed_result = expected_result(index,sequence,original), expected_result(index,sequence,corrected)
            payload = validate_result(old_result,original)
            review = locked(db,ReviewResult,ident('review_results',code))
            check(review,dict(submission_id=submission.id,attempt_id=attempt_id,schema_version='1.0',source_kind='mock',
                prompt_version='seed-v1',model_name=None,latency_ms=0,created_at=when+timedelta(seconds=12),
                result=old_result,**derive_metrics(payload,original)))
            rows = list(db.scalars(select(CriterionEvaluation).where(CriterionEvaluation.review_id == review.id).with_for_update()))
            if len(rows) != len(old_result['criteria']):
                reject('CRITERIA_COUNT_CHANGED',review.id)
            by_id = {row.id:row for row in rows}
            for old, new in zip(old_result['criteria'],fixed_result['criteria']):
                criterion_id = ident('criterion_evaluations',code+'-'+old['rule_key'])
                criterion = by_id.get(criterion_id)
                if criterion is None:
                    reject('CRITERION_LINK_CHANGED',review.id)
                check(criterion,dict(review_id=review.id,guideline_id=UUID(old['guideline_id']),version_id=UUID(old['version_id']),
                    rule_key=old['rule_key'],verdict=old['verdict'],evidence=old['evidence'],actions=old['actions']))
                add_change(changes,criterion,{'version_id':UUID(new['version_id'])})
            if original != corrected:
                changed_submissions += 1
                add_change(changes,context,{'snapshot':corrected,'snapshot_sha256':digest(corrected)})
                add_change(changes,review,{'result':fixed_result})
    # 실제 사용자 context의 이전 결과 연결도 수정하거나 무시하지 않는다.
    targets = {str(ident('review_results',f'{code}-{sequence}')) for _,code,_ in STORES for sequence in [1,4]}
    for row_id, snapshot in db.execute(select(AnalysisContext.id,AnalysisContext.snapshot)):
        if (snapshot.get('previous_review') or {}).get('review_id') in targets:
            reject('EXTERNAL_SNAPSHOT_DEPENDENCY',row_id)
    return changes, changed_submissions


def write_backup(backup_dir, changes):
    directory = Path(backup_dir)
    if directory.is_symlink():
        raise RepairConflict('BACKUP_DIRECTORY_SYMLINK')
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(directory,0o700)
    path = directory/(REPAIR_VERSION+'-'+uuid4().hex+'.json')
    content = {'repair_version':REPAIR_VERSION,'purpose':'pre_change_backup',
               'originals':[{'table':change['row'].__tablename__,'id':str(change['row'].id),'values':change['before']} for change in changes]}
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as stream:
        json.dump(content,stream,ensure_ascii=False,indent=2); stream.flush(); os.fsync(stream.fileno())
    return path


def repair_fixtures(db, *, apply=False, backup_dir=None):
    if db.new or db.dirty or db.deleted:
        raise RepairConflict('PENDING_UNRELATED_CHANGES')
    try:
        changes, changed_submissions = build_plan(db)
        report = {'repair_version':REPAIR_VERSION,'mode':'applied' if apply else 'dry-run',
                  'changed_submissions':changed_submissions,'change_count':len(changes),
                  'changes':[change['report'] for change in changes]}
        if not apply or not changes:
            db.rollback()
            return report
        if backup_dir is None:
            raise RepairConflict('BACKUP_REQUIRED')
        write_backup(backup_dir,changes)
        for change in changes:
            for key,value in change['values'].items():
                setattr(change['row'],key,deepcopy(value))
        db.commit()
        return report
    except Exception:
        db.rollback()
        raise


def local_database_url(alias):
    if alias not in ('demo','test'):
        raise RepairConflict('LOCAL_DATABASE_REQUIRED')
    values = dotenv_values(PROJECT_ROOT/'.local/runtime.env')
    value = values.get('DATABASE_URL' if alias == 'demo' else 'STORELOOP_TEST_DATABASE_URL')
    if not value:
        raise RepairConflict('LOCAL_DATABASE_MISSING')
    url = make_url(value)
    expected = 'storeloop' if alias == 'demo' else 'storeloop_test'
    if (url.drivername != 'postgresql+psycopg' or url.host not in ('127.0.0.1','localhost')
            or url.port != 55443 or url.database != expected or url.username != 'storeloop' or url.query):
        raise RepairConflict('LOCAL_DATABASE_REQUIRED')
    return value


def main():
    parser = argparse.ArgumentParser(description='검증된 원래 합성 fixture만 정정합니다. 기본 dry-run입니다.')
    parser.add_argument('--database',choices=['demo','test'],required=True)
    parser.add_argument('--apply',action='store_true')
    args = parser.parse_args()
    engine = None
    try:
        engine = make_engine(local_database_url(args.database))
        with Session(engine,expire_on_commit=False) as db:
            report = repair_fixtures(db,apply=args.apply,backup_dir=PROJECT_ROOT/'.local/seed-repair-backups'/args.database)
        print(json.dumps(report,ensure_ascii=False))
    except RepairConflict as error:
        print(json.dumps({'status':'conflict','code':str(error)},ensure_ascii=False))
        return 2
    except Exception:
        # 연결 문자열·원문 결과·DB 매개변수는 출력하지 않는다.
        print(json.dumps({'status':'failed','code':'REPAIR_FAILED'},ensure_ascii=False))
        return 1
    finally:
        if engine is not None:
            engine.dispose()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
