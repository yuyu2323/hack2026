# F01-SCOPE-001 담당 등록 후 목록 조회 정체

상태: REVIEW 동결 — UI17개 및 build PASS, root 실제 재검증 대기

root의 실제 OFC 담당 등록 관측: 후보는0건·저장 성공으로 변하지만 관리 목록이0건이며 최신 정보 조회 표시가10초 이상 남았다. 소스상 Stores는 TanStack Query의 문자열 path queryKey를 사용하므로 객체 dependency 무한조회가 아니다.

claim의 useAction 성공에서 전체 invalidateQueries를 실행하며 session도 새로 조회한다. App의 session signature(id/role/region/store_ids/version)가 바뀌면 removeQueries로 활성 영업 조회까지 제거한다. 이때 기존 observer가 취소된 refetch에 남아 늦은 응답이 화면에 연결되지 않는다.

실제 App + MemoryRouter + QueryClient와 합성 API를 사용한 tests/session-scope.test.tsx에서 claim후 /auth/me의 새store_ids를 먼저 반환하고 /stores를 지연시켰다. 늦은 정상 목록 응답을 resolve한 뒤에도 담당 매장 링크가 나타나지 않는 RED를 재현했다. 실제 DB·브라우저·로그인 상태·서버는 건드리지 않았다.

제안: 범위 변경의 활성 query를 remove하는 대신 이전 데이터를 비우고 같은 observer를 재조회하는 resetQueries 사용을 검토한다. 권한 축소 시 기존 자료가 즉시 없어지는 회귀를 함께 요구한다. root에게 원인/회귀/수정안을 전달했으며 제품 소스는 아직 변경하지 않았다.

## root 승인 후 수정·검증

App.tsx의 session 범위 signature 변경 effect만 removeQueries에서 resetQueries로 바꿨다. 과거 자료를 비운 후 활성 observer를 유지해 서버의 최신 권한 범위로 재조회한다. 401/로그인/로그아웃 처리와 shared API client는 변경하지 않았다.

새 회귀3개는 (1) claim 성공·session 우선 응답·늦은 stores 응답, (2) 담당 범위 축소 시 이전 자료 즉시 제거·조회 완료, (3) OFC→운영자 역할 변화의 자료/메뉴 제거다. 변경 전 앞의2개 RED·역할1개 PASS, 변경 후3개 GREEN이다. 전체 UI17개/4파일 PASS, tsc+Vite build PASS. 최종 소스 및 산출물 해시는 stores-scope-refresh.json에 있다.

02/03/04/05는 읽기 전용으로 검색했으며 TanStack Query의 removeQueries/resetQueries/invalidateQueries/QueryClient 패턴이 없다. 02는 자체useResource와 epoch, 03은 session signature key로 Shell 재마운트, 04는 account/version/store_ids key, 05는 자체useData와 별도 refresh 흐름이다. 이 확인은 동일 제거 경쟁 패턴의 부재만 의미하며 다른 방식의 모든 상태 변경을 새로 인수했다는 주장은 아니다. 네 시안 제품 파일은 수정하지 않았다.
