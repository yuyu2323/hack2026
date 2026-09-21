"""합성 이력 정정의 건조 실행·원자성·비대상 보호를 검증한다."""
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
from uuid import uuid4
import pytest
from sqlalchemy import select
from server.core.config import get_settings
from server.core.models import (
    Submission, AnalysisContext, ReviewResult, CriterionEvaluation,
    ReferencePhoto, GuidelineVersion, Issue, Notification,
)
from server.seed import __main__ as seeder
from scripts.repair_seed_fixtures import repair_fixtures, RepairConflict, digest


@pytest.fixture
def legacy_seed(request, tmp_path, monkeypatch):
    db = request.getfixturevalue(getattr(request, 'param', 'db'))
    root = tmp_path/'seed-root'
    (root/'scripts').mkdir(parents=True)
    (root/'scripts/seed').symlink_to(seeder.PROJECT_ROOT/'scripts/seed', target_is_directory=True)
    monkeypatch.setattr(seeder, 'PROJECT_ROOT', root)
    monkeypatch.setattr(get_settings(), 'media_root', root/'media')
    seeder.seed(db)
    v2 = db.get(GuidelineVersion, seeder.ident('guideline_versions', 'beverage-facing-2'))
    for code in ['spring-station','bank-road','green-hill','star-river','sunset-park','spring-road']:
        for sequence in [1, 4]:
            stable = f'{code}-{sequence}'
            context = db.get(AnalysisContext, seeder.ident('analysis_contexts', stable))
            snapshot = deepcopy(context.snapshot)
            for item in snapshot['guidelines'] + snapshot['candidate_guidelines']:
                if item['guideline_id'] == str(v2.guideline_id):
                    item.update(version_id=str(v2.id), version=2, text=v2.text)
            context.snapshot, context.snapshot_sha256 = snapshot, digest(snapshot)
            review = db.get(ReviewResult, seeder.ident('review_results', stable))
            payload = deepcopy(review.result)
            for item in payload['criteria']:
                if item['guideline_id'] == str(v2.guideline_id):
                    item.update(version_id=str(v2.id), version=2)
            review.result = payload
            criterion = db.get(CriterionEvaluation, seeder.ident('criterion_evaluations', stable+'-facing'))
            criterion.version_id = v2.id
    for reference in db.scalars(select(ReferencePhoto)):
        reference.created_at = seeder.BASE-timedelta(days=70)
    db.commit()
    return db, tmp_path/'backups'


def fingerprint(db):
    from server.business_common import encode
    models = [Submission, AnalysisContext, ReviewResult, CriterionEvaluation, ReferencePhoto, Issue, Notification]
    return digest({model.__tablename__: [
        {column.name:encode(getattr(row,column.name)) for column in model.__table__.columns}
        for row in db.scalars(select(model).order_by(model.id))
    ] for model in models})


@pytest.mark.parametrize('legacy_seed', ['db', pytest.param('postgres_db', marks=pytest.mark.postgres)], indirect=True)
def test_dry_run_apply_backup_and_repeat_preserve_other_records(legacy_seed):
    db, backup_dir = legacy_seed
    source = db.scalar(select(Submission))
    unrelated = Submission(id=uuid4(), store_id=source.store_id, category_id=source.category_id,
                           submitted_by_id=source.submitted_by_id, question='사용자가 작성한 별도 제출', source_kind='user_upload')
    db.add(unrelated); db.commit()
    before = fingerprint(db)
    plan = repair_fixtures(db, backup_dir=backup_dir)
    assert plan['mode'] == 'dry-run' and plan['changed_submissions'] == 12 and plan['change_count'] == 40
    assert fingerprint(db) == before and not backup_dir.exists()
    applied = repair_fixtures(db, apply=True, backup_dir=backup_dir)
    assert applied['mode'] == 'applied' and applied['change_count'] == 40
    files = list(backup_dir.glob('*.json'))
    assert len(files) == 1 and files[0].stat().st_mode & 0o777 == 0o600
    backup = json.loads(files[0].read_text())
    assert len(backup['originals']) == 40
    db.refresh(unrelated)
    assert unrelated.question == '사용자가 작성한 별도 제출' and unrelated.source_kind == 'user_upload'
    after = fingerprint(db)
    repeated = repair_fixtures(db, apply=True, backup_dir=backup_dir)
    assert repeated['change_count'] == 0 and fingerprint(db) == after
    assert len(list(backup_dir.glob('*.json'))) == 1
    for context in db.scalars(select(AnalysisContext)):
        assert digest(context.snapshot) == context.snapshot_sha256


@pytest.mark.parametrize('change', ['snapshot', 'review', 'real_ai', 'reference', 'criterion', 'hash', 'external_child'])
def test_modified_or_external_records_fail_closed_without_backup(legacy_seed, change):
    db, backup_dir = legacy_seed
    code = 'spring-station-1'
    submission = db.get(Submission, seeder.ident('submissions', code))
    context = db.get(AnalysisContext, seeder.ident('analysis_contexts', code))
    review = db.get(ReviewResult, seeder.ident('review_results', code))
    if change == 'snapshot':
        snapshot = deepcopy(context.snapshot); snapshot['question'] = '사용자 변경 내용'
        context.snapshot, context.snapshot_sha256 = snapshot, digest(snapshot)
    elif change == 'review':
        payload = deepcopy(review.result); payload['summary'] = '사용자 변경 결과'
        review.result = payload
    elif change == 'real_ai':
        review.source_kind = 'real_ai'
    elif change == 'reference':
        db.get(ReferencePhoto, seeder.ident('reference_photos','beverage-reference-01')).caption = '사용자 변경 설명'
    elif change == 'criterion':
        db.get(CriterionEvaluation, seeder.ident('criterion_evaluations', code+'-facing')).verdict = 'unknown'
    elif change == 'hash':
        context.snapshot_sha256 = '0'*64
    else:
        db.add(Submission(store_id=submission.store_id, category_id=submission.category_id,
                          submitted_by_id=submission.submitted_by_id, parent_submission_id=submission.id,
                          question='사용자 후속 제출', source_kind='user_upload'))
    db.commit(); before = fingerprint(db)
    with pytest.raises(RepairConflict):
        repair_fixtures(db, apply=True, backup_dir=backup_dir)
    assert fingerprint(db) == before and not backup_dir.exists()


def test_commit_failure_rolls_back_all_rows_and_retains_private_backup(legacy_seed, monkeypatch):
    db, backup_dir = legacy_seed
    before = fingerprint(db)
    def fail_after_flush():
        db.flush()
        raise RuntimeError('합성 커밋 실패')
    monkeypatch.setattr(db, 'commit', fail_after_flush)
    with pytest.raises(RuntimeError, match='합성 커밋 실패'):
        repair_fixtures(db, apply=True, backup_dir=backup_dir)
    assert fingerprint(db) == before
    files = list(backup_dir.glob('*.json'))
    assert len(files) == 1 and files[0].stat().st_mode & 0o777 == 0o600


def test_cli_database_alias_rejects_external_or_wrong_database(monkeypatch):
    from scripts import repair_seed_fixtures as tool
    values = {'DATABASE_URL':'postgresql+psycopg://storeloop@127.0.0.1:55444/storeloop',
              'STORELOOP_TEST_DATABASE_URL':'postgresql+psycopg://storeloop@127.0.0.1:55444/storeloop_test'}
    monkeypatch.setattr(tool, 'dotenv_values', lambda _:values)
    assert tool.local_database_url('demo') == values['DATABASE_URL']
    assert tool.local_database_url('test') == values['STORELOOP_TEST_DATABASE_URL']
    with pytest.raises(RepairConflict):
        tool.local_database_url('other')
    for value in ['postgresql+psycopg://storeloop@example.invalid:55444/storeloop',
                  'postgresql+psycopg://storeloop@127.0.0.1:5432/storeloop',
                  'postgresql+psycopg://storeloop@127.0.0.1:55444/other',
                  'postgresql+psycopg://storeloop@127.0.0.1:55444/storeloop?options=x',
                  'sqlite:///irrelevant.db']:
        values['DATABASE_URL'] = value
        with pytest.raises(RepairConflict):
            tool.local_database_url('demo')
