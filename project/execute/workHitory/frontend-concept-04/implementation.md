# 시안04 구현 이력
## 2026-09-21 / 착수
- G1 ACCEPTED 및 CONTRACT-DATA-1.0c(context 평탄화·담당후보 페이지) 수신 확인. context.guidelines/references, assignees list envelope로 구현한다.
- DS04-001 신규 기획·디자인·검수 기준: docs04 모바일현장의 큰 터치·4단계 제출·bottom navigation을 확정. API/공통 명세 변경 없음. root에 전달하고 독립 검수 담당은 인계 때 확인.
- 소유권 준수, 실제 AI/브라우저 mutation은 root와 조정. 사용자 실AI 합성자료 호출 승인 확인.

## DS04-001 구현 및 자체 검증 / REVIEW
- 독립 디자인: `execute/design/concept-04/{brief,design-spec,acceptance}.md`. 모바일 현장 포켓의 하단 탭·큰 행동·4단계 제출을 구현했다. 다른 시안 소스/레이아웃을 복제하지 않았다.
- 역할 분리: `src/app` 인증/현재역할/라우팅, `store-owner` 제출·평가·비교, `ofc-admin` 관제/기준/Reference/이슈/분석, `platform-admin` 계정/매핑/마스터/공지/상태/재처리/감사. 단일 Vite 빌드, 포트5176.
- `@storeloop/api-client` CSRF·세션·멱등키를 사용. 실제 업무 API와 연결하는 코드를 작성했으며 고정 성공결과나 seed fallback 없음. 사진·문의·담당등록·재처리에 멱등키 사용. 주 제출은 동일 payload 네트워크 재시도에 같은 key 유지, 입력변경시 새 key.
- 점주: 연결없음/카테고리없음, 매장→사진→질문→확인,1~5장·10MiB·형식·미리보기·삭제·순서, queued/running2초polling/성공실패종료/30초지연, 근거 사진 선택, criteria/Reference/snapshot, 질문답변/한계/unknown/Mock, 문의/재제출/전후비교/이력·알림.
- 영업: 범위필터/드릴다운, 미제출·기술실패·판단불가 구분, OFC후보담당등록, 진열기준 4단계/버전/활성상태, Reference등록·미리보기·교체·과거목록, 이슈담당후보/해결사유/다음확인/조치, 추이SVG·산점도SVG·대응표·Mock상관/기간집계.
- 운영: 일반 계정 생성/역할·지역·활성상태/암호변경, 전체매핑교체, 지역·매장·카테고리 생성/변경, 공지 게시기간/일반텍스트, 서비스별 상태/실제·fixture작업분리, attempt이력/실패만재처리, 안전 감사정보. 변경은 사유→영향확인→실행, 저장한 비밀번호 input은 즉시 비움.
- 공통: 현재권한오류시 화면 데이터 폐기, 401로그인/403접근안내, 같은역할return만 허용, 필터·페이지URL, 상세왕복 query보존, 모든폼명시label, status문구/색병기, contain근거사진, 키보드 focus, 모바일하단안전공간.

### TDD와 검증 기록
1. `tests/rules.test.ts`: 구현 전 roleHome/safeReturn·사진경계·null점수·query보존 4개 실제 assertion RED. 구현 후4 GREEN.
2. `tests/flows.test.tsx`: 4단계·이전이동입력보존·파일순서·네트워크 동일key재송신, 빠진매장차단, 운영변경2단계/409입력보존·최신재조회, 현재권한오류후이전데이터폐기 회귀4 PASS.
3. PD-003 영업알림 역할경계 회귀1 PASS. 운영자 메뉴제외, 직접 `/platform-admin/notifications`는 상태홈으로이동하고 영업알림API 호출하지 않음.
4. root 보안패치 vitest4.1.11 반영 후 `npm run test --workspace @storeloop/concept-04`: **2파일9테스트PASS**. 테스트 서버응답은 합성 mock; 실제 AI 인수와 구분.
5. `npm run build --workspace @storeloop/concept-04`: **TypeScript+Vite7.3.6 PASS**, 모든역할포함. 마지막 산출물 JS347.19kB/gzip105.58kB, CSS17.20kB.
6. 자체 검토 중 발견·수정: 상세왕복query손실, 관리자filter지역누락, 기준필터에불필요한날짜,4xx후오래된자료노출방지,409새버전조회시입력유지, Reference업로드미리보기, 결과Mock배지, 새제출URL로이동시polling재시작.

### 변경 전파 ACK
- CONTRACT-DATA-1.0c: context평탄화/assignees페이지 적용.
- PD-003: 운영자영업알림없음, 운영공지는모든역할. 구현·회귀9개중1개 확인. root회신완료.
- MEDIA-CLARIFY-1 제안 수신: 현재 context.references에source_kind없음 발견을 root에 알림. root가docs06먼저확정후 최상위reference_photos 보강 예정. 지금은 근거없는AI생성단정 없이 ‘분석에 적용한 Reference’ 표시. 새메타데이터 수신 후lookup 배지연결 필요. 다른 작업을 차단하지 않음.

### 인계 및 미실행
- 상태 **REVIEW**, 기능/디자인 최종DONE 아님. 독립 실제 브라우저390×844/1440×900·5역할·실제AI제출/재제출·보안검수·HTML매뉴얼은 root 배정 담당이 검증해야 한다. 본 담당은 API DB를 변경하는 브라우저검증/실AI호출을 실행하지 않았음.
- 실행: 프로젝트루트 `npm run dev --workspace @storeloop/concept-04` 또는 해당폴더 `npm run dev`; 127.0.0.1:5176. API8000·AI8010·worker필요. 직접경로 SPA fallback은Vite dev/preview 제공.
- 소스/디자인소유권을 REVIEW수정대기 상태로 root에 인계. 후속결함은 지정받아수정하며공통package.json/rootlock은root소유.
