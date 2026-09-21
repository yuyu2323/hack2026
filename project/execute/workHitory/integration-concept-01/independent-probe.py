"""지정된 01·02 실제 제출을 READ ONLY로 대조하고 본문 없는 메타데이터만 남긴다."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import AnalysisAttempt, AnalysisContext, AnalysisJob, GuidelineVersion, MediaAsset, ReferencePhoto, ReviewResult, Submission, SubmissionPhoto
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import validate_result, derive_metrics

CONCEPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
assert CONCEPT in (1, 2)
# 뒤에 추가되는 과거 fixture 재처리와 독립 검토 대상 신규 제출을 섞지 않는다.
TARGETS = {
    1: ('17f959e5-831a-4ff7-842d-22575e6cfad5', '2b0e717c-c161-4caa-8d1e-f1b7c9c88106'),
    2: ('8259ce47-90ce-4a85-8496-8ed27edeb375', 'bca082c1-56fe-4bd4-9c0f-9b7ce1ed0ee9', 'e9fd4f27-0d3e-42a1-9e58-9c255f49d703'),
}
OUT = ROOT / f'execute/workHitory/integration-concept-{CONCEPT:02d}'
checks = []
report = {'status': 'RUNNING', 'started_at': datetime.now(timezone.utc).isoformat(),
          'concept': CONCEPT, 'checks': checks, 'submissions': [], 'reference_changes': [],
          'scope': 'PostgreSQL READ ONLY·보호 파일 읽기; 본문/비밀/이미지 바이트 출력 없음; AI·Browser·업무 쓰기 없음'}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def check(name, value):
    checks.append({'check': name, 'status': 'PASS' if value else 'FAIL'})


def need(value):
    if value is None or value is False:
        raise ValueError('검사 선행조건 없음')
    return value


def protected_file(media):
    base = (ROOT / '.local/test-media').resolve()
    target = (base / media.storage_key).resolve()
    need(target.is_relative_to(base))
    data = target.read_bytes()
    return len(data) == media.byte_size and hashlib.sha256(data).hexdigest() == media.sha256


def main():
    all_exported = json.loads((OUT / 'actual-ai.json').read_text())
    exported = [need(next((r for r in all_exported if r['submission_id'] == ident), None)) for ident in TARGETS[CONCEPT]]
    report['root_export_rows'] = len(all_exported)
    report['selected_submission_ids'] = list(TARGETS[CONCEPT])
    url = need(dotenv_values(ROOT / '.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL'))
    parsed_url = make_url(url)
    need(parsed_url.host in ('127.0.0.1', 'localhost') and parsed_url.port == 55432 and parsed_url.database == 'storeloop_test')
    engine = create_engine(url, hide_parameters=True, connect_args={'options': '-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        check('read_only_transaction', conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on')
        with Session(bind=conn, autoflush=False) as db:
            private = {}
            for baseline in exported:
                ident = UUID(baseline['submission_id'])
                sub = need(db.get(Submission, ident))
                ctx = need(db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == ident)))
                job = need(db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == ident)))
                reviews = list(db.scalars(select(ReviewResult).where(ReviewResult.submission_id == ident)))
                check(f'{ident}:one_result', len(reviews) == 1)
                review = need(reviews[0])
                attempts = list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id == job.id).order_by(AnalysisAttempt.attempt_number)))
                snap = ctx.snapshot
                check(f'{ident}:canonical_snapshot', digest(snap) == ctx.snapshot_sha256)
                check(f'{ident}:real_ai_success', job.status == 'succeeded' and review.source_kind == 'real_ai' and not job.is_fixture)
                check(f'{ident}:question_preserved', sub.question == snap['question'] and 0 < len(sub.question) <= 2000)
                check(f'{ident}:one_applied_current_attempt', job.current_attempt_id == review.attempt_id
                      and sum(a.result_applied for a in attempts) == 1
                      and any(a.id == review.attempt_id and a.result_applied and a.status == 'succeeded' for a in attempts))
                raw_input = {'schema_version': ctx.schema_version, 'job_id': str(job.id), 'attempt_id': str(review.attempt_id),
                             'submission_id': str(ident), **{k: snap[k] for k in ('question', 'guidelines', 'photos', 'references', 'previous_review')}}
                # DB 연결용 media_id를 제외하는 실제 worker의 입력 규칙을 적용한다.
                raw_input['photos'] = [{k: photo[k] for k in ('photo_id', 'position', 'mime_type', 'sha256')} for photo in snap['photos']]
                context = AnalysisInput.model_validate(raw_input)
                result = validate_result(review.result, context)
                metrics = derive_metrics(result, context)
                check(f'{ident}:strict_input_output_and_references', True)
                check(f'{ident}:stored_derived_metrics', all((float(getattr(review, k)) if isinstance(v, float) else getattr(review, k)) == v for k, v in metrics.items()))
                photos = []
                for photo in snap['photos']:
                    link = need(db.get(SubmissionPhoto, UUID(photo['photo_id'])))
                    media = need(db.get(MediaAsset, link.media_id))
                    check(f'{ident}:photo:{photo["position"]}:link_and_file', link.submission_id == ident and link.position == photo['position']
                          and str(media.id) == photo['media_id'] and media.sha256 == photo['sha256'] and protected_file(media))
                    photos.append({'photo_id': str(link.id), 'media_id': str(media.id), 'position': link.position,
                                   'sha256': media.sha256, 'source_kind': media.source_kind})
                references = []
                for ref in snap['references']:
                    row = need(db.get(ReferencePhoto, UUID(ref['reference_id'])))
                    media = need(db.get(MediaAsset, row.photo_id))
                    check(f'{ident}:reference:{row.id}:immutable_and_file', str(row.photo_id) == ref['photo_id']
                          and row.caption == ref['caption'] and media.sha256 == ref['sha256'] and protected_file(media))
                    references.append({'reference_id': str(row.id), 'lineage_id': str(row.lineage_id), 'version': row.version,
                                       'media_id': str(media.id), 'sha256': media.sha256, 'active_now': row.is_active,
                                       'store_specific': row.store_id is not None, 'position': ref['position']})
                for group in ('guidelines', 'candidate_guidelines'):
                    for guide in snap[group]:
                        version = need(db.get(GuidelineVersion, UUID(guide['version_id'])))
                        check(f'{ident}:{group}:{version.id}:immutable', version.version == guide['version'] and str(version.guideline_id) == guide['guideline_id']
                              and version.text == guide['text'] and version.created_at <= sub.created_at)
                row = {'submission_id': str(ident), 'parent_submission_id': str(sub.parent_submission_id) if sub.parent_submission_id else None,
                       'job_id': str(job.id), 'review_id': str(review.id), 'schema_version': ctx.schema_version, 'model': review.model_name,
                       'prompt_version': review.prompt_version, 'source_kind': review.source_kind, 'status': job.status,
                       'snapshot_sha256': ctx.snapshot_sha256, 'result_sha256': digest(review.result), 'ai_input_sha256': digest(raw_input),
                       'question_length': len(snap['question']), 'question_sha256': hashlib.sha256(snap['question'].encode()).hexdigest(),
                       'counts': {k: len(snap[k]) for k in ('photos', 'guidelines', 'references')},
                       'model_ms': review.latency_ms, 'submit_to_db_ms': round((job.finished_at - sub.created_at).total_seconds() * 1000),
                       'guidelines': [{k: g[k] for k in ('guideline_id', 'version_id', 'version', 'rule_key', 'level')} for g in snap['guidelines']],
                       'qa_candidates': [{k: g[k] for k in ('guideline_id', 'version_id', 'version', 'rule_key', 'level', 'selected')}
                                         for g in snap['candidate_guidelines'] if g['rule_key'].startswith(f'qa{CONCEPT:02d}')],
                       'photos': photos, 'references': references, 'metrics': metrics,
                       'attempts': [{'number': a.attempt_number, 'status': a.status, 'error_code': a.error_code, 'result_applied': a.result_applied} for a in attempts]}
                check(f'{ident}:root_export_unchanged', all(baseline[k] == row[k] for k in ('job_id', 'review_id', 'snapshot_sha256', 'model_ms'))
                      and all(baseline[b] == row['counts'][c] for b, c in (('photos', 'photos'), ('criteria', 'guidelines'), ('references', 'references'))))
                report['submissions'].append(row)
                private[str(ident)] = (sub, ctx, review)
            for row in report['submissions']:
                sub, ctx, review = private[row['submission_id']]
                previous = ctx.snapshot['previous_review']
                if row['parent_submission_id'] is None:
                    check(row['submission_id'] + ':no_parent', previous is None)
                    continue
                parent_sub, parent_context, parent_review = private[row['parent_submission_id']]
                check(row['submission_id'] + ':frozen_parent_review', previous['submission_id'] == str(parent_sub.id)
                      and previous['review_id'] == str(parent_review.id) and previous['criteria'] == parent_review.result['criteria'])
                parent_meta = next(x for x in report['submissions'] if x['submission_id'] == row['parent_submission_id'])
                for old in parent_meta['references']:
                    for new in row['references']:
                        if old['lineage_id'] == new['lineage_id'] and old['reference_id'] != new['reference_id']:
                            report['reference_changes'].append({'parent_submission_id': parent_meta['submission_id'], 'child_submission_id': row['submission_id'], 'before': old, 'after': new})
    engine.dispose()
    report['status'] = 'PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL'


try:
    main()
except Exception as error:
    report['status'] = 'FAIL'
    report['failure_type'] = type(error).__name__
    report['failure_detail'] = '자격값/본문 보호를 위해 예외 원문과 traceback은 저장하지 않는다.'
finally:
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    path = OUT / 'independent-ai-metadata.json'
    if path.exists():
        path = path.with_name(path.stem + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    path.chmod(0o600)
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'failed_checks': [x['check'] for x in checks if x['status'] == 'FAIL'],
                      'failure_type': report.get('failure_type'), 'counts': [{'submission_id': x['submission_id'], **x['counts']} for x in report['submissions']],
                      'evidence': str(path.relative_to(ROOT))}, ensure_ascii=False))
    if report['status'] != 'PASS':
        raise SystemExit(1)
