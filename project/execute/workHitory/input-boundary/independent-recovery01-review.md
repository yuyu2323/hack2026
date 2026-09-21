# F01-INPUT-RECOVERY-001 독립 소스 검토

- 담당 contract_ai / 상태 **REVIEW_COMPLETE · PASS — R01-01/02 수정 재검수 완료**. 제품 코드·Browser·DB·모델 조작 없음. 본인 소유 `independent-recovery01-*`만 기록했다.
- 작성자 신규3개는 재실행 PASS. 기준 Form key가 대상id로 유지되고 CSRF가 production QueryClient의 권한철회 이벤트에서 제외되는 정상 경로는 확인했다. Reference 편집 초안/파일 보존 정상 경로도 PASS다.
- 추가로 실제 App/production QueryClient를 쓰는 합성 회귀2개에서 다음 결함을 재현했다. 원래29장 디자인 판정은 변경하지 않는다.

| ID | 재현/실제 | 요구·영향 | 수정 요청 |
|---|---|---|---|
| R01-01 · P1 | A의409 후 최신조회 응답을 지연→B 편집 선택/설명 입력→A 응답 도착→사용자 저장. `/references/reference-b1` 대신 `/references/reference-a2`로 **B 설명**이 전송됨 | 요청의 사용자 선택 대상 보존. 의도하지 않은 Reference lineage를 변경할 수 있음 | `Standards.tsx/refreshEditing`에서 편집세대 또는 현재대상 확인, 대상 변경/취소/정상완료 후 늦은응답 폐기 |
| R01-02 · P1 | 최신조회 직접 `api.get`이403을 반환해 권한 오류가 보이지만 production App의 `['/references']` cache에 기존 사진 metadata/설명이 남음 | docs04§2의 현재 권한 오류 즉시 업무 캐시·열린 이미지 폐기 | 수동 조회도 기존 auth 오류 처리로 연결. CSRF만 제외한401/403 경로 유지 |

수정 작성자 product_design과 root에게 두 건을 전달했다. 작성자 코드 수정은 하지 않았다. `npx vitest run --config execute/workHitory/input-boundary/independent-recovery01-vitest.config.ts`는2 FAIL(exit1)이며 모듈/import/환경 오류가 아니라 정확 저장 대상·캐시 제거 assertion에서 실패했다. 명령·실패당시 소스/테스트 hash는 [RED 근거](independent-recovery01-red.json). 데이터는 전부 테스트 내부 합성 값이다. 실제 서버 요청이나 새 AI 호출을 하지 않았다.

초기에는 위 두 경쟁/권한 경계를 CHANGES_REQUESTED로 인계했다. 정상 단일409 복구만으로 해소하지 않고 아래 동일 회귀로 수정 여부를 확인했다.

## 알려진 두 결함 수정 재확인

작성자 동결 후 제품 소스의 refreshSequence가 선택/취소/unmount에 변경되고 await 뒤 세대를 검사하는 것을 확인했다. 직접 복구 조회의 현재401/403은 공통 handleAuthError를 통과하며 References 접근 오류 상태에서 업무 조회를 비활성화하고 목록/편집 본문을 제거한다. CSRF만 권한철회에서 제외하는 기존 분기는 유지한다.

독립 원본2개를 수정 없이 다시 실행하여 **2 PASS(exit0)**다. R01-01의 저장대상 B 유지와 R01-02의 업무 캐시 폐기를 각각 확인했으며 두 지적을 해소한다. [최종 hash/실행 기록](independent-recovery01-index.json). 사용자 매뉴얼 우선 지시에 맞춰 새 경계·테스트를 추가하지 않았다. Browser/DB/모델은 실행하지 않았다. 기존 작성자3개 재실행과 이번2개를 합해 이 검수에서 실행한 서로 다른 회귀는5개이며, 전체20/build는 작성자 근거다.
