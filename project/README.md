# StoreLoop

점주의 사진 제출과 AI 피드백, 영업 관리자의 기준·Reference·후속 조치, 플랫폼 운영자의 계정·연결·장애 관리를 하나의 업무 API로 연결합니다. 각 React 시안은 모든 역할 화면을 포함하며 같은 PostgreSQL·인증·AI 작업자를 사용합니다.

현재 구현·검증 상태의 정본은 [전체 체크리스트](execute/checkList/orchestration/master.md)입니다. 아직 검증하지 않은 항목은 완료로 표시하지 않습니다.

## 로컬 실행

검증 환경: macOS arm64, Python 3.13.3, Node 26.4.0/npm 11.17.0, PostgreSQL 16.10, Codex CLI 0.154.0. Python 3.11+, Node 22.12+, npm 10+, PostgreSQL 14+가 필요합니다. Codex CLI는 사용자의 기존 로그인 상태를 이용합니다. 별도 모델 호출 비용·이용량은 로그인된 계정의 조건을 따릅니다.

```sh
cd /path/to/hack2026/project
./scripts/setup.sh
./scripts/start.sh --concept 1
```

`setup`은 버전을 확인하고 로컬 설정, Python 환경 두 개, lockfile의 Python/npm 패키지를 준비합니다. Gitleaks를 설치하고 로컬 Git 훅을 설정한 뒤 프로젝트 전용 PostgreSQL을 포트55432에 구성·시작하여 마이그레이션과 합성 시드를 적용합니다. 기존 외부 DB를 초기화하지 않습니다. 최초 패키지·도구 설치에는 다운로드가 필요합니다. PostgreSQL 실행 파일이 기본 위치에 없으면 `PG_BIN_DIR`을 지정합니다.

설정은 `.local/runtime.env`, 시연 로그인 정보는 사용자 전용 `.local/demo-credentials`에 있습니다. 후자는 JSON이며 로그인 ID마다 `password`를 확인할 수 있습니다. 이 파일의 내용은 캡처·로그·커밋·매뉴얼에 복사하지 마세요. 기존 설정과 비밀번호는 다시 실행해도 유지됩니다.

| 시안 | 디렉터리 | 주소 | 정보 구조 |
|---|---|---|---|
| 01 | web-concepts-01 | http://127.0.0.1:5173 | 관제 데스크 |
| 02 | web-concepts-02 | http://127.0.0.1:5174 | 우선순위 카드 |
| 03 | web-concepts-03 | http://127.0.0.1:5175 | 사진·근거 중심 |
| 04 | web-concepts-04 | http://127.0.0.1:5176 | 현장 포켓 |
| 05 | web-concepts-05 | http://127.0.0.1:5177 | 탐색·비교 작업대 |

`--concept`를 여러 번 지정하면 선택한 시안을 함께 실행합니다. 각 디렉터리에서도 `npm run dev`, `npm run build`, `npm run preview`를 사용할 수 있습니다. preview는 먼저 build를 완료하고 같은 시안의 dev를 종료한 뒤 실행합니다. dev와 preview는 표의 같은 포트를 사용하며, 포트가 점유되어 있으면 다른 포트로 옮기지 않고 실패합니다. 별도 터미널에서 실행한 dev/preview는 해당 터미널에서 종료합니다. 모든 역할 경로는 한 서버에서 새로고침을 지원합니다. API는8000, 내부 AI 서버는8010입니다. 브라우저는 AI 서버에 직접 연결하지 않습니다.

`./scripts/stop.sh`는 자신이 기록한 프로세스에 종료 신호를 보내고 즉시 반환합니다. worker가 끝났다는 뜻은 아니므로 곧바로 DB를 중지하지 마세요. DB도 중지하려면 **stop 전에** [관리 PID 기록 → 종료 요청 → 종료 확인 → DB 중지 절차](docs/10-execution.md#관리-프로세스와-db-종료)를 실행합니다. 별도로 띄운 서버는 해당 터미널에서 종료하고 프롬프트가 돌아왔는지 확인합니다. 중단된 분석은 작업 상태·lease 복구 규칙에 따라 처리됩니다.

## 시연 계정과 자료

| 역할 | 로그인 ID | 기본 범위 |
|---|---|---|
| 점주 | owner.north / owner.south | 지역별3매장 |
| OFC | ofc.north / ofc.south | 지역별2담당매장, 미배정1후보 |
| 지역 관리자 | regional.north / regional.south | 해당 지역 |
| 본사 | hq.demo | 전사 영업 |
| 플랫폼 운영자 | operator.demo | 계정·연결·기준정보·처리 메타데이터 |

`owner.inactive`와 `owner.unmapped`는 비활성·연결 누락 경계용입니다. 사진은 [시연 이미지](scripts/seed/assets/shelves), 용도·hash·검수 결과는 [manifest](scripts/seed/manifest.json)에 있습니다. Reference4장과 제출6장은 서로 다른 파일입니다.

1. 점주로 로그인해 봄빛역점·음료를 선택하고 `beverage-before-01.png`와 질문을 제출합니다.
2. 실제 AI 결과의 질문 답변, 기준별 판정, 사진 근거와 개선 행동을 확인합니다. 판단 불가는 위반·기술 실패와 구분됩니다.
3. 해당 평가에서 재피드백으로 `beverage-after-01.png`를 제출하고 이전 평가와 비교합니다.
4. OFC·지역·본사로 관제에서 같은 매장과 사진으로 이동해 이슈를 확인하고 조치를 남깁니다.
5. 기준·Reference를 새 버전으로 변경하면 이후 제출에 적용됩니다. 과거 평가의 snapshot은 보존됩니다.
6. 운영자로 계정·매장 연결·공지·작업 상태와 실패 시연 항목을 확인합니다. 운영자는 영업 질문·사진·평가 본문을 조회할 수 없습니다.

AI 생성 시연 사진, Mock 과거 평가, 실제 AI 신규 평가를 별도로 표시합니다. 매출·재고는 가상 데이터이며 상관은 인과관계·매출 예측을 의미하지 않습니다. 실제 모델 응답은 매번 달라질 수 있고 OFC 확인 흐름을 유지합니다.

## 검증

```sh
./scripts/verify.sh
./scripts/verify.sh --postgres
```

일반 검증은 비밀 검사·훅/실행 스크립트 회귀·서버/AI 단위·공통 클라이언트와 각 프론트의 일반/UI 테스트·빌드입니다. `--postgres`는 `STORELOOP_TEST_DATABASE_URL`의 별도 `_test` DB에 임시 스키마를 만들어 동시성까지 확인합니다. 이 설정은 환경변수, 없으면 `.local/runtime.env`에서 읽으며 `DATABASE_URL`과 구분합니다. 실제 AI 호출은 이 명령에서 실행하지 않습니다. [검증 계약의 현재 명령과 실제 AI 절차](docs/09-validation.md#7-실행-명령증거-규격)를 따르고, 실제 AI·브라우저·디자인 결과는 각각 증거로 남깁니다.

브라우저 인수는 시연 DB와 별도로 준비합니다. 실행 중인 API와 worker의 종료를 확인하고 PostgreSQL은 유지한 뒤 먼저 준비 명령을 완료합니다.

```sh
server/.venv/bin/python scripts/browser_test_runtime.py prepare
```

다음 두 명령은 프로젝트 루트의 **서로 다른 터미널**에서 실행합니다.

```sh
# 터미널 A: 테스트 API
server/.venv/bin/python scripts/browser_test_runtime.py api
# 터미널 B: 테스트 worker
server/.venv/bin/python scripts/browser_test_runtime.py worker
```

이 구성은 `.local/test-media`와 `storeloop_test`를 사용합니다. AI 서버와 선택한 Vite도 실행되어 있어야 합니다. 이 foreground 프로세스들은 `start/stop`의 PID 관리 대상이 아니므로 각 실행 터미널에서 Ctrl+C 후 프롬프트 복귀를 확인합니다. UI 주소와 합성 로그인 정보는 같습니다. [브라우저 인수 환경의 전체 실행 순서](docs/10-execution.md#브라우저-인수용-foreground-실행)를 따르고, 완료 후 테스트 프로세스를 종료한 뒤 일반 시작 명령으로 돌아옵니다.

시안별 실제 UI 인수는 Codex in-app Browser의 Playwright 인터페이스로 E01~E08을 수행합니다. 저장소용 Playwright Test CLI runner는 현재 제공하지 않습니다. 단위 테스트·API 검증은 실제 UI 조작, 각 시안의 실제 AI 제출·재제출, 독립 디자인·매뉴얼 검수를 대체하지 않습니다.

보안 훅은 Gitleaks8.30.1과 금지 경로 검사를 사용합니다. 새 branch를 포함한 전송 이력 전체를 검사하고 도구 실패도 차단합니다. GitHub CI 구성은 제공하지만 이번 작업에서 원격 push·보호 설정 변경은 하지 않습니다. 로컬 검사와 원격 적용 상태는 구분해 기록합니다.

## 주요 문서

- [요구사항·수용 기준](docs/03-requirements.md), [화면](docs/04-screens.md), [DB](docs/05-database.md), [API](docs/06-api.md)
- [AI·복구 규칙](docs/07-ai-processing.md), [데이터](docs/08-data.md), [검증](docs/09-validation.md), [실행·인계](docs/10-execution.md)
- [사용자 매뉴얼 통합 목차](deliverables/manuals/index.html) — 역할별 시작, 시연 순서와 5개 매뉴얼을 한곳에서 확인합니다.
- HTML 매뉴얼: [01 관제 데스크](deliverables/manuals/concept-01/index.html), [02 우선순위 카드](deliverables/manuals/concept-02/index.html), [03 사진·근거 중심](deliverables/manuals/concept-03/index.html), [04 현장 포켓](deliverables/manuals/concept-04/index.html), [05 탐색·비교 작업대](deliverables/manuals/concept-05/index.html). 역할별 사용법·실제 화면·실행 및 복구 안내를 작성했고 지정 데스크톱/모바일 문서 화면과 로컬 이미지를 확인했습니다. 200% 확대 등 미실행 항목은 각 문서에 구분했습니다. 시안별 실제 상태는 매뉴얼과 전체 체크리스트를 확인합니다.

최종 시안은 사람이 선택합니다. 선택 대기는 다섯 시안의 구현·검증·인계를 생략하는 조건이 아닙니다.
