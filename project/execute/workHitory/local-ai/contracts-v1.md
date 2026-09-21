# contracts-v1: AI·데이터·검증 공통 계약

- 담당: contract_ai
- 체크리스트: ../../checkList/local-ai/contracts-v1.md
- 현재 상태: RUNNING / 문서 작성 중, 구현 없음

## 2026-09-21 준비 및 변경 제안 AI-001

- 00→01→02 및 사용자 목표 파일을 읽었다. 기존 project에는 실행 소스/AI/시드/검증 후속 문서가 없다.
- 변경 전: AI의 개념 구조만 있고 출력 필드·참조 검증·시도 만료와 상세 검증 계약이 없다.
- 변경 후 계획: docs/07에 JSON Schema와 내부 multipart·오류·상태 전이, docs/08에 시드/이미지, docs/09에 인수 기준을 정의한다.
- 근거: 01의 실제 Codex 이미지 분석, 모델 120초/HTTP 130초/대기 180초, 영속 작업자·시도 이력·권한 제한을 구체화한다.
- 영향: DB/API, 모든 시안, AI/작업자, 데이터/이미지, 테스트/매뉴얼. 구현은 G1 확정 이후다.
- 로컬 읽기 조사: `/opt/homebrew/bin/codex`, `codex-cli 0.154.0`. `codex exec --help`에서 `--image`, `--output-schema`, `--output-last-message`, `--sandbox read-only`, `--ephemeral`, `--ignore-user-config` 확인. `codex login status`: ChatGPT 로그인 상태. 인증 파일·토큰은 읽지 않았다.
- CLI는 PATH alias 생성 권한 경고를 냈으나 도움말·버전·로그인 상태 명령은 exit 0. 실제 모델 실행/이미지 인수는 아직 NOT_RUN이며 로그인 상태만으로 모델 가용성을 보장하지 않는다.
- OpenAI Docs skill을 읽었고 상위 도구 지침과 부모 지시에 따라 로컬 CLI 조사 우선. 별도의 모델/API 구현·호출은 하지 않았다.
- 문서 검증 계획: 05/06/04의 필드·상태 대조, 스키마 JSON 파싱, 상대 링크 존재 검사. 문서 작업에는 형식적인 코드 테스트를 추가하지 않는다.

## 변경 전파

전파 전체 추적표 소유자는 root이며 이 파일에는 발신/수신 사실만 기록한다. AI-001을 contract_data·product_design·root에 전달하고 각 수신·반영 증거를 받는다.

## 2026-09-21 AI-001 / DATA-001 / QA-001 초안과 교차 조정

- 생성: docs/07-ai-processing.md, docs/08-data.md, docs/09-validation.md. API/DB 이름을 기준으로 `ReviewResult.result`, `attempt_number`, `rule_key` 최대80자를 사용한다.
- contract_data가 AI-001 구조·rate0..100 소수1자리·attempt enum 수신·반영 확인. product_design이 AI-001 수신, 화면/결과 계약 반영 확인. root도 동일 rate 단위를 승인했다.
- root의 실행10 계약 수신: PostgreSQL55432, API8000/AI8010, front5173~5177, 독립 Python 환경, .local 비밀, 별도 test DB/media를08/09에 반영했다.
- PD-001 docs03의 R-M01..24/AT-01..24, R-S01..02/AT-S01..02를 읽고09 추적표 정본으로 참조한다. 실제 AI 브라우저 인수는 각 시안의 제출→재제출→관리자 확인이다.
- 독립 검토자 contract_data 1차 수정 반영: model_result 필드명, attempt_number, rule_key80, CLI120초/Attempt.deadline130초/lease140초 구분, discarded는 본문 없는 안전 로그, retry 현재Job 시각/오류 초기화.
- 상위01과 양립하도록 첫 attempt는 점유 시 생성하고 retry는 queued attempt를 예약한다. 큐 만료는 job failed/attempt expired로 통일하며 시작되지 않은 시도 started_at은 null이다.
- 로컬 도움말 이후 공식 OpenAI 비대화형/설정 참조를 열어 output-schema/last-message 및 shell_tool/project_doc_max_bytes 설명을 확인하고07에 출처 링크를 남겼다.
- 실제 CLI 모델 요청·소스·마이그레이션은 아직 실행하지 않았다. 문서만 REVIEW 예정이며 G1 확정은 root의 독립 검토 반영 후다.

## 검증·인계

- 문서 내부 JSON code block은 Python json.loads로 정상 파싱. 07/08/09의 상대 Markdown 링크 존재 검사 PASS. 03의 AT-01..24 및 AT-S01..02가 09에 모두 포함되어 추적 ID coverage PASS.
- contract_data의 독립 검토 `../db-schema/independent-ai-review.md`는 AIR-01~05 및 retry 현재Job 초기화 재확인 후 PASS, 미해소 차단 없음이라고 회신했다. 실제 실행검증은 NOT_RUN으로 유지한다.
- DOC-EXEC-002 수신 확인: 08 시드 명령을 `server/.venv/bin/python -m server.seed`로 정합화했다. root의 shared validator 소유권 결정을07 §9에 추가했다.
- 현재 상태 REVIEW. AI·데이터·검증 계약은 독립 검토를 통과했으며 공통 G1 확정/후속 담당자 전파 등록은 root가 마무리한다.
- 추가 schema 구조 검사: 모든 중첩 object에 additionalProperties=false이고 required 집합=properties 집합임을 재귀적으로 검증하여 PASS. 실제 모델/JSON Schema 라이브러리 실행 검증과 구분한다.
