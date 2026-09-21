# 영업 업무 구현 기록
- 담당 root. G1 전 소스 없음.
- CONTRACT-DATA-1.0a 수신: region/date/is_active drilldown 동일 필터, latest_job, 이슈 담당 후보·상세 경로 보완. 모델/마이그레이션 단일 소유권 유지.
- AI-001 수신: result 모델본문, attempt_number, rule_key80, rate0..100소수1, CLI120/worker결과수락130/lease140초, 늦은 결과는 본문 없는 로그만.
- DOC-EXEC-002: 프로젝트 루트 server.* 패키지, 두 venv, .local/runtime.env env override.
- TDD 및 통합 결과는 실제 실행 후 아래 추가한다.

## BUS-001 구현·검증
- 상태 RUNNING. root 소유의 영업 API(main/guidelines/submissions/reviews/dashboard/issues/notifications/analytics), api-client를 구현했다. analysis_jobs/service·worker와 테스트 소유권은 contract_ai로 인계, 해당 담당의 PG/실제 AI 증거를 참조한다.
- 순수 기준 선택·이미지 검증·상관 계산 RED4→GREEN4. 공백 title 허용 결함은 실패 테스트 재현→문자열 trim/영문 rule_key 계약 적용으로 GREEN5.
- main 조립 전 API테스트4개는 모듈 부재 ERROR(업무 논리 실패와 구분), 구현 후 4 PASS. 이후 기준/Reference 버전·과거 snapshot 보존·현재범위/비활성 이력·이슈 해결/409/알림 포함7 PASS.
- api-client: 쿠키·탭 메모리 CSRF, 변경 직렬화, 403 자동 재전송 금지와 명시 재시도·같은 멱등키 지원. 테스트2 PASS.
- 전체 서버 `pytest server/tests -q --tb=short -m 'not real_ai'`: 추가 업무3개 전 시점64 PASS/실제AI1 deselected. SQLite만42 PASS. 후속 업무7 PASS는 별도 실행 증거이며 전체합계를 임의 합산하지 않는다.
- G1 API context 평탄화·assignees Page를 적용하고 버전보존 API 테스트로 확인했다. Mock/실제 AI source_kind, NULL 지표, 운영자 본문403를 유지한다.
- PostgreSQL production 0001~0004 적용, seed 초기573개 생성·재실행0생성. DB/model 소유자의 independent-review 인수는 남아 있다.
