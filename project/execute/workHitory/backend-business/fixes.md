# 독립 검수 결함 수정
- BI01: 제출시각 이전 latest 기준버전으로 시드snapshot 고정. 원본사용자행을 덮어쓰지 않음. 독립 RED→GREEN.
- BI02: 해결상태의 최종 resolution 값 검증, null 명시도422. 독립RED2→GREEN2.
- BI04: 기준지역필터에 매장소속지역 포함, 매장필터에 해당REGION만 허용. 독립RED2→GREEN2.
- MEDIA-CLARIFY1: docs06먼저확정, 응답누락RED→business7PASS, snapshot/history불변 별도독립PASS.
- seed경계: 30과거제출+장기대기fixture/기준도입전Mock2개. 기존30은보존. 기대32 RED→seed1PASS. 초기장기대기는worker시작시정상 QUEUE_TIMEOUT으로만료되며 실제AI를자동호출하지않음. 새큐화면은브라우저실제제출에서도검증.

### 시드 정정의 독립 검토·적용 및 미래 Reference 회귀
- root가 contract_data 작성 repair_seed_fixtures.py 전체를 독립 검토: 원본 UUID/본문/해시/사진/버전/Mock 여부·외부 의존성 대조, 일반 seed 분리, dry-run 기본, 원자 commit 및 0600 백업을 확인.
- 격리 테스트 `python -m pytest server/tests/test_seed_repair.py -m 'not postgres' -q --tb=short`: 10 PASS. 작성자의 PostgreSQL 1 PASS는 별도 증거이며 재집계하지 않음.
- 두 로컬 DB alias demo/test dry-run 각각 12개 합성 제출·40행만 대상. 각 apply 성공, 재실행 0행. JSON 지문 보고서는 같은 폴더 seed-repair-*.json, 원본 백업은 공유하지 않는 .local/seed-repair-backups/{demo,test}/ (0600).
- 일반 seed에 새 경계 fixture를 추가할 때 현재 Reference가 과거 날짜에 섞이는 후속 결함 발견. 시간필터 회귀 assertion RED → historical_versions에서 created_at 필터·position 재정렬 → test_seed.py 1 PASS. 기존 context를 재작성하지 않는다.

### SR-01 내부 건강조회 프록시 차단
- 독립 product_design transport 회귀가 환경 HTTP_PROXY로 내부 인증 요청 전달을 재현.
- operations.service_dashboard의 httpx.get에 trust_env=False 적용. 인증 계약은 유지.
- 보안 회귀+운영 비PG 11 PASS, 격리 PG 운영 동시성1 PASS. 최초 mixed 실행은 sandbox PG 연결불가1건이었으며 escalation으로 해당1건 재검증.
- 테스트 API root 프로세스를 정상 종료 후 수정본으로 재시작(새PID28285); 실제AI 대기 없는 시점에 수행.
