# C02-HMR-001 · 앱 진입점 HMR 루트 중복 조사
- 상태 REVIEW / 담당 concept02 / 2026-09-21
- 선행 체크리스트: execute/checkList/frontend-concept-02/implementation.md
- 범위: 5개 진입점 읽기 전용 조사, 시안02 entry·회귀만 수정. 다른 시안·공유 DB·브라우저 조작 없음.
- root가 독립 브라우저 콘솔에서 편집 중 duplicate createRoot 및 removeChild NotFoundError를 전달했고 편집 동결 후 화면 정상임을 확인했다.

## 원인과 영향
- 02 `src/app/main.tsx`는 App React 컴포넌트 export와 모듈 본문 `createRoot(container).render`를 함께 포함한다. HMR 재평가 시 같은 DOM 컨테이너에 새 React root를 만든다. 기존 root는 해제되거나 재사용되지 않는다.
- 설치된 React `react-dom-client.development.js:26741`의 동일 컨테이너 중복 createRoot 경고는 기존 root.render 사용을 요구한다. Vite React 플러그인의 component refresh 경계는 모듈 부수효과의 중복 root 생성을 막지 않는다.
- DOM 자식을 서로 다른 root가 관리하게 되면 removeChild 경쟁 가능성이 생긴다. 콘솔의 NotFoundError 전체를 한 원인으로 단정하지 않으며 최종 브라우저 재검수는 root가 수행한다.
- 03/04 `src/app/main.tsx`에도 컴포넌트와 무조건 createRoot가 함께 있다. 01/05 `src/main.tsx`는 App 파일 분리로 일반 컴포넌트 갱신의 영향이 작지만 entry 자체 재평가에는 무조건 createRoot 위험이 남는다. 타시안 파일은 변경하지 않았다.

## 수정·검증 계획
- 02 DOM 컨테이너에 시안 전용 Symbol 키로 React root를 보존하고 entry 재평가에서는 같은 root.render를 호출한다. 새 문서의 새 DOM에는 새 root를 만들며 계정·서버 데이터 저장을 추가하지 않는다.
- 회귀는 같은 DOM에서 entry를 두 번 평가해 createRoot 1회/render 2회를 확인한다. DOM이 교체된 경우 새 root 생성도 확인한다.
- 최초 패치 적용 때 기존 미수정 entry가 만든 root에는 Symbol이 없으므로 최종 검수 시작 전에 브라우저 전체 새로고침 1회가 필요함을 root에 전달했다.

## 소유권 확장·수정
- root가 01/03/04/05도 구현 동결 상태임을 확인하고 5개 entry의 createRoot/HMR 보존 부분만 단독 수정 소유권을 확장했다. 메시지 수신 후 모든 진입점에 같은 최소 수정안을 적용했다.
- 각 시안별 `Symbol.for("storeloop.concept-0N.react-root")`를 실제 DOM 컨테이너에 저장한다. JSX 트리, App, provider, 라우팅·화면 구성은 변경하지 않았다. import Root 타입과 mount 블록만 변경했다.
- 회귀 RED: 같은 DOM에 entry 두 번 평가 시 createRoot 2회로 기대 1회 assertion 실패. 새 DOM 별도 root 테스트는 PASS.
- GREEN: entry 재평가 시 createRoot 1회/render 2회, 새 DOM 교체 시 createRoot 2회 PASS. 02 기존 회귀 포함 15/15 PASS (Vitest4.1.11). 이 테스트는 모듈 재평가와 mount 호출 수를 검증하며 실제 브라우저 콘솔 재현/재검수를 대신하지 않는다.
- 01~05 `npm run build --workspace @storeloop/concept-0N` 모두 TypeScript와 Vite build PASS. 별도 공유 패키지/lockfile 변경 없음.
- 수정 파일: `web-concepts-01/src/main.tsx`, `web-concepts-02/src/app/main.tsx`, `web-concepts-03/src/app/main.tsx`, `web-concepts-04/src/app/main.tsx`, `web-concepts-05/src/main.tsx`, `web-concepts-02/tests/hmr-entry.test.tsx` 및 본 기록/02 체크리스트.
- root에게 수정 완료·소스 동결·기존 탭 전체 새로고침 1회 및 재검수 재개 가능 시점을 전달했다. root는 각 시안의 독립 콘솔 재검수를 수행한다. 다른 시안 원작성자/후속 검수 담당에게 이 보존 규칙 전파를 요청한다.
- 최종 상태 REVIEW. 앱 entry 외 UI 소스·공유 DB·브라우저·원격 작업은 수행하지 않았다.
