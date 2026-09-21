# 09. 검증·실제 AI·5개 시안 인수 계약

- 버전: QA-001 / 1.0.1 / 2026-09-21 / G1 ACCEPTED, CMD-01 실행 안내 정합화 (contract-register 추적)
- 상위 기준: [00](00-vision.md), [01](01-architecture.md), [02](02-development-orchestration.md).
- 수용 기준 ID의 정본은 [03 §3·4](03-requirements.md), 화면은 [04](04-screens.md), 데이터/API/AI/실행은 [05](05-database.md)·[06](06-api.md)·[07](07-ai-processing.md)·[08](08-data.md)·[10](10-execution.md).
- 소유자: 검증 담당. G1 작성 당시 실제 실행은 NOT_RUN이었다. 현재 결과는 [전체 체크리스트](../execute/checkList/orchestration/master.md)와 시안별 검증 보고를 따른다. 이 문서 작성·수정 자체는 테스트 통과 증거가 아니다.

## 1. 판정·독립성·격리

검증 결과는 `PASS|FAIL|BLOCKED|NOT_RUN`. 인증·환경·선행 기능이 없으면 BLOCKED 또는 NOT_RUN이며 Mock 검증을 실제 AI/브라우저 PASS로 바꾸지 않는다. 한 시안의 성공은 다른 시안의 성공이 아니다. UI를 API 요청만으로 대체하거나 DOM 존재만으로 디자인 검수를 끝내지 않는다.

구현자는 의미 있는 TDD RED→GREEN→REFACTOR→통합 증거를 남긴다. RED는 기능 부재/결함 때문에 기대한 assertion이 실패해야 한다. import/의존성 오류만 난 것을 기능 RED로 기록하지 않는다. Python 도메인·AI·시드 로직은 pytest, React 동작은 Vitest/Testing Library, 최종 브라우저는 Playwright를 기본으로 한다. UI/이미지 산출물은 사전 기준과 실제 시각 검수로 확인한다.

기능 인수 담당은 해당 구현자와 달라야 한다. 최종 디자인 검수자는 해당 디자인/개발자 및 기능 인수 담당과 구분한다. 가용 슬롯이 부족하면 같은 독립 담당자가 여러 시안을 순서대로 확인하되 시안별 보고서는 분리한다. root가 배정과 증거를 추적한다.

전용 PostgreSQL 포트 55432의 `storeloop_test`를 사용한다. pytest는 `STORELOOP_TEST_DATABASE_URL`을 환경변수, 없으면 `.local/runtime.env`에서 읽고 DB 이름의 `_test` 접미사를 검사한 뒤 `test_UUID` 스키마를 생성·검증·삭제한다. 브라우저 인수는 같은 전용 테스트 DB와 `.local/test-media`에 준비한 합성 자료를 사용하며 pytest의 임시 스키마와 구분한다. 시연 DB와 미디어를 reset하지 않는다. DB 초기화·같은 계정/매핑 변경은 직렬화한다. 실제 AI는 기본 concurrency 1을 지키며 5개 시안 요청을 순서대로 실행한다. 각 역할·시안은 별도 브라우저 context/session. Cookie/CSRF/token 포함 raw trace·네트워크 기록은 추적/공유하지 않는다.

## 2. AT 추적표

아래 AT 정의는 [03](03-requirements.md)를 참조하며 축약으로 요구를 줄이지 않는다. 실행 결과는 `AT-NN-C01` … `C05`로 시안별 분리한다.

| AT | 주된 검증 계층·증거 |
|---|---|
| AT-01 | 5개 개별 npm build/dev/preview, 한 dist·역할 경로·공통 API 연결; 정보 구조 비교 캡처 |
| AT-02 | 계정 단위/HTTP 통합 + 로그인/로그아웃·CSRF 브라우저 |
| AT-03 | 모든 역할×목록/상세/집계/변경/미디어 보안 행렬 + 기존 로그인 권한 변경 |
| AT-04 | 계정/역할/매핑 mutation·감사 원자성 + 운영 UI |
| AT-05 | 4개 이상 카테고리·기준 정보 비활성·FK 보존·신규 입력 거절 |
| AT-06 | PostgreSQL 동시 OFC 후보 등록 + 해당 지역 후보 제한·등록 후 본문 접근 |
| AT-07 | 4단계 우선순위·동일 rule_key·불변 version·신규/기존 snapshot 비교 |
| AT-08 | Reference upload/교체/비활성·범위·실제 바이트·과거 hash 보존 |
| AT-09 | 사진/질문 경계·미리보기·순서·중복 제출·snapshot·실제 protected media |
| AT-10 | 실제 Codex 이미지+질문+기준+Reference·schema·ID/버전/사진 참조·DB 저장 |
| AT-11 | queued/running/poll 종료·30초 지연·재접속·실측 시간 표 |
| AT-12 | pass/fail/unknown·근거/행동·누락기준·점수·confidence·OFC 동선 |
| AT-13 | parent 새 제출·이력·사진·동일/변경 기준 비교·과거 불변 |
| AT-14 | owner_question/ai_review_required·상태/담당/조치·AI 원본 불변 |
| AT-15 | 관제 숫자→동일 필터 목록→근거·미제출/실패/unknown 분리 |
| AT-16 | 정확한 집계·결측·n<3·분산0·Mock 시각화·기본 기간 리포트 |
| AT-17 | 앱 수신자·읽음 분리·대상 현재 권한 재검증 |
| AT-18 | 서비스 프로세스·CLI 설치·실제 모델 최근 결과·worker heartbeat·fixture 분리 |
| AT-19 | PostgreSQL 점유/재처리/중단/timeout/late result 전체 경쟁 시험 |
| AT-20 | 운영 변경 actor/target/time/reason/outcome와 본문/비밀 미포함 |
| AT-21 | 두 번 시드·새 데이터 보존·manifest·10개 실생성 이미지·시각 검수 |
| AT-22 | 시안별 독립 디자인 검수·모바일/desktop·키보드·상태 캡처 |
| AT-23 | 각 시안 실제 AI 제출→재제출→관리자 확인, 설치부터 시연·HTML 매뉴얼 |
| AT-24 | secret 검사 합성 차단·산출물 검수·계약 전파·정직한 상태 |
| AT-S01 | 운영 공지 게시기간/활성/감사·사용자 표시 |
| AT-S02 | URL filter/page 복귀·재조회 상태·비강제 초점 |

## 3. 단위·HTTP 검증

| 세부 증거 ID | 검증 동작 | 연결 AT |
|---|---|---|
| U-AUTH01 | 세션 random/hash·만료·폐기·로그인 교체·비활성 계정; CSRF 누락/오류·Origin 불일치 | 02/03 |
| U-SCOPE01 | owner 매핑/OFC 담당/지역/HQ/운영자 현재 범위; 권한 감소·인접 ID 추측 | 03/04/06 |
| U-MEDIA01 | 0/6장·10MiB 경계·합계·잘못된 MIME/확장자/디코딩·압축폭탄·EXIF·path traversal | 08/09 |
| U-GUIDE01 | CATEGORY>STORE>REGION>HQ, 같은 rule_key·범위 충돌·Reference 선택·과거 snapshot | 07/08 |
| U-AI01 | JSON strict parsing·unknown/extra field·누락/중복 기준·틀린 version·사진 index 0/N+1·Reference ID 위조·NaN | 10/12 |
| U-AI02 | pass/fail 근거·fail 행동 요구, unknown·빈 기준·빈 Reference·null 점수·소수 1자리·low confidence | 12 |
| U-AI03 | argv/stdin 분리·실제 이미지 순서·제출/Reference mapping·timeout 자식 kill·임시 파일 cleanup | 10/19/24 |
| U-AI04 | binary 없음/auth/nonzero/empty/invalid JSON/schema/네트워크·busy를 안전 오류로 변환 | 10/18/19 |
| U-METRIC01 | 준수/판단가능 분모·unknown 제외·주차 상관·결측·n2·분산0·필터 범위 | 12/15/16 |
| U-WORKFLOW01 | 이슈 상태·해결사유·조치 보존·수신자 dedupe/현재 권한·공지 유효기간 | 14/17/S01 |
| U-SEED01 | deterministic ID/값·2회 멱등·사용자 수정 보존·credential 생성/재사용·manifest 역할 hash 충돌 | 21/24 |
| U-UI01 | 업로드 미리보기/순서/검증·mutation 중복방지·2s polling 종료·empty/loading/error/unknown·키보드 | 09/11/12/22 |

executor double/시간 제어/HTTP fixture를 쓰는 단위 테스트는 명시적으로 Mock이다. 지연을 짧게 설정한 오류 시험은 실제 120초 모델 timeout의 실측으로 보고하지 않는다. 서버/AI가 같은 schema를 공유하거나 스키마 hash로 호환성을 검증한다.

## 4. PostgreSQL 필수 통합 시험

실제 PostgreSQL에서 `FOR UPDATE SKIP LOCKED`, 부분 고유 제약, transaction/CAS를 검사한다. SQLite 통과로 대체할 수 없다. 테스트는 barrier/event로 경쟁 시점을 제어해 시간을 무작정 기다리는 불안정한 테스트를 피한다.

| 세부 ID | 준비·행동 | 기대 |
|---|---|---|
| I-DB01 | 새 테스트 DB migration upgrade→schema 비교 | FK/check/index·revision 정합, create_all 사용 없음 |
| I-WK01 | 2 worker가 같은 queued job 동시 점유 | 한 worker·한 running attempt·한 실제 executor 호출 |
| I-WK02 | failed job에 같은 key 2회 재처리 | 같은 queued attempt/resource 응답; 이전 실패 불변 |
| I-WK03 | failed job에 다른 key 2개 동시 재처리 | 하나 수락, 다른 409; running/succeeded 재처리 409 |
| I-WK04 | 최초 queued 및 retry queued deadline 초과 | job failed/attempt expired QUEUE_TIMEOUT, started_at null |
| I-WK05 | CLI timeout/HTTP timeout | MODEL_TIMEOUT, attempt expired, 자식/임시 파일 정리 |
| I-WK06 | 점유 worker 종료→lease 전 새 worker→lease 후 sweep | lease 전 빼앗기 없음, 이후 failed+expired WORKER_INTERRUPTED; 수동 retry 가능 |
| I-WK07 | attempt1 만료→attempt2 성공→attempt1 결과 지연 | 성공 review/attempt2/종료 attempt1 불변, body 없는 폐기 기록 |
| I-WK08 | 같은 성공 응답 중복 전달 | review 한 개·criterion/issue/notification 중복 없음 |
| I-WK09 | review save 도중 DB rollback·worker 중단 | 부분 결과 없음, 성공 상태만 남지 않음, lease 복구 |
| I-IDEM01 | 사진 제출 same key/same hash vs same key/different hash | 전자는 한 submission/job, 후자는 409; 다른 대상 URL에 같은 key/reason도409; 현재 권한 검사는 재요청에도 수행 |
| I-SNAPSHOT01 | version/reference 교체→신규 제출→이전 job retry | 신규는 최신, 과거/재처리는 옛 ID/본문/hash 유지; Reference 오래된 state_version 변경409 |
| I-AUDIT01 | mutation+audit 중간 실패·정상 변경 | 함께 rollback 또는 함께 commit, 비밀/영업본문 미포함 |
| I-ACCESS01 | 같은 session 중 비활성/역할/매장 변경·미디어 원본/썸네일 | 다음 요청부터 현재 범위 강제; 캐시 응답으로 타 범위 본문 노출 없음 |

추가로 OFC 미배정 동시 등록과 최종 1담당자 제약, 기준 정보 비활성 후 FK 보존, notification 수신자·현재 권한을 검증한다. 재시작·장애 시험은 테스트 worker/AI 프로세스만 대상으로 하며 사용자의 다른 프로세스를 중지하지 않는다.

## 5. 실제 AI 조기 인수

G1 확정 직후 AI 서버를 먼저 구현하고 프론트 완성을 기다리지 않는다. 실행자는 다음 증거를 한 보고서에 남긴다.

1. CLI 버전·저장된 인증의 성공 여부만 확인. 모델 설정·schema/prompt 버전·서버 준비 상태 기록. 인증 원문을 읽거나 복사하지 않는다.
2. 시각 검수된 생성 제출 1장과 **다른 이미지**인 Reference 1장, 적용 기준 ID/version/rule_key, 구체 질문을 준비한다. 파일 hash·dimension·첨부 순서·역할을 기록한다.
3. worker 경로 또는 내부 HTTP의 실제 Codex 실행으로 JSON을 받는다. 모델 실행 event를 확인하되 raw prompt·stderr 전체를 보고서에 넣지 않는다.
4. JSON Schema+참조+의미 검증을 통과하고 request ID→job→attempt→review를 연결한다. 질문 답변과 Reference 비교가 입력에 맞는지 이미지와 결과를 함께 검수한다.
5. 제출 이미지만 다른 것으로 바꾼 시나리오, 기준 version을 바꾼 새 제출, 판단곤란 이미지를 추가 확인한다. 고정 답변/한 입력만 성공하는 경로를 배제한다. 테스트 성공의 기준은 구조·정확한 입력 연결·관찰 가능한 사실이며 모델 문장 동일성이 아니다.

실제 모델 응답에서 관찰과 맞지 않는 판정이 나오면 golden 관찰 사실·모델 출력·실패 범위를 기록하고 프롬프트/검증/UX를 수정한 뒤 재검증한다. 눈에 안 보이는 상품·점수의 정답을 만들어 성공률을 부풀리지 않는다. unknown 시 “OFC 확인 필요” 정상 경로를 검증하되 모델이 반드시 특정 문장을 생성한다고 강제하지 않는다.

30초 목표는 실제 `submit_to_visible_ms`를 시안마다 기록하고 queue/model/DB/poll 시간을 함께 설명한다. early 내부 호출은 model/서버 latency만 측정하므로 브라우저 전체 지연과 별도로 표기한다. 표본별 actual_ms, 목표 내 여부, 이미지수/기준수/Reference수·모델 이름, 시안, 데이터 버전을 기록한다. 평균만으로 timeout을 가리지 않으며 n이 적으면 일반적 성능 보장을 주장하지 않는다.

## 6. 각 시안 브라우저 인수 시나리오

5개 시안 모두 아래 E01~E08을 실제 화면 조작으로 수행한다. 필수 실제 AI 호출은 E01과 E02의 새 제출에서 이루어지며 최소 한 번은 실제 Codex로 끝나야 한다는 상위 기준보다 약하게 해석하지 않는다. 재제출 또한 실제 서비스의 정상 분석 경로로 완료한다. 실제 AI와 기술 장애 fixture 시험 보고서를 구분한다.

| 흐름 | 브라우저 행동·기대 | AT |
|---|---|---|
| E01 기준→첫 평가 | 영업 역할 로그인→4단계 기준/Reference 등록→점주 로그인→매장/카테고리/사진/질문→queued/running→실제 AI 결과→답/근거/행동/Reference 확인 | 02/07/08/09/10/11/12/23 |
| E02 개선→관리자 확인 | after 사진 재제출→parent 연결·실제 AI→전후 비교→OFC 관제 숫자→해당 이력/근거→이슈 조치/해결→점주 이력/앱 알림 | 13/14/15/17/23 |
| E03 기준 보존 | 기준/Reference 변경→신규 제출의 버전/hash 확인→과거 결과 재열람→기준 변경 비교 한계 표시 | 07/08/13 |
| E04 권한 즉시 반영 | 운영자에서 owner 비활성/매핑 변경→기존 owner context 재조회→차단; OFC/지역/HQ 범위 차이와 운영자 영업본문 직접 API/이미지 차단 | 03/04/05/06/20 |
| E05 실패 복구 | fixture인 실패 표시→운영자 reason 포함 retry→실제 실행 결과 상태→과거 attempt 보존; 진행/성공 retry 차단 | 18/19/20 |
| E06 상태 경계 | 빈 매장/이력·로딩·입력 오류·통신 오류·queued 지연·failed·unknown·기준/Reference없음·긴 질문/기준 표시 | 09/11/12/15/22 |
| E07 분석·알림·공지 | Mock 배지·표본/n·결측/상관불가·기본 리포트, 수신함 읽음/타수신자차단, 유효 운영 공지·필터 뒤로가기 | 16/17/S01/S02 |
| E08 실행·매뉴얼 | 개별 build/preview에서 role 경로 직접접속·새로고침; 로컬 HTML 매뉴얼의 링크/실제 버튼/캡처·시연 순서 | 01/21/22/23/24 |

점주 모바일 기준 viewport `390×844`와 `360×800`, 관리자 desktop `1440×900` 및 좁은 화면 `1280×800`에서 주요 동선을 확인한다. resize만으로 모바일 PASS 하지 않고 업로드·결과·재제출을 실제 조작한다. 키보드 탭/초점·폼 label·오류 연결·버튼 accessible name·대비·긴 한국어 줄바꿈·페이지 수평 잘림·이미지 비율을 확인한다. 버튼 최소 크기 등 정확 기준은 해당 컨셉 acceptance의 정본을 따른다.

브라우저 콘솔의 uncaught 오류와 실패한 필수 network 요청을 확인한다. 캡처는 password input에 입력하기 전/로그인 후 영업 합성 데이터 화면만 남긴다. 사용자 인증 상태 파일을 증거에 복사하지 않는다. 실제 Playwright trace를 사용한 디버깅 파일은 `.local`에 보관하고 비밀 제거 검수 후 필요한 화면 증거만 추출한다.

## 7. 실행 명령·증거 규격

아래는 현재 저장소에 제공된 명령이며 모두 `hack2026/project`에서 실행한다. 사전 구성은 [README](../README.md)와 [10](10-execution.md)을 따른다. 실행 명령이 있다는 사실과 해당 인수의 PASS를 구분한다. 명령 변경은 [10](10-execution.md)과 함께 갱신하고 전파한다.

| 목적 | 현재 재현 명령 |
|---|---|
| 업무 단위/HTTP | `server/.venv/bin/python -m pytest server/tests -q --tb=short -m 'not postgres and not real_ai'` |
| AI 단위 | `ai-service/.venv/bin/python -m pytest ai-service/tests -q --tb=short` — fake executor/HTTP fixture이며 실제 모델 호출 아님 |
| PostgreSQL 통합 | `server/.venv/bin/python -m pytest server/tests -q --tb=short -m 'postgres and not real_ai'` — §1의 전용 테스트 DB/스키마 사용 |
| 공통 프론트 클라이언트 | `npm run test:client` |
| 각 시안 일반·UI 검사 | `npm run test --workspaces --if-present`와 `npm run test:ui --workspaces --if-present`를 모두 실행. 시안01의 일반 test만으로 별도 UI 검사를 대체하지 않음 |
| 전체 빌드 | `npm run build` |
| 개별 실행·빌드 인수 | 해당 `web-concepts-0N`에서 `npm run dev`, `npm run build`, `npm run preview`. preview는 build 후 같은 시안 dev를 종료하고 같은 포트5173~5177에서 실행; E08의 직접 경로·새로고침을 실제 조작 |
| 전체 빠른 검사 | `./scripts/verify.sh` — 비밀·훅·실행 스크립트 회귀, 서버/AI 단위, 프론트 일반/UI 검사·빌드 |
| PostgreSQL 포함 전체 검사 | `./scripts/verify.sh --postgres` — 위 검사에 PostgreSQL 추가. 실제 AI·브라우저는 별도 절차이며 verify 옵션으로 제공하지 않음 |

실제 AI는 CLI 로그인, 내부 AI 서버8010, 로컬 토큰 설정과 생성 이미지가 준비된 상태에서 명시적으로 호출한다. 조기 내부 HTTP smoke는 다음과 같다. 출력 파일명의 `YYYYMMDD-HHMMSS`를 실행마다 고유한 값으로 바꾸고 기존 증거를 덮어쓰지 않는다.

```sh
PYTHONPATH=.:ai-service ai-service/.venv/bin/python -m app.smoke --output execute/workHitory/local-ai/evidence/real-ai-YYYYMMDD-HHMMSS.json
```

이 smoke는 실제 모델·JSON Schema·입력 참조·내부 HTTP 지연을 확인한다. worker의 DB 저장과 브라우저 제출→표시 전체 지연은 별도 인수다. 실제 worker→AI→PostgreSQL 검사는 업무 테스트에 있다.

```sh
STORELOOP_RUN_REAL_AI=1 server/.venv/bin/python -m pytest server/tests/test_analysis_jobs.py -q --tb=short -m real_ai
```

환경 플래그가 없으면 실제 AI 테스트는 skip한다. §1의 `STORELOOP_TEST_DATABASE_URL`이 필요하며, 실행 전 `execute/workHitory/analysis-jobs/evidence/real-worker-001.json`이 이미 있으면 별도 파일로 보존한다. 이 테스트의 출력 경로는 현재 고정되어 있다. `ai-service/tests -m real_ai`에는 해당 인수 테스트가 없으므로 그 명령을 실제 AI 검증으로 사용하지 않는다.

현재 시안별 실제 UI 인수는 **Codex in-app Browser의 Playwright 인터페이스**로 §6의 E01~E08을 수행한다. 테스트 DB/미디어와 역할·시안별 context/session을 분리하고 실제 AI concurrency 1을 유지한다. 시안별 `execute/workHitory/integration-concept-0N/browser.md`, 같은 폴더의 `actual-ai.json`, `execute/designReview/concept-0N/evidence/`의 비밀 없는 viewport 캡처에 AT·기대/실제·시간·결함/재검증을 남긴다. 독립 디자인·키보드·모바일 실제 조작·매뉴얼 검수도 필수다.

저장소용 `playwright.config`와 `npx playwright test --project=concept-01` … `concept-05` CLI runner는 현재 제공하지 않으며, 해당 독립 CLI 자동화는 NOT_RUN이다. 이는 실제 브라우저 검증의 면제가 아니다. API 요청이나 DOM 단위 검사로 E01~E08을 대체하지 않는다. DB 결과 메타데이터 보조 추출은 `server/.venv/bin/python -m scripts.export_acceptance_evidence --help`에서 인자를 확인할 수 있지만, 이 도구도 실제 UI 조작이나 화면 표시 시간을 검증하지 않는다.

검증 보고서 위치는 `execute/workHitory/{module-id}/{task-id}.md`, 독립 디자인 보고는 `execute/designReview/concept-0N/review-001.md`와 evidence 폴더, 시안별 기능 증거는 `execute/workHitory/integration-concept-0N/`이다. 실제 문서와 캡처 파일을 만들고 상대 링크를 검증한다.

각 보고서는 소스 상태/빌드 hash(커밋 전이면 대상 파일 hash 목록), 계약·디자인·schema·prompt·seed/manifest 버전, OS/runtime/browser/viewport, 테스트 DB 별칭, 실행 명령(비밀은 env 이름만), AT/세부 ID, 준비조건, 기대/실제, PASS/FAIL/BLOCKED/NOT_RUN, 비밀 없는 출력 요약·캡처, 결함/담당·재현법/수정 후 재검증 결과를 포함한다.

## 8. 결함 수정과 게이트

검증 실패는 재현 조건·원인·영향 시안을 기록하고 파일 소유자에게 전달한다. API/DB/AI 계약 변경이면 문서→수신확인→구현→영향 테스트→매뉴얼 순서로 동기화한다. 테스트를 약화하거나 필수 흐름을 숨겨서 PASS로 만들지 않는다. 공통 모듈 결함은 영향받는 5개 시안에서 회귀 확인한다.

G1은 계약 독립 검토 완료, G2는 TDD·실제 AI 조기 성공, G3는 실제 시드·생성 이미지 연결, G4는 시안별 전체 기능·보안·실제 AI·독립 디자인 및 결함 재검증, G5는 5개 HTML 매뉴얼·실행 재현·비교 자료다. 필수 FAIL/BLOCKED/NOT_RUN이 남으면 프로젝트 완료로 표시하지 않는다. 30초 목표 달성 여부와 별도로 기능·입력 검증 성공 여부를 정직하게 보고한다. 목표 초과는 실제 시간·개선 시도·남은 제약을 기재한다.

원격 보안 설정은 권한 범위에서 확인하고 미적용 원인을 기재한다. 로컬 secret 검사 도구/훅/합성 fixture 차단은 실제 실행으로 확인한다. 원격 공개·유료 구매·파괴적 초기화 등 사용자 결정 사항을 검증 편의를 위해 자동 수행하지 않는다. 최종 프론트 선택은 사용자의 판단이며 기술 인수와 구분한다.
