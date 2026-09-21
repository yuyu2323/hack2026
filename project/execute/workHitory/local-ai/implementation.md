# 로컬 AI 서버·공유 평가 계약 구현

- 상태: RUNNING, G1 ACCEPTED 확인 후 구현 착수
- 기준: AI-001/DATA-001/QA-001 및 CONTRACT-DATA-1.0b
- 범위: ai-service, packages/review_contract 단일 소유

## 설계 및 초기 계약 반영

- root의 G1 ACCEPTED 등록과 project/AGENTS.md를 읽었다. 새 서비스를 실제 구현하되 DB/worker 저장은 root 소유다.
- CONTRACT-DATA-1.0b 수신: 멱등 hash에 HTTP method/target ID, Reference state_version 충돌 보호. AI snapshot 구조는 변경 없음. docs07 멱등 참조 및09 해당 회귀 범위를 보완한다.
- AI 서버는 dotenv와 환경 설정을 지원하되 환경 우선. Codex subprocess에는 업무 DB/AI 내부토큰을 상속하지 않는다.
- Python 공유 인터페이스는 docs07 §9 정본대로 만들고 양쪽 venv Pydantic 호환 버전 설치를 root에게 요청한다.

## TDD 및 설정

- ai-service/requirements.in 작성 후 root가 독립 .venv 설치 및 requirements.lock 고정. `.local/runtime.env`는 root가0600 생성, dotenv보다 환경변수가 우선한다.
- 사용자 Codex config의 모델/모델제공자/추론설정 허용키만 조회: gpt-6-astra/xhigh. 모델 이름을 그대로 사용하고 사진검토는 low reasoning으로 설정해 실제 검증한다. 원시 인증파일은 읽지 않았다.
- 공유 계약 RED: 표준 unittest로 중복 JSON 키와 필수 기준 누락이 거절되지 않는 실패2개 확인. pytest 설치 진행 중 실패는 RED에 포함하지 않았다. Pydantic strict/추가필드/UUID/길이·범위/중복·참조·부모·점수 구현 후16 tests PASS.
- HTTP·이미지 RED: 인증없는요청200, metadata미검증, byte hash/MIME/확장자/손상/크기미검증 등10개 실패 확인→구현후10개 PASS.
- 어댑터 RED: 실제 실행인터페이스 미구현으로7개 실패→서브프로세스/환경allowlist/argv/stdin/출력검증/timeout구현. test executable shebang에공백있는venv경로가 들어가는 fixture 문제를 실제Python실행경로로 수정.
- 명령: `ai-service/.venv/bin/python -m pytest ai-service/tests -q` (project 기준). 현재33 PASS, 설치 라이브러리의 TestClient deprecation warning2개. 성공테스트는 fake executor를 명시하며 실제모델성공으로 대체하지 않는다.
- 서버 `PYTHONPATH=. ai-service/.venv/bin/python -m uvicorn app.main:app --app-dir ai-service --host 127.0.0.1 --port 8010 --no-access-log`: sandbox bind EPERM 후 자동검토 승격 승인으로 loopback 실행 성공.

## 실제 AI 조기 검증 권한·진행

- demo-images 담당이 beverage-before-01/reference-01 생성·시각검수·manifest를 인계했다. 각각서로다른hash이며 실제인물/영업정보가없는합성매대다.
- 초기 sandbox의 localhost HTTP 요청은32ms에 연결 실패. evidence/real-ai-early-001.json에 FAIL 기록, 모델실행증거로 사용하지 않는다.
- 첫 승격 smoke요청은 자동승인검토가 'goal파일읽기만승인했고해당payload 외부전송권한불명확' 사유로 거절했다. 우회하지 않았다.
- 읽기조사로 사용자가 지정한 goal-objective1행(완성본구현검증),71행(실제사진·Reference AI전달),149행(개발초기실제AI검증) 및 사용자기준01§5.1(로컬Codex+인증모델서비스),manifest 합성이미지출처·hash를 재확인했다.
- 동일명령/동일목적지의 승인 justification에 위 증거를 제출한 재심사는 승인되었다. 인증/원문프롬프트/전체stderr를출력하거나별도우회하지않았다. 실행결과는다음기록에추가한다.

## 실제 결과와 자기 검증 완료

- `evidence/real-ai-early-002.json`: 실제 HTTP 200 PASS. Codex CLI 0.154.0 / gpt-6-astra, HTTP 36,089ms / CLI 35,762ms. 30초 목표는 미달이며 브라우저 표시 시간과 혼동하지 않는다.
- 제출·Reference 실파일 각각 전달, 엄격 JSON Schema와 모든 기준/Reference ID·사진 position 검증 PASS. 질문 답변·2개 fail 기준·사진 1 근거·개선 행동·Reference different 결과를 받았다. 직접 본 제출 사진의 중앙 빈 공간과 앞줄 불균일이 관찰 문장과 대응한다.
- 보완: Content-Length 없는 본문의 스트리밍 크기 제한, 중복 metadata JSON 422, 동시 분석 busy, 도구 실행 이벤트 차단, 호출 취소와 자식 프로세스 그룹 정리. 자식 종료 검증은 문서화한 3초 정상 종료 유예가 지난 뒤의 생존 여부를 검사한다.
- 최종 명령: `ai-service/.venv/bin/python -m pytest ai-service/tests -q --tb=short`. 결과 39 passed, 설치된 Starlette/TestClient의 deprecation warning 2개. 실제 모델 조기 성공은 별도 위 증거로 구분한다.
- 후속 worker 소유권을 root에서 인계받았다. 분석 작업 TDD·실제 PostgreSQL 통합은 analysis-jobs 체크리스트·이력으로 분리한다.

## 작업자 통합과 REVIEW

- `server/analysis_jobs`에서 같은 validator를 호출하는 실제 PostgreSQL 통합 PASS. 사용자 명시 승인 이후 재심사를 통과한 호출이며, `execute/workHitory/analysis-jobs/evidence/real-worker-001.json`에 25,805ms·model gpt-6-astra·사진/Reference hash·원자 저장 결과를 기록했다.
- AI 테스트 39 PASS, 작업자 PostgreSQL/HTTP 회귀 28 PASS, 기본 실행의 실제모델 1 SKIP, 별도 승인 실제모델 1 PASS. 처리 시간 36.1초/25.8초는 각각 다른 기준 개수의 실측값이며 30초 달성을 일반화하지 않는다.
- 현재 상태 REVIEW. 8010 최신 서버 PID 41350/session 67243을 root 실행 오케스트레이션에 전달했다. root의 독립 구현 검토 및 5개 시안 실제 브라우저 검증이 뒤따른다.
