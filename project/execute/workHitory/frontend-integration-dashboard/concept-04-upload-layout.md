# D04-V01 모바일 사진 제어행 보완

상태: REVIEW · 소스 동결

## 재현 근거와 원인
root의 `execute/designReview/concept-04/evidence/vp-mobile360-resubmit-preview.png`를 직접 열어 2열 사진 카드의 삭제 버튼이 카드 오른쪽으로 돌출한 것을 확인했다. 사진 제어행은 `flex-wrap:nowrap`, 모바일 버튼은 `min-width:40px`여서 좁은 카드에서 세 버튼을 한 줄에 배치했다.

## 변경
소유권이 부여된 `web-concepts-04/src/shared/style.css` 두 선언만 바꿨다. 사진 제어행에 `flex-wrap:wrap`을 적용하고 모바일 버튼 최소 너비를 44px로 올렸다. 공통 버튼 최소 높이 48px, 사진 2열 배치, 입력/삭제/순서 변경 동작은 유지한다. 작은 카드에서는 제어 버튼이 다음 줄로 흐를 수 있다.

## 검증 경계
이 변경은 CSS만 수정하므로 구조를 복제하는 새 테스트는 만들지 않는다. 기존 제출 흐름 관련 검사와 04 빌드를 수행한다. 현재 전체 검증 258 PASS를 재실행하거나 대체하지 않는다. 실제 수정 후 360px/390px 화면에서 카드 내부 배치와 터치 영역을 확인하는 작업은 root의 재촬영 및 contract_ai 독립 검수 대기이다.

변경 전후 원본 해시는 `upload-layout04-sha256.json`에 기록한다.

## 검증 결과
- `npm test --workspace @storeloop/concept-04 -- tests/flows.test.tsx -t '제출 네 단계를|현재 단계 입력'`: PASS 2 / 제외 4. 단계별 제출·미선택 경계·재시도 키 보존 검증을 통과했다. 픽셀 배치 검증으로 해석하지 않는다.
- `npm run build --workspace @storeloop/concept-04`: TypeScript 및 Vite 빌드 PASS. 산출물 `index-Dbe_430Q.css`, `index-Baxmq-8-.js`.
- CSS 정적 확인: upload-grid 기본/모바일 제어행 모두 wrap을 상속하고 버튼 최소 너비 44px, 최소 높이 48px를 유지한다. 사진 카드 min-width:0 및 설명 overflow-wrap도 유지한다.
- 소스 동결 후 root 재촬영 및 contract_ai 독립 검토로 인계. 수정 후 실제 viewport 결과는 아직 NOT_RUN.
