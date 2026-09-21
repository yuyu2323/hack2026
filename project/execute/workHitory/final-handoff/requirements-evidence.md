# 요구 ID별 기존 실행 근거

2026-09-21 · contract_data · 기록 대조만 수행. [docs03](../../../docs/03-requirements.md)의 R-M01~24/R-S01~02를 기준으로 한다. 새 테스트·AI·DB·Browser·서비스 실행은 없다.

**판독 규칙:** 공통 API/단위·PostgreSQL 결과는 서버 동작의 근거이며 5개 UI 실행을 대신하지 않는다. UI01~05는 각각 별도 시안의 실제 브라우저 기록이다. “부분”은 확인된 기능을 취소하거나 미구현을 확정하는 뜻이 아니라, 해당 요구 전체의 인수 근거가 아직 충분하지 않다는 뜻이다. 새 경계 검수를 요청하지 않는다. 기존 초기 FAIL과 정정본을 구분하며, 아래 HTTP01/02는 초기 실패 파일이 아닌 최종 시각별 PASS 파일이다.

| 요구 | 권위 있는 기존 결과·명령 근거 | 실제 확인 범위 | 미완료·근거 한계 |
|---|---|---|---|
| **R-M01** 공통 서비스·5개 시안 | [최종 빌드 hash][build], [preview 원시 JSON][preview], [최종 서비스 JSON][runtime], [실행 명령·결과][run]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 5개 각각 build, dev/preview 포트·공통 세션/API, 점주/본사/운영자 **3경로군** 직접 접근·reload, 최종8서비스 생존. OFC·지역 업무는 각 시안의 앞선 dev UI 기록에 있음. | preview 3경로군을 모든 역할의 모든 화면으로 확대하지 않음. IA·배치의 최종 독립 판정은 R-M22. |
| **R-M02** 로그인·세션·CSRF | [코어 실행 명령·23 HTTP/SQLite+3 PG][core], [전체 실행 결과][verify], [독립 보안 검토][sec]; [HTTP01]·[HTTP02]·[HTTP04]·[HTTP05], [UI03] | 로그인 전 CSRF·세션 교체·logout 폐기·만료·CSRF/Origin 거절은 공통 tests/test_accounts.py. 각 UI 로그인·권한 철회, 별도 HTTP 검사 세션 login/logout. [실제 오류 복구][input]는01/02/04에 한정. | 5개 UI 각각의 모든 CSRF/Origin 오류 조합은 증거 없음. 공통 API 거절과 UI 초안 복구를 같은 검증으로 세지 않음. |
| **R-M03** 현재 역할·범위 | [HTTP01]·[HTTP02]·[HTTP03]·[HTTP04]·[HTTP05]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05]; [독립 서버 PG][backend] | 각 시안의 비활성/매핑 종료/역할 변경 후 기존 본문 제거, 지역·OFC·HQ 범위 차이. 실제 보호 media 허용200 기준과 운영자403·범위밖404. 03 HTTP는 운영자 경계만이며 지역 경계는 해당 UI 기록. | 모든 목록·집계·변경 경로의 모든 역할 조합을 UI에서 전수 실행한 것은 아님. 04 잘못된 photo ID의 최초404는 제외하고 정정67검사/16GET만 인용. |
| **R-M04** 계정·연결 관리 | [core], [verify], [운영01 JSON][op01], [운영02 정리 JSON][op02], [운영05 JSON][op05]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 다섯 시안 각각 합성 계정 생성·매핑·비활성·역할 변경·복원 UI. 공통 API 승격 금지/버전 충돌/연결 이력. 독립 JSON01/02/05는 최종 현재 상태와 감사까지 대조. | 03/04 운영 변경 전부에 별도 독립 DB JSON이 있는 것은 아님. 계정 검색의 모든 조건·운영자 승격 UI 부재 전수 확인은 공통 소스/정책 검토 수준. |
| **R-M05** 지역·매장·카테고리 | [core], [verify], [운영02 검수][op02review], [op05]; [seed]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 공통 test_operations의 매장 비활성·지역 변경/연결 정리·과거 행 보존. seed 카테고리4개. 각 UI에서 QA 카테고리 등록→수정→비활성,03은 신규 제출 목록에서 제외 확인. | **부분:** 지역·매장의 등록/수정/비활성 전체를 다섯 UI 각각 조작했다는 근거는 확인 못함. 공통 기능·카테고리 사례로 나머지를 완료 처리하지 않음. |
| **R-M06** OFC 내 관리 매장 | [core]의 PG 동시 claim 1승자 및 test_stores; [verify]; [op01]·[op02]·[op05]; [UI01]·[UI02]·[UI04]·[UI05] | 공통 범위·최소 후보·멱등 target·1명 제약/운영 정정.01/02/04/05 실제 후보→등록→관리1/후보0→역할 복원/연결 종료.01 목록 갱신 결함은 수정 후 실제 재확인. | **부분:**03에서 OFC 역할 변경·담당 범위 조회는 있으나, 후보에서 직접 담당 등록하는 완료 근거는 해당 기록에서 확인 못함. |
| **R-M07** 4단계 기준·버전 | [독립 PG 경합·범위][backend], [AI01]·[AI02]·[AI03]·[AI04]·[AI05]; [독립02 메타][meta02], [운영02 검수][op02review], [meta04], [pair05] | 01/03/04/05는 UI4단계 등록 후 CATEGORY 승자·버전 변경·불변 snapshot.02는 실제 AI3건 이후 상위3개 등록 및 읽기 전용 resolve에서4후보/CATEGORYv2 승자 확인. 공통 변경 경쟁1성공/1충돌. | 02의 후속4단계 후보를 이전 AI 입력에 소급하지 않음. 모든 역할×단계 편집 거절 UI 조합은 전수 근거가 아님. |
| **R-M08** Reference 관리 | [AI01]·[AI02]·[AI03]·[AI04]·[AI05], [meta01]·[meta02]·[meta04]·[pair05]; [비활성 원본 독립9검사][inactive]; [input] | 각 시안 등록·실파일 교체·과거v1 원본 유지. 실제 분석 Reference2장 또는3장 입력/hash. 현재 관리 범위의 미사용 비활성 원본 허용과 다른 범위 거절.01/02/04는409 재조회 후 파일·설명 보존 재저장. | 0장 분석은 기존 Mock/공통 검증과 구분; 실제AI 모든 시안에서0~3장 각각 호출한 것은 아님.03/05 별도409 복구 UI는 미확인. |
| **R-M09** 사진·질문 제출 | [입력 JSON][inputjson], [input], [공통 업무 실행][business], [verify], [backend], [AI01]·[AI02]·[AI03]·[AI04]·[AI05] | 다섯 UI 각각 형식/10MiB 초과/6장 차단,0장 처리,5장 미리보기·순서·삭제,2000자와 추가키 제한. 실제 제출1장 및 worker snapshot. 공통 submission replay1건·불법 이미지/멱등키 누락 거절·실패 업로드 정리. | 정확10MiB 허용/합계50MiB를 UI에서 실제 실행한 증거는 없음. 각 UI의 동시 이중 제출을 DB에서 전수 대조한 결과도 아님. |
| **R-M10** 실제 AI·검증 저장 | [AI01]·[AI02]·[AI03]·[AI04]·[AI05], [meta01]·[meta02]·[meta04]·[pair05]; [실제 worker PG JSON][workerreal], [AI 구현 실행][aiimpl], [verify] | 시안별 실제 export3건씩 별도. 사진/질문/기준/Reference의 실제 전달, strict schema/ID/version/position 검증 및 저장. 단위39건은 fake executor, 실제 모델 근거와 구분.03은 root 실제 export/브라우저 기록이며 다른 시안의 독립 DB 검사 수를 빌리지 않음. | 30초 달성은 별도 성능 항목. 실제 시안 표본은 미달이며 단일 조기 worker25.805초를 일반화하지 않음. |
| **R-M11** 처리·지연 | [AI01]·[AI02]·[AI03]·[AI04]·[AI05], [다섯 UI 큐/통신 기록][queued], [복구 JSON][qrecovery], [timeout 독립 JSON][qmeta] | 각 시안 queued/running/지연/완료/기술실패, 동일 탭 API 오류→복구, 합성 큐의 timeout·결과0. 실제 모델/DB 시간 및 가능한 브라우저 관찰창 보존. | **부분:** 화면 이탈 polling 종료·정확2초 동작의 각 UI 실측 근거 없음.02 첫/child의 정확 표시시간 미기록, 일부는 관찰 상한.05 재처리 시계 역전은 [원인 미확정][op05review] 유지.30초 목표 미달. |
| **R-M12** 결과·unknown | [AI01]·[AI02]·[AI03]·[AI04]·[AI05]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05]; [input], [독립 디자인 잔여][designpending] | 각 시안 실제 질문답·사진근거·기준판정·행동·Reference·제한 확인.02 실제5 unknown/준수null·판단0;03/04/05도 실제 또는 Mock unknown을 구분. 기준0/Reference없음은01/02/05 추가 UI,03/04 기존 근거. |01 unknown 세부의 최종 독립 시각 확인,02 Reference 번호 카드의 정상 viewport 등 일부 시각 증거는 최종 검토 중. 존재하는 DOM과 보이는 화면을 같게 판정하지 않음. |
| **R-M13** 이력·재피드백 | [AI01]·[AI02]·[AI03]·[AI04]·[AI05], [meta01]·[meta02]·[meta04]·[pair05]; [보존 JSON][qmeta]; 각 [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 다섯 시안 새 사진·parent 재제출, 날짜·기준 버전·비교 제한, 기존 snapshot 보존. 사후25검사의 기존15 snapshot/사전 hash가 있는12 result 보존 범위 명시. |03의 나머지3 result에는 같은 사전 hash baseline이 없어 “15 result hash 모두 불변”으로 확대하지 않음. 모든 기간/페이지/뒤로 동작은 R-S02 별도. |
| **R-M14** 이슈·조치 | [business], [backend], [verify]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 각 UI 문의/자동 확인 이슈→OFC 의견·해결→점주 읽기 전용 이력. 공통 resolved resolution null 거절, 이슈 version409, 같은 멱등 요청1건. AI review와 조치 분리. | 모든 시안에서 후속 결과를 근거로 재개/종결하는 모든 분기까지 실행한 근거는 없음. 사용자 저장 댓글의 의미 타당성을 자동 테스트가 증명하지 않음. |
| **R-M15** 관제·검색 | [business], [backend], [verify]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 각각 OFC→대상 기록/사진·조치, 현재2/지역3/HQ6 범위.01 동일 매장·분류·기간 URL/뒤로 복귀 명시,04 동일 조건 제출/성공/실패/이슈 집계,05 조건 이력 링크. 공통 API 동일 필터. | 모든 시안의 전체 필터 조합·모든 KPI drilldown·미제출 대표 화면을 전수 확인한 것은 아님.04 미제출 대표 카드 등 시각 잔여는 [designpending]. |
| **R-M16** Mock 상관·집계 | [독립 PG 통계][backend], [verify]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 공통 동일 주차 유효쌍·누락/unknown 제외·분산0/null.01 n17/n3분산0/n0,02 기간리포트/n0,03 n5+n3분산0 및 기간집계 후속,04 n6/n0,05 n6/n3분산0/n0·지역 단위. Mock·비인과 표시. | **부분:**02/04의 분산0 및04 기간 집계 전체를 해당 UI에서 직접 본 완료 근거는 약함. 공통 계산 PASS로 시안별 표시 전부를 대체하지 않음. |
| **R-M17** 앱 알림 | [backend]의 매핑 철회·운영자 알림 거절, [business], [verify]; [HTTP01]·[HTTP02]·[HTTP03]·[HTTP04]·[HTTP05]; [UI01]·[UI02]·[UI03]·[UI04]·[UI05] | 각 UI 점주 조치 알림→읽음/이슈 이력;01 22→21,03 13→12,05 16→15. 운영자 목록/본문·영업 알림403 및 메뉴 제외. 현재 매핑 종료 후 목록0/read404 공통 독립 검증. | **부분:** OFC·지역·HQ 각각의 수신/읽음 및 다른 수신자 알림 차단을 모든 시안에서 UI 전수 실행한 근거는 없음. 외부 푸시 구현/검증으로 확대하지 않음. |
| **R-M18** 플랫폼 상태 | [core], [verify]의 test_service_health_never_calls_model_and_separates_fixture; [sec], [preview], [runtime] | API/DB/AI/worker 상태, heartbeat·실제 모델 결과 상태와 프로세스 생존 구분, Mock 작업 분리. 상태 조회가 analyze를 호출하지 않는 공통 검사. 최종 preview 운영 화면 별도 포함. | preview의 일부03/04/05 직접 접근 snapshot은 로딩 중이며05 reload도 로딩이다. 이를 모든 운영 데이터의 완성 렌더 근거로 확대하지 않음; 앞선 시안별 운영 UI 관측과 분리. |
| **R-M19** 실패 재처리 | [worker], [BR 수정/PG 결과][br], [verify], [op01]·[meta04]·[op05], [UI01]·[UI02]·[UI03]·[UI04]·[UI05]; [qmeta] | 실제PG 경쟁·키 replay·다른키 충돌·lease/기한·늦은 결과·원자 rollback. 다섯 UI 종료 실패→사유→실제AI 새시도 성공/과거 보존, 진행/성공 재처리 제한.03·공통 큐 timeout 포함. | worker 경합/늦은응답은 격리 테스트이며 브라우저에서 같은 경합을 실행했다고 하지 않음. 과거 fixture의 최초 접수시간은 정상 신규 성능에서 제외. |
| **R-M20** 운영 감사 | [core], [sec], [verify]; [op01]·[op02]·[op05], [UI03]·[UI04] | 공통 동일 version 경쟁1commit/감사1건, 재처리 후처리 실패 rollback. 각 시안 수행자/사유/전후값·종료 연결 이력 표시;01/02/05는 독립 DB 대조. 비밀/영업 본문 whitelist·수정삭제 UI 없음 소스 검토. | 일부01/03 캡처는 audit-after 전체가 화면 밖이다. 모든 종류의 운영 변경에 개별 실패 주입을 수행한 것은 아니므로 원자성 전수시험으로 표현하지 않음. |
| **R-M21** 시드·생성 이미지 | [실제 생성10장/hash][images], [독립 Golden3][golden], [seed], [backend], [정정 실행 JSON][repair], [최종 setup][run] | 6매장·역할 계정·4분류·4단계/Mock8주·실제10파일·4Reference/6평가 이미지 용도 분리.573행→재seed0,32제출 경계 보완. 두 DB 한정40행 시간순서 정정→반복0, 최종 setup 기존 seed263개 보존. | 초기 generation의 REVIEW/Golden0 및 master G3 미체크는 후속 근거보다 오래됨. 정정 도구의 멱등0과 일반 시드 멱등0은 별도 검사. 신규 실제 데이터 생성 필요 없음. |
| **R-M22** 접근성·독립 디자인 | [디자인01][d01]·[디자인02][d02]·[디자인03][d03]·[디자인04][d04]·[디자인05][d05], [designpending] | 각 시안 독립 검토자가 실제 지정 크기 PNG·일부 키보드/초점·사진/표/대비 결함과 수정본을 검수. 기능 QA·작성자와 구분. 현재 추가 기존 PNG 검토는 contract_ai 담당. | **미완료:** 모든 기준의 최종 독립 PASS 아님. 미관측 키보드/목록4상태·부분 잘림/초점 등 해당 정본 상태 유지.200%는 사용자 후행 NOT_RUN. 이 표 작성으로 시각 판정하지 않음. |
| **R-M23** 전체 흐름·실행 인계 | [UI01]·[UI02]·[UI03]·[UI04]·[UI05]와 각 [AI01]·[AI02]·[AI03]·[AI04]·[AI05]; [run], [build], [preview], [stop], [runtime]; [매뉴얼5개 목차][manual], [문서 독립 PNG][manualreview], [문서 DOM][manualdom] | 각 시안 실제 제출/재제출/기준·Reference 변경/관리자 조치, 전용 storeloop_test·test-media. 문서 setup 재실행 exit0,5개 최종build/preview·stop종료/재start 확인.5 HTML/47화면·지정1440/390 렌더 인계. | setup은 **기존 의존성/DB 보존 재실행**이며 빈 새 기계 최초 설치와 같지 않음. 미확인 전체 디자인 인수는 R-M22. 문서 200%/OS 차단 오프라인/인쇄 미실행, Markdown 내장 뷰어 제한 유지. |
| **R-M24** 보안·전파·정직성 | [초기 훅 실제7검사][hooks], [sec], [마지막 보안 JSON][secfinal], [오탐 정정][secresolution], [내용 보존 대조][secpreserve], [계약 전파][contracts], [원본 hash 독립 대조][original] | 합성 임시Git pre-commit/pre-push, merge2회귀 및 최종 보안11. 전체1084후보에서 보고서 SHA 인접문구 오탐1건을 형식만 변경; 변경22재검사,경로검사1087. before/after 각216해시 및 나머지 결과 필드 보존. 계약별 ACK·반영·독립 검토 추적. | 원격 CI NOT_RUN·branch protection403 플랜 제약. 스캔 PASS는 모든 비밀 위험 부재의 수학적 증명 아님. 이전 실패/오탐/시간 이상·미실행을 보존하며 최종 디자인 전체 완료로 선언하지 않음. |
| **R-S01** 운영 공지 | [core]의 공지 기간 테스트, [verify], [op02], [UI01]·[UI02]·[UI03]·[UI04]·[UI05], [preview] | 각 시안 QA 공지 생성/역할 화면 게시·활성 변경과 종료 공지 제외;02/03은 비활성 후 새 조회의 비노출 명시. 공통 기간/감사 검증, 최종 운영 역할에도 공통 시연 안내 확인. | 모든 역할×기간 경계×시안의 UI 조합을 전수 검증한 것은 아님.01/04의 비활성 저장을 새 점주 조회 비노출과 동일시하지 않음. |
| **R-S02** 목록 탐색 편의 | [UI01]의 필터/기간→상세→뒤로 실제 유지, [UI04]의 조건 복귀, [UI05]의 주소복사/동일조건 이력 링크; [designpending], [verify] | 01 연속필터 수정 후 실제 URL·뒤로 복귀,04 조건 유지 링크,05 주소복사·조건 연결. 테스트·소스 근거는 각 UI 관측과 분리. | **부분:**02/03 전체 페이지·필터 복귀,05 복사 URL 직접 재열기, 모든 시안 재조회 중 기존 내용/갱신 표시·초점 비강제 이동은 아직 완결 근거 없음. |

이 표는 실행을 추가하지 않은 시점별 근거 색인이다. [이전 완료 감사](independent-completion-audit.md)의 runtime RUNNING은 이후 [최종 실행 기록][run]으로 해소됐다. 나머지 원시 기록의 초기 실패·대기 문단은 삭제하지 않고 후속 결과와 함께 읽는다. 200% 후행과 사람의 최종 시안 선택은 계속 별개다.

[UI01]: ../integration-concept-01/browser.md
[UI02]: ../integration-concept-02/browser.md
[UI03]: ../integration-concept-03/browser.md
[UI04]: ../integration-concept-04/browser.md
[UI05]: ../integration-concept-05/browser.md
[AI01]: ../integration-concept-01/actual-ai.json
[AI02]: ../integration-concept-02/actual-ai.json
[AI03]: ../integration-concept-03/actual-ai.json
[AI04]: ../integration-concept-04/actual-ai.json
[AI05]: ../integration-concept-05/actual-ai.json
[HTTP01]: ../integration-concept-01/independent-live-http-20260921T124615Z.json
[HTTP02]: ../integration-concept-02/independent-live-http-20260921T124627Z.json
[HTTP03]: ../integration-concept-03/operator-live-http.json
[HTTP04]: ../integration-concept-04/independent-metadata-http.json
[HTTP05]: ../integration-concept-05/independent-live-http.json
[meta01]: ../integration-concept-01/independent-ai-metadata-20260921T124354Z.json
[meta02]: ../integration-concept-02/independent-ai-metadata-20260921T124410Z.json
[meta04]: ../integration-concept-04/independent-metadata-http.json
[pair05]: ../integration-concept-05/independent-pair-metadata.json
[op01]: ../integration-concept-01/independent-operations-metadata-20260921T125136Z.json
[op02]: ../integration-concept-02/independent-operations-cleanup-metadata.json
[op02review]: ../integration-concept-02/independent-operations-review.md
[op05]: ../integration-concept-05/independent-operations-metadata.json
[op05review]: ../integration-concept-05/independent-operations-review.md
[verify]: ../final-verification/verify-latest-20260921T111826Z.json
[core]: ../db-schema/implementation-v1.md
[business]: ../backend-business/implementation.md
[backend]: ../backend-independent/g4-review.md
[br]: ../backend-review/independent.md
[worker]: ../analysis-jobs/implementation.md
[workerreal]: ../analysis-jobs/evidence/real-worker-001.json
[aiimpl]: ../local-ai/implementation.md
[inactive]: ../backend-independent/inactive-reference-media.md
[input]: ../input-boundary/browser.md
[inputjson]: ../input-boundary/browser-evidence.json
[queued]: ../queued-browser/browser.md
[qrecovery]: ../queued-browser/api-recovery.json
[qmeta]: ../queued-browser/independent-metadata.json
[seed]: ../demo-data/seed.md
[images]: ../demo-images/generation.md
[golden]: ../demo-images/golden-review.md
[repair]: ../backend-business/seed-repair-independent-summary.json
[run]: runtime.md
[build]: build-files.json
[preview]: preview-browser.json
[stop]: stop-result.json
[runtime]: runtime-final.json
[sec]: ../security-independent/final-review.md
[hooks]: ../repository-security/initial-audit.md
[secfinal]: security-final.json
[secresolution]: security-resolution.json
[secpreserve]: security-report-preservation.json
[contracts]: ../docs/contract-register.md
[original]: ../local-ai/command-doc-independent.json
[manual]: ../../../deliverables/manuals/index.html
[manualreview]: ../manuals-browser/independent-recheck.md
[manualdom]: ../manuals-browser/final-dom.json
[designpending]: ../frontend-comparison/pending-visual-evidence.md
[d01]: ../../designReview/concept-01/review-001.md
[d02]: ../../designReview/concept-02/review-001.md
[d03]: ../../designReview/concept-03/review-001.md
[d04]: ../../designReview/concept-04/review-001.md
[d05]: ../../designReview/concept-05/review-001.md
