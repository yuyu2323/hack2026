# IB-C03 Reference 새 버전 충돌 복구
- 담당 concept04 / 상태 REVIEW
- 입력: input-boundary/independent-plan.md §4 IB-C03, docs04 충돌 복구·입력 보존.
- 소유: web-concepts-04 및 frontend-concept-04 전용 체크리스트/이력.
- 범위: 실제 References 컴포넌트의 사진·설명 새 버전 편집만. 공유 DB·Browser·runtime·모델 호출 금지.
- [x] 실제 컴포넌트에서 409→최신 revision 확인 후 초안/파일/사유 손실 RED
- [x] 최신 lineage id/state_version만 갱신하고 입력·파일 보존
- [x] 자동 저장 없이 사용자 명시 재저장 검증
- [x] 관련 전체 UI 테스트·TypeScript·build
- [ ] root 실제 UI 확인 인계

- 실제 References 회귀2 PASS, concept04 전체16 PASS, TypeScript+build PASS.
- root 실제 UI 재확인: 별도 수행, 본 담당 NOT_RUN.
