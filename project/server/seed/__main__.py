"""합성 자료를 전용 DB에 추가하며 기존 행과 사용자 변경은 보존한다."""
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import secrets
from uuid import UUID, uuid5
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from server.core.config import PROJECT_ROOT, get_settings
from server.core.db import SessionLocal
from server.core.security import hash_password
from server.core.models import *
from server.submissions.media import normalize_image
from server.submissions.service import make_snapshot
from server.guidelines.resolution import resolve_guidelines
from packages.review_contract.validation import validate_result, derive_metrics

NAMESPACE = UUID('e3359552-691b-5b94-9a80-a46d7a8e12d7')
BASE = datetime(2026, 9, 21, tzinfo=timezone.utc)
VERSION = 'storeloop-demo-v1'

def ident(kind, code):
    return uuid5(NAMESPACE, kind + ':' + str(code))

def historical_versions(db, snapshot, when):
    candidates = []
    for item in snapshot['candidate_guidelines']:
        guideline = db.get(Guideline, UUID(item['guideline_id']))
        version = db.scalar(select(GuidelineVersion).where(
            GuidelineVersion.guideline_id == guideline.id,
            GuidelineVersion.created_at <= when,
        ).order_by(GuidelineVersion.version.desc()).limit(1))
        if version is not None:
            candidates.append(dict(item, version_id=str(version.id), version=version.version, text=version.text,
                                   store_id=str(guideline.store_id) if guideline.store_id else None,
                                   category_id=str(guideline.category_id) if guideline.category_id else None))
    effective, history = resolve_guidelines(candidates)
    keys = ('guideline_id', 'version_id', 'version', 'level', 'rule_key', 'text')
    snapshot['guidelines'] = [{key:row[key] for key in keys} for row in effective]
    snapshot['candidate_guidelines'] = [{key:row[key] for key in (*keys, 'selected', 'selection_reason')} for row in history]
    # 재실행 시 새로 추가되는 과거 fixture에도 미래 Reference를 섞지 않는다.
    historical_references = set(db.scalars(select(ReferencePhoto.id).where(ReferencePhoto.created_at <= when)))
    snapshot['references'] = [dict(item, position=position) for position, item in enumerate(
        (item for item in snapshot['references'] if UUID(item['reference_id']) in historical_references), 1)]
    return snapshot

def private_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as output:
        output.write(content)

def seed(db):
    created_files = []
    try:
        return _seed(db, created_files)
    except Exception:
        db.rollback()
        for path in created_files:
            path.unlink(missing_ok=True)
        raise

def _seed(db, created_files):
    counts = Counter()
    def add(model, stable_code, **values):
        key = ident(model.__tablename__, stable_code)
        existing = db.get(model, key)
        if existing:
            counts['existing'] += 1
            return existing
        if 'created_at' in model.__table__.columns:
            values.setdefault('created_at', BASE - timedelta(days=70))
        row = model(id=key, **values)
        db.add(row); db.flush(); counts['created'] += 1
        return row

    credential_file = PROJECT_ROOT / '.local/demo-credentials'
    credentials = json.loads(credential_file.read_text()) if credential_file.exists() else {}
    accounts = {}
    regions = {code: add(Region, code, code=code, name=name) for code, name in [('north','가상 북부권'),('south','가상 남부권')]}
    specifications = [(role + '.' + area, role, area) for role in ('owner','ofc','regional') for area in ('north','south')]
    specifications += [('hq.demo','hq',None),('operator.demo','platform_operator',None),('owner.inactive','owner',None),('owner.unmapped','owner',None)]
    for login, role, area in specifications:
        role = 'store_owner' if role == 'owner' else role
        existing = db.get(Account, ident('accounts', login))
        if login not in credentials:
            if existing:
                raise ValueError('SEED_CONFLICT: 기존 계정의 로컬 자격 파일이 없습니다.')
            credentials[login] = {'password': secrets.token_urlsafe(24), 'role': role}
        accounts[login] = add(Account, login, login_id=login, display_name=login,
                             role=role, region_id=regions[area].id if area and role in ('ofc','regional') else None,
                             is_active=login != 'owner.inactive', password_hash=hash_password(credentials[login]['password']))
    if not credential_file.exists():
        private_file(credential_file, json.dumps(credentials, ensure_ascii=False, indent=2).encode())
    elif json.loads(credential_file.read_text()) != credentials:
        # 부분 설치를 복구할 때도 기존 계정 비밀번호는 바꾸지 않는다.
        temporary = credential_file.with_suffix('.new')
        private_file(temporary, json.dumps(credentials, ensure_ascii=False, indent=2).encode())
        temporary.replace(credential_file)
    operator, hq = accounts['operator.demo'], accounts['hq.demo']
    names = [('north','spring-station','봄빛역점'),('north','bank-road','은행길점'),('north','green-hill','푸른언덕점'),
             ('south','star-river','별하천점'),('south','sunset-park','노을공원점'),('south','spring-road','새봄로점')]
    stores = []
    for index, (area, code, name) in enumerate(names):
        store = add(Store, code, code=code, name=name, region_id=regions[area].id, store_type='도심형' if index % 2 == 0 else '주택가형', address='가상 시연 주소')
        stores.append(store)
        add(StoreOwnerMapping, code, account_id=accounts['owner.'+area].id, store_id=store.id, changed_by_id=operator.id, reason='합성 시연 연결')
        if index % 3 < 2:
            add(OFCStoreMapping, code, account_id=accounts['ofc.'+area].id, store_id=store.id, changed_by_id=operator.id, reason='합성 시연 연결')
    categories = {code: add(Category, code, code=code, name=name, description='가상 시연 카테고리') for code, name in
                  [('beverage','음료'),('snack','스낵'),('ready_meal','간편식'),('household','생활용품')]}
    rules = [('hq-label','label_visibility','가격 라벨','HQ',None,None,None,'사진에 보이는 선반 라벨이 상품에 가려지지 않아야 한다.'),
             ('hq-facing','facing','앞줄 정렬','HQ',None,None,None,'동일 상품의 앞줄이 선반 앞선에 맞게 정렬되어야 한다.')]
    for area in regions:
        rules.append((area+'-facing','facing','지역 앞줄 정렬','REGION',regions[area].id,None,None,'앞줄 상품의 앞면 방향과 간격을 일정하게 맞춘다.'))
    for store in stores:
        rules.append((store.code+'-gap','shelf_gap','빈 간격 확인','STORE',None,store.id,None,'넓은 빈 간격이 보이면 보충하거나 간격을 고르게 조정한다.'))
    for code in ('beverage','snack'):
        rules.append((code+'-group','category_grouping','상품군 구분','CATEGORY',None,None,categories[code].id,'같은 상품군을 묶고 다른 상품군과 구분해 배치한다.'))
    rules.append(('beverage-facing','facing','음료 앞줄 정렬','CATEGORY',None,None,categories['beverage'].id,'병과 캔의 앞면을 정렬하고 앞줄의 간격을 일정하게 유지한다.'))
    for code, key, title, level, region_id, store_id, category_id, text in rules:
        current = 2 if code == 'beverage-facing' else 1
        rule = add(Guideline, code, rule_key=key, title=title, level=level, region_id=region_id, store_id=store_id, category_id=category_id,
                   scope_key=f'{level}:{store_id or region_id or "all"}:{category_id or "all"}', current_version=current, created_by_id=hq.id)
        for revision in range(1, current + 1):
            add(GuidelineVersion, f'{code}-{revision}', guideline_id=rule.id, version=revision,
                text=text if revision == current else '음료 앞줄 상품의 앞면을 일정하게 정렬한다.', change_reason='합성 시연 기준 '+str(revision),
                created_by_id=hq.id, created_at=BASE - timedelta(days=65 if revision == 1 else 7))
    manifest = json.loads((PROJECT_ROOT / 'scripts/seed/manifest.json').read_text())
    media = {}
    for image in manifest['images']:
        path = (PROJECT_ROOT / 'scripts/seed' / image['path']).resolve()
        if not path.is_relative_to((PROJECT_ROOT / 'scripts/seed/assets').resolve()) or image['review_status'] not in ('approved','golden_approved'):
            raise ValueError('SEED_CONFLICT: 이미지 경로 또는 검수 상태 불일치')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != image['sha256']:
            raise ValueError('SEED_CONFLICT: 이미지 해시 불일치')
        normalized = normalize_image(raw, path.name, image['mime_type'])
        code = image['image_id']; key = ident('media_assets', code)
        original, thumb = f'{key}.png', f'{key}-thumbnail.jpg'
        for filename, content in [(original, normalized['content']), (thumb, normalized['thumbnail'])]:
            target = get_settings().media_root / filename
            if target.exists():
                if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(content).digest():
                    raise ValueError('SEED_CONFLICT: 보호 이미지 파일이 변경되었습니다.')
            else:
                private_file(target, content); created_files.append(target)
        media[code] = add(MediaAsset, code, storage_key=original, thumbnail_key=thumb, uploaded_by_id=hq.id,
                          source_kind='ai_generated_demo', **{name: normalized[name] for name in ['sha256','mime_type','byte_size','width','height']})
        if image['purpose'] == 'reference':
            rid = ident('reference_photos', code)
            add(ReferencePhoto, code, lineage_id=rid, version=1, state_version=1, photo_id=media[code].id,
                category_id=categories[image['category_code']].id, store_id=stores[0].id if code.endswith('02') else None,
                caption='AI 생성 시연 Reference · '+image['category_code'], created_by_id=hq.id, created_at=BASE-timedelta(days=65))
    rng = random.Random(20260921)
    for index, store in enumerate(stores):
        area = names[index][0]; owner = accounts['owner.'+area]
        parent = None
        for sequence in range(5):
            code = f'{store.code}-{sequence}'
            if db.get(Submission, ident('submissions', code)):
                counts['existing'] += 1
                if sequence == 0:
                    parent = db.get(Submission, ident('submissions', code))
                continue
            category_code = 'beverage' if sequence < 2 or sequence == 4 else 'snack'
            category = categories[category_code]
            state = 'before' if sequence in (0,4) else 'after' if sequence == 1 else 'uncertain' if sequence == 2 else 'before'
            photo = media[f'{category_code}-{state}-01']
            when = BASE - timedelta(days=(55 if index == 5 else 20) - sequence * 3 + index % 2)
            submission = add(Submission, code, store_id=store.id, category_id=category.id, submitted_by_id=owner.id,
                             question='앞줄 정렬과 빈 간격을 어떻게 개선하면 좋을까요?', parent_submission_id=parent.id if sequence == 1 else None,
                             source_kind='seed_demo', created_at=when)
            if sequence == 0:
                parent = submission
            row = add(SubmissionPhoto, code, submission_id=submission.id, media_id=photo.id, position=1)
            previous = None
            if sequence == 1:
                old = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == parent.id))
                previous = {'submission_id': str(parent.id), 'review_id': str(old.id), 'criteria': old.result['criteria']}
            snapshot = make_snapshot(db, store, category, submission.question,
                       [{'photo_id': str(row.id), 'media_id': str(photo.id), 'position': 1, 'mime_type': photo.mime_type, 'sha256': photo.sha256}], previous)
            # 합성 과거 평가도 제출 시각에 이미 존재했던 기준 버전만 참조한다.
            historical_versions(db, snapshot, when)
            digest = hashlib.sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            add(AnalysisContext, code, submission_id=submission.id, snapshot=snapshot, snapshot_sha256=digest, created_at=when)
            failed = sequence == 3
            job = add(AnalysisJob, code, submission_id=submission.id, status='failed' if failed else 'succeeded', queued_at=when,
                      queue_deadline_at=when+timedelta(seconds=180), started_at=when+timedelta(seconds=1), finished_at=when+timedelta(seconds=12),
                      error_code='AI_UNAVAILABLE' if failed else None, error_message='분석 서비스에 연결하지 못했습니다.' if failed else None,
                      is_fixture=True, created_at=when)
            if sequence == 4:
                add(AnalysisAttempt, code+'-failed', job_id=job.id, attempt_number=1, status='failed', queued_at=when,
                    started_at=when+timedelta(seconds=1), finished_at=when+timedelta(seconds=3), error_code='AI_UNAVAILABLE',
                    error_message='시연용 과거 연결 실패', created_at=when)
            attempt = add(AnalysisAttempt, code, job_id=job.id, attempt_number=2 if sequence == 4 else 1,
                          status='failed' if failed else 'succeeded', queued_at=when+timedelta(seconds=4 if sequence == 4 else 0),
                          started_at=when+timedelta(seconds=5 if sequence == 4 else 1), finished_at=when+timedelta(seconds=12),
                          result_applied=not failed, error_code='AI_UNAVAILABLE' if failed else None,
                          error_message='분석 서비스에 연결하지 못했습니다.' if failed else None, created_at=when)
            job.current_attempt_id = attempt.id
            if failed:
                continue
            criteria = []
            for n, guideline in enumerate(snapshot['guidelines']):
                verdict = 'unknown' if sequence == 2 else 'pass' if sequence == 1 or (n + index + sequence) % 3 else 'fail'
                criteria.append({**{key: guideline[key] for key in ['guideline_id','version_id','version','rule_key']}, 'verdict': verdict,
                                 'reason': '합성 과거 평가: 가림으로 관찰하기 어렵습니다.' if verdict == 'unknown' else '합성 과거 평가: 진열 기준과 사진을 비교한 시연 결과입니다.',
                                 'evidence': [] if verdict == 'unknown' else [{'photo_position': 1, 'observation': '시연 사진의 앞줄과 선반 간격을 확인했습니다.'}],
                                 'actions': ['밝은 조명에서 선반 전체를 다시 촬영해 주세요.'] if verdict == 'unknown' else ['앞줄 간격을 고르게 조정해 주세요.'] if verdict == 'fail' else []})
            payload = {'schema_version':'1.0','question_answer':'Mock 과거 평가입니다. 앞줄 간격과 상품군을 기준에 맞춰 정리해 주세요.',
                       'summary':'합성 데이터로 구성한 과거 진열 평가입니다. 실제 AI 분석 결과가 아닙니다.',
                       'overall_confidence':'low' if sequence == 2 else 'medium','criteria':criteria,
                       'reference_comparisons':[{'reference_id':ref['reference_id'],'verdict':'unknown' if sequence == 2 else 'similar' if sequence == 1 else 'different',
                                                 'photo_positions':[] if sequence == 2 else [1],'observation':'합성 시연 비교입니다.'} for ref in snapshot['references']],
                       'limitations':['가려진 부분의 상품과 라벨은 확인할 수 없습니다.'] if sequence == 2 else [],
                       'ofc_review_required':sequence == 2,'follow_up_comparison':'합성 이전 평가와 비교한 개선 시연입니다.' if sequence == 1 else None}
            result = validate_result(payload, snapshot)
            metrics = derive_metrics(result, snapshot)
            review = add(ReviewResult, code, submission_id=submission.id, attempt_id=attempt.id, result=result.model_dump(),
                         source_kind='mock', prompt_version='seed-v1', model_name=None, latency_ms=0, created_at=when+timedelta(seconds=12), **metrics)
            for criterion in criteria:
                add(CriterionEvaluation, code+'-'+criterion['rule_key'], review_id=review.id, guideline_id=UUID(criterion['guideline_id']),
                    version_id=UUID(criterion['version_id']), rule_key=criterion['rule_key'], verdict=criterion['verdict'], evidence=criterion['evidence'], actions=criterion['actions'])
            add(Notification, code+'-review', recipient_id=owner.id, kind='review_ready', submission_id=submission.id,
                title='시연 평가 결과가 도착했습니다.', dedupe_key='seed:'+code, read_at=when+timedelta(minutes=10) if sequence == 0 else None, created_at=when+timedelta(seconds=13))
            if sequence in (0,1,2):
                assigned = accounts['ofc.'+area].id if index % 3 < 2 else None
                status = ['in_progress','resolved','open'][sequence]
                issue = add(Issue, code, submission_id=submission.id, review_id=review.id, type='ai_review_required' if sequence == 2 else 'owner_question',
                            status=status, priority='high' if sequence == 2 else 'normal', title='사진 진열 확인 요청', description='시연용 후속 확인 요청입니다.',
                            assignee_id=assigned, created_by_id=owner.id if sequence != 2 else None,
                            resolution='진열 개선을 확인했습니다.' if sequence == 1 else None,
                            resolved_at=when+timedelta(hours=1) if sequence == 1 else None, created_at=when+timedelta(minutes=1))
                if assigned:
                    add(IssueAction, code, issue_id=issue.id, actor_id=assigned, action_type='comment', body='시연용 매장 확인을 진행했습니다.', created_at=when+timedelta(minutes=2))
                    add(Notification, code+'-issue', recipient_id=assigned, kind='issue_created', submission_id=submission.id, issue_id=issue.id,
                        title='확인 요청이 등록되었습니다.', dedupe_key='seed:issue:'+code, created_at=when+timedelta(minutes=3))
        for category_code in ('beverage','snack'):
            for week in range(8):
                if index == 0 and category_code == 'beverage' and week == 2:
                    continue
                add(SalesMock, f'{store.code}-{category_code}-{week}', store_id=store.id, category_id=categories[category_code].id,
                    week_start=(BASE-timedelta(weeks=week)).date(), amount=250000 if index == 4 else 180000 + index*23000 + rng.randrange(60000), source_kind='mock')
            for sku in range(5):
                add(InventoryMock, f'{store.code}-{category_code}-{sku}', store_id=store.id, category_id=categories[category_code].id,
                    sku=f'{category_code}-{sku}', name=f'가상 {categories[category_code].name} {sku+1}', quantity=rng.randrange(10,60), observed_on=BASE.date())
    # 오래 대기한 작업과 기준 도입 전 평가를 독립 합성 경계 사례로 남긴다.
    for code, queued in [('boundary-pending', True), ('boundary-no-criteria', False)]:
        if db.get(Submission, ident('submissions', code)):
            counts['existing'] += 1
            continue
        when = BASE - timedelta(days=1 if queued else 66)
        store, category, owner = stores[0], categories['beverage'], accounts['owner.north']
        photo = media['beverage-uncertain-01']
        submission = add(Submission, code, store_id=store.id, category_id=category.id, submitted_by_id=owner.id,
                         question='시연용 경계 사례입니다. 관찰할 수 있는 내용과 한계를 알려주세요.', source_kind='seed_demo', created_at=when)
        row = add(SubmissionPhoto, code, submission_id=submission.id, media_id=photo.id, position=1)
        snapshot = make_snapshot(db, store, category, submission.question,
            [{'photo_id':str(row.id), 'media_id':str(photo.id), 'position':1, 'mime_type':photo.mime_type, 'sha256':photo.sha256}], None)
        historical_versions(db, snapshot, when)
        if not queued:
            # 기준 도입 이전 시점에는 비교 자료가 없었다는 합성 이력을 표현한다.
            snapshot.update(guidelines=[], candidate_guidelines=[], references=[])
        digest = hashlib.sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        add(AnalysisContext, code, submission_id=submission.id, snapshot=snapshot, snapshot_sha256=digest, created_at=when)
        job = add(AnalysisJob, code, submission_id=submission.id, status='queued' if queued else 'succeeded',
                  queued_at=when, queue_deadline_at=when+timedelta(seconds=180),
                  started_at=None if queued else when+timedelta(seconds=1),
                  finished_at=None if queued else when+timedelta(seconds=12), is_fixture=True, created_at=when)
        if not queued:
            attempt = add(AnalysisAttempt, code, job_id=job.id, attempt_number=1, status=job.status, queued_at=when,
                          started_at=job.started_at, finished_at=job.finished_at, result_applied=True, created_at=when)
            job.current_attempt_id = attempt.id
            payload = dict(schema_version='1.0', question_answer='Mock 과거 평가입니다. 당시 등록된 진열 기준과 Reference가 없어 OFC 확인이 필요합니다.',
                summary='기준 도입 이전의 합성 경계 사례입니다.', overall_confidence='low', criteria=[], reference_comparisons=[],
                limitations=['당시 적용할 기준과 비교 Reference가 없었습니다.'], ofc_review_required=True, follow_up_comparison=None)
            result = validate_result(payload, snapshot)
            review = add(ReviewResult, code, submission_id=submission.id, attempt_id=attempt.id, result=result.model_dump(),
                         source_kind='mock', prompt_version='seed-v1', model_name=None, latency_ms=0,
                         created_at=when+timedelta(seconds=12), **derive_metrics(result, snapshot))
            add(Issue, code, submission_id=submission.id, review_id=review.id, type='ai_review_required', status='open', priority='normal',
                title='시연: 기준 도입 전 평가 확인', description='판단 기준이 없는 과거 합성 기록을 OFC가 확인합니다.',
                created_by_id=owner.id, assignee_id=accounts['ofc.north'].id, created_at=when+timedelta(seconds=13))
    add(Announcement, 'active', title='StoreLoop 시연 안내', body='AI 생성 사진과 Mock 과거 데이터를 사용합니다. 새 제출은 실제 AI로 분석됩니다.', severity='info',
        starts_at=BASE-timedelta(days=1), ends_at=BASE+timedelta(days=365), created_by_id=operator.id)
    add(Announcement, 'expired', title='종료된 시연 점검', body='종료 공지 조회 경계용입니다.', severity='maintenance', starts_at=BASE-timedelta(days=10), ends_at=BASE-timedelta(days=9), created_by_id=operator.id)
    add(AuditEvent, 'seed', actor_id=operator.id, action='seed.initialize', target_type='seed', target_id=NAMESPACE, reason='가상 시연 데이터 초기 구성', before_data={}, after_data={'seed_version':VERSION}, outcome='succeeded', request_id=ident('request','seed'))
    db.commit()
    return dict(counts)

if __name__ == '__main__':
    try:
        with SessionLocal() as db:
            result = seed(db)
        print(json.dumps({'seed_version':VERSION, 'status':'ok', **result, 'credentials':'.local/demo-credentials (0600)'}, ensure_ascii=False))
    except (SQLAlchemyError, ValueError, OSError):
        # DB 연결 정보와 비밀번호가 traceback에 포함되지 않게 한다.
        raise SystemExit('SEED_FAILED: 관계·이미지·전용 DB 구성을 확인해 주세요. 기존 데이터는 보존됩니다.')
