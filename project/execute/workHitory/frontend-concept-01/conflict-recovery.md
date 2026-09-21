# F01-INPUT-RECOVERY-001 기준·Reference409 및 CSRF 복구

상태: REVIEW 동결 — 작성자 새3회귀 포함 전체UI20개 + 독립 원본2개·TypeScript/Vite PASS. root 실제 기준/Reference409·CSRF 복구 PASS.

## 범위와 RED

root의 실제01 기준409 초안/사유 유실 인계에 따라 실제 GuidelineDetail/References와 App을 사용한 한정 회귀3개를 작성했다. 기준은 최신 version2 조회 뒤 textarea가 다른 사람이 저장한 본문으로 덮이는 assertion FAIL, Reference는 명시 재저장에도 /references/r1 및 state_version1을 다시 보내는 assertion FAIL, CSRF는 실제 QueryCache/MutationCache 연결의 App에서 매장 query removed 이벤트1회와 잘못된 권한거부 문구로 FAIL이었다. 빈 버튼 존재 여부나 잘못된 import 실패를 최종 RED로 대신하지 않았다.

## 최소 변경

- Standards.tsx 기준 편집 Form key를 내용 version 대신 대상id로 유지한다. 서버 최신버전은 표시/다음 payload에 반영하되 사용자 title/text/reason DOM을 재생성하지 않는다.
- Reference 편집을 사용자가 새로 선택/취소/정상저장했을 때만 editorKey로 초기화한다. 409 복구는 `최신 Reference 확인 (입력 유지)`에서 현재 category/store 범위·include_inactive·100개씩 페이지 순회로 같은 lineage의 최신version/id/state_version을 찾아 편집 대상만 교체한다. caption/reason/file input은 유지하며 자동 재저장하지 않는다. 최신 비활성 revision도 구revision 대신 사용한다. 현재 범위에서 못 찾으면 안전한 오류를 보여 준다.
- 기존 main.tsx의 QueryClient 구성을 `app/query-client.ts:createAppQueryClient`로 옮겨 실제 App 회귀도 동일 설정을 사용하게 했다. CSRF_INVALID만 권한철회 이벤트에서 제외하고, 다른401/403 경로는 유지한다. shared ErrorBox는 입력 유지·명시재시도 안내를 표시한다. 공통 api-client의 토큰 재갱신/자동재송신 금지/멱등키 규칙을 바꾸지 않는다.

## 검증과 한계

`tests/conflict-recovery.test.tsx`2개는 최신version 및 lineage/state_version으로의 사용자 명시 재저장·초안/사유/File 보존을 확인한다. jsdom은 fireEvent의 FileList를 native FormData 변환에서 읽지 못하므로 해당 테스트에서만 브라우저의 FileList→FormData 동작을 보완했다. 실제 파일 선택/전송은 root 브라우저가 별도 검증한다.

`tests/csrf-recovery.test.tsx`1개는 실제 App 및 production QueryClient 구성에서 CSRF 오류에 업무 query 제거0, 보존된 사진·질문, 자동재송신0, 같은키·같은File의 명시 재시도만 확인한다. 새모델/서버/브라우저 호출은 없다.

새3개 GREEN 후 `npm run test:ui --workspace=@storeloop/concept-01`은20개/6파일 PASS, `npm run build --workspace=@storeloop/concept-01`은 tsc/Vite PASS. 산출물/소스 최종SHA-256은 conflict-recovery.json에 기록했다. 전체 공통검증258개는 불필요하게 반복하지 않았다. API/DB/다른시안/package/lock/이미지/매뉴얼을 변경하지 않았다.

## 독립 후속 R01-01/02 종결

독립 검토자 contract_ai의 기존 actual App 두 RED를 그대로 사용했다. A의 최신 조회 대기 중 B를 선택한 뒤 A 응답이 B의 저장 대상을 바꾸던 문제는 요청 세대를 선택·취소·unmount 시 무효화하고 각 await 이후 대조하여 해결했다. 직접 최신 조회의401/403은 production 인증 오류 처리 함수에 연결하고 접근 오류 상태에서 업무 조회와 기존 편집/사진 메타데이터를 비웠다. CSRF_INVALID는 계속 초안을 보존하며 자동 저장하지 않는다.

원본 독립 테스트 파일은 수정하지 않았다. 동일 두 회귀2 PASS, 기존 UI20개/6파일 PASS, tsc/Vite build PASS다. 독립 작성자도 같은 두 회귀를 재실행해2 PASS를 보고했다. root는 실제 기준409·Reference409·CSRF 초안 보존과 사용자 명시 저장을 확인했다. 새 경계/테스트·Browser·DB·모델 호출로 범위를 확대하지 않았다. 마지막 소스/기존 테스트/독립 원본/빌드 hash는 conflict-recovery.json을 따른다.

사용자의 매뉴얼 우선 지시에 따라 제품 소스를 동결하고 네 매뉴얼의 상태·복구 안내·근거 링크를 별도 MAN-FIRST-001에 갱신했다. 기존 이미지/CSS는 변경하지 않았다.
