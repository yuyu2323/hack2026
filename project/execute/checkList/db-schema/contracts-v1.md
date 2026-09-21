# contracts-v1: DB·API 공통 계약
- 모듈 / 담당: db-schema / contract_data
- 상태: REVIEW
- 목표: 00·01·02 요구를 구현 가능한 DB/API 계약으로 연결하고 독립 검토에 인계한다.
- 입력: docs/00-vision.md → 01-architecture.md → 02-development-orchestration.md, 사용자 goal-objective (2026-09-21)
- 선행: G0 조사, 기존 구현/후속 계약 없음 확인
- 수정 범위: docs/05-database.md, docs/06-api.md, execute/checkList/db-schema, execute/workHitory/db-schema
- 공유 파일 소유자: 모델·migration 단일 작성자 contract_data (G1 확정 전 구현 금지)
- 이력: ../../workHitory/db-schema/contracts-v1.md

## 검증 기준
- [x] 상위 문서 순차 읽기, 기존 구현·문서 확인
- [x] 체크리스트 및 변경 전 이력 작성
- [x] 모든 역할의 현재 DB 기반 권한·이미지 접근·비활성화 정책 정의
- [x] 엔티티 필드·FK·고유·체크·인덱스·보존·migration 순서 정의
- [x] 화면에서 필요한 요청·응답·오류·목록·멱등 계약 정의
- [x] AI 입력/출력·작업/시도 및 재처리 계약 담당자와 대조
- [x] 계약 연결과 문서 링크 자체 검증
- [ ] 영향 담당자/root에 전달하고 수신/반영 확인
- [ ] 독립 검토 요청 및 발견 차단 문제 수정
