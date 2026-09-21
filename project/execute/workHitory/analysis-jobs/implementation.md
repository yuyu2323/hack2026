# 분석 작업자·재처리 구현

- 담당 contract_ai, 상태 RUNNING. root에서 단일 소유권을 인계받았다.
- 수정 범위는 service.py/worker.py/작업 테스트이며 모델은 contract_data 소유다.
- retry_job(db,account,job_id,reason,idempotency_key,request_id) -> (AnalysisJob,replayed) 인터페이스를 사용한다. 권한·잠금·멱등·감사·commit을 담당한다.
- business_common의 lock_idempotency/save_idempotency/request_hash/audit 재사용, method+실제대상ID를 hash에 넣고 기존 종료 시도를 보존한다.
- ServiceStatus worker heartbeat와 model의 last_success_at/last_failure_at/error_code를 갱신한다. 사진·질문·결과·전체 stderr는 운영 상태에 넣지 않는다.
- 네트워크 대기 중에는 DB transaction/lock을 유지하지 않는다. 성공 저장 시 현재 attempt/worker/deadline/lease 및 Review unique를 다시 검사한다.
- PostgreSQL은 postgres_db의 전용 테스트 schema를 사용하고 --tb=short로 비밀을 출력하지 않는다. SQLite로 동시성 인수를 대체하지 않는다.

## PostgreSQL TDD와 HTTP 경계

- 전용 PostgreSQL 임시 schema에서 상태 전이 11개 RED 확인: 점유·재처리·만료·저장 함수가 동작하지 않아 기대 상태/횟수와 불일치했다.
- 짧은 job→attempt 잠금 순서, SKIP LOCKED 점유, 계정+job 직렬 재처리, 기존 종료 시도 보존, 큐/lease 만료, 130초 결과 수용 상한, 공유 schema/참조 재검증, 후처리 rollback을 구현했다. 11개 GREEN.
- 실제 보호 미디어 파일 연결·hash 검증, HTTP 대기 중 별도 DB 연결의 NOWAIT job 잠금 획득, heartbeat, task 취소 후 lease 복구, 고정 오류 메시지, multipart 실제 바이트/metadata/토큰, busy·인증·timeout·본문 상한 검사를 추가했다.
- 자기 검토에서 내부 AI envelope의 `model/duration_ms`와 DB의 `model_name/latency_ms`를 혼동한 매핑을 발견했다. 실제 계약 envelope를 넣은 테스트 RED를 확인하고 저장 경계에서 명시적으로 매핑했다.
- 최종 명령: `PYTHONPATH=. server/.venv/bin/python -m pytest server/tests/test_analysis_jobs.py server/tests/test_worker_http.py -q --tb=short`. 결과 24 passed (실제 모델 테스트 추가 전). 외부 모델 호출은 포함하지 않는다.
- 운영 담당의 별도 API 통합 PASS: 실제 로그인/CSRF→retry 202, 동일 key replay·동일 attempt, 과거 expired 보존, 운영 본문 비노출. 근거 `server/tests/test_operations.py::test_operator_retry_api_replays_same_attempt_and_omits_business_body`.

## 실제 worker 통합 시도

- 최신 AI 서버 재시작: PID 41350, tool session 67243, localhost:8010. 기존 PID 26801이 해당 리스너임을 확인한 뒤 정상 종료했다. 인증 환경값은 출력하지 않았다.
- `STORELOOP_RUN_REAL_AI=1 ... test_real_worker_generated_images_to_postgres` 구현. 실제 모델 응답을 검증하고 Review/Criterion 저장 및 safe metadata 증거를 기록한다. 기본 테스트 실행에서는 명시적으로 SKIP한다.
- 승격 요청은 자동 승인 검토에서 거절됨. 사유: 외부 Codex 모델로 이미지·질문·기준 전송에 신뢰 가능한 사용자 메시지의 구체적 payload/destination 승인이 없다고 판단. 요청에는 goal 3·4·7, 이미 승인·성공한 동일 합성 이미지 2개·Codex 인증 모델 목적지, 전용 테스트 DB를 적었다.
- 거절된 호출을 우회하거나 다른 경로로 재실행하지 않았다. 실제 worker 통합은 NOT_RUN이며 root에 차단 이유를 전달했다. 별도 local-ai의 실제 HTTP 모델 PASS 증거와 worker PostgreSQL 검증 PASS는 그대로 구분하여 보존한다.

## 추가 회귀와 승인 해결

- SKIP LOCKED의 잠긴 선두 작업 건너뛰기, 동일 결과 동시 저장 1회, 후처리 도중 기한 초과 시 전체 rollback, 재처리 예약의 대기 만료를 검증했다. 최신 회귀 결과: 28 passed, 1 skipped(실제 모델), 2 dependency deprecation warnings.
- root가 payload/destination과 호출 범위(작업자 1회 및 5개 시안 제출·재제출)를 사용자에게 명시적으로 질문했고, 사용자가 “실제 AI 검증 호출 승인”이라고 답했다. 이 승인 내용을 같은 명령의 재심사 justification에 적어 자동 승인 검토를 통과했다. 다른 전송 경로나 우회를 사용하지 않았다.
- 승인된 동일 합성 이미지 두 장으로 실제 worker 통합 검증 실행 중. 결과는 아래 최종 기록 및 evidence 파일로 확인한다.

## 최종 실제 통합 결과와 REVIEW 인계

- 사용자 명시 승인으로 동일 실행 재심사 승인 후 실제 테스트 **1 passed**. 증거: `evidence/real-worker-001.json`.
- 2026-09-21T09:12:14Z, gpt-6-astra, worker 총 25,805ms / 모델 25,472ms. 이번 단일 기준 사례는 30초 목표 달성. 앞선 2기준 HTTP 조기 사례 36,089ms 미달을 지우지 않았다. 어느 결과도 브라우저 표시 시간을 포함하지 않는다.
- before/reference SHA가 manifest와 일치하고, frozen 질문·기준·Reference를 전달했다. 모델은 사진 1의 앞줄 불균일 및 Reference와의 차이를 설명했다. 엄격 schema·입력 참조 재검증 PASS, Review 1·Criterion 1·Notification 1 저장, attempt succeeded/result_applied=true. unknown/확인 필요가 없어 자동 Issue 0은 정상이다.
- 전용 PostgreSQL 테스트 schema는 fixture 종료 후 삭제했다. 원본 인증값·전체 prompt·stderr·DB 연결 자격값은 증거와 로그에 없다.
- CLI `PYTHONPATH=. server/.venv/bin/python -m server.analysis_jobs.worker --help` PASS. 운영 retry 인터페이스는 별도 API 통합 PASS로 확인했다.
- 현재 상태 REVIEW. 코드 경계: service.py의 retry_job/claim_next_job/sweep_expired/heartbeat/complete_attempt/fail_attempt, worker.py의 load_request/call_analyzer/process_claim/run_worker. 공유 validator는 packages/review_contract에서 재사용한다. root의 독립 구현 검토·5개 시안 브라우저 인수로 인계한다.
- 유지 중인 AI 서버: PID 41350/session 67243/localhost:8010. 별도 worker daemon은 시작하지 않았다. root 실행 오케스트레이션에서 `python -m server.analysis_jobs.worker`로 시작한다.
