# D04-V01 모바일 미리보기 제어행

상태: REVIEW · 소스 동결 · 담당: product_design · 범위: web-concepts-04/src/shared/style.css만

- [x] root 배정과 실제 360px 재제출 미리보기 캡처를 직접 확인했다.
- [x] `.upload-grid .actions`의 nowrap과 모바일 최소 너비 40px를 확인했다.
- [x] 사진 제어행 줄바꿈과 최소 터치 너비 44px를 적용한다. 기존 높이 48px는 유지한다.
- [x] 04 제출 흐름 관련 검사 및 04 빌드를 수행한다. 기존 전체 258개 검증은 반복하지 않는다.
- [x] 변경 전후 해시를 기록하고 root 재촬영 및 contract_ai 독립 검토로 인계한다.

CSS만 바꾸므로 구현을 그대로 옮긴 단위 테스트는 추가하지 않는다. 실제 카드 경계/터치 영역의 최종 판단은 root의 수정 후 viewport 캡처와 독립 시각 검수로 확인한다.
