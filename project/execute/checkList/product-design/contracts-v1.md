# contracts-v1: 공통 요구사항·화면 계약

- 모듈 / 담당: product-design / product_design
- 상태: REVIEW
- 목표: 00·01·02 및 사용자 목표를 수용 기준과 동일 기능의 5개 시안 화면 계약으로 연결한다.
- 입력: docs/00-vision.md → 01-architecture.md → 02-development-orchestration.md 순서로 전체 확인, goal-objective.md 확인 (2026-09-21).
- 선행: G1 문서 준비. 구현 소스·마이그레이션은 작성하지 않는다.
- 수정 경로: docs/03-requirements.md, docs/04-screens.md, 본 체크리스트·product-design 작업 이력. concept-01은 별도 체크리스트.
- 이력: [contracts-v1](../../workHitory/product-design/contracts-v1.md)

## 실행 항목

- [x] 강제 문서·목표·실제 프로젝트 상태 확인
- [x] 비코드 검증 기준 정의: 요구사항 ID→수용 기준→테스트 ID, 모든 화면의 역할/API/상태 매핑
- [x] Must·Should·제외 및 역할별 업무 흐름 작성
- [x] 공통 라우트·필드·정상/빈/로딩/오류 및 접근성 작성
- [x] DB/API·AI 담당과 필드·권한·처리 상태 대조
- [x] 5개 시안 차별화·디자인 검수·매뉴얼 인계 계약 작성
- [x] 자기 검증 및 미확정 항목 표기
- [x] 변경 PD-001/002를 담당자·조정자에게 전파; 미배정 후속 담당은 root 배정시 수신 확인
- [x] 독립 검토 PASS 수신 (작성자는 확정/DONE 판정하지 않음)

## 비밀·Git

- 실제 비밀번호·인증 값·민감 데이터·사용자 자료를 문서에 복사하지 않는다.
- Git 작업은 조정자 소유이며 수행하지 않는다.
