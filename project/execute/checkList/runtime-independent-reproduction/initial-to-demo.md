# 초기 구성부터 로컬 시연까지 독립 재현

- 소유: contract_data 독립 실행 검토. 제품 소스는 읽기 전용이며 실행 기록/검증 harness만 작성한다.
- 보호: 현재 API8000/AI8010/PG55432/Vite5173~5177/worker와 기존 .local 비밀을 중단·수정·복사하지 않는다.
- [x] docs10/README 및 setup/start/stop/local_runtime/services의 설정 지원 확인
- [x] 임시 소스 사본, 새 무작위 비밀, preflight/prepare/venv 구성 실제 실행
- [x] 비충돌 임시 PostgreSQL에 migration/seed 실행 및 재실행 보존 검증: 584행→0행
- [x] 임시 API/AI/worker/프론트 기동·SPA/proxy/5역할 HTTP 로그인·업무조회 확인
- [x] PID 소유권·반복 시작·관련 프로세스만 종료·DB 종료 확인: RUNTIME-01 root 수정 후 PASS
- [x] PASS/FAIL/NOT_RUN 및 최초 문서 명령 제약 증거 root 보고
- [x] runtime 단위5개 독립 PASS, 실제 격리 실행13개 확인 PASS
- [x] 세 임시 실행의 잔여 프로세스0 확인 후 본인 생성 디렉터리/새 비밀 삭제

최종 상태: **PASS_WITH_NOT_RUN**, 증거 result.json. 테스트/보고서 동결. 문서 기본포트의 전체 실행은 root가 QA 후 별도 인수한다.

고정 포트 때문에 문서 setup/start 전체를 그대로 실행할 수 없다. 인터넷 설치·Git 훅 설정은 금지 범위이므로 실행하지 않는다. 기존 의존성을 읽기 재사용한 구성은 신규 의존성 설치 PASS로 보고하지 않는다.
