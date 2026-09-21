# D03-V01 / F03-VERSION 보완 기록

## 착수

root의 실제 vp-desktop1440-ofc-photo-dashboard.png 검수에서 첫 viewport 사진0장으로 DS03-001 acceptance① 불충족. Dashboard는 제목/필터/KPI/모든 매장 카드 뒤 contact sheet를 렌더하고 있었다. 필수 API·필터·KPI·매장 drilldown을 유지하며 사진을 앞에 놓고 제목 여백을 압축한다. 하단 지표·매장 현황으로 이동하는 링크를 제공한다.

기준 비활성화 이후 top-level version은 증가하나 기준 내용 버전은 증가하지 않으므로 현재 저장 버전 표시가 오해를 준다. docs06 Guideline 정본의 current_version을 표시하고 저장 payload의 version은 보존한다. latest_version 필드는 계약에 없다. 기존 충돌 복구 테스트도 표시 기대값을 내용 버전으로 갱신한다.

공유 API·DB·브라우저·서비스·다른 담당 파일은 수정하지 않는다. 회귀는 합성 DTO의 실제 React 렌더/동작으로 수행하며 화면 기하/실제 사진 가시성은 root 브라우저와 contract_ai의 독립 시각검수를 기다린다.


## 구현·검증 완료 · REVIEW 동결

- Dashboard: 제목의 위아래 여백을 줄이고 필터 바로 아래 최근 사진6장 contact sheet를 배치했다. KPI8개·표본/Mock 설명·미제출 해석·이슈/기술실패 링크·매장별 상태 및 drilldown은 아래 지표·매장 현황에 보존했다. 상단 지표·매장 현황 anchor와 하단 사진으로 돌아가기 anchor는44px 영역을 둔 native link다.
- CSS는 .photo-dashboard 하위만 추가했다. 기존 contact sheet의 desktop3열/mobile1열·이미지 비율과 공통 폼/다른 페이지는 변경하지 않았다.
- GuidelineEditor: top-level version을 현재 기준으로 잘못 표시하던 부분을 current_version으로 바꾸었다. POST 새 버전 및 PATCH 활성 상태 payload에는 기존 top-level version을 계속 전달한다.
- TDD: tests/dashboard-display.test.ts 2개는 구현 전 각각 사진이 KPI보다 뒤라는 실패, 현재 기준 v2 표시 없음으로 RED였다. 최초 root cwd 직접 node 실행은 tsconfig 경로 문제로 React 미정의였고 제품 결함 RED로 세지 않았다. 해당 workspace cwd로 재실행하여 의미있는 두 실패를 확인했다.
- GREEN: 새2개 + 기존 충돌복구6개 =8 PASS. 이후 workspace 전체23 PASS, TypeScript+Vite build PASS. recovery.test.ts는 기존 충돌 후 입력 유지/상태 version2 재전송 검사를 보존하며 표시 기대값만 현재 기준 v2로 맞췄다.
- 검사하는 내용: 사진이 KPI/매장 링크보다 선행, 지역/매장/category/날짜 입력 유지, 사진/관제 GET 필터 보존, 매장/미해결/기술실패 drilldown 쿼리 보존, 내용 v2/상태version4 분리와 활성화 payloadversion4, 기존 409 입력보존·최신 version 재시도.
- 빌드 산출: index-BTOOH4yA.css / index-BH4U8Nqg.js. 파일별 SHA-256은 source-sha256.json 참조.
- 이 작업의 코드 수정 범위: web-concepts-03/src/ofc-admin/pages.tsx의 Dashboard 및 GuidelineEditor 표시, src/app/style.css의 dashboard 한정 규칙. 테스트 신규 dashboard-display.test.ts 및 recovery.test.ts 기대 문구. shared/ui.tsx·store-owner/pages.tsx·패키지·공유클라이언트·DB·브라우저·서비스·Git은 변경하지 않았다.
- 남음: root가 1440×900 첫 viewport에 실제 사진이 충분히 보이는지 및390px/200%에서 배치·anchor·drilldown을 확인하고 contract_ai가 독립 디자인 판정한다. jsdom 순서 검사만으로 최종 시각 PASS를 선언하지 않는다. 소스 REVIEW 동결 인계.


## 독립 시각 재검수 수신

contract_ai가 root의 vp-desktop1440-photo-dashboard-fixed.png를 직접 검수해 본사 첫 viewport 사진3열이 주요 데이터로 보이고 KPI/매장 상태는 하단임을 확인, DS03-01만 PASS로 갱신했다. 이 확인을 다른 실제 항목의 최종 PASS로 확장하지 않는다.
