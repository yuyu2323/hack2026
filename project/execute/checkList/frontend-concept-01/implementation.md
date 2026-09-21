# implementation: 관제 데스크 전체 프론트

- 담당: product_design / frontend-concept-01
- 상태: REVIEW
- 선행: G1 ACCEPTED, 03 PD-001, 04 PD-002, DB/API CONTRACT-DATA-1.0c, DS01-002 확정.
- 소유: web-concepts-01/* 및 본 체크리스트/이력·자신의 design-concept-01. root의 초기 frontend 경로 오배정은 즉시 정정되어 그 경로에 파일을 만들지 않았다.
- 공통 클라이언트: @storeloop/api-client api/ApiError/idempotencyKey/queryString/AccountMe/Page. 루트 workspace 설치는 root.
- 목표: 단일React19/Vite7/TS5패키지의 모든역할·Must/Should·실제공통API·관제IA·4상태·모바일/키보드.
- 이력: [implementation](../../workHitory/frontend-concept-01/implementation.md)

- [x] 확정 문서·실제클라이언트·역할별 화면·정정경로 확인
- [x] RED: 역할라우팅·파일검증·poll종료·null점수·필터보존 테스트 및 UI 행동
- [x] GREEN: app/shared/store-owner/ofc-admin/platform-admin 소스 분리, 실제API 연결
- [x] 로그인·CSRF·현재권한·캐시폐기·직접URL/새로고침
- [x] 점주 업로드/처리/근거/재제출/비교/이력/문의/알림
- [x] 영업 관제·담당등록·기준버전·Reference·이슈조치·Mock분석/집계
- [x] 운영 계정·연결·기준정보·상태·실패재처리·감사·공지
- [x] 필터URL·페이지·빈/로딩/오류·Unknown·Mock/생성이미지
- [x] 정책6·UI6 테스트 및 단일빌드 PASS
- [ ] 실제API 브라우저/실제AI/반응형 자체 확인 — Browser 런타임 없음, root 독립 인계
- [ ] 독립기능/디자인QA 및 매뉴얼 담당 인계 (구현자 자체PASS로 대체금지)

실제AI는 root가 보고한 외부승인 대기와 구분하며 본프론트에서 Mock대체 성공을 주장하지 않는다. 사용자자격파일을 로그/캡처/소스에 출력하지 않는다.

WEB01-004 root 정적결함(운영자 영업알림 노출) 수정과03/04/C01설계변경 완료. REVIEW는 구현인계 상태이며 미실행 브라우저/독립디자인/실제AI 인수를 완료로 선언하지 않는다.

## MEDIA-CLARIFY-1 임시 통합 보완

- 담당 product_design, 상태 REVIEW 동결, 기존 독립 검수와 별도.
- [x] 실제 reference_photos를 context 순서/reference_id에 대응, 보호URL/source_kind 사용
- [x] metadata 누락 fallback·출처 비추정·추가 Reference API 없음 회귀
- [x] 기존 테스트·build 후 REVIEW 동결
- 기록: execute/workHitory/frontend-integration-metadata/media-clarify-1.md

최종 실제 화면의 독립 디자인 재검수는 contract_ai/root 인계 항목이다.

## F01-FILTER · 관리 범위 조건 보존
- root 실제 브라우저: 매장 선택 뒤 카테고리를 고르면 이전 매장이 전체로 돌아가고 URL에서 사라짐.
- root가 01 필터 관련 경로만 재개함. 공통 API 클라이언트·다른 앱 수정 금지.
- [x] 실제 Router/필터 UI의 매장+카테고리+날짜 조합 보존 의미 회귀 RED
- [x] 원인 최소 수정 후 해당 UI 회귀/전체01 UI/빌드 확인
- [ ] root 브라우저 재검증 인계, 매뉴얼 이미지 작업 재개

## F01-ANALYTICS · 업무 대상 표시명
- root 실제 상관표/기본 집계의 UUID 표시 문제. Analytics 표시 관련 경로만 추가 소유.
- [x] 허용된 매장/카테고리/지역 조회 범위의 이름으로 표시, 원본 ID·API/URL 유지
- [x] 누락 이름 안전 fallback 및 실제 보고서 UI 회귀 RED→GREEN
- [x] 전체01 UI14/빌드 PASS 후 root 최종 브라우저 검수 인계
