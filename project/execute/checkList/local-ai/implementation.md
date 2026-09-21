# 로컬 AI 서버·공유 평가 계약 구현

- 담당: contract_ai / local-ai
- 상태: REVIEW
- 선행: G1 ACCEPTED, execute/workHitory/docs/contract-register.md의 확정 결정 확인
- 소유: ai-service/*, packages/review_contract/*, local-ai 체크리스트·이력, docs07/08/09
- 목표: 엄격 계약 공유, 실제 multipart 이미지 검증·Codex 분석·오류/timeout/격리·비밀보호 구현 및 실제 이미지 조기 성공 증거
- 금지: 타 담당 파일 수정/Git, 실제AI 실패 Mock 대체, 인증원문·전체stderr·프롬프트 기록

- [x] 의존성 요구·함수 인터페이스 root 전달
- [x] 공유 JSON/Pydantic/참조/점수 RED→GREEN
- [x] 이미지·HTTP인증·busy·정리·timeout RED→GREEN
- [x] Codex argv/stdin·환경 격리·실패 분류 구현
- [x] 실제 생성 제출/Reference 두 장으로 모델 분석 조기검증
- [x] 실제 지연·schema/참조/hash·모델 증거 기록
- [x] 업무 worker 통합·독립 검토 인계

AI 테스트 39 PASS. 실제 HTTP 조기 검증 PASS(36,089ms), 실제 worker·PostgreSQL 통합 PASS(25,805ms). 후속 독립 구현 검토를 위해 root에 REVIEW로 인계했다.
