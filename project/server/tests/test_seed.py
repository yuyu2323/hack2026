"""시드 재실행의 불변성·관계·시간·비밀 저장 경계를 검사한다."""
import hashlib
import json
from sqlalchemy import select, func
from server.core.config import get_settings
from server.core.db import as_utc
from server.core.models import Store, Submission, ReviewResult, ReferencePhoto, AnalysisContext, MediaAsset, Issue, IssueAction, AnalysisJob
from server.seed import __main__ as seeder

def test_seed_replay_preserves_user_changes_and_mock_truth(db, tmp_path, monkeypatch):
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts/seed').symlink_to(seeder.PROJECT_ROOT / 'scripts/seed', target_is_directory=True)
    monkeypatch.setattr(seeder, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(get_settings(), 'media_root', tmp_path / 'media')
    first = seeder.seed(db)
    assert first['created'] > 500
    store = db.scalar(select(Store).order_by(Store.code))
    store.name = '사용자가 수정한 매장명'; db.commit()
    snapshots = list(db.scalars(select(AnalysisContext.snapshot_sha256)))
    counts = {model: db.scalar(select(func.count()).select_from(model)) for model in (Submission, ReviewResult, MediaAsset)}
    second = seeder.seed(db)
    assert second.get('created', 0) == 0
    assert store.name == '사용자가 수정한 매장명'
    assert snapshots == list(db.scalars(select(AnalysisContext.snapshot_sha256)))
    assert counts == {model: db.scalar(select(func.count()).select_from(model)) for model in counts}
    assert counts[Submission] == 32
    assert db.scalar(select(AnalysisJob).where(AnalysisJob.status == 'queued', AnalysisJob.is_fixture == True)) is not None
    empty_contexts = [row for row in db.scalars(select(AnalysisContext)) if not row.snapshot['guidelines'] and not row.snapshot['references']]
    assert len(empty_contexts) == 1
    empty_review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == empty_contexts[0].submission_id))
    assert empty_review.compliance_rate is None and empty_review.assessable_rate is None
    assert empty_review.needs_ofc_review and empty_review.source_kind == 'mock'
    assert set(db.scalars(select(ReviewResult.source_kind))) == {'mock'}
    assert (tmp_path / '.local/demo-credentials').stat().st_mode & 0o777 == 0o600
    refs = set(db.scalars(select(ReferencePhoto.photo_id)))
    from server.submissions.models import SubmissionPhoto
    assert not refs & set(db.scalars(select(SubmissionPhoto.media_id)))
    for issue in db.scalars(select(Issue)):
        submission = db.get(Submission, issue.submission_id)
        assert as_utc(issue.created_at) > as_utc(submission.created_at)
        for action in db.scalars(select(IssueAction).where(IssueAction.issue_id == issue.id)):
            assert as_utc(action.created_at) > as_utc(issue.created_at)
    # 나중에 등록한 Reference를 과거 경계 fixture에 넣지 않는다.
    from copy import deepcopy
    snapshot = deepcopy(db.get(AnalysisContext, seeder.ident('analysis_contexts', 'boundary-pending')).snapshot)
    future_reference = db.get(ReferencePhoto, seeder.UUID(snapshot['references'][0]['reference_id']))
    future_reference.created_at = seeder.BASE
    db.flush()
    seeder.historical_versions(db, snapshot, seeder.BASE - seeder.timedelta(days=1))
    assert str(future_reference.id) not in {item['reference_id'] for item in snapshot['references']}
