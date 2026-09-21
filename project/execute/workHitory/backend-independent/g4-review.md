# G4 백엔드·시드 독립 검토
- 상태: 할당된 영업 백엔드 독립 검토 완료; 제한 범위와 별도 정정 도구 검토 대기 명시
- 소유: contract_data. root가 구현한 영업업무/seed/scripts를 독립 검토한다.
- 본인 구현 core/auth/DB/models/migrations/accounts/stores/operations는 독립 PASS 대상으로 세지 않는다.
- 00→01→02는 앞선 계약작업에서 읽은 원본을 유지, G1확정03~10 및 최신PD-003과 대조한다.
- 작업 전 범위/체크리스트 생성. 운영 DB/브라우저테스트 public 스키마 변경·서버 재시작·원문비밀 출력 금지.
- 모든 테스트는 --tb=short, PostgreSQL은 기존 postgres_db fixture의 _test DB/독립 UUID스키마만 사용한다.
- 변경 전 계획 NOTIFY-CLARIFY-1: PD-003에 따라 docs06 역할표에 platform_operator /notifications403을 명시. 기존 서버권한의 문서표현 보완이며 신규권한 없음. root/product_design에 전파 및 ACK 추적.

## NOTIFY-CLARIFY-1 완료
- docs06 §2에 운영자 알림 GET/read403·공지 유지 명시. root 수신 ACK 및 등록부 기록, 04/05 기존 PD-003 수신 ACK를 root가 확인했다. 이전 product_design 세션 메시지 도구 실패는 root 경로로 해소했다.

## BI-01 / BI-02 독립 RED
- 전용 PostgreSQL `_test` DB의 UUID 임시 스키마만 생성·삭제했다. public/시연 DB·런타임 불변.
- 명령: `server/.venv/bin/python -m pytest server/tests/test_independent_acceptance.py -q --tb=short`
- 결과: 3 failed / 1 passed, 4.94초. 검증 중 비밀 원문·계정 자격을 출력하지 않았다.
- BI-01: seed 현재버전 snapshot 생성 후 첫 제출만v1 보정하여, 12개 과거 제출에 생성 전 v2를 사용한다. effective/candidate 합계24개 참조. 기준 생성시간≤제출시간 검사 실패. 멱등 재실행·사용자 매장명 보존·snapshot hash·Mock 표시 검사는 통과했다.
- BI-02: 이미 resolved 이슈에서 resolution:null 요청은 status 생략/명시 모두200. 최종 해결 상태에는 유효한 조치내용이 필요하므로422여야 한다.
- 현재 매핑 종료 후 알림 목록0/read404, 운영자 GET/read403 독립검증 PASS. 본인 인증/core 구현의 독립 PASS 의미는 아니다.
- root에게 재현 테스트 freeze 전달. root는 두 결함 수정 담당이며 이 검토자는 구현하지 않는다.

## MEDIA-CLARIFY-1 변경 전 계획
- root 요청에 따라 docs06 SubmissionDetail 최상위 읽기 전용 reference_photos를 추가한다. snapshot/reference 입력 필드·hash·AI strict schema·DB는 변경하지 않는다.
- 각 {reference_id,photo:Photo}는 해당 제출의 불변 context.references에 실제 포함된 photo_id에서만 구성한다. 현재 제출 범위를 재인가한다. 미디어 source_kind 배지에 필요한 표현 계약이다.
- root TDD 구현, 04/05 및 각 프론트 전파/ACK는 root 추적. 과거 비활성 Reference라도 허용된 snapshot 사용원본을 표시한다.

## BI-01 / BI-02 수정 후 독립 GREEN
- root가 seed 과거 기준을 제출 시각 이전 최신버전으로 선택하도록 수정했다. 기존 namespace의 이미 저장된 snapshot은 재실행 시 덮어쓰지 않는다.
- root가 이슈 PATCH 후의 최종 status/resolution 조합을 검사하도록 수정했다.
- 독립 실행 8 passed / 6.42초: 위 결함 3개 재현 테스트가 GREEN. 요청한 status:null/priority:null도 각각422이며500을 재현하지 않았다.
- 통계: 동일 매장·카테고리·주차 유효쌍3개에서 r=1, 매출 누락1/unknown-only1은 각각 제외; 매출 분산0은 r=null; unknown-only 대시보드는 준수율null·판단가능률0·표본1.
- 업로드 원자성: 사진 저장 이후 총 적용 기준30000자 초과로422일 때 제출/MediaAsset 행과 새 파일이 모두 정리되는 것을 확인했다.

## BI-03 실행 서비스 혼합 방지
- 기존 services.launch는 미관리 포트의 /health=200이면 기존 서비스를 재사용했다. browser_test_runtime의 test DB API와 일반 prod worker가 섞일 수 있어 root에게 보고했다.
- root 수정: 미관리 health/TCP 포트 점유를 거부하고 전체 포트를 먼저 검사한다. PID marker와 현재 프로젝트 절대경로를 함께 검사한다. 기존 프로세스 종료 없이 모의 health 응답으로 독립 회귀 PASS.
- root 작성 tests/runtime/test_services.py의 기존 구현 RED→수정 GREEN도 별도로 확인했다. 실제 브라우저 인수 런타임은 이 검토자가 시작/정지하지 않았다.
- setup에 사전 버전 검사 추가, verify에 runtime 및 모든 workspace test:ui 추가 확인.
- 직접 preflight 실행: Python3.13.3/Node26.4.0/npm11.17.0/PostgreSQL16.10/Codex0.154.0 모두 PASS. 버전 확인만 실행하고 신규 설치·설정 변경은 하지 않았다.

## 독립 추가 회귀 12 PASS
- 명령은 위 동일, 최종 해당 실행 결과 12 passed / 8.05초, 테스트 라이브러리 deprecation warning 2개.
- 실제 PostgreSQL 두 Session 경쟁: 같은 문의+멱등키 두 요청에서 최초1/replay1·동일 resource·행1개. 같은 기준 version1 수정은 하나 성공·하나409·버전총2개.
- MEDIA-CLARIFY-1: 과거 Reference를 비활성화해도 허용된 제출의 reference_photos는 당시 매체와 source_kind를 제공하며 보호 원본 인가 성공, snapshot JSON/hash 불변. 새/과거 참조의 표현 메타데이터만 추가됨.
- 설치된 Gitleaks8.30.1 stdin: 일반 합성 문서 허용, 외부 유효하지 않은 합성 탐지 표본 차단. 도구 stdout/stderr가 사용자 출력으로 유출되지 않음. Git 명령 없이 검사기를 직접 호출했다.
- 검토 대상 영업 코드에서 현재 매핑 필터, 원본/썸네일 공통 인가, JSON extra 금지, 사진 형식/치수/EXIF/파일경로 보호, criterion/version 보존, 버전 잠금, 권한 우선 멱등 처리 확인.

## 남은 인수 범위
- docs08 초기 경계인 처리대기/기준 없음 시드는 현재 종료된30개에 없으므로 root가 명시적 fixture 보완 중. 보완 후 독립 재검증 필요.
- 이미 적재된 합성 과거 snapshot의 BI-01 정정은 기본 seed가 덮어쓰지 않아 별도 안전한 정정 절차 검토가 필요. 현재 이 검토자는 기존 production/public 기록을 수정하지 않았다.
- setup 전체 신규 설치 및 start/stop 실제 전체 실행은 공유 런타임 보호 때문에 NOT_RUN. 사전 검사·스크립트 소스·모의 충돌 경계만 독립 PASS.
- 기존 Git hook/임시 저장소 보안 테스트는 root의7PASS 증거를 읽었으며 이번 검토에서 Git 작업을 반복하지 않았다. 원격 보호/CI 실제 실행은 독립 PASS 범위가 아니다.
- 실제 AI·5개 UI의 완성도/디자인/브라우저 인수는 각각 지정 검수자의 증거가 필요하며 이 백엔드 테스트 결과로 대체하지 않는다.

## BI-04 기준 목록의 지역·매장 필터 오류
- 심각도 P2, 범위 필터 기능 결함. 본사 계정 자체는 전사 조회권한이 있어 권한 밖 데이터 유출 판정은 아니다.
- 재현 조건: 북부/남부 두 지역, 각 매장 및 남부 REGION 기준을 생성하고 본사로 북부 region_id 또는 store_id 필터 요청.
- 실제: region_id는 row.region_id=NULL인 남부 STORE 기준을 포함한다. store_id는 row.store_id=NULL인 남부 REGION 기준을 포함한다.
- 기대: 전사 공통 기준은 유지하되 매장 전용 기준은 해당 매장의 실제 지역을, REGION 기준은 선택 매장의 소속 지역을 확인하여 후보를 제한한다.
- 신규 테스트 `test_guideline_scope_filters_exclude_other_regions[region_id/store_id]`, 명령은 `... pytest server/tests/test_independent_acceptance.py -q --tb=short -k guideline_scope_filters`.
- 독립 RED: 2 failed / 12 deselected / 1.61초. 재현 결과와 테스트 freeze를 root에 전달했고 root 소스는 수정하지 않았다.

## 요구 대비 독립 확인 범위
| 요구 | 코드/독립 증거 | 판정 제한 |
|---|---|---|
| R-M03/17 현재 범위·알림 | 실제 세션에서 매핑 종료→목록0/read404, 운영자 GET/read403 | core 내부는 본인 작성이므로 독립 구현 검토 제외 |
| R-M07/08 기준·Reference | PostgreSQL 기준 버전 경합1성공/1충돌, 과거 Reference 비활성 후 사용원본 메타·media 허용, snapshot/hash 불변 | BI-04 범위 필터 수정 대기 |
| R-M09 사진 제출 | decode/MIME/확장자/치수·EXIF·보호경로 정적 확인, 총기준 초과시 파일·DB 원자 정리 | 실제 브라우저 사진 업로드 인수는 별도 |
| R-M13/14 이력·조치 | seed 시간 모순 재현·수정 검증, 해결조치 null삭제422, 두 문의 동시요청 멱등1건 | 기존 시연 DB 합성 기록 정정 대기 |
| R-M15/16 관제·통계 | 같은 모집단/필터 코드 대조, 주차 유효쌍·결측·unknown·분산0 독립 PG | 전체 UI drilldown은 시안별 QA |
| R-M21 데이터 | 안정ID·변경보존·재실행 무중복·Mock 구분·snapshot hash·이미지매체 계보 | 추가 queued/기준없음 경계 보완 대기 |
| R-M23/24 실행·보안 | preflight 실제5종, 미관리 API 재사용차단, Gitleaks actual stdin 무출력 차단 | 신규환경 setup/start/stop 및 Git/원격은 미실행 |
| R-S01/02 | 공지 운영 코드는 본인 작성 범위로 독립 PASS 제외, URL 상태 보존은 프론트 검수 범위 | 다른 독립 검수자 필요 |

## BI-04 GREEN 및 경계 시드 BI-05 RED
- root가 기준 필터를 실제 매장 소속지역까지 확인하도록 수정. 독립 필터2개 GREEN.
- root가 boundary-pending / boundary-no-criteria 2개를 추가하여 제출32개로 보완했다.
- BI-05a: 최초queued fixture에 queued Attempt1을 미리 만들어07의 최초 점유 시 생성 계약과 불일치. 재처리 예약과 구분하여 최초 상태에는 current_attempt_id=null/attempt0이어야 한다.
- BI-05b: 기준 도입 전(BASE−66) 빈Reference 시나리오보다 먼저(BASE−70) 같은 매장/카테고리의 Reference가 이미 등록되어 있다. Reference 도입시각 또는 시나리오 연결의 정합화가 필요하다.
- 독립 실행: 필터2 PASS / 시드1 FAIL / 11 deselected, 2.93초. 두 시드 문제를 하나의 경계 검증에서 모두 확인했다. root에 수정 요청·테스트 freeze 전달.
- 루트/래퍼 shell 스크립트9개는 각각 sh -n 구문검사 통과. 실행/정지·설치 자체를 실행한 증거로 간주하지 않는다.

## BI-05 GREEN / 최신 독립14 PASS
- root 보완: 최초 pending에는 Attempt를 만들지 않고 current_attempt_id=null 유지. 초기 Reference.created_at=BASE−65로 명시하여 기준/참조 도입 전 BASE−66 사례와 시간 순서 일치.
- historical_versions는 당시에 존재한 버전만 선택하고 실제 store/category scope를 복원해 우선순위를 다시 계산한다. 저장된 과거 snapshot은 기본 seed에서 갱신하지 않는다.
- 최신 독립 실행: `server/.venv/bin/python -m pytest server/tests/test_independent_acceptance.py -q --tb=short` → **14 passed, 7.91초**, deprecation warning2개.
- 새로 적재한 데이터와 할당된 root 영업 API·제한적 실행도구 검증에서 현재 열린 재현 결함은 없다. 이 판정은 기존 시연 DB의 과거12개 합성 snapshot 정정 실행을 포함하지 않는다.
- root는 별도 명시적 합성 이력 정정 도구 작성 예정. source_kind/안정ID/원본 hash/관계 가드와 반복 실행, 비대상 불변성을 추가 검토한다.

## 인계
- root 영업 API·새 seed·제한적 스크립트 독립 검증14 PASS. 최초대기 fixture는 모델 점유 없음→QUEUE_TIMEOUT/expired→시드 재실행 보존까지 추가 검증1 PASS(기존14 중 시드 검사 확장, 5.59초).
- BI-01~05의 재현 결함은 새 코드/새 데이터에서 해소했다. 기존 합성 이력 실데이터는 root의 별도 정정 절차로 처리한다.
- root의 후속 명시 배정으로 신규 정정 도구를 작성했다. 이 도구는 본인이 구현했으므로 독립 판정에서 제외하며 자기검증11 PASS만 보고한다. 상세는 seed-repair-implementation.md.
- root에 소스 freeze·독립 검토·실적용 소유권을 인계했다. 실제 demo/public 수정·백업은 이 검토자가 수행하지 않았다.
- 전체 신규 환경 setup/start/stop, Git hook/원격CI, 실제 AI/5개 프론트 전체 인수는 이 보고서의 독립 PASS로 대체하지 않는다.

## root 후속 Reference 시간 경계 독립 재검토
- 배정 범위: root가 수정한 `server/seed/__main__.py`의 historical_versions와 `server/tests/test_seed.py` 마지막 회귀만 읽고 실행한다. 소스·공유 DB·브라우저·런타임은 변경하지 않는다.
- 소스 확인: snapshot의 원래 Reference 후보 중 `ReferencePhoto.created_at <= when`인 ID만 남긴다. 필터 후 기존 순서를 유지하면서 position을 1부터 다시 부여한다. 새 과거 fixture 생성 시 미래 Reference가 섞이지 않으며, 기존 저장 snapshot을 갱신하는 경로는 추가하지 않았다.
- 새 root 회귀는 실제 seeded Reference의 created_at을 제출 시각 이후로 변경한 뒤 과거 snapshot을 다시 구성하여 해당 ID가 제외되는지 검사한다. 임시 SQLite DB와 tmp_path 이미지/자격 파일만 사용한다.
- 독립 실행: `server/.venv/bin/python -m pytest server/tests/test_seed.py -q --tb=short` → **1 passed, 2 warnings, 3.51초**. 경고는 테스트 라이브러리 deprecation이며 실패 없음.
- 해당 root 후속 수정은 독립 검토 PASS. 열려 있는 시간 경계 결함 없음. 이 검토 중 새 소스 파일이나 공유 DB 행은 수정하지 않았다.
- 기존 합성 이력 정정 실행은 root가 직접 독립 검토/실행 완료로 보고했다: 비PG10 PASS, demo/test dry-run 각40행, 0600 원본 백업 후 적용, 재실행0행, 경계 fixture 각11행 추가 후 재seed0행. 이는 root 보고 증거이며 이 검토자의 직접 실행 증거로 취급하지 않는다. 정정 도구는 본인 작성이라 여전히 자기 독립 PASS 범위에서 제외한다.
