# DEMO-001 시드 실행
- root 작성, docs08 계약. UUIDv5·2026-09-21 고정시각·난수20260921.
- PostgreSQL 시연 DB 초기573행 생성, 동일 실행0행 생성(existing261개 직접조회, 자식생략). 6매장/10계정/4카테고리/10보호이미지/4Reference/30과거제출/24Mock평가/6종료실패fixture/8주Mock매출/가상재고/이슈/알림/공지/감사.
- `pytest server/tests/test_seed.py -q --tb=short`: PASS. 수정 매장명·snapshot 불변, DB 행 수 동일, 모든과거평가Mock, Reference/제출media 교집합0, issue/action 시간순서, credentials0600.
- `.local/demo-credentials` 비밀번호는 무작위 최초생성·재실행 보존, 소스/콘솔/기록에는 원문 없음.
- 생성 이미지의 원본SHA/decode/approved 상태 검사 후 정규화·보호저장. 부분 적재 실패 시 이번에 새로 생성한 보호파일만 정리한다.
- 브라우저 인수는 storeloop_test/.local/test-media에 별도로 적재하여 시연 DB 보존. 실제 AI source_kind는 작업자만 생성한다.
- 상태 REVIEW: 독립 데이터·업무 관계 검수와 브라우저 표시 증거는 후속.
