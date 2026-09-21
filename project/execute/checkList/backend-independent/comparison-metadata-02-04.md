# 시안02/04 전후 비교 날짜·기준 버전 보완

- root 배정 소유: 두 시안 src/store-owner/Owner.tsx Comparison 및 필요한 상세 조회, 신규 tests/comparison-metadata.test.tsx.
- 제품/API/DB 계약 변경 없음. 현재/부모 제출의 저장 context.guidelines만 사용한다.
- [x] 날짜·전후 기준 버전 누락 의미 RED: 각2 FAIL/1 PASS
- [x] 기준 추가/제거·없는 부모·상세 조회 실패 처리 검증: 각 신규3 PASS
- [x] 기존 사진/rate/기준 변경 경고/반응형 구조 유지
- [x] 두 시안 전체 테스트·build GREEN: 02 19 PASS,04 14 PASS, 두 build PASS
- [x] contract_ai 독립 검토/root 실제 브라우저 인계·소스 freeze
- [x] 독립 소스 검토 PASS 수신 (contract_ai 소유)
- [ ] 실제 브라우저 재촬영/인수 (root 소유)

본 작업은 구현 자기검증이다. 다른 담당의 독립 디자인 검수·실제 브라우저 인수와 구분한다.
