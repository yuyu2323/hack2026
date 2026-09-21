# DB·코어·계정·기준 정보·운영 구현
- 상태: REVIEW
- 입력: G1 ACCEPTED, CONTRACT-DATA-1.0b
- 소유: core, 모든 models, migrations, accounts/stores/operations API, requirements.in, tests/conftest 및 담당 테스트
- 이력: ../../workHitory/db-schema/implementation-v1.md

- [x] G1 확정·최종 독립 검토 확인
- [x] 의존성 명세 전달
- [x] 모델·4개 migration TDD/upgrade/제약
- [x] 공통 fixture 제공·root 모델 인계
- [x] DB 세션·CSRF·현재권한 TDD
- [x] 계정/기준정보/매핑/운영 상태·공지·감사 TDD
- [x] 재처리 API와 contract_ai.retry_job 실제통합 (HTTP202·replay·과거시도보존 PASS)
- [x] 관련 회귀·PostgreSQL 검증·1차 인계
- [ ] 독립 검토·남은 통합 후 최종 인계
