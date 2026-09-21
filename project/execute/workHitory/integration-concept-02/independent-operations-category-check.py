"""QA02 분류 검증의 공백 고정 오판을 원문 노출 없이 별도 확인한다."""
from pathlib import Path
from datetime import datetime, timezone
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import Category


def main():
    value = dotenv_values(ROOT / '.local/runtime.env')['STORELOOP_TEST_DATABASE_URL']
    url = make_url(value)
    if url.host not in ('127.0.0.1','localhost') or url.port != 55432 or url.database != 'storeloop_test':
        raise ValueError('TARGET_MISMATCH')
    engine = create_engine(value, hide_parameters=True, connect_args={'options':'-c default_transaction_read_only=on -c statement_timeout=10000'})
    with engine.connect() as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        with Session(bind=conn, autoflush=False) as db:
            cat = db.scalar(select(Category).where(Category.code == 'qa02_test_category'))
            result = {'checked_at':datetime.now(timezone.utc).isoformat(), 'read_only':conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on',
                      'category_id':str(cat.id), 'version':cat.version, 'is_active':cat.is_active,
                      'expected_name_matches_ignoring_whitespace': ''.join(cat.name.split()) == 'QA02검증완료분류',
                      'cause':'최초 검증기가 요청에 없는 공백 위치를 추가하여 완전 일치로 비교했다. 공백만 제거해 요청의 식별 이름과 비교한다.'}
    engine.dispose()
    result['status'] = 'PASS' if result['read_only'] and result['version'] == 2 and not result['is_active'] and result['expected_name_matches_ignoring_whitespace'] else 'FAIL'
    path = ROOT / 'execute/workHitory/integration-concept-02/independent-operations-category-correction.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps(result,ensure_ascii=False))
    return result['status'] == 'PASS'


if __name__ == '__main__':
    try:
        ok = main()
    except Exception:
        raise SystemExit('READ_ONLY_CHECK_FAILED: 민감 원문 미기록') from None
    if not ok:
        raise SystemExit(1)
