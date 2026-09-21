# D03-V02 새 기준 버전 이력 체크리스트

root 한정 배정:03 GuidelineEditor 및 신규 회귀. 독립 검수자 contract_ai의 실제 vp-desktop1440-guideline-v2.png 재현과 동일 증상.

- [x] 소스 확인: 새 버전 POST 성공은 상세 onSaved만 호출, 별도 versions 자원은 갱신하지 않음.
- [x] 실제 React 컴포넌트에서 v1→v2 저장 후 이력도 즉시 표시하는 회귀 RED.
- [x] 새 버전 저장 성공 후 상세와 이력 둘 다 refresh, 기존 payload/권한/입력/충돌복구 보존.
- [x] 신규·기존 테스트/build 및 REVIEW 동결 인계.
- [ ] root 실제 화면 재촬영·contract_ai 독립 시각 확인.
