# 시안 04 모바일 현장 구현
- 담당: concept04 / 상태: REVIEW
- 계약: docs00→01→02,03 PD-001,04 PD-002,06 CONTRACT-DATA-1.0c,09 QA-001, G1 ACCEPTED 확인.
- 소유: web-concepts-04, execute/design/concept-04, 본 체크리스트와 작업 이력.
- 공통 API·서버·모델·다른 시안은 수정하지 않는다.
- [x] 계약과 변경 전파 등록부 확인
- [x] 독립 brief/design-spec/acceptance 작성
- [x] 의미 있는 실패 테스트→구현→통과 (구현/자체검증, 실제브라우저 인수별도)
- [x] 점주 제출·상태·평가·후속·비교·이슈·알림 (구현/자체검증, 실제브라우저 인수별도)
- [x] 영업 관제·담당 등록·기준/Reference 버전·조치·분석 (구현/자체검증, 실제브라우저 인수별도)
- [x] 운영 계정/매핑·기준정보·공지·상태/재처리·감사 (구현/자체검증, 실제브라우저 인수별도)
- [x] 권한·직접 경로·URL 필터/페이지·오류·모바일 (구현/자체검증, 실제브라우저 인수별도)
- [x] 자체 테스트 및 단일 빌드 (구현/자체검증, 실제브라우저 인수별도)
- [ ] 독립 기능/디자인/실제 AI 검토 인계 (자체검증과 구분)

- 독립 브라우저·디자인·실제AI 인수: NOT_RUN(해당담당 인계).
- 후속 MEDIA-CLARIFY-1 metadata연결: docs06 확정대기, root가소유자배정.

## MEDIA-CLARIFY-1 임시 통합 보완

- root 임시 소유권 이관: product_design, 상태 REVIEW 동결.
- [x] context 순서/reference_id에 Photo metadata 대응, 실제 생성 이미지 배지
- [x] metadata 누락 fallback·출처 비추정·점주 GET /references 없음
- [x] 기존 테스트·build 후 REVIEW 동결
- 기록: execute/workHitory/frontend-integration-metadata/media-clarify-1.md

최종 실제 화면의 독립 디자인 재검수는 contract_ai/root 인계 항목이다.
