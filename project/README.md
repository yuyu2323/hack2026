# StoreLoop · 시안 04

`codex/concept-04`는 main의 `edb64ba`에서 분리한 독립 실행 브랜치입니다. 공통 FastAPI 백엔드, PostgreSQL, worker, Codex CLI AI 서비스, API 클라이언트와 **web-concepts-04 하나**를 포함합니다. 이 프론트 안에 점주·영업관리·플랫폼 운영자 화면이 모두 있습니다. 다른 시안 소스 없이 설치·빌드·실행합니다.

## 설치와 실행

Python 3.11+, Node 22.12+/npm 10+, PostgreSQL 14+ 실행 파일, 로그인된 Codex CLI가 필요합니다. `PG_BIN_DIR`로 PostgreSQL 실행 파일 위치를 지정할 수 있습니다.

```sh
cd project
./setup.sh
./start.sh
```

`setup.sh`가 Python 가상환경 2개, npm 의존성, 전용 PostgreSQL·마이그레이션·합성 시드를 구성합니다. 비밀은 자동 생성되어 gitignore된 `.local`에만 저장됩니다. 다른 브랜치의 `.local`을 복사하지 마세요. `start.sh`는 이 시안만 기본 실행하며 `--concept 4`도 허용합니다. 다른 시안 번호는 거부합니다.

| 서비스 | 주소/포트 |
|---|---|
| 프론트 | http://127.0.0.1:5184 |
| 업무 API | http://127.0.0.1:8104 |
| 내부 AI | http://127.0.0.1:8204 |
| PostgreSQL | 127.0.0.1:55444 |

각 분리 브랜치는 서로 다른 포트·DB 디렉터리·세션 쿠키 이름을 사용하므로 main 실행 환경과 분리됩니다.

## 로그인과 매뉴얼

점주 `owner.north`, 영업 본사 `hq.demo`(OFC `ofc.north`), 플랫폼 운영자 `operator.demo`를 사용합니다. 비밀번호는 `.local/demo-credentials`의 해당 로그인 ID의 `password`에서 확인합니다. 같은 브랜치에서 역할을 바꿀 때 로그아웃 후 로그인합니다.

[시안 04 사용자 매뉴얼](deliverables/manuals/concept-04/index.html). 시연 이미지는 `scripts/seed/assets`에 있으며 합성 사진과 Mock 과거 이력입니다. 새 사진 제출은 실제 Codex AI를 호출합니다.

## 빌드와 검증

```sh
npm run build
./verify.sh --postgres
```

공통 백엔드·AI·API 클라이언트와 이 시안의 테스트만 실행합니다. 실제 AI 호출은 자동 단위 검증에 포함되지 않습니다. 설치 후 `npm --workspace web-concepts-04 run dev`도 가능하며, API·AI·worker는 먼저 실행해야 합니다. `npm --workspace web-concepts-04 run preview`는 빌드 후 사용하며 해당 프론트 dev를 먼저 종료해야 합니다.

## 종료

```sh
./stop.sh
./scripts/db.sh stop
```

분석 요청이 진행 중이면 완료를 기다린 뒤 종료합니다. `stop.sh`는 종료 신호를 보낸 뒤 반환하므로 관리 서비스가 실제 종료된 것을 확인한 다음 DB를 종료하세요.

## 문서 범위

`docs/00`~`09`, `goal.md`, 기존 `execute` 기록과 매뉴얼의 화면 증거는 main에서 수행한 원래 개발·검수의 이력입니다. 그 안의 5개 시안·이전 포트 언급은 역사적 내용이며 현재 브랜치 실행에는 위 절차를 적용합니다. 원래 상위 계약 docs/00~02는 변경하지 않았습니다. 이번 분리 검증은 `execute/workHitory/branch-split/concept-04.md`에서 확인합니다. 200% 확대 등 기존 후행 검수는 그대로 남습니다.
