# C02-RECOVERY-001 독립 소스 검토

- 검수자 contract_ai / **REVIEW_COMPLETE · PASS**. 발견된 차단 결함 없음.
- 범위: 시안02 `shared/core.tsx`, `ofc-admin/Standards.tsx`, 신규 `input-recovery.test.tsx`; 호출 경로인 App/Submit 및 공통 API client를 읽기 대조했다. docs04의 초안 보존/명시 재시도·Reference lineage와 docs06의 권한/CSRF/state_version 계약을 유지한다.
- 제품 소스·기존29장 검수 기록·Browser·DB·서비스·모델은 변경/호출하지 않았다. 본인 소유 `independent-recovery02-*`에 합성 테스트와 보고서만 추가했다.

## 검토 결과

1. **CSRF 초안 보존**: `isAccessRevoked`가 `CSRF_INVALID`만 제외하므로 mutation 실패가 App 권한철회 이벤트/epoch 변경으로 제출폼을 제거하지 않는다. Submit의 values/File/key는 그대로 있고, ErrorBox는 보존과 사용자 명시 재전송을 설명한다. API client는 실패 시 메모리 CSRF만 비우며 자동 재전송하지 않는다. 다음 사용자 요청에서 CSRF를 갱신하고 동일 내용의 요청 키를 유지한다.
2. **일반 권한 차단 유지**: FORBIDDEN·ORIGIN_DENIED 403,401,404는 기존 `storeloop-access`를 발생시킨다. useResource도 해당 오류의 cached data를 제거한다. App의401 로그인/그 외 forbidden 및 epoch 전환 경로를 그대로 확인했다. CSRF 복구를 이유로 서버 권한/Origin 검증을 생략하지 않는다.
3. **Reference 충돌 복구**: category/store·include_inactive=true로 모든 페이지를 읽고 같은 lineage만 비교한다. 가장 높은 내용 version 및 동일 version의 최신 state_version을 고르므로 다른 lineage의 큰 version에 잘못 붙지 않는다. 최신 id/state_version을 가진 edit만 바꾸고 사용자 caption/reason/File은 보존한다. 서버 최신 설명을 별도 표시한 후 사용자가 새 버전 저장을 다시 눌러야 PATCH가 발생한다.
4. **경쟁 응답 방어**: 읽는 동안 저장 버튼을 잠그며 편집 시작/닫기에 recoveryGeneration을 증가시킨다. 다른 대상을 연 뒤 늦게 도착한 응답은 새 대상과 초안을 덮지 않는다. 조회 실패·대상 없음은 오류를 표시하며 권한403은 기존 철회 경로로 전달한다.

이 변경은 Reference **교체 편집폼**의 충돌 복구다. 과거 revision의 상태 변경을 최신 내용에 자동 적용하거나 모든 운영폼의409 복구까지 완료한 것으로 확대하지 않는다. 새 mutation API나 자동 재저장은 없다.

## 독립 실행 근거

| 명령/검사 | 결과 |
|---|---|
| 작성자 input-recovery.test.tsx 재실행 | 3 PASS: CSRF 질문/File/키, 내용 revision 및 상태 version 충돌 |
| 공통 API client 회귀 재실행 | 2 PASS: 다음 명시 요청 CSRF 갱신·자동 재송신 없음, query false/0 |
| 독립 independent-recovery02-edge.test.tsx | 3 PASS: 권한 이벤트 구분, 페이지 밖/비활성/다른 lineage·동일 revision 최신 state, 편집 전환 후 늦은 응답 |

합계8개 PASS, exit0. 독립 테스트는 API를 합성 stub으로 대체하며 Browser나 실제 서버를 호출하지 않았다. 실제 File identity와 PATCH 대상/metadata, 자동 재저장 없음도 검증했다. 실행 명령·소스 SHA256은 [index](independent-recovery02-index.json)에 고정했다. 전체22개·tsc/Vite PASS는 작성자 근거이며 본 검수에서 전체 build를 다시 수행했다고 주장하지 않는다.

root의 후속 메시지에 실제 Browser02 CSRF 복구 및409(v1→선행v2)→최신조회 후 초안/File 보존→사용자 명시 v3 저장 PASS가 인계됐다. 이는 root 기능 증거이며 본인의 독립 Browser/시각 PASS로 바꾸지 않는다. 이번 소스 판정은 기존 전체 시안·200% 미완료 상태를 바꾸지 않는다.
