# 공통 계약 확정·변경 전파 등록부
- 단일 수정 소유자: root
- 상태: G1 ACCEPTED — 상세 계약 확정, G2 구현 착수 승인(오케스트레이터 자율 결정)
- 상위 계약: docs/00·01·02 원문. 사용자가 첨부한 목표의 상세 수행 권한에 따라 세부 결정을 자율 확정한다.

## 초기 문서 작성과 독립 검토
| 문서 | 작성자 | 독립 검토자 | 버전/상태 | 차단 결함 |
|---|---|---|---|---|
| 03 요구사항/04 화면 | product_design | contract_ai | v1 초안 작성중 | 검토 대기 |
| 05 DB/06 API | contract_data | product_design | v1 초안 작성중 | 검토 대기 |
| 07 AI/처리,08 데이터,09 검증 | contract_ai | contract_data | v1 작성·독립검토 PASS | AIR-01~05 수정 재확인 |
| 10 실행 | root | contract_ai | v1 초안 | 검토 대기 |

## 변경 전달
| ID | 영향 담당 | 행동 | 상태 | 확인/검증 근거 |
|---|---|---|---|---|
| DOC-EXEC-001 / docs10,AGENTS 신규 | contract_data | 환경·DB 실행 계약 확인 | 확인 완료 | 담당 에이전트 수신 회신·각 작업 이력 |
| DOC-EXEC-001 | contract_ai | 데이터·검증·AI 실행 반영 | 확인 완료 | 에이전트 메시지, local-ai 이력 반영 예정 |
| DOC-EXEC-001 | product_design | 공통 화면·실행 범위 확인 | 확인 완료 | 담당 에이전트 수신 회신·각 작업 이력 |
| 초기 계약 전부 | 향후 구현/QA/디자인/매뉴얼 담당 | 배정 시 최신 버전 필독·영향 확인 | 전달 대기 | 미배정 |

확정은 파일이 있다는 사실만으로 하지 않는다. DB/API 필수 내용, 문서 간 데이터·권한·상태·테스트 대응, 독립 검토 차단 문제 해소 후 버전과 근거를 기록한다.

- DOC-EXEC-002 (G1 초안 정합화): Python import는 프로젝트 루트에서 server.* 절대 패키지를 사용. seed 명령을 python -m server.seed로, Alembic 명령을 루트 기준 -c server/alembic.ini로 명확히 함. 모델/AI 담당에게 전달; 실제 구현·검증은 G1 후.

- 독립 AI/데이터/검증 검토 근거: [independent-ai-review](../db-schema/independent-ai-review.md). 실제 실행 검증은 아직 NOT_RUN.

## G1 확정 결정 — 2026-09-21
- 요구03 PD-001/1.0-review, 화면04 PD-002/1.1-review, DB/API05·06 CONTRACT-DATA-1.0b, AI07 AI-001/1.0.0, 데이터08 DATA-001/1.0.0, 검증09 QA-001/1.0.0, 실행10 DOC-EXEC-002/v1.0을 공통 계약으로 확정한다. 원본 헤더의 검토대기 표시는 이 확정 기록으로 대체하고 각 작성자가 ACCEPTED로 갱신한다.
- Concept01 상세 디자인 DS01-002/1.1-review는 별도 구현 선행 문서 검토 통과. 최종 실제 디자인 검수는 G4에서 수행.
- 독립 데이터 검토: [DR-D01~07 전부 해소/PASS](../product-design/independent-data-review.md). 상세/담당후보API, 동일filter drilldown, 최신job·이슈 이름, 멱등 targetID, Reference state_version, 입력검증 보완.
- 독립 AI/데이터/검증 검토: [AIR-01~05 해소/PASS](../db-schema/independent-ai-review.md). result/attempt_number/rule_key80, worker deadline130·CLI120·lease140, 늦은본문 폐기 명확화.
- 독립 제품/실행/디자인01 문서 검토: [PDR 재검토 PASS](../local-ai/independent-product-review.md). DTO/endpoint 및 컨트롤 대비 토큰 반영.
- DB/API 필수 입력·응답·권한·상태·제약이 정의되었고 구현 차단 결함이 남지 않음. 관련 문서의 같은 결정 반영을 실제 파일에서 재확인함. 상위00~02 원문 해시 동일. 사람 판단이 필요한 상위충돌 없음.
- 따라서 추가 사람 승인 없이 G2 TDD·구현·실제 AI 조기검증을 시작한다. 이 결정은 실제 구현·DB·AI·브라우저 PASS를 의미하지 않는다.
- 공통 결정 수신: 세 작성자와 root가 변경 전파 메시지로 확인. 후속 구현/QA 담당은 배정 때 이 확정본과 이후 변경을 읽고 확인·반영 결과를 각 이력에 기록한다.

## G2 명확화·전파
| 변경 ID | 대상 | 상태 | 근거 |
|---|---|---|---|
| CONTRACT-DATA-1.0c context평탄화·assignees페이지 | root 업무API | 반영·검증 완료 | business_api7 PASS |
| CONTRACT-DATA-1.0c | frontend01 | 확인 완료 | product_design ACK, 화면 구현중 |
| CONTRACT-DATA-1.0c | frontend02·03 | 전달 완료 | 배정시 최신06 및 추가메시지 전달 |
| IMG-GOLDEN-001 독립3파일관찰 | product_design | 확인 완료 | manifest수정소유 인계ACK, golden-review.md |
| 공통계약 G1 이후 전체 | frontend04·05/QA/매뉴얼 | 전달 대기 | 미배정, 배정시 최신계약필독 |

- frontend01 경로 배정 오기 frontend/concept-01은 코드 생성 전 web-concepts-01로 정정하고 수신 확인했다. 상위02 원문은 변경하지 않았다.

## PD-003 / NOTIFY-CLARIFY-1
- docs03/04/06은 영업 알림을 점주·영업 역할에 한정하고 platform_operator GET/read 403을 명확화. 공지는 전 역할 유지. 기존 API 권한을 바꾸지 않는 명세 일치 수정.
- 01~05 모두 ACK·운영자 영업 알림 비노출/직접 경로 제한 반영. 01 정책6+UI9, 02 13, 03 17, 04 11, 05 정책5+UI10 검사 PASS(후속 HMR 회귀는 별도 기록).
- root가 docs06 수정 수신. 매뉴얼은 동일 역할 구분 반영 필요.

## MEDIA-CLARIFY-1
- docs06 SubmissionDetail에 선택적 reference_photos:[{reference_id,photo:Photo}] 추가. 현재 제출 인가 후 저장snapshot에 연결된 미디어 메타만 조회. 원본 snapshot/hash/AI strict 입력/DB 변경 없음.
- 작성자 contract_data·root ACK. root 응답누락 KeyError RED→business7 PASS. 독립검토자 과거 비활성 Reference/보호URL/snapshot불변 PASS.
- 01~05 모두 ACK·snapshot 순서의 reference_id→Photo 메타 연결 반영, 생성 이미지 배지/보호URL 회귀와 5개 build PASS. 근거 execute/workHitory/frontend-integration-metadata/media-clarify-1.md. 실제 화면은 시안별 브라우저 인수에서 따로 확인한다.

## MEDIA-CLARIFY-2
- 실제03 HQ 관리화면에서 미사용 교체 Reference v1의 보호사진만404인 것을 확인했다. GET Reference관리이력은허용되고DTO에URL도있지만기존매체규칙은활성/snapshot만허용한계약공백이다.
- 상위00/01/02의기준·Reference관리/과거보존과현재권한원칙을유지한다. 새DTO/DB변경없이 영업관리자 현재Reference조회범위안에서비활성/교체revision원본·썸네일접근을허용하도록docs06을먼저명확화. 점주/운영자/다른범위/종료매핑권한은확대하지않는다.
- 독립 contract_data가 같은원인확인·회귀RED작성, root가계약정합확인후구현담당. 5개UI는기존보호URL을사용하므로클라이언트호출구조변경없음. 영향담당에전달하고테스트·실제브라우저·매뉴얼재검수추적.
- 상태: root 구현 완료, contract_data 독립 기능·권한 검증 PASS. 수정 전 관리자4개 RED/보호 경계5개 PASS → 수정 후 신규9개 모두 PASS(1.90초). 현재 관리 범위만 비활성 원본·썸네일을 허용하고 점주·운영자·다른 지역·미배정/종료 매핑의 제한을 보존함을 소스/HTTP로 확인했다.
- 증거: `server/tests/test_inactive_reference_media.py`, `execute/workHitory/backend-independent/inactive-reference-media.md`. 실제 브라우저 재확인·매뉴얼 재검수는 root의 별도 인수 결과로 추적한다.

## CMD-01 실행·검증 명령 정합화

- 원인: G1의 예정 명령이 현재 README/docs09/docs10에 남아 저장소에 없는 Playwright CLI, 잘못된 실제 AI pytest 경로, 일부 프론트 검사 누락 및 환경·종료 절차의 불일치가 발생했다. [독립 대조 CMD-01~09](../runtime-independent-reproduction/command-document-review.md)에 실제 수집 결과와 수정안을 기록했다.
- 영향: root가 수정안을 수락했고 contract_data가 세 문서와 이 절을 단독 반영한다. 원본00/01/02, E01~E08, 시안별 실제 UI·실제 AI·독립 디자인·매뉴얼 완료 요구는 유지한다. API/DB 변경은 없다. PREVIEW-PORT-01 제품 보완은 5개 resolveConfig 독립 PASS이며 실제 preview 인수와 구분한다.
- 검증 계획·추적: [반영 이력](../runtime-independent-reproduction/command-document-update.md), [체크리스트](../../checkList/runtime-independent-reproduction/command-document-update.md). 명령 수집·구문·링크·필수 요구 보존을 확인하고 contract_ai 독립 문서 재검토와 root 수신을 추적한다.
- 상태: README/docs09/docs10 반영 완료·동결, contract_ai 수신·[독립 재검토 PASS](../local-ai/command-doc-independent.md), 미해소 결함 없음. [실증 결과](../runtime-independent-reproduction/command-document-update.md#실제-검증)와 [해시·링크·구문·종료 예시 검사](../runtime-independent-reproduction/command-document-checks.json)를 보존했다. 원본00/01/02·docs09 §2~6 해시 불변, 링크39·shell구문9·격리 종료경계3 PASS. 실제AI 테스트 위치는 collect-only로 재확인했다. 독립 검토도 현재 스크립트/테스트·문서 해시·상위 필수 범위 보존을 확인했다. 문서 정합성 PASS이며 서비스 실행·실제 AI·브라우저 인수 PASS를 뜻하지 않는다. root 완료 인계.
