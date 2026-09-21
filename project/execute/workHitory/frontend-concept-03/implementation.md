# 시안 03 구현 이력
- 2026-09-21: 사용자목표와 G1확정기록 수신. 공통계약 변경 없이 사진contact sheet/분할근거inspector/운영attempt타임라인 DS03-001신규정의. root에전파하며 최종독립QA는별도담당.
- 소유경로는web-concepts-03 및concept03기획·체크리스트·이력으로한정한다. 공통클라이언트만공유하며다른시안코드를복제하지않는다.
- 사용자실제AI호출승인수신. root배정실제브라우저인수와중복유료호출을조정한다.

## 구현·자체 검증 결과 (REVIEW 인계)
- DS03-001 사진 contact sheet→이미지/근거 분할 inspector 및 운영 요청/attempt 타임라인을 구현했다. src/app, store-owner, ofc-admin, platform-admin, shared를 분리하고 React19/Vite7/TypeScript5 단일 빌드에 모든 역할 화면을 담았다.
- package: @storeloop/concept-03. 포트5175, `/api`→공통127.0.0.1:8000 proxy. AI직접호출 없음. npm 설치/lockfile은root소유.
- 점주: 로그인/연결매장, 사진1~5/10MiB/JPEGPNG·순서/제거/미리보기·질문/멱등제출,2초상태조회/종료중단/30초지연,실제결과/기준별근거·Reference snapshot·판단가능률·준수율·Mock출처,후속제출·비교·문의·알림.
- 영업: 범위관제·동일필터drilldown,매장/후보claim,4단계기준버전·비활성·이력,Reference업로드·교체·비활성,문의담당/상태/해결/다음점검/코멘트,추이·상관산점도·표본/결측·Mock집계.
- 운영: 일반계정/역할/지역/비활성/비밀번호변경·매장연결,지역/매장/카테고리,상태·실제/fixture구분·attempt·실패retry,감사읽기,공지게시/변경·미리보기. 영업API/사진을요청하지않음.
- 로그인은공통메모리CSRF클라이언트. 현재계정재검증 및 역할/매핑변경시화면트리재구성. URL조회/페이지·직접경로·권한가드·4상태·mobile CSS를소스에구현했다.

### 실행한 검사
1. `npm run test --workspace @storeloop/concept-03`: 최초기능stub에6개기대assertion FAIL(권한/returnURL/null/파일제약/polling/기준레벨)→구현후6 PASS.
2. 서버schema와교차읽기중 이슈미해결상태변경의 빈resolution이422가될결함발견. 회귀assertion `'' !== null` FAIL→issueChange 정규화후7 PASS. 이슈priority와공지severity enum,제목/본문길이도정합화.
3. `npm run build --workspace @storeloop/concept-03`: 초기CSS빈data import는Vite PostCSS에서ENOENT. 불필요한import제거후 TypeScript/Vite PASS. 최종dist JS303.22kB(gzip91.40),CSS18.60kB(gzip4.90).
4. 실제 브라우저/실제API 변경/실제AI/React컴포넌트상호작용/접근성·디자인 시각확인: NOT_RUN. root의 전용test DB전환 및독립인수와세션/HMR충돌을피하도록실행대기했고, 이후root의명시적소스동결요청으로REVIEW인계한다. 정책단위테스트를브라우저통과로보지않는다.

### 첫 인계 당시 잔여사항 (아래 DS03-FIX-001에서 네 코드 결함 해소)
- 공통서비스AI_UNAVAILABLE 진단은root담당이며03호출성공증거는아직없다.
- 폼수정409후최신version재조회와입력유지 동선은실제검수필요. 현재변경오류문구가있으며독립QA에서재조회동선을확인한다.
- Reference교체파일의선택이름은표시되지만업로드전이미지preview는현재구현되지않았다. 제출사진은실제preview구현. S-B04/공통업로드기준검수시보완필요.
- CSRF_INVALID403도공통authError에서접근불가경로로이동한다. 일반권한403과CSRF재시도경로를구분하는수정이필요할수있다.
- 현재프로토타입양식에서멱등키는실패재시도시유지되며성공시교체된다. 실패후같은화면에서문의/claim/retry본문을수정할경우새키생성세부동선검수필요(제출은payload변경시새키구현).
- root의요청으로현재시점소스를동결한다. 독립검수결함수신후배정된파일만수정하고재빌드한다.

## DS03-FIX-001 — 검수 전 필수 복구 동선 수정
root가 첫 인계의 네 코드 결함 수정을 재배정했다. 동일 소유경로의 src/tests/기록과 테스트 의존성 선언만 수정했다. 공통API 계약은변경하지않았다.

1. **CSRF403 복구**: 일반 `FORBIDDEN`만 접근불가로이동하고 `CSRF_INVALID`는폼·입력·선택파일을유지한다. 안전한안내에서사용자에게저장버튼의명시재시도를안내한다. 다음변경요청은공통api-client가폐기한CSRF를갱신한뒤전송한다. 자동재전송하지않고동일본문멱등키를유지한다. 401세션만료는기존로그인복귀를유지한다.
2. **Reference 미리보기**: 실제선택File에BlobURL을발급해비율유지이미지와파일명·용량을보여준다. 교체및언마운트시URL을폐기한다. 제출사진의기존순서미리보기는유지한다.
3. **409 초안 유지**: 기준/Reference/계정·연결/기준정보/이슈/공지변경폼에 `입력 유지하고 최신 정보 확인` 버튼을추가했다. version변경으로폼컴포넌트를재생성하던key를안정적인레코드ID로바꿔초안을유지하고,새서버version을다음명시저장에사용한다. Reference는lineage최신revision과state_version을다시찾으며교체선택파일까지보존한다. 새등록폼의일반충돌은폼을닫지않고사용자가입력을수정할수있다.
4. **멱등키**: 문의/담당claim/작업retry에대상경로+본문서명을사용한다. 같은논리요청실패의명시재시도는같은키를재사용하고,본문/대상이바뀌면새키를만든다. 성공후키를초기화한다. useAction은동기pending ref로중복이벤트도차단한다.

### TDD 및 검증
- `tests/recovery.test.ts`: jsdom/Testing Library로폼상호작용검증. 수정전4개기능FAIL을확인했다: CSRF가잘못forbidden으로이동,409최신조회버튼없음,Reference미리보기없음,수정본문에같은키재사용. import/의존성오류가아닌각기능assertion/locatorFAIL이다.
- 수정후4개GREEN,추가로CSRF명시재시도와Referencelineage충돌의파일/초안보존회귀2개PASS.
- 정책검사8개(기존7+대상/본문/성공reset키경계1)와React상호작용6개, **14/14 PASS**.
- 명령: `npm run test --workspace @storeloop/concept-03`.
- 명령: `npm run build --workspace @storeloop/concept-03`: TypeScript/Vite PASS. JS305.56kB(gzip92.02),CSS18.83kB(gzip4.95).
- 테스트의HTTP응답은명시적인test double이며실제API/브라우저/AI성공으로보고하지않는다. 실제인수는root독립QA에서수행한다.
- jsdom^26.1.0/@testing-library/react^16.3.0를package.json에명시하고root에lockfile갱신을요청했다. 이미설치된동일라이브러리로검사수행.
- 상태: 다시소스동결, **REVIEW 재인계**. 이번배정의네미해결코드항목은해소. 실제브라우저/실제AI/최종독립디자인검수는NOT_RUN이며root배정유지.
