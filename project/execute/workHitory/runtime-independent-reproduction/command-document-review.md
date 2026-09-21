# 실행·검증 명령 문서 독립 대조

검토 범위는 README·docs09/10과 실제 명령/runner/프로세스 운영 방식이다. 원본00/01/02 및 제품·문서는 수정하지 않는다. 요구 감소 없이 현재 구현에 맞는 문구/명령 수정안만 root에게 전달한다. 현재 QA·DB·브라우저·외부 네트워크는 조작하지 않는다.

## 결론

docs09 §7은 G1 때의 예정 명령이 남아 있다. 프로젝트 Playwright Test runner가 설치되어 있지 않은데 실행 명령을 제시하고, 실제 AI pytest의 위치가 틀리며, 시안01 UI 테스트 명령이 빠져 있다. 현재 in-app Browser/Playwright의 실제 화면 인수를 프로젝트 CLI 자동화와 구분하여 명시해야 한다. 상위01의 검증 도구와02 §308의 Playwright 기본 원칙은 유지하며, E01~E08·시안별 실제 AI/재제출·권한·독립 디자인·매뉴얼·정직한 NOT_RUN 요구를 줄일 이유가 없다.

## 불일치와 구체 수정안

| ID | 위치·근거 | 영향·수정안 |
|---|---|---|
| CMD-01 | docs09:128~137의 `npx playwright test --project=concept-01…05`; 프로젝트 config0/spec0, 직접 @playwright/test 의존성 없음 | 현재 실행 가능한 저장소 CLI가 아니다. §7 브라우저 행은 아래 제안 문구로 바꾸고, CLI runner는 미제공/NOT_RUN으로 분리한다. 실제 in-app Browser 도구 사용을 단위 DOM 테스트나 API 호출 대체로 낮추면 안 된다. |
| CMD-02 | docs09:135의 `pytest ai-service/tests -m real_ai`; 실제 collect-only는0/39선택, exit5 | 실제 AI smoke는 `ai-service/app/smoke.py`, 실제 worker 통합 pytest는 `server/tests/test_analysis_jobs.py`에 있다. 아래 명시 명령으로 교체하고 내부HTTP smoke와 DB저장/브라우저전체지연 범위를 구분한다. |
| CMD-03 | README:29/docs09:136의 bare preview; 최초 resolveConfig에서01=5173,02~05=4173 | 초기 Origin5173~5177과 달라 로그인403 위험을 root에게 보고했다. root PREVIEW-PORT-01 제품 수정 후 독립 resolveConfig5개 PASS로 해소했다. 문서의 bare preview는 유지 가능하며 같은 시안 dev 종료 후 preview를 시작한다는 전제만 명확히 한다. 실제 preview 기동/로그인 인수는 아직 별도다. |
| CMD-04 | docs09:136의 `npm test -- --run`만으로 모든 React 동작 검증을 대표 |01 test는 native Node 정책6개이며 UI Vitest는 별도 test:ui다. 실제 명령도6 PASS만 실행됨을 확인했다. --run이 현재Node에서 실패한다는 주장은 하지 않는다. 루트의 test/workspaces + test:ui/workspaces --if-present를 함께 명시한다. verify.sh는 이미 둘 다 실행한다. |
| CMD-05 | docs09:134의 격리 DATABASE_URL/MEDIA_ROOT 설명 | 실제 PostgreSQL fixture는 STORELOOP_TEST_DATABASE_URL을 우선하고 없으면 .local/runtime.env의 같은 키를 읽는다. _test DB 여부 확인 후 임시 test_UUID schema를 생성/삭제한다. DATABASE_URL만 바꾸면 해당 fixture 대상은 바뀌지 않으므로 정확한 키와 수명을 적는다. 브라우저의 storeloop_test/test-media 운영과 pytest 임시schema를 구분한다. |
| CMD-06 | README:9/docs10:11의 Node22+/npm 미명시 | preflight.py:24~25는 Node22.12.0+, npm10.0.0+를 요구한다. Python3.11+/PG14+는 일치한다. 문서 최소 버전을 실제 사전검사와 맞춘다. |
| CMD-07 | docs10:24~30의 setup 범위와 verify 옵션 서술 | setup은 설정/venv/npm뿐 아니라 Gitleaks 다운로드·Git훅 설정·PG시작·migration·seed까지 수행한다. README:17은 DB/seed까지 이미 설명한다. docs10에 전체 포함 범위를 적고2~4단계는 개별 재실행 명령임을 명시한다. verify의 구현된 옵션은 --postgres 하나이며 실제AI/browser는 별도 명령·도구 절차이지 제공되는 옵션으로 오인하면 안 된다. |
| CMD-08 | README:31~36/68~76, services.py:80~86; RUNTIME-01 진입점 변경 | 사용자 start/stop 명령 문법은 그대로다. 내부 API --app-dir ROOT/절대 worker_entry.py는 PID 식별 보존이며 worker 업무 CLI는 유지된다. browser_test_runtime api/worker는 foreground exec이므로 PID관리 start/stop 대상이 아니며 각 터미널에서 종료해야 한다. stop은 SIGTERM 요청 후 즉시 PID파일을 제거하므로 worker 종료를 확인한 뒤 DB stop을 수행하도록 안내한다. 진행중 AI를 둔 종료 실험은 이번 문서 검토에서 실행하지 않았다. |
| CMD-09 | docs09:6의 ‘현재 모든 실제 실행 검증은 NOT_RUN’과128의 계획형 문구 | 현재 early AI/worker/시안별 Browser 증거가 이미 존재하므로 시제가 낡았다. ‘G1 작성 당시에는 NOT_RUN이었다. 현재 상태는 시안별 검증 보고와 master를 따른다. 문서 자체는 PASS 증거가 아니다’로 바꾼다. 개별 남은 FAIL/BLOCKED/NOT_RUN을 일괄 PASS로 바꾸면 안 된다. |

## docs09 §7에 넣을 현재 재현 명령

모든 명령의 cwd는 `hack2026/project`다. 자격값은 명령행/보고서에 넣지 않는다.

```sh
server/.venv/bin/python -m pytest server/tests -q --tb=short -m 'not postgres and not real_ai'
ai-service/.venv/bin/python -m pytest ai-service/tests -q --tb=short
server/.venv/bin/python -m pytest server/tests -q --tb=short -m 'postgres and not real_ai'
npm run test:client
npm run test --workspaces --if-present
npm run test:ui --workspaces --if-present
npm run build
./scripts/verify.sh
./scripts/verify.sh --postgres
```

PostgreSQL 명령은 로컬 설정의 `STORELOOP_TEST_DATABASE_URL`을 사용한다. override가 필요할 때도 같은 환경변수 이름을 사용하고 실제 URL을 문서에 쓰지 않는다. 일반 AI 단위39개는 fake executor/HTTP fixture이며 실제 모델 인수가 아니다.

실제 AI 조기 HTTP smoke의 존재하는 명령:

```sh
PYTHONPATH=.:ai-service ai-service/.venv/bin/python -m app.smoke --output execute/workHitory/local-ai/evidence/real-ai-YYYYMMDD-HHMMSS.json
```

위 출력 파일명은 실행마다 고유하게 정하고 기존 증거를 덮어쓰지 않는다. 독립 AI 서버8010과 CLI인증/내부토큰/합성 이미지가 준비되어 있어야 한다. 실제 Codex 모델을 호출하므로 일반 빠른 검사에 포함하지 않는다. 이 smoke는 내부 HTTP/schema/참조/모델지연을 확인하며 worker DB 저장이나 브라우저 submit-to-visible 전체 검증을 대체하지 않는다.

실제 worker→AI→PostgreSQL 저장 pytest의 존재하는 명령:

```sh
STORELOOP_RUN_REAL_AI=1 server/.venv/bin/python -m pytest server/tests/test_analysis_jobs.py -q --tb=short -m real_ai
```

실제1개가 수집되며 환경 플래그가 없으면 skip한다. 테스트는 `execute/workHitory/analysis-jobs/evidence/real-worker-001.json`으로 고정 저장하므로 재실행 전에 기존 증거 보존을 계획해야 한다. 이 문서 검토에서는 실행하지 않고 collect-only로 위치/선택만 검증했다.

브라우저 행 제안 문구:

> 현재 시안별 실제 UI 인수는 Codex in-app Browser의 Playwright 인터페이스로 E01~E08을 순서대로 수행한다. 로컬 테스트 DB/미디어와 역할별 세션을 분리하고 실제 AI concurrency1을 유지한다. 시안별 browser.md, actual-ai.json, 비밀 없는 viewport 캡처에 AT·기대/실제·시간·결함/재검증을 기록한다. 저장소용 playwright.config 및 `npx playwright test --project=…` runner는 현재 제공하지 않으므로 해당 CLI 자동화는 NOT_RUN이다. UI 조작·실제 AI 재제출·독립 디자인·매뉴얼 인수의 필수 범위는 변경하지 않는다.

보고서 정본은 기존 `execute/workHitory/integration-concept-0N/browser.md`, 실제AI 데이터는 같은 폴더 actual-ai.json, 디자인 캡처는 `execute/designReview/concept-0N/evidence/`다. `scripts/export_acceptance_evidence.py`의 `--help`로 시안번호와 제출UUID 인자가 존재함을 확인했다. 이 exporter는 DB 결과 메타데이터를 기록하며 브라우저 조작이나 표시지연 검증을 대신하지 않는다.

## RUNTIME-01 사용법 영향

- README의 `./scripts/start.sh --concept N`, `./scripts/stop.sh`, `./scripts/db.sh stop` 경로/인자는 변경할 필요가 없다.
- start가관리한서비스는 기존과 같은 PID 파일·프로젝트 marker로 종료한다. 새 worker_entry.py는 기존 main/--once 의미를 보존한다. README는 내부 진입점을 사용자가 직접 교체할 필요 없이 자동 처리한다고 짧게 설명할 수 있다.
- browser_test_runtime의 `prepare`를 먼저 완료하고 `api`, `worker`는 서로 다른 터미널에서 실행한다. 이미 준비된 AI서버와 선택한 Vite가 필요하다. 이 명령들은 foreground이므로 시작한 터미널의 종료로 관리하며, 일반 start의 PID파일로 관리한다고 설명하면 안 된다.
- docs10은 현재 포트가 고정이고 다른 미관리 프로세스를 자동 종료/재사용하지 않는다는 사실을 명확히 할 수 있다. 격리 harness PASS는 기본포트의 전체 setup/start/stop 인수나 clean dependency install PASS를 대신하지 않는다.

## 실제 확인·제한

- Playwright config/spec/직접 의존성0과 lock의 @playwright/test 미설치 확인. lock의 선택적 @vitest/browser-playwright peer 문자열은 프로젝트 runner 제공 증거가 아니다. npx를 실행해 패키지를 다운로드하지 않았다.
- ai-service `--collect-only -m real_ai`:39 deselected/0 tests/exit5. server `--collect-only -m real_ai`: test_real_worker_generated_images_to_postgres 1/103 collected. 실제 모델·DB fixture는 실행하지 않았다.
- smoke CLI/exporter의 --help 성공. 실제 요청/DB export는 하지 않았다.
-01의 문서 프론트 명령을 실행하면 Node 정책6개만 PASS. 실제UI별도 test:ui 필요성만 확인했으며 전체 검증을 반복하지 않았다.
- PREVIEW-PORT-01 root 수정 전 실제 resolved preview포트01=5173/02~05=4173. 수정 후 독립 재확인:01~05 각각5173~5177,host127.0.0.1,strictPort=true,proxy/api→8000 모두 PASS. 실제 preview 프로세스/브라우저 기동은 현재 QA 보호 때문에 NOT_RUN이다.
- 대상 README/docs09/docs10 및 원본00/01/02는 전혀 수정하지 않았다. root가 계약 변경 ID/영향 담당 ACK를 추적하여 반영할 구체 수정안으로 인계한다.
