# implementation: 관제 데스크

- 담당: product_design
- 상태: REVIEW
- 체크리스트: [implementation](../../checkList/frontend-concept-01/implementation.md)

## WEB01-001 — 착수·계약 수신

- G1 확정본03/04/06, 디자인DS01-002, 공통API클라이언트 인터페이스를 수신했다.
- 경로는상위02의 web-concepts-01로확정. root초기메시지 frontend/concept-01은오기였으며아무파일도작성하지않고정정수신.
- CONTRACT-DATA-1.0c의 context평탄화(context.guidelines/references), assignee후보페이지계약확인.
- 구현계획: 역할소스분리·관제테이블/필터→근거흐름, TanStackQuery/ReactRouter, 공통클라이언트만시안간공유. 실제API외fallback평가없음.
- 검증계획: 역할접근/입력/poll종료/null/필터보존 RED→GREEN, UI행동검사, 단일build, 백엔드가용후실브라우저점검. 실제AI차단은별도인수에남김.

## WEB01-002 — TDD 및 구현

- 초기 정책 RED: 역할 시작/직접URL, 사진 한도, 종료 polling, null 준수율, 동일조건 drilldown 5개 실패를 확인했다. 구현 후 GREEN5.
- UI RED: 확정 context.references의 photo_id 이미지를 표시하지 못함, 활성 연결 매장 없는 제출 버튼이 활성인 2건. snapshot의 보호 미디어 URL과 제출 disabled를 구현해 GREEN. 질문·사진을 현재 Reference로 대체하지 않는다.
- 자체 권한 검토 RED: OFC의 HQ 기준, 지역 관리자의 타 지역 기준, 공통 CATEGORY/Reference 변경 허용 판정 오류. 권한 helper와 편집 UI에 반영해 정책 GREEN6.
- 세션 회귀 RED: 기존 session 데이터가 있는 상태에서 auth/me 401이어도 화면이 남음. 401 시 업무 cache와 session 폐기·로그인 복귀를 구현해 GREEN.
- 정상 unknown/mock 결과 및 로그인 실패 UI도 검증한다. 최종 정책6+UI6 PASS, build PASS.
- 빌드 최적화: Recharts 분석 화면을 lazy로 분리, 초기 bundle 375.9kB / 분석381.9kB, 큰 단일 chunk 경고 해소.

## WEB01-003 — 완료한 구현 범위

- app/shared/store-owner/ofc-admin/platform-admin 소스 분리, 세션/CSRF 공통 클라이언트, 현재 역할 시작/직접URL 경계, 10초 현재 계정 재검증과 변경 시 업무 cache 폐기.
- 점주 한 화면 업로드: 실제 multipart·사진1~5·MIME/10MiB/질문2000·미리보기/제거/순서·멱등키·parent 재제출. 이력/상세/2초poll/기술실패/unknown/근거/Reference snapshot·전후사진/날짜/기준버전·문의/읽음 알림.
- 업로드 시작·접수·job완료·결과 최초표시 시각을 세션 내 timing 값으로 기록하고 30초 목표를 실제 차이로 표시한다. 화면 이탈 시간이 포함됨을 안내한다.
- 영업 관제 KPI/현재scope 드릴다운·매장/후보담당·4단계기준/새버전/활성·Reference 생성/새revision/status(state_version)·이슈담당/상태/조치·주별추이/Mock상관/기본집계.
- 운영 서비스/model readiness/fixture 분리·계정생성/수정/매핑영향·지역/매장/카테고리·job/attempt 메타·실패재처리 사유확인 dialog·감사·운영공지.
- Should: 공통 유효 공지, 필터·페이지 URL 보존/뒤로가기, 갱신안내. 컴포넌트 빈/로딩/오류/재조회, null/Mock/source 표시.
- 관제 IA 토큰·224px sidebar·KPI/표·사진5:평가7·모바일 점주하단nav/제출이력card·drawer초점/ESC·키보드tab/표region·44px폼control 구현.

## WEB01-004 / PD-003 / DS01-003 — 독립 정적 검토 결함 수정

- root 지적: 플랫폼 운영자에게 영업 `/notifications` 링크와 라우트를 노출했다. API 권한분리와 맞지 않는 UI.
- 회귀 UI RED1 확인 후 운영자 알림 링크·라우트를 제거해 GREEN. 점주/OFC/지역/본사 알림과 모든 역할의 운영공지 유지.
- docs03 R-M17, docs04 S-C01/endpoint 표, C01 brief/design-spec/acceptance를 같은 결정을 명시하도록 보완했다. 상위 문서/필수 기능 축소가 아니며 API 변경 없음.
- root에게 수정 완료 ACK 전송. contract_data 전파는 tool `agent thread limit reached`로 전달 실패해 root가 현재 담당에게 전파하도록 요청했다.

## WEB01-005 — 실행 검증 및 REVIEW 인계

- 명령: `npm run test --workspace=@storeloop/concept-01` → 정책6 PASS.
- 명령: `npm run test:ui --workspace=@storeloop/concept-01` → UI6 PASS.
- 명령: `npm run build --workspace=@storeloop/concept-01` → TypeScript/Vite PASS.
- dev 실행은 sandbox listen EPERM 후 승인된 local listen 재실행 성공, http://127.0.0.1:5173, session22739. root가 turn 종료 후 직접 관리 재실행하기로 했다.
- 자체 브라우저: 정식 Browser 스킬을 읽고 getForUrl(5173) → No browser is available. 공식 troubleshooting에 따라 browsers.list() → []. 자체 브라우저/화면 캡처 **NOT_RUN**. 별도 우회나 mock브라우저 증거 없음.
- root가 concept02 인수 후 별도 테스트 DB의 공통API로 concept01 독립 브라우저/실제AI/디자인 검수 수행 예정. 같은 host cookie 공유 때문에 자체 로그인/데이터 변경을 하지 않았다.
- 실제 AI 성공·30초 목표는 이 구현 단위테스트로 PASS 선언하지 않는다. 최종 디자인/기능 검수 및 실제 화면 HTML 매뉴얼은 후속 담당이 확정해야 한다.
- 인계: `web-concepts-01/README.md` 실행/주요동선; source `src/app/App.tsx` 전체 라우트; `tests/` 재현검사. 계약 변경 없는 자체 구현 완료, 상태 **REVIEW**.

## F01-FILTER 조사 착수
root 실제 OFC 브라우저에서 매장·카테고리 연속 변경 시 먼저 선택한 조건이 URL과 UI에서 소실됨을 보고했다. 01 필터 경로 재개 권한을 받았고 공통 API 클라이언트는 변경하지 않는다. useFilters가 렌더 시점 values를 캡처해 새 URL을 만드는 점을 먼저 확인한다. 실제 Router와 입력 이벤트를 사용한 회귀로 재현한 뒤 의미를 유지하는 최소 수정만 적용한다.

### F01-FILTER 완료 · REVIEW 동결

- 실제 ScopeFilters·MemoryRouter를 사용하여 같은 tick의 매장/카테고리/시작·종료일 입력, 단일해제+상태일괄변경, 뒤로가기 후 초기화+즉시입력 3개 의미 회귀를 추가했다. 초기 구현에서 모두 RED였다. 마지막 변경만 남거나 초기화 전 조건이 되살아나는 것이 원인이다.
- shared/data.ts useFilters의 최신 선택값을 ref에 동기적으로 누적하고, Router params가 실제 변경되면 그 URL을 기준으로 다시 맞춘다. page 리셋과 초기화 기본값, 뒤로가기 의미를 유지한다. 공유 API/다른앱 변경 없음.
- 새3개 GREEN, 전체 UI12 PASS 및01 build PASS. 이후 Analytics 변경과 함께 최종 UI14/build PASS로 갱신했다.

### F01-ANALYTICS 완료 · REVIEW 동결

- root 실제 상관표의 매장/category 식별자 표시를 보고했다. Analytics 화면의 허용 /stores·/categories·/regions 목록을 페이지 끝까지 읽어 표시명을 해석한다. 점수/상관/집계 재계산과 원본 ID/URL 변경은 없다.
- 집계 DTO의 의미 있는 name은 fallback으로 유지한다. 목록에 이름이 없으면 대상 종류·이름 확인 불가·원본 ID를 표시하며 다른 권한의 operations API를 호출하지 않는다.
- 신규 UI회귀2개 RED→GREEN: 상관/집계의 다음 페이지 매장명·카테고리명, 이름 누락 안전 표시. 실제 Analytics/Table을 렌더하며 차트만 레이아웃 의존 제거용 컴포넌트 대역을 사용했다.
- 최종 `npm run test:ui --workspace=@storeloop/concept-01` →3 files/14 PASS. `npm run build --workspace=@storeloop/concept-01` → TypeScript/Vite PASS. index-2N61yu91.js / Analytics-w4uV38Vh.js.
- 수정 소유 파일: src/shared/data.ts, src/ofc-admin/Analytics.tsx, tests/filters.test.tsx, tests/analytics.test.tsx. app01 소스 다시 동결, root가 실제 브라우저 재검수한다.
