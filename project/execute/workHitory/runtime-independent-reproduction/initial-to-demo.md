# 초기 구성부터 로컬 시연까지 독립 재현

## 사전 조사와 격리 계획
- root 배정: 문서 실행 절차 재현 가능성을 조사하고 현재 QA 서비스를 보호한 채 가능한 범위를 실제 실행한다. 제품 소스 변경·원격/외부 전송·기존 .local 비밀 복사를 금지한다.
- docs10 §3 및 README의 setup은 preflight→prepare→Python venv/pip→npm ci→보안도구/Git 훅→PG→migration→seed다. start는 PG 준비→AI→API→worker→선택 Vite이며 stop은 기록한 PID를 검사하여 종료한다.
- 소스 조사: local_runtime DB 포트55432와 이름, services API8000/AI8010/프론트5173~5177, Vite API proxy8000이 고정되어 있다. PG_BIN_DIR만 실행 파일 위치를 바꾼다. 따라서 현재 QA와 문서 명령 그대로 병행하는 격리 실행은 NOT_RUN이며 기능 실패로 단정하지 않는다.
- /private/tmp 새 디렉터리에 필요한 소스/합성 seed 이미지 사본만 만든다. 기존 .local/.git/.venv/cache/인증 파일을 복사하지 않는다. prepare로 새 로컬 비밀을 생성하고 임시 환경만 비충돌 포트에 맞춘다.
- 신규 venv는 실제 생성하되 의존성은 기존 설치의 site-packages를 읽기 재사용한다. 외부 통신과 신규 패키지 다운로드를 하지 않으므로 clean dependency install 검증과 구분한다.
- PostgreSQL은 새 data/socket 디렉터리·임시 포트·새 비밀로 직접 시작한다. 원본 코드의 migration/seed와 services.launch/stop 공통함수를 활용한 독립 포트 런타임을 검증한다. 실제 모델 호출은 요청하지 않는다.

## 최초 실제 실행과 RUNTIME-01 RED
- 실행 harness: `server/.venv/bin/python execute/workHitory/runtime-independent-reproduction/reproduce.py`. loopback 임시 포트 사용 권한으로 실행했다. 외부 요청·현재 QA 접근 없이 /private/tmp에 새 source 사본, 비밀, PG cluster를 만들었다.
- PASS: preflight5종, prepare의0600 및 재실행 동일 hash, 새 venv2개, 신규 PG/DB2개, Alembic head, 최초 seed584행 및 재seed0행.
- RUNTIME-01(P1): macOS Framework Python은 ps argv[0]에서 venv 경로를 `/Library/Frameworks/.../Python`으로 바꾼다. API의 `-m uvicorn server.main:app`에는 프로젝트 경로가 없어 alive의 ROOT 검사에 실패한다. AI는 --app-dir에 경로가 있어 통과한다. 기존 worker의 -m 실행도 같은 구조다.
- 이 상태에서는 직접 시작한 API/worker를 재시작 때 재사용하지 못하고 stop이 종료하지 않은 채 PID 기록을 삭제한다. 실제 API 기동 후 인식 실패를 두 번 재현했고, harness가 별도 보유한 자기 자식 PID를 종료한 뒤 임시 PG도 종료했다. 보존 증거 `result-red.json`의 실제 비밀 없는 argv와 실패 위치를 참고한다.
- 초기 합성 실제 자식 회귀는 인식/stop2 FAIL, 다른 cwd 보존1 PASS(2.86초). 이후 제품이 지원하는 start 명령 검증으로 범위를 정확히 좁혔다.
- 최종 독립 회귀 `tests/runtime/test_process_ownership.py`: 제품 start()의 실제 API/worker 명령을 캡처하고 관측한 macOS argv[0] 변환을 반영했다. API/worker 인식 및 stop signal3 RED, 타프로젝트 보존1 PASS(0.04초). 서비스/DB/외부 프로세스 없이 명령과 소유권 경계를 검사한다.
- 제품 수정은 root에 인계했다. root는 API에 --app-dir ROOT를 추가하고 worker를 절대 경로 scripts/worker_entry.py로 실행하여 argv에 프로젝트를 보존한다. alive의 marker+ROOT 보수 검사는 그대로 유지한다.
- root 수정 소스 독립 확인: worker 진입점은 자기 프로젝트를 import 경로에 추가하고 기존 worker.main()을 호출하여 업무 루프/종료 신호 의미를 유지한다. runtime 단위 전체5개 독립 재실행 PASS(0.04초). 수정 후 새 임시 환경 전체 재현은 별도 결과로 기록한다.

## 수정 후 실제 격리 전체 실행
- 같은 harness를 새 임시 디렉터리에서 재실행했다. 제품 start()가 실제 구성한 AI/API/worker 명령을 수집하고 --port만 임시 포트로 바꾸어 실행했다. 새 worker_entry.py 및 API --app-dir ROOT가 실제 ps 명령에 남고 alive가 세 서비스 모두를 인식했다.
- 최종 임시 포트는 PostgreSQL60537/API60538/AI60539/Vite60540이며 현재 QA 포트와 중복되지 않았다. Vite는 검증 harness의 별도 설정으로 임시 API proxy와 임시 cacheDir를 사용했다. 따라서 제품 Vite 기본 proxy8000 자체를 변경하거나 동시 격리 지원으로 주장하지 않는다.
- 실제13개 확인 PASS: 비밀 제외 소스 사본, preflight, prepare0600/재실행보존, 분리 venv, 새 PG/DB, migration·seed584/재seed0, AI/API/worker 기동, API 반복 시작의 동일 PID, Vite SPA 새로고침·TS 엔트리 변환·API proxy 및5역할 로그인/업무조회, 실제 AI 호출 없음, 자기4서비스 종료/무관 프로세스 보존, stop 재실행, 임시 PostgreSQL 종료.
- 다섯 역할의 실제 HTTP200을 확인했다: 점주 submissions, OFC/지역 dashboard, 본사 references(include_inactive), 운영자 accounts. 운영자의 영업 submissions는403으로 확인했다. 이는 초기 구성의 연결·시연 준비 smoke이며 본인 작성 인증 도메인의 새로운 독립 보안 PASS나 실제 브라우저 전체 인수를 의미하지 않는다.
- 실제 모델 호출을 하지 않았으며 독립 AI health의 last_success_at/last_failure_at은 둘 다 null이다. worker는 시드 fixture만 있는 자기 DB에서 동작했다.
- stop은 PID파일을 사용해 자기 AI/API/worker/Vite4개를 종료했고, 잘못 연결한 무관 sleep PID는 남겼다. harness가 직접 만든 sleep은 검증 후 별도로 종료했다. PG 종료 후 세 번의 임시 실행 경로를 가리키는 잔여 프로세스가0인지 확인했다.
- 증거 `result.json`: PASS_WITH_NOT_RUN, 실행 소스 SHA-256, 비밀 없는 실제 argv, 포트, 확인 항목, 정리 결과. 결함 당시 결과는 `result-red.json`으로 보존했다.
- 새로 만든 임시 디렉터리3개와 그 안의 임시 비밀·PG 데이터·합성 시드 자격을 삭제했다. 현재 프로젝트 .local·QA 서비스·원본 비밀은 읽거나 복사/수정하지 않았다.

## 최종 판정과 미실행 범위
- RUNTIME-01 독립 **해소/PASS**. 신규 회귀파일과 이력/harness 동결. 제품 services.py/worker_entry.py 수정자는 root이고 이 검토자는 제품 소스를 수정하지 않았다.
- **NOT_RUN**: 기본 고정 포트의 `scripts/setup.sh`→`scripts/start.sh`→`scripts/stop.sh` 전체 순서. 현재 QA를 종료해야 하므로 root가 QA 종료 후 별도 인수한다.
- **NOT_RUN**: pip/npm/Gitleaks 인터넷 신규 설치 및 Git hook 설정. 이번 권한은 외부 전송/Git 변경을 금지했고, 신규 venv가 기존 설치된 의존성을 읽기 재사용했으므로 clean install로 표시하지 않는다.
- **NOT_RUN**: 실제 모델 분석·5개 시안 브라우저 클릭·모든 시안 dev/preview 전체. 이번 검증은 시안01의 HTTP SPA/proxy 연결과 공통 런타임 수명주기에 한정한다.
- 위 제한을 포함해 초기 구성/로컬 시연의 격리 가능 범위는 PASS_WITH_NOT_RUN이다. 원격/외부 통신 없이 확인 가능한 작업을 완료하고 root에게 결과와 남은 인수 범위를 인계했다.
