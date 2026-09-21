# Concept02 오늘 할 일 구현
- 담당: concept02 / 상태 REVIEW
- 계약: docs00→01→02, PD-001/PD-002, CONTRACT-DATA-1.0b, QA-001, G1 ACCEPTED 확인
- 소유: web-concepts-02, execute/design/concept-02, 본 체크리스트·이력
- 공유 클라이언트·루트 의존성·백엔드는 root 소유
- 이력: ../../../execute/workHitory/frontend-concept-02/implementation.md

## 실행
- [x] 요구사항·역할·모듈·API 계약 확인
- [x] 시안별 사전 디자인 명세 및 검수 기준 작성
- [x] 의미 있는 React 동작 RED → GREEN
- [x] 모든 역할 canonical 화면·실제 API·권한 처리
- [x] 사진 제출·상태·결과·재제출·비교·문의
- [x] 영업 업무 보드·기준·Reference·분석
- [x] 운영 복구 업무·계정·연결·기준정보·감사·공지
- [ ] 모바일·키보드·빈값·오류·필터 보존
- [x] build/test 검증
- [x] 독립 기능·디자인 QA 인계 (자체 완료와 구분)

## 독립 검수 보완 C02-QA-001
- [x] 운영자 영업 알림 직접 경로 및 API 호출 차단
- [x] 기술 상태의 사용 불가 문구
- [x] 상관표 매장/매대 이름 및 누락 안내
- [x] reference_photos 출처 및 원본 순서 대응, 권한금지 유지
- [x] 회귀 테스트·빌드·root 재인계

## C02-HMR-001
- [x] 5개 앱 진입점 읽기 전용 조사·원인 전달
- [x] 동일 컨테이너 entry 재평가 회귀 RED→GREEN
- [x] 02 루트 재사용 최소 수정·빌드·기존 테스트
- [x] 변경 시점·최초 전체 새로고침 안내 및 REVIEW 인계

## D02-P2 Reference 번호 표시
- [x] 독립 디자인 증거 수신·검수자 ACK
- [x] 원본 Photo.position이 모두1인 fixture로 화면 번호 회귀 RED→GREEN
- [x] snapshot 순서/position 표시 및 Photo URL·출처·원본 불변
- [x] 02 테스트·빌드·소스 동결·재검수 인계

## C02-RECOVERY-001 · 입력 보존 복구
- [x] 실제 App/Reference 컴포넌트 CSRF·409 결함 재현 RED
- [x] CSRF 토큰 오류에서 초안·사진·멱등키 유지, 권한 거절 분리
- [x] 동일 Reference lineage 최신 id/state_version 읽기, 초안·사진 유지
- [x] 테스트·타입·빌드 및 독립 복구 확인 인계
