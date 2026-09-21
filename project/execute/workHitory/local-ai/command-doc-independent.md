# CMD-01 실행 안내 독립 재검토

- 상태: REVIEW_COMPLETE / PASS. 검토자 contract_ai, 수정자 contract_data. 대상 문서/서비스는 수정하지 않았다.
- 대상: README.md, docs/09-validation.md, docs/10-execution.md 및 계약 등록부 CMD-01. 작성자의 [변경 이유](../runtime-independent-reproduction/command-document-review.md)와 [반영·자기 검증](../runtime-independent-reproduction/command-document-update.md)을 읽고 현재 구현과 직접 대조했다.
- 검토 대상 문서/소스 SHA-256 및 원본·필수 구간 보존 독립 재계산은 [독립 기록](command-doc-independent.json)에 있다. 수정 문서3개의 hash는 작성자 동결 기록과 일치한다. 원본00/01/02 및 docs09 §2~6도 기록된 hash와 일치한다.

| 대조 항목 | 독립 결론 |
|---|---|
| 설치·최소 버전 | preflight의 Python3.11/Node22.12/npm10/PG14와 일치. setup의 두 환경/lock/npm/Gitleaks/훅/PG/migration/seed를 빠짐없이 설명하며 이미 포함된 개별 재실행 단계를 구분한다. |
| 프론트 검사·preview | root package 및 시안01의 test와 test:ui가 구분되고 두 workspace 명령이 모두 포함됐다. build 후 dev 종료와 같은 포트 preview/strictPort 설명이 현재 설정과 일치한다. 실제 preview 기동 성공으로 과장하지 않는다. |
| verify | 일반/--postgres의 marker 선택, AI fixture 검사, client/workspace 일반/UI/build 단계와 일치. 제공되지 않는 actual AI/browser 옵션을 주장하지 않는다. |
| PostgreSQL 격리 | postgres_db fixture의 STORELOOP_TEST_DATABASE_URL 환경 우선/파일 fallback, _test 검사, 임시 schema 생성·폐기와 일치한다. 브라우저의 지속 테스트 DB/test-media와 구분한다. |
| 실제 AI 검사 | app.smoke의 실제 HTTP·생성 이미지·schema/ref 검증과 별도 worker real_ai pytest 경로가 정확하다. 플래그 없을 때 skip, 고정 real-worker-001.json 증거 보존, 고유 smoke 경로를 명시한다. 일반 AI fixture39개를 실제 모델 성공으로 설명하지 않는다. |
| 관리 프로세스 종료 | services.stop의 소유 marker 검사→SIGTERM 그룹 요청→PID 파일 삭제와 일치한다. 예시는 삭제 전에 PID를 읽고 동일 alive 검사로 기다린 뒤 DB stop을 요청한다. 시간 초과는 DB stop 전 종료한다. worker의 신호 handler는 신규 점유를 멈추며 현재 process_claim 완료까지 DB를 사용할 수 있어 대기 필요성도 정확하다. |
| 종료 범위 제한 | 이미 PID 파일이 지워졌거나 별도 foreground 프로세스가 있으면 예시만으로 전체 종료를 주장하지 않는다. 별도 터미널 Ctrl+C/프롬프트 복귀와 worker 먼저 기다리는 절차가 명시돼 있다. 진행 중 실제 서비스에 종료 실험을 하지 않았다. |
| 브라우저·인수 범위 | 저장소 Playwright CLI 미제공/NOT_RUN을 실제 in-app Browser Playwright E01~E08과 구분한다. 모든 시안 실제 제출·재제출/모바일 조작/키보드/독립 디자인/매뉴얼 요구와 API·DOM 대체 금지를 유지한다. 전체 완료나 개별 인수 PASS를 문서 변경만으로 선언하지 않는다. |
| 링크·현재 인계 | 5개 실제 HTML 매뉴얼 경로와 각 파일의 존재를 확인했다. 최종 화면·문서 렌더 검수 대기를 명시하고 현재 상태는 master/시안별 증거로 위임한다. 등록부의 영향·독립 응답 추적도 일치한다. |

미해소 결함 없음. 작성자 검사(링크39/구문9/격리 종료경계3/collect-only/5개 preview resolveConfig)의 범위와 제한을 검토했다. 독립 검토에서 해당 실행을 불필요하게 반복하지 않았으며, 본 PASS는 문서와 구현의 정합성에 한정된다. 실제 설치·프로세스 시작/종료·DB·모델 호출·브라우저/preview·매뉴얼 렌더 인수의 PASS를 추가하지 않는다.
