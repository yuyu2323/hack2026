# 실행·협업·인계 계약 v1.1 (G1 확정, CMD-01 실행 안내 정합화)

기준: 00·01·02. 최초 작성자 root, CMD-01 실행 안내 반영 contract_data. G1 독립 검토를 통과했으며 확정·변경 근거는 [계약 등록부](../execute/workHitory/docs/contract-register.md)에 있다. 아래 명령은 현재 구현을 따른다. 설치·실행 성공과 미실행 범위는 [전체 체크리스트](../execute/checkList/orchestration/master.md) 및 각 실행 증거로 별도 기록한다.

## 1. 저장소와 초기 차이

실제 저장소는 `hack2026`, 제품 루트는 `hack2026/project`다. 처음에는 00·01·02만 추적되어 있었고 실행 코드/후속 상세 계약/AGENTS/ralph는 없었다. 기존 미추적 `project/goal.md`, `project/execute`의 사용자 기록, `project/deliverables/submission`은 보존한다. 상위 storeloop 저장소로 범위 밖 파일을 올리지 않는다. 새 AGENTS는 현재 제품명/5개 시안/작업 패키지를 명시한다.

## 2. 환경·실행 계약

- Node 22.12 이상, npm 10 이상, Python 3.11 이상, PostgreSQL 14 이상과 Codex CLI의 이미지·JSON Schema 기능이 필요하다. `scripts/preflight.py`가 최소 버전과 Codex 실행 파일을 확인한다. 실제 검증한 버전과 Python/npm lockfile을 제공한다.
- 업무 Python 환경 `server/.venv`, AI Python 환경 `ai-service/.venv`를 분리한다. 서버는 SQLAlchemy 2·psycopg·Alembic, AI는 FastAPI·Pydantic·Pillow·Codex 어댑터를 사용한다.
- PostgreSQL은 기존 사용자 클러스터를 건드리지 않고 프로젝트 `.local/postgres`에 전용 클러스터/DB를 구성한다. 기본 전용 포트 55432, localhost 바인딩. 사용자·DB 이름 storeloop/ storeloop_test를 사용하고 비밀 값은 추적 제외된 환경 파일에서 읽는다. 전용 데이터 초기화는 최초 생성 때만 수행하고 기존 데이터 삭제/리셋은 자동 수행하지 않는다.
- runtime `.local/`은 gitignore, 생성 파일 권한은 사용자 전용. `.env.example`은 실제 인증값 없이 REPLACE_ME 자리표시자만 포함한다.
- API 127.0.0.1:8000, AI 127.0.0.1:8010, 프론트 127.0.0.1:5173~5177. Vite dev/preview 모두 `/api` proxy 및 SPA fallback을 제공한다. 시안별 dev와 preview는 같은 포트이며 strictPort로 충돌 시 실패한다. 허용 Origin은 실제 localhost/127.0.0.1 개발 포트만 열거한다. 시작 스크립트는 미관리 프로세스가 점유한 포트를 자동 종료하거나 재사용하지 않는다.
- 업무 요청은 프론트→API, AI는 worker→내부 AI 서버 경로만 허용한다. AI_SERVICE_TOKEN은 서버 환경에만 주입한다. 브라우저 번들에 비밀이나 내부 토큰을 넣지 않는다.
- Codex 인증은 기존 CLI 인증을 사용한다. 상태만 검사하고 원시 인증 파일은 읽거나 복사하지 않는다. CODEX_BIN/CODEX_MODEL은 실제 설치 환경 검증 후 예제와 실행 문서에 반영한다.
- 미디어는 `.local/media`의 보호 파일, API ID 기반 인가 후 제공. 테스트는 별도 `.local/test-media`와 DB로 격리한다.

## 3. 재현 명령의 최종 산출물

현재 `README.md`와 `scripts/`는 다음 명령을 제공한다. 모두 프로젝트 루트 `hack2026/project`에서 실행한다.

1. `./scripts/setup.sh`: 버전 확인·기존 값을 보존하는 로컬 설정 생성, 두 Python 환경과 lockfile 패키지·npm 설치, Gitleaks 설치·로컬 Git 훅 설정, 전용 PostgreSQL 구성/시작, 마이그레이션, 합성 seed까지 실행한다. 최초 의존성/도구 설치에는 다운로드가 필요하다. 아래2~4는 setup에 이미 포함된 단계의 개별 재실행 명령이다.
2. `./scripts/db.sh start`: 전용 PostgreSQL 시작. 기존 외부 클러스터는 변경하지 않는다.
3. 프로젝트 루트에서 `server/.venv/bin/alembic -c server/alembic.ini upgrade head`: 리뷰된 마이그레이션 적용. 앱 시작의 create_all 금지.
4. `server/.venv/bin/python -m server.seed`: 재실행 시 중복되지 않는 합성 기준·계정·이미지·이력 데이터 적재. 비밀번호는 실행시 생성하거나 환경 입력으로 주입한다. 비밀번호를 콘솔/소스/매뉴얼에 출력하지 않는다. 시연 로그인 정보 파일을 사용자 전용 `.local/demo-credentials`에 저장하고 사용자가 로컬에서 열람하도록 안내한다.
5. `./scripts/start.sh --concept 1`: 전용 DB 시작을 확인하고 AI 서버→업무 API→worker→선택 시안 순서로 시작한다. API/AI 준비상태와 관리 PID를 기록하며 자동 실제 모델 health 호출은 하지 않는다. `--concept 2 --concept 3`처럼 시안을 함께 선택할 수 있고, `--without-worker`는 worker만 생략한다. 미관리 포트 충돌은 서비스 일부를 시작하기 전에 거부한다.
6. 해당 `web-concepts-0N` 디렉터리에서 `npm run dev`: 시안별 한 서버로 모든 역할 제공. `npm run build` 후 **같은 시안 dev를 종료하고** `npm run preview`를 실행한다. 표준 포트5173~5177을 그대로 사용한다. API/AI/worker는 별도로 실행 중이어야 전체 업무를 시연할 수 있다.
7. `./scripts/verify.sh`: 비밀·훅·실행 스크립트 회귀, 업무/AI 단위, 공통 클라이언트·시안별 일반/UI 테스트와 빌드. `./scripts/verify.sh --postgres`는 PostgreSQL 검사를 추가한다. 실제 AI·브라우저는 이 스크립트의 옵션으로 제공하지 않으며 [09 §7의 별도 명령·도구 절차](09-validation.md#7-실행-명령증거-규격)를 따른다. 일반 Mock 검사와 실제 인수의 결과를 구분한다.

스크립트명·명령의 구현상 변경이 필요하면 문서를 먼저 갱신하고 관련 담당에 전파한다.

### 관리 프로세스와 DB 종료

`./scripts/stop.sh`는 `.local/pids`에 기록되고 현재 프로젝트 경로·서비스 marker가 일치하는 프로세스 그룹에 SIGTERM을 보낸 뒤 PID 파일을 지우고 즉시 반환한다. **반환만으로 worker 종료를 판단하지 않는다.** worker는 종료 신호를 받으면 신규 점유를 중지하고 현재 처리를 끝내는 동안 DB를 계속 사용할 수 있다. DB는 종료 확인 후 중지한다. 중단된 분석은 [07의 실패·lease 복구 규칙](07-ai-processing.md)을 따른다.

다음은 `start.sh`로 관리 중인 프로세스를 **stop 실행 전에** 기록하고, 종료 요청 후 같은 프로세스가 사라졌는지 최대180초 확인한 경우에만 DB를 중지하는 절차다. 환경 파일·프로세스 명령 원문은 출력하지 않는다. 시간 초과 시 추가 종료 신호나 DB 중지를 실행하지 않으므로 원인을 확인한다.

```sh
server/.venv/bin/python - <<'PY'
import json
from pathlib import Path
import subprocess
import sys
import time

project_root = Path.cwd().resolve()
sys.path.insert(0, str(project_root / 'scripts'))
from services import alive

# 종료 요청이 PID 파일을 지우므로 먼저 메모리에 보관한다.
managed = [json.loads(path.read_text())
           for path in (project_root / '.local/pids').glob('*.json')]
subprocess.run(['./scripts/stop.sh'], check=True)
deadline = time.monotonic() + 180
while True:
    remaining = [item for item in managed if alive(item['pid'], item['marker'])]
    if not remaining:
        break
    if time.monotonic() >= deadline:
        raise SystemExit('관리 프로세스 종료를 확인하지 못했습니다. DB는 유지합니다.')
    time.sleep(1)
print('기록된 관리 프로세스 종료 확인 완료')
subprocess.run(['./scripts/db.sh', 'stop'], check=True)
PY
```

이 확인은 읽어 둔 관리 PID에만 적용된다. 별도 터미널에서 띄운 API/AI/worker/dev/preview는 각 터미널의 Ctrl+C 후 **프롬프트 복귀**까지 확인한다. 이미 stop을 실행해 PID 기록이 지워졌거나 실행 주체를 확인할 수 없으면 이 예시로 모든 프로세스 종료를 판정하지 말고 해당 실행 터미널·프로세스 소유자를 확인한 뒤 DB를 중지한다. 사용자의 다른 프로세스를 일괄 종료하지 않는다.

RUNTIME-01 보완은 내부 API 실행에 `--app-dir ROOT`, worker 실행에 절대 경로 `scripts/worker_entry.py`를 사용하여 운영체제의 Python 재실행 후에도 프로젝트 소유권을 식별하게 한다. 공개 `start.sh`/`stop.sh` 명령과 worker의 업무 동작은 동일하다.

### 브라우저 인수용 foreground 실행

브라우저 인수는 시연 DB를 바꾸지 않고 `scripts/browser_test_runtime.py`의 전용 `_test` DB와 `.local/test-media`를 사용한다. 일반 API/worker의 종료를 확인하고 PostgreSQL은 켜 둔다. 먼저 루트에서 다음 준비 명령이 끝날 때까지 기다린다. 이 단계는 전용 테스트 DB에 마이그레이션·합성 seed를 적용하며, pytest의 자동 폐기 UUID 스키마와 다르다.

```sh
server/.venv/bin/python scripts/browser_test_runtime.py prepare
```

다음 네 명령은 각각 프로젝트 루트의 **별도 터미널**에서 실행한다. 동일한 AI8010/Vite가 이미 실행 중이면 해당 명령은 중복 실행하지 않는다. 테스트 API8000과 worker는 반드시 위 전용 테스트 환경으로 실행한다.

```sh
# 터미널 A: 내부 AI 서버
ai-service/.venv/bin/python -m uvicorn app.main:app --app-dir ai-service --host 127.0.0.1 --port 8010 --no-access-log
# 터미널 B: 테스트 API
server/.venv/bin/python scripts/browser_test_runtime.py api
# 터미널 C: 테스트 worker
server/.venv/bin/python scripts/browser_test_runtime.py worker
# 터미널 D: 선택 시안 (예: 01)
npm run dev --workspace @storeloop/concept-01
```

`browser_test_runtime.py api/worker`는 foreground `exec`로 실행되어 일반 시작 스크립트의 PID 파일에 등록되지 않는다. 종료는 시작한 터미널에서 Ctrl+C 후 프롬프트 복귀를 확인한다. 진행 중인 분석을 마무리하려면 worker를 먼저 종료 요청하고 기다리는 동안 API/AI/DB를 유지한다. 종료를 확인한 다음 나머지 테스트 서버를 중지하고 `./scripts/start.sh --concept 1`로 일반 시연 환경을 다시 시작할 수 있다. 테스트와 시연 worker를 동시에 실행하지 않는다. 브라우저 검증은 [09의 E01~E08 및 증거 절차](09-validation.md#6-각-시안-브라우저-인수-시나리오)를 따른다.

## 4. 작업 패키지와 선행 관계

| 패키지 | 내용 | 선행 | 파일 소유권/완료 증거 |
|---|---|---|---|
| DOC | 03 요구·04 화면·05 DB·06 API·07 AI/처리·08 데이터·09 검증·10 실행 | 00~02 | master 배정표, 독립 검토 및 확정 기록 |
| SEC | ignore·Gitleaks·pre-commit/push·CI 정책·합성 차단 검증 | DOC | root 지정 보안 담당, repository-security 기록 |
| DB | 초기 migration·모델·제약·seed 경계 | DOC 확정 | contract-data 단일 모델/migration 소유자 |
| API | 인증/범위·도메인 API·미디어·관제·운영 | DB | 담당별 전용 도메인 경로, pytest RED/GREEN |
| AI | 독립 서버·Codex·출력 검증·실제 조기 검증 | DOC | local-ai 담당, 이미지/질문/기준/Reference 증거 |
| JOB | 영속 worker·점유·실패·재처리·늦은 결과 | DB/AI 계약 | PostgreSQL 동시성 및 복구 증거 |
| DESIGN-01..05 | 각 컨셉 전담 기획·디자인 명세 | DOC 화면 | brief/design-spec/acceptance |
| WEB-01..05 | 역할별 화면·라우팅·API 연결 | 각 DESIGN/API 계약 | 5개 개별 build 및 테스트 |
| IMG/DATA | 실제 생성 이미지·manifest·합성 시드 | DOC/DB | 시각검수·재적재/관계 검사 |
| QA-01..05 | 독립 기능/보안/브라우저 실제 AI | 각 WEB/API/AI/DATA | 시안별 PASS/FAIL/BLOCKED/NOT_RUN 보고 |
| DR-01..05 | 구현·기획자와 다른 디자인 검수 | 각 WEB/DESIGN | desktop/mobile 실제 캡처·재검수 |
| MANUAL-01..05 | 실제 완성 화면 기반 HTML | 각 QA/DR | 오프라인 HTML·상대 이미지/링크 검수 |
| HANDOFF | 실행표·검증/제약·비교·시안선택 질문 | 모든 패키지 | 완료표/최종 보고 |

문서·공통 코드 변경 전 원본 작업 이력에 변경 ID/이유/영향/검증 계획을 남긴다. 변경 후 에이전트별 전달→수신 확인→반영/검증 근거를 contract-register에 추적한다. 미배정 담당자는 배정 시 최신 확정 버전을 읽고 수신 확인한다. 무응답은 승인/확인으로 취급하지 않는다.

## 5. 검증·인계 게이트

- G1: 실제 상세 계약 존재, 독립 검토의 차단 결함 해소, 동명 필드/상태/권한 결정 일치, 버전·근거·소유자 기록. 그 후 구현 자동 시작.
- G2: TDD 기록, 실제 로컬 AI 조기 검증, 모델/마이그레이션/공통 API 동작. 진단 실패가 있으면 원인과 영향 기록.
- G3: 실제 생성 이미지가 보호 미디어와 시드에 연결되고 가상 데이터 UI 표시. 재피드백 부모와 기준 스냅샷 보존.
- G4: docs/09 및 컨셉별 acceptance 통과. 실제 AI 요청별 경과 시간을 기록하고 30초 초과를 숨기지 않는다. 최종 테스트 DB/미디어로 재현하며 시연 DB는 보존한다.
- G5: 각 HTML 매뉴얼에 실제 경로/버튼명/화면/권한/오류·unknown 대응/시연 순서를 포함. 상대 링크와 오프라인 이미지 확인. 비교자료와 선택 질문에는 5개 실행 주소와 매뉴얼·캡처·검증 결과를 제공한다.

## 6. 저장소 보안

도구 버전을 고정한 Gitleaks와 금지 파일 검사, staged pre-commit, push 대상 전체 범위 pre-push, 최소 권한 CI를 구성한다. 합성 fixture로 차단을 검증하며 원격에 보내지 않는다. .git 설정은 실제 로컬 설치 결과를 기록한다. 실패/미설치는 통과가 아니며 커밋·push를 하지 않는다.

원격 공개·배포·push·PR·보호설정 변경은 로컬 완성 목표에 포함되지 않는다. GitHub 보호는 읽기 가능한 범위에서 상태를 확인하고 권한/플랜/연결 부재는 사실대로 기록한다. 로컬 보안 차단과 원격 미적용을 구분한다. 기존 사용자 자료를 자동 스테이징하지 않는다.

## 7. 최종 보고 형식

완료 기능 및 5개 시안별 상태, 미완료/차단과 필요한 입력, 테스트 명령/결과/실제 AI·브라우저 증거, 로컬 실행·시연 순서, 매뉴얼과 주요 산출물, 제약과 시안 비교를 포함한다. 문서 작성 완료만으로 프로젝트 완료를 선언하지 않는다. 최종 시안 선택은 `execute/question/frontend-selection/select-concept.md`에서 사용자가 한다.
