# 시안03 표시 결함 후속 수정
- root 명시 배정: shared/ui.tsx FileImage/ContactSheet, store-owner/pages.tsx FilePreview 표시 및 신규 tests만.
- 이전 seed 읽기 검토보다 우선한다. 편집 시작을 root에게 전달했다.
- 새 역할은 제한 UI 구현이며 독립 PASS 판정이 아니다. root 실제 브라우저 인수와 구분한다.
- 계획: 빈 src 초기 렌더/실패 상태 오표시를 의미 테스트 RED로 확인 → 해당표시만 수정 → 신규 및 기존17개 테스트·build → freeze 인계.
- 브라우저·DB·런타임·다른 시안·Git은 변경하지 않는다.

## 완료 확인
- [x] FileImage 초기 렌더와 FilePreview 파일 선택에서 빈 src 경고를 재현했다.
- [x] ContactSheet 기술 실패가 대기 문구를 출력하는 의미 회귀를 재현했다.
- [x] blob URL 준비 전 img 렌더를 생략하고 실패 상태의 운영자 재처리 안내를 추가했다.
- [x] 기존 URL 생성·해제와 queued/running/성공 결과 표시를 보존했다.
- [x] 신규4개 포함 전체21개 테스트 및 TypeScript/Vite build PASS.
- [x] root에게 지정 소스 변경 동결을 전달했다. 실제 브라우저 인수는 root가 수행한다.
