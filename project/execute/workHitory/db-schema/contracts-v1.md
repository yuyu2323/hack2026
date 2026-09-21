# contracts-v1: DB·API 공통 계약
- 담당: contract_data / 체크리스트: ../../checkList/db-schema/contracts-v1.md
- 상태: RUNNING, 구현 없음

## 2026-09-21 변경 전 기록
- 읽기: 00 → 01 → 02 순서, 첨부 goal-objective 전체. project에 00·01·02 이외 후속 명세 및 구현은 없음.
- 변경 ID: CONTRACT-DATA-1.0
- 변경 전: DB/API는 아키텍처의 개념 수준만 존재.
- 변경 후 계획: 05 DB와 06 API에 필드/관계/제약/인덱스/보존, 세션+CSRF 및 현재 권한, 모든 업무 엔드포인트·집계·오류·멱등·작업/시도를 정의.
- 이유: G1 공통 계약 선행 조건과 독립 구현의 동일 이름/타입을 충족.
- 영향: backend 전체, worker/local-ai, 공통 api-client, 시안 01~05, seed, 통합검증, 매뉴얼.
- 호환: 상위 세 문서 수정 없음. 01 결정인 PostgreSQL/SQLite 제한, DB 세션, 별도 worker, 영업/운영 권한 분리를 유지.
- 검증 계획: 상위 요구 ↔ DB/API, AI 상태/결과와 화면 필드 대조, JSON 예시 파싱, 상대 링크 확인, 독립 검토.
- Git 작업과 모델/migration 작성은 수행하지 않음.

## 전파 기록
- contract_ai: 초안 공통 이름과 상태·AI 필드 협의 요청 전달.
- product_design: prefix/목록/응답/오류와 도메인 API 계획 전달.
- 전체 전파 표 소유자는 root이며 본 이력은 수신·반영 증거만 추가한다.

## 2026-09-21 작성·상호 조정
- 05 DB: 전체 엔티티/필드/FK/check/index/보존/migration, 06 API: 모든 역할 엔드포인트/DTO/오류/세션CSRF/멱등/집계/구현인터페이스 작성.
- AI-001 수신: result 객체·0..100 소수1자리 rate, 큐180/CLI120/HTTP130/lease140/heartbeat10, 최초 Attempt 점유생성·재처리 queued 예약·큐만료 expired 반영. 07-ai-processing.md 정본으로 연결.
- PD-001 수신: 화면에서 필요한 parent/children/context/비교, 이슈조치·알림, 운영 version/impact/can_retry, 최소 후보 데이터 반영.
- DOC-EXEC-001 수신: docs/10-execution.md 및 AGENTS.md 확인. 전용 PostgreSQL 55432, 분리 venv, .local 미디어, 시드 비밀번호 실행 주입·무출력 반영. 구현 경로/기능 축소 영향 없음.
- 구현 인터페이스는06 §9 고정: get_db, Base/SessionLocal, get_current_account/require_csrf/require_roles, accessible_store_ids/require_store_access, ApiError; 모든 domain/models.py 단일 작성.
- 자체 검증은 JSON 예시/상대링크/계약 키 대조 예정. 문서 작성은 실행검증이 아님.
- root 요청으로 본인 작성이 아닌07/08/09 독립 검토를 다음 작업으로 수행한다. 05/06 독립 검토자는 product_design.

## 자체 검증 결과
- Python json.loads로06의 JSON예시2개 파싱 PASS. 05/06 상대 링크 존재 확인 PASS. 잘못 혼입한 다른 언어 표현을 한국어로 교정.
- 05↔06 rate0..100/소수1자리, 상태·재처리예약,07 참조 링크 대조 PASS.
- 이미지 가로/세로32..8192·총4000만pixel, 기준 최대100개 제한을07과 일치시킴.
- 부모/자식 기준 version_id 변경은 criterion_changed=true/change=unavailable로 처리하여 다른 기준의 개선율 오판을 방지(07 규칙 수신).
- 상태 REVIEW. 독립 검토 미완료이며 실행검증은 NOT_RUN.

## root 검토 수신
- 06 §8 미정의 is_active 제출필터 문구 정정: 과거 Submission 목록/상세는 활성 여부와 무관하게 현재 매핑범위로 조회, 대시보드는 활성 매장만 집계. 불필요한 필터 추가 없이 상위의 과거 기록 접근을 유지.
- project루트 server.* 절대 import·모듈실행 경로 수신. G1 후 구현에서 적용.

## 독립 검토 보완 CONTRACT-DATA-1.0a
- product_design 발견: 새로고침용 기준/운영계정 단건 조회, 이슈 담당 후보, dashboard drilldown 필터 및 최신job 누락.
- 06에 GET guidelines/{id}, references/{id}, operations/accounts/{id}, issues/{id}/assignees를 추가. 후보는 현재 활성·매장권한 최소정보만.
- Submission/Issue에 region/date/is_active 필터를 맞추고 dashboard 기본 is_active=true를 반환 필터와 drilldown에 포함. 이력 기본은 활성여부 무관한 현재범위를 유지한다. 이슈 날짜는 연결 제출시각 기준.
- StoreDashboard.latest_job과 IssueSummary 매장/카테고리 최소표시 필드 추가.
- 이유: 요약숫자→동일조건 목록, 직접상세 URL/새로고침, 담당변경 화면의 실제 구현 가능성 확보. 필수 기능 축소 없음. DB 필드 추가 필요 없음.
- 검증 계획: product_design 재검토·04 화면명세에 endpoint/필터 반영, root 구현 수신 확인.

## G2 예정 경계 수신 (아직 미착수)
- root 소유: server/main.py 조립, guidelines/submissions/reviews/analysis_jobs/dashboard/issues/notifications/analytics의 schemas/service/router, seed·통합·보안·설치·lock.
- contract_data 예정 소유: server/core 설정/DB/인증/권한, 모든 도메인 models.py, 단일 migrations, accounts/stores/operations API와 테스트, server/requirements.in.
- core.Settings는 project/.local/runtime.env 기본 읽기+환경변수 override; root가 파일0600을 기존값 보존하여 생성. 모델/코어에서는 실제 비밀을 코드에 기본값으로 쓰지 않는다.
- project 루트에서 server.* 절대 import 및 `python -m server.seed`, `python -m server.analysis_jobs.worker` 사용.
- 공용 AI schema/validator는 contract_ai가 packages/review_contract에 소유, worker/AI가 재사용.

## 독립 검토 보완 CONTRACT-DATA-1.0b
- DR-D05: 멱등 operation은 경로template별 고정값, request_hash에 method/실제target ID 포함. 같은 reason·key의 다른 job/store는409로 구분.
- DR-D06: ReferencePhoto.state_version 추가(활성상태/교체 충돌용), immutable version과 분리. lineage 최신행 잠금+요청id/state_version 검증, 구revision 변경거절, 최신상태만 낙관 갱신. 05/06 DB·API 먼저 수정, 아직 모델 구현없음.
- DR-D07: DB 사전의 길이/NULL/CHECK 상속, extra forbid, login3..80/password12..128/q120, 공백/null/생략/배열중복, 빈PATCH422·실질무변경200 정책 명시.
- 영향: Reference DB모델/공통타입/화면폼은 state_version 사용, 모든 mutation validation·멱등 테스트. product_design 및 root에 전달하고 재검토 요청.

- DR-D03 최종 보완: GET /issues unresolved=true(open+in_progress)/false(resolved), status와 동시 지정422. 미해결 KPI의 정확한 목록 재현 규칙을06에 고정.

## 1.0b 자체 재검증
- 05/06 전체 상대링크 존재와06 JSON예시2개 파싱 PASS. 05 163행/06 238행 상태 기준.
- 모델/마이그레이션 및 Git 작업은 여전히 수행하지 않음.
- root는1.0a/b의 범위필터·Reference state_version·target 멱등 보완 수신/구현반영 확인.
- 테스트 공통 경계 추가 수신: server/tests/conftest.py 단일 소유. 예정 fixture db/client/make_client/account_factory/login_as/postgres_db; SQLite도 Alembic으로구성, 실제 PG는 STORELOOP_TEST_DATABASE_URL의 격리run schema로검증.
