# D04-V02 상세 사진의 질문 가림 보완

상태: REVIEW · 소스 동결

## 직접 확인
`execute/designReview/concept-04/evidence/vp-desktop1440-ofc-evidence.png`를 직접 열었다. 스크롤된 상세의 사진·캡션·사진 선택 버튼이 아래 질문 카드의 본문과 겹쳤다. `SubmissionDetail`에서 사진 블록만 sticky이고 다음 질문 카드는 일반 흐름이다. `design-spec.md`는 데스크톱 상세 2열을 요구하며 사진 sticky를 필수로 정하지 않는다.

## 최소 변경
소유권이 지정된 `web-concepts-04/src/shared/style.css`에서 min-width:1200px의 `.photos-main{position:sticky;top:24px}`만 제거했다. 사진, 캡션, 사진 탭, 현장 질문이 동일한 일반 문서 흐름을 따라 배치된다. 두 열 구조와 사진 선택·근거 이동·원본 열기 기능은 변경하지 않았다. 앞선 D04-V01의 제어행 wrap/모바일 버튼 44px 보완도 유지했다.

## 검증
새 테스트는 추가하지 않으며, 상세 관련 기존 검사와 빌드로 제품 기능/산출물의 손상을 확인한다. 픽셀 겹침 해소와 스크롤 동작은 root의 수정 후 실제 1440px 캡처 및 contract_ai 독립 검수 대기다. 전체 258개 검증을 반복하지 않는다.

## 결과와 인계
- `npm test --workspace @storeloop/concept-04 -- tests/flows.test.tsx -t 'MEDIA-CLARIFY-1'`: 상세 표시 관련 2 PASS, 제외 4. 픽셀 배치 검증을 대신하지 않는다.
- `npm run build --workspace @storeloop/concept-04`: TypeScript/Vite PASS.
- `layout04-final-sha256.json`에 D04-V01/V02를 모두 포함한 최종 style.css 및 새 CSS/JS 산출물 해시 기록.
- D04-V01은 contract_ai 소스 독립 검토 PASS를 수신했다. 두 결함 모두 실제 수정 후 캡처 시각 검수는 대기한다.
- root 재촬영 및 contract_ai 독립 검토로 REVIEW 동결 인계한다.
