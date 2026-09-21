# design-v1: 시안 01 관제 중심 디자인

- 담당: product_design
- 상태: RUNNING
- 체크리스트: [design-v1](../../checkList/design-concept-01/design-v1.md)

## 2026-09-21 — DS01-001 작성 전 기록

- 변경 전: concept-01 상세 명세 없음.
- 변경 후 계획: brief.md(정보 구조), design-spec.md(구체 배치·토큰·상태), acceptance.md(검수 ID).
- 이유: 02 §8.4에 따라 구현과 독립 검수의 기준 필요.
- 영향: frontend-concept-01, integration-concept-01, design-review-concept-01, manual-concept-01.
- 근거: 관제 중심은 표·필터·지표에서 원본으로 이어지는 탐색을 첫 화면에 둔다. 점주 모바일에서는 빠른 제출과 이력 확인을 유지하며 플랫폼에는 기술 메타데이터만 표시한다.
- 검증: 공통 기능 누락·권한 혼합·단순 색상 테마 여부를 문서 단계에서 확인하고, 실제 시각 검수는 G4 독립 담당자가 수행한다.
- Git/상위문서/기존 사용자 산출물 변경 없음.

## 2026-09-21 — DS01-002 변경 전 기록

- 독립 검토 PDR-02 수신: panel border를 control border로 쓰면 흰 배경 3:1 대비 부족.
- 변경 계획: color.control-border #7A8994 별도 토큰, input/select/secondary button 경계에 적용. panel/table 구분선은 기존 토큰 유지.
- 영향: frontend-concept-01, 디자인 검수 D01-16, manual 화면.
- 검증 계획: sRGB 상대명도 계산과 독립 디자인 검수의 실제 computed style 대조.

## 2026-09-21 — 명세 인계·독립 검토 결과

- 작성 파일: brief/design-spec/acceptance (1.1-review, DS01-002).
- 기능: 5개 역할 공통 S-* 전체, 표·KPI·필터 중심 IA, 한 페이지 제출/2열 결과/상태·attempt 관리, 토큰·문구·mobile/desktop·키보드·4상태·D01-01~20 정의.
- control-border 실제 계산3.60:1, 텍스트 주요 대비4.5:1 이상 확인. 렌더 QA는 후속 독립 검수 필요.
- contract_ai 독립 문서 검토 PASS: [결과](../local-ai/independent-product-review.md). 실제 UI 디자인 인수 PASS와 다르다.
- 공통04 CONTRACT-DATA-1.0b의 Reference state_version 적용을 읽도록 frontend01에 인계한다. 디자인 수정 경로/DB/API 소유권 유지.
- 상태: REVIEW. 이후 frontend01/기능QA/디자인QA/매뉴얼 담당 배정시 버전 수신 확인 필요; 조정자 전파표가 원본이다.
