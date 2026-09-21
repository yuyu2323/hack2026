# 독립 검토: AI·데이터·검증 계약
- 검토자: contract_data (07/08/09 미작성자)
- 기준: 00→01→02 및 05/06 CONTRACT-DATA-1.0
- 상태: REVIEW_COMPLETE
- 대상: docs/07-ai-processing.md, docs/08-data.md, docs/09-validation.md

## 2026-09-21 1차 (07 AI-001)
| ID | 심각도 | 발견 | 조치/결과 |
|---|---|---|---|
| AIR-01 | 차단 | §5 ReviewResult.model_result, §6 attempt_no가 05/06 result/attempt_number와 불일치 | contract_ai에 정정 요청 전달 |
| AIR-02 | 차단 | 입력 rule_key 최대100 vs DB varchar80 | 80으로 통일 요청 |
| AIR-03 | 차단 | Attempt.deadline_at이 CLI120/HTTP130 중 무엇인지 불명확 | 합의한 worker 시작+130 수용상한 명시 요청 |
| AIR-04 | 보완 | 부모/자식 다른 기준 버전 비교 제외가06에 없음 | 06에 criterion_changed=true 및 unavailable 반영, product_design/root에 전파 |
| AIR-05 | 보완 | 늦은 응답 discarded 이벤트 영속 저장 엔티티 없음 | 본문 없는 안전한 서비스 로그로 명시 제안 |

07의 이미지 입력 순서·hash, Reference 구분, schema/참조 검증, unknown/실패 분리, 독립worker/DB잠금·수동재처리·성공결과 보존, 운영자 본문 차단, 실제 AI 시간측정 범위는 상위문서와 일치.

08/09는 1차 읽기 시 아직 파일이 없어 검토 NOT_RUN. 작성 완료 후 재검토한다. 이 상태는 G1 통과가 아니다.

## 2026-09-21 2차 재검토
- 07 작성자가 AIR-01~05 및 재처리 시작/종료/오류 초기화 보완을 반영한 파일을 다시 읽음. result/attempt_number/rule_key80/deadline130·CLI120·lease140/본문 없는 discarded 로그 정합 PASS.
- 08 DATA-001 전체 검토: 고정 기준시각/안정 UUID, 누락만 적재·기존 사용자 수정 보존, runtime 비밀번호,4개 카테고리/6매장/역할·범위·비활성/미배정,4단계 기준·immutable 버전,Reference와 제출 이미지 분리,10개 실생성파일·외부 독립 Golden 검수,Mock 표시,상관 경계 fixture가00/01/02 및05/06에 대응. 발견 차단 문제 없음.
- 09 QA-001 전체 검토: AT-01..24/S01/S02가03 요구와 연결되고 PostgreSQL 다중 점유/멱등/기한/재시작/늦은결과·rollback·scope 감소,실제AI 조기 검증/시안별 제출·재제출,기능/디자인 검토 분리,격리DB,비밀캡처 금지,30초 측정·실패 정직 보고가 상위 기준에 대응. 발견 차단 문제 없음.
- 검증 제한: 문서 독립 검토이며 실제 기능/AI/DB/브라우저 테스트는 NOT_RUN. 구현 완료 판정으로 사용하지 않는다.
- 최종 독립 문서 검토 판정: PASS (현재 검토 범위07/08/09의 개발 차단 문제 해소).
