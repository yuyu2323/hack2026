# contracts-v1: 공통 요구사항·화면 계약

- 담당: product_design
- 상태: RUNNING
- 체크리스트: [contracts-v1](../../checkList/product-design/contracts-v1.md)

## 2026-09-21 — PD-001 작성 전 기록

- 기존 상태: docs에는 00·01·02만 있으며 서비스·프론트 소스 없음. 존재하지 않는 화면/API 계약을 확정된 것으로 취급하지 않는다.
- 변경: docs/03-requirements.md, docs/04-screens.md 신설.
- 이유: 사용자 목표의 G1 선행 요구사항과 화면→API/DB/AI→인수 검증 대응 필요.
- 영향: 백엔드·AI·시안 01~05·시드·독립 기능/디자인 검수·매뉴얼.
- 호환성: 00·01·02는 수정하지 않는다. 00 우선순위의 Should 중 DoD 및 사용자 완료 기준에 반복되는 재피드백·상위 기준·Mock 기본 분석은 이번 인수 Must로 승격한다. 상위 요구 축소 없음.
- 검증 계획: ID/라우트/상태/역할 전수 대조, API 담당과 필드 교차 확인, 독립 검토.
- 결정: 단일 세션·현재 DB 권한, 운영자의 영업 본문 금지, unknown과 실패 분리, 컨셉별 동일 업무·독립 IA 유지.
- 전파표 원본 소유자: orchestration. 아래는 발신 사실만 기록하며 최종 상태는 조정자 원본에서 관리한다.

| 변경 | 대상 | 전달·확인 |
|---|---|---|
| PD-001 | orchestration | 작성 착수·범위 변경 수신 완료 |
| PD-001 | contract_data | 화면 데이터 요구 전달; 확정 후보 필드 대기 |
| PD-001 | contract_ai | 평가/상태 표시 요구 전달; 확정 후보 필드 대기 |
| PD-001 | 프론트·검수·매뉴얼 | 미배정, 조정자 인계 필요 |

## 2026-09-21 — PD-002 교차 계약 반영 전 기록

- 수신: DOC-EXEC-001(10 및 AGENTS), AI-001(결과·처리), CONTRACT-DATA-1.0(05/06), 독립 지적 PDR-01/02.
- 변경 계획: 04의 개념 필드를 API 정본명으로 교체(source_kind/error_message/result_applied/can_retry/n/r/reason/points), notification.body·미정의 jobs 날짜 필터 제거, 실제 endpoint 대응표 확정. 결과는 review.result와 서버 derived를 분리.
- 호환성: 업무 기능·권한·인수 기준 유지, 추정 필드 제거로 구현 계약 불일치 해결.
- 검증: 06 endpoint/DTO 대조와 문서 검색, AI 담당 재검토 요청.
- DOC-EXEC-001 영향: 포트5173~5177, dev/preview 단일 패키지, 매뉴얼에 비밀번호 대신 로컬 자격 위치, G1 코드 금지 반영.

## 2026-09-21 — 자기 검증·독립 회신

- 03 요구/수용 기준 24쌍 및 Should 2쌍, 04 역할별 22개 화면군과 공통4상태·실제 API 연결표, concept01 필수3문서 작성.
- 실제 문서 점검: 5개 문서의 상대링크 확인, Must/AT 고유 ID 각24개 확인. 최초 누락 링크1개(독립 데이터 검토 보고 예정 경로)는 보고서 생성으로 해소.
- sRGB 대비 계산: control-border #7A8994/white=3.60:1, ink/white=14.41:1, muted/white=6.05:1, white/primary=6.29:1. 실제 렌더 검수는 NOT_RUN.
- 독립 검토자 contract_ai가 PDR-01/02 실제 수정본 재확인 후 PASS 회신. 근거: [independent-product-review](../local-ai/independent-product-review.md).
- CONTRACT-DATA-1.0a 수신·반영: 상세 GET·이슈배정후보·region/date/is_active drilldown·최신job.
- CONTRACT-DATA-1.0b 수신·반영: Reference.state_version, target ID 멱등 충돌, 공통 입력 검증. 04 §2/7 업데이트. 업무·역할 범위 축소 없음.
- 코드/DB migration/Git 작업 없음. 화면 QA·실제 AI·브라우저 테스트 미실행; G1 문서 검토와 구분.

## 2026-09-21 — 최종 계약 대조

- CONTRACT-DATA-1.0b 최종 재확인: state_version 요청/응답/DB, 대상ID 포함 멱등 hash, 입력 검증 규칙, unresolved=true→open+in_progress 드릴다운 일치. 본 범위 개발 차단 없음.
- 최종 5개 산출물 상대링크 검사 누락0, S-* 화면ID22, 폐기 필드 검색0. 버전은 03=1.0-review(PD-001), 04=1.1-review(PD-002), concept01=1.1-review(DS01-002).
- root와 contract_data/contract_ai에 완료본·영향·재검토 증거 전달. 후속 배정자는 최신 문서와 독립검토 기록을 읽고 수신 확인한다.
- 상태 REVIEW: G1 확정은 root가 수행. 모든 실제 구현/브라우저/최종 디자인 인수는 후속 작업이다.
