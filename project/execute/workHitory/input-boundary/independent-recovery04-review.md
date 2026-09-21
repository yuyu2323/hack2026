# IB-C03 시안04 Reference 충돌 복구 독립 검토

- 담당 contract_ai / **REVIEW_COMPLETE · PASS**. 이번 변경 원인·정확 저장 대상·권한 경계에서 차단 결함을 발견하지 않았다.
- 제품 소스/Browser/DB/모델을 변경하거나 호출하지 않았다. 원래29장 디자인 검수는 동결을 유지한다.

`ReferenceRevisionForm`은 각 기존 card의 ref.id에 속한 별도 컴포넌트다. 충돌 확인 때 전체 목록을 다시 불러 편집 DOM을 교체하지 않고 target의 id/version/state_version만 변경한다. 따라서 설명·사유·file input·미리보기를 유지한다. 같은 category/store 범위에서 include_inactive=true로 페이지를 순회하며 같은 lineage의 최고 revision과 state_version을 선택한다. 실제 PATCH는 사용자가 다시 저장했을 때 선택된 target으로 보낸다. 조회가 mutation을 자동 실행하지 않는다.

01의 단일 공용 editor와 달리 다른 card를 열어도 기존 인스턴스의 target/입력을 공유하지 않는다. 늦은 응답이 다른 lineage의 editor 대상으로 갈 경로를 발견하지 않았다. 새 조회는 `checked(api.get(...))`를 사용하여 실제401/일반403의 기존 access-error 경로를 유지한다. 같은 함수가 mutation의 권한 오류에도 사용되며 CSRF 토큰 갱신/자동 재송신 금지 규칙은 바꾸지 않았다. 다음 동시 변경은 서버의 revision/state_version409로 보호된다.

작성자 실제 References 컴포넌트 회귀를 독립 재실행했다. 기본 목록·과거 버전 포함 목록 **2/2 PASS, exit0**이며 초안/사유/File/미리보기 보존·자동 저장 없음·최신id/state_version의 명시 재저장을 확인한다. FileList→FormData 환경 보정은 테스트에만 있고 제품 전송 코드를 바꾸지 않는다. 명령과 소스hash는 [index](independent-recovery04-index.json). 작성자 전체16/build PASS는 별도 근거이고 본인은 재실행하지 않았다.

실제 두 탭의409 복구와 화면 배치는 root가 확인하는 별도 Browser 인수다. 본 검토의 소스/합성 회귀 PASS를 전체 제품·접근성·브라우저 완료로 쓰지 않는다.
