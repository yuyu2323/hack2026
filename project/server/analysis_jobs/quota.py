"""공개 시연의 전역 UTC 일별 신규 분석 요청을 원자적으로 제한한다."""
from server.core.config import get_settings
from server.core.db import utcnow
from server.core.errors import ApiError
from server.analysis_jobs.models import DailyAnalysisUsage


def consume_public_analysis(db):
    if not get_settings().demo_public_access_enabled:
        return
    if db.get_bind().dialect.name == 'postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    stmt = insert(DailyAnalysisUsage).values(day=utcnow().date().isoformat(), used=1)
    stmt = stmt.on_conflict_do_update(index_elements=['day'],
        set_={'used': DailyAnalysisUsage.used + 1}, where=DailyAnalysisUsage.used < 20)
    if db.scalar(stmt.returning(DailyAnalysisUsage.used)) is None:
        raise ApiError(429, 'DEMO_DAILY_LIMIT', '오늘의 공개 시연 분석 한도 20회에 도달했습니다. 내일 다시 이용해 주세요.')
