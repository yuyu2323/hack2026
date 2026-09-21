# 시안 03 구현 체크리스트
- [x] 목표 파일·상위00→01→02·03/04/06/09 및 G1 확정 계약 수신 확인.
- [x] DS03-001 brief/design-spec/acceptance 작성 후 구현 시작.
- [x] 권한·사진검증·상태표현 RED→GREEN 테스트. 최초6 RED→GREEN 및 이슈 빈해결내용1 RED→GREEN, 총7 PASS. 후속복구7개추가, 최종14 PASS.
- [x] 점주 사진 contact sheet·제출·실제 결과 inspector·비교·문의·알림.
- [x] OFC/지역/본사 범위 관제·매장·기준·Reference·이슈·분석.
- [x] 운영자 상태·계정/연결·기준 정보·작업/attempt·재처리·감사·공지.
- [x] URL 필터·페이지 보존, 직접 URL/새로고침·오류·빈 상태·반응형 소스 구현. 실제 브라우저 검증은 NOT_RUN.
- [x] TypeScript 검사/Vite production build 및 node/tsx 정책8개+Testing Library 상호작용6개, 총14 PASS.
- [ ] 실제 API 화면·React interaction·실제 AI 확인: NOT_RUN, root 독립검수 배정.
- [x] REVIEW 상태로 root에 소스동결 인계. 최종 기능/디자인 QA 승인과는 구분.

- [x] DS03-FIX-001: CSRF403명시복구,Reference미리보기,409초안보존+최신version,본문/대상변경멱등키 네건수정·회귀검사 후 REVIEW 재인계.

## MEDIA-CLARIFY-1 / NOTIFY-CLARIFY-1 임시 통합 보완

- root 임시 소유권 이관: product_design, 상태 REVIEW 동결.
- [x] context 순서/reference_id에 Photo metadata 대응, 실제 생성 이미지 배지
- [x] metadata 누락 fallback·출처 비추정·점주 GET /references 없음
- [x] 운영자 알림 메뉴/라우트 검토·필요 정책 회귀
- [x] 기존 테스트·build 후 REVIEW 동결
- 기록: execute/workHitory/frontend-integration-metadata/media-clarify-1.md

최종 실제 화면의 독립 디자인 재검수는 contract_ai/root 인계 항목이다.
