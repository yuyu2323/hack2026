# D03-V02 보완 기록

root 실제 CATEGORY 기준v1→v2 저장 후 현재 기준v2/저장 성공/새 본문은 갱신됐으나 버전 이력은v1만 남았다. contract_ai도 같은 캡처로 독립 확인했다. GuidelineEditor는 detail을 부모 onSaved로 다시 읽지만 versions는 별도 useResource이고 path/revision이 바뀌지 않는다. 새 버전 성공 콜백에서 versions.refresh도 실행하는 최소 수정이 필요하다.

회귀는 서버를 흉내 내는 합성 DTO/API 응답으로 실제 Guidelines 컴포넌트를 렌더한다. v1 이력을 읽은 뒤 새본문·사유를 입력해 저장하고, 상세v2와 이력v2/v1이 둘 다 나타나는지 및 POST 충돌용version을 확인한다. 실제 브라우저/DB·서비스·다른03제품파일·패키지·매뉴얼은 수정하지 않는다.


## RED → GREEN 및 REVIEW 동결

- 신규 tests/guideline-history.test.ts: 상세 현재 기준v2 갱신을 먼저 확인하고 이력 article2개를 기대했으나1개여서 RED. root의 실제 증상과 일치했다.
- GuidelineEditor 새 버전 POST 성공 콜백만 onSaved(); if(current) versions.refresh()로 보완했다. 신규 생성은 기존 목록 갱신만 진행하고 현재 항목의 상세·이력은 각각 자원별 재조회한다. 저장 API·version본문·권한·활성 변경·충돌입력보존 동작은 변경하지 않았다.
- GREEN: 새/이전 버전 본문·사유 동시 표시, 상세GET/이력GET 각각2회(최초+저장후), POST충돌version4 유지. 전체25 PASS, TypeScript/Vite build PASS, index-BEPwAE2t.js.
- 수정 제품 범위는03 ofc-admin/pages.tsx의 GuidelineEditor submit 성공콜백 한 곳, 신규 회귀1파일. 다른 앱·공유·DB·서비스·브라우저·매뉴얼 변경 없음.
- root에 REVIEW 동결/새로고침 가능을 즉시 전달했다. 실제 화면 재촬영 및 contract_ai 독립 재판정 대기. 기존 guideline-v2 캡처는 결함이 보이므로 최종 매뉴얼 정상 예시로 쓰지 않는다.
