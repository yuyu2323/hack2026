#!/usr/bin/env python3
"""전용 인수 DB에서 비밀과 업무 본문을 제외한 실제 분석 증거만 내보낸다."""
import argparse
import json
from pathlib import Path
from uuid import UUID
from dotenv import dotenv_values
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from server.core.models import Submission, AnalysisContext, AnalysisJob, AnalysisAttempt, ReviewResult

ROOT = Path(__file__).resolve().parents[1]

def milliseconds(start, end):
    return round((end-start).total_seconds()*1000) if start and end else None

def export(concept, submissions):
    values = dotenv_values(ROOT/'.local/runtime.env')
    engine = create_engine(values['STORELOOP_TEST_DATABASE_URL'], hide_parameters=True)
    output = []
    with Session(engine) as db:
        for ident in submissions:
            submission = db.get(Submission, UUID(ident))
            if submission is None:
                raise ValueError('검증 제출을 찾지 못했습니다.')
            context = db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == submission.id))
            job = db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == submission.id))
            review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == submission.id))
            attempts = list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id == job.id).order_by(AnalysisAttempt.attempt_number)))
            output.append(dict(concept=concept, submission_id=ident, parent_submission_id=str(submission.parent_submission_id) if submission.parent_submission_id else None,
                job_id=str(job.id), review_id=str(review.id) if review else None, status=job.status, is_fixture=job.is_fixture, source_kind=review.source_kind if review else None,
                model=review.model_name if review else None, model_ms=review.latency_ms if review else None,
                prompt_version=review.prompt_version if review else None, schema_version=context.schema_version,
                snapshot_sha256=context.snapshot_sha256, submitted_at=submission.created_at.isoformat(),
                submit_to_db_result_ms=milliseconds(submission.created_at, job.finished_at),
                photos=len(context.snapshot['photos']), criteria=len(context.snapshot['guidelines']), references=len(context.snapshot['references']),
                attempts=[dict(number=a.attempt_number,status=a.status,error_code=a.error_code,result_applied=a.result_applied,
                    queue_ms=milliseconds(a.queued_at,a.started_at),run_ms=milliseconds(a.started_at,a.finished_at)) for a in attempts]))
    engine.dispose()
    path=ROOT/f'execute/workHitory/integration-concept-{concept:02d}/actual-ai.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output,ensure_ascii=False))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('concept',type=int,choices=[1])
    parser.add_argument('submissions',nargs='+',type=str)
    args=parser.parse_args()
    try:
        export(args.concept,args.submissions)
    except Exception:
        raise SystemExit('검증 증거 내보내기에 실패했습니다. 환경과 제출 식별자를 확인해 주세요.') from None
