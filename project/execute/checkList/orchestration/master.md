# StoreLoop 구현·검증·시연 인계
- 담당: root (오케스트레이터)
- 상태: 사용자 승인 범위 완료. 남은 세부 검수는 후행으로 인계하고 이번 목표 종료.
- 기준: docs/00-vision.md → 01-architecture.md → 02-development-orchestration.md (원문 보존)
- 실제 Git 루트: hack2026. 프로젝트 루트: hack2026/project. 기존 미추적 deliverables, execute, goal.md 보존.
- 기존 구현/AGENTS/ralph 문서: 없음. 기준 3개만 추적됨.

## 게이트
- [x] G0 저장소·상위 문서 조사
- [x] G1 요구사항·화면·DB·API·AI·상태·데이터·검증·실행 계약 작성
- [x] G1 독립 검토와 차단 결함 해소, 버전 확정
- [x] G2 저장소 보안·의존성·실제 AI 조기 검증
- [x] G2 공통 백엔드·PostgreSQL·작업자·AI 서버
- [x] G2 5개 React 패키지, 각 점주·영업·플랫폼 영역
- [x] G3 생성 이미지·재현 시드·시연 구성
- [ ] G4 전체 인수 — 핵심 기능·보안·독립 검토 및 발견 결함 수정 완료. 미검수 세부 항목은 사용자 결정으로 후행 인계.
- [x] G5 5개 HTML 매뉴얼·화면 증거·실행 방법·선택 자료 인계

## 파일 소유권과 의존성
| 담당 | 전용 수정 경로 | 현재 작업 | 선행 |
| root | AGENTS.md, docs/10-execution.md, execute/*/orchestration, execute/workHitory/docs/contract-register.md, 루트 구성·보안 | 실행/통합/확정 | 상위 문서 |
| contract-data | docs/05-database.md, docs/06-api.md, execute/*/db-schema | DB/API 계약 | 상위 문서 |
| product-design | docs/03-requirements.md, docs/04-screens.md, execute/design/*, execute/*/product-design | 요구사항·5개 시안 명세 | 상위 문서 |
| contract-ai | docs/07-ai-processing.md, docs/08-data.md, docs/09-validation.md, execute/*/local-ai | AI/상태·데이터·검증 계약 | 상위 문서 |

코드·마이그레이션은 G1 확정 후 시작한다. 모델·마이그레이션 작성자는 contract-data 한 명으로 유지한다. 독립 검토 담당은 본인이 작성하지 않은 계약을 검토한다. Git 변경은 root만 수행하며 원격 반영은 이번 로컬 목표에 포함하지 않는다.

## G2 실행 배정 (G1 확정 후)
| 담당 | 단일 수정 소유 경로 | 완료 증거 |
|---|---|---|
| contract_data | 모든 server/*/models.py, core/*, migrations/*, alembic.ini, accounts/stores/operations의 schemas/service/router, requirements.in, tests/conftest.py·해당 도메인 테스트 | 모델/migration·세션·현재범위·운영 테스트 |
| contract_ai | ai-service/*, packages/review_contract/*, server/analysis_jobs/service.py·worker.py·작업자 테스트, AI/스키마 테스트 | Codex 실제 조기 입력·출력·실패검증·PG 상태전이/경쟁 검증 |
| product_design (demo-images) | scripts/seed/assets/shelves/*, scripts/seed/manifest.json, demo-images 기록 | 실제10파일·시각검수·Reference/제출 분리 |
| root | 보안/루트설정/런타임/scripts(이미지경로 제외), packages/api-client, server/main.py 및 backend-business 체크리스트에 명시된 코드 | 설치·실행·업무통합·seed·검증 |
| product_design (frontend-01) | web-concepts-01/*, 해당 작업 기록·design/concept-01 | 관제 데스크 전체 역할·실제 API 연결 |

프론트02~05 디자인/개발, 독립 QA/디자인/매뉴얼 담당은 선행준비와 슬롯 가용에 따라 다음 배치에서 지정한다.

## 추가 프론트 배정
- concept02: web-concepts-02와 design/concept-02·자기기록만. 우선순위카드.
- concept03: web-concepts-03와 design/concept-03·자기기록만. 사진/근거 inspector.
- 두 담당은 G1정본 수신·세부설계 후 구현. frontend04/05 및 독립검토는 다음 가용 슬롯에 배정.

## 후속 배정
- concept04: web-concepts-04와 design/concept-04·자기 기록. 모바일 현장 포켓, 전체 역할.
- concept05: web-concepts-05와 design/concept-05·자기 기록. 탐색·비교 작업영역, 전체 역할.
- contract_data: root 구현 업무·시드·스크립트의 독립 검수, backend-independent 기록과 신규 독립 테스트만. 기존 root 코드 수정 금지.
- root: 시안별 실제 브라우저 기능 인수. 최종 디자인 검수는 별도 담당 배정 필요.

## 최종 검수·인계 소유권
- root: 5개 실제 브라우저 기능 인수·실제 AI·viewport PNG·런타임 재현·통합 기록.
- contract_ai: 5개 최종 독립 디자인 검수(개발/기능QA와 분리), 매뉴얼02, 시안 비교.
- product_design: 매뉴얼01/03/04/05(초안 동결), 핵심 서버·AI·런타임 최종 독립 보안 검토.
- contract_data: root 업무·시드 독립검증14 PASS, 정정도구 구현11 PASS 인계; root가 정정도구 독립검토·로컬 두DB 적용/재실행0 완료.
- concept02: 제한적 5개 entry root 재사용 HMR 보완 완료, 02 테스트15 PASS·5개 build PASS, 다시 동결.
- G4/G5는 브라우저·실제 AI·최종 시각/매뉴얼/실행 재현이 끝날 때까지 진행 중이다.

## 2026-09-21 매뉴얼 우선 인계 상태

사용자의 “나머지 검수 최소화, 매뉴얼 먼저” 지시에 따라 추가 경계 검수를 확대하지 않는다. 5개 HTML과 실제 화면47장·통합목차를 인계했다. G3의 오래된 대기 표시는 후속 근거에 맞게 갱신했다. [독립 완료 점검](../../workHitory/final-handoff/independent-completion-audit.md).

- 설치 문서 그대로 재실행 PASS: 기존 설정·263개 기존 seed 보존. macOS Python CA 누락은 TLS 검증을 유지하는 certifi CA 추가로 수정했다.
- 최종5개 build와 preview의 점주/본사/운영자3경로×5 직접접속·새로고침 PASS. 실제 API 로그인·화면 확인, 추가 모델 호출0.
- 일반 시연 DB start→중복 start→stop→종료 확인→start 재현 완료. 현재 API8000/AI8010/worker/5시안5173~5177 실행 중이다.
- [최종 실행 근거](../../workHitory/final-handoff/runtime.md), [매뉴얼 목차](../../../deliverables/manuals/index.html).
- G4/G5 전체 PASS를 주장하지 않는다. 실제200%는 사용자 후행, 일부 독립 디자인 근거·목록/키보드 세부 확인은 미실행이다. 이미 확인한 핵심 업무·AI·복구는 반복하지 않는다. 실제AI30초 목표는 미달이며 최종시안은 사람이 선택한다.

## 목표 종료 결정

2026-09-21 사용자 명시 응답: “남은 검수는 후행으로 넘기고 목표 마무리”. 이번 최소 검수·매뉴얼 인계 범위는 완료한다. 원래 G4 전수 인수의 미확인 항목을 PASS로 올리지 않고 후행 작업으로 분리한다. 200% 확대를 비롯한 실제 잔여·근거는 [독립 디자인 대조](../../workHitory/final-handoff/design-evidence-reconciliation.md) 및 [요구사항별 표](../../workHitory/final-handoff/requirements-evidence.md)에 보존한다. [결정 기록](../../question/orchestration/minimum-handoff.md), [최종 로컬 인계](../../../deliverables/local-handoff.md). 최종 시안 선택은 사용자에게 남기며 원격 push·배포는 하지 않았다.
