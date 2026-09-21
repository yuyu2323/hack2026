# contracts-v1: AI·데이터·검증 공통 계약

- 모듈 / 담당 에이전트: local-ai / contract_ai
- 상태: REVIEW
- 목표 / 완료 조건: 00·01·02에 맞는 실행 가능한 AI 입출력·상태 전이, 재현 시드·이미지 계획, 5개 시안 검증 계약을 작성하고 DB/API/화면 소유자 및 독립 검토자에게 인계한다.
- 입력 문서: docs/00-vision.md → docs/01-architecture.md → docs/02-development-orchestration.md (2026-09-21)
- 선행 작업: G1 공통 문서 작성. G1 확정 전 구현·마이그레이션·모델 요청 금지.
- 수정 가능 경로: docs/07-ai-processing.md, docs/08-data.md, docs/09-validation.md, execute/checkList/local-ai, execute/workHitory/local-ai
- 작업 이력: ../../workHitory/local-ai/contracts-v1.md
- 공유 파일 소유자: root(조정), contract_data(DB/API), product_design(요구/화면)

## 실행 항목

- [x] 상위 문서 순서대로 읽기 및 목표 파일 확인
- [x] 설치된 Codex CLI 버전·옵션·인증 상태 비밀 없는 읽기 조사
- [x] 비코드 수용 기준: 모든 AI 필드·검증·오류·처리 경쟁 상황 명시
- [x] AI 계약 작성 및 DB/API/화면 이름 협의
- [x] 시드/계정/실제 생성 이미지 manifest/Mock 구분 계약 작성
- [x] 단위/PostgreSQL/실제 AI/5개 시안 인수 검증 계획 작성
- [x] 문서 간 필드·상태 대조 및 변경 전파·수신 확인
- [x] 비밀 값 미포함 및 로컬 링크 검사
- [x] 독립 검토 인계: contract_data independent-ai-review.md PASS, G1 확정은 root 담당
