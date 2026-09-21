# D03-V01 / F03-VERSION 체크리스트

담당 product_design. root가 03 ofc-admin/pages.tsx Dashboard·GuidelineEditor와 dashboard 한정 CSS 소유권을 임시 이관했다. 다른 담당의 shared/ui.tsx·store-owner/pages.tsx 수정과 분리한다.

- [x] 실제 코드·DS03-001 acceptance·docs06 버전 계약 확인.
- [x] 사진 우선 순서·필터/drilldown 보존과 상태/내용 버전 분리 회귀 RED.
- [x] 필터 다음 최근 사진, 보조 KPI/매장 현황 유지, 반응형 dashboard CSS 구현.
- [x] 내용 버전 표시만 변경하고 저장 payload 충돌 버전 보존.
- [x] 해당 회귀 및 기존 테스트·build 검증.
- [x] root/contract_ai에 REVIEW 동결 인계.
- [ ] root 실제 1440×900 사진 첫 화면·390px/200% 재검수, contract_ai 독립 디자인 판정.

상태 REVIEW 동결. 합성 DTO 테스트23 PASS, build PASS. 실제 geometry/첫 viewport 판정은 별도 대기.
