# IB-C03 Reference 새 버전 충돌 복구
## 2026-09-21 / RED
- 독립 검토의 후보를 실제 `References` 컴포넌트에서 재현했다. 기존 revision1에 설명·사유·교체사진 입력 → PATCH409 → ‘상태를 다시 확인’ → 목록은 revision2 새ID 반환.
- 실패 assertion: 사진 설명이 ‘내가 작성 중인 설명’ 대신 ‘다른 사람이 저장한 설명’으로 바뀜. 원인은 Card key가 revision ID이고 전체 목록 재조회가 편집 DOM을 교체하는 것.
- 첫 테스트 작성의 exact label은 UploadField 도움말 포함 accessible name과 달라 selector를 정정했으며 이 locator 실패는 기능 RED로 세지 않는다. 정정 후 실제 초안 유실 assertion RED를 확인했다.
- 수정 계획: 해당 편집 폼에만 최신 저장 대상 id/state_version을 별도 보관. 충돌 확인은 같은 lineage의 허용된 Reference 목록을 페이지 단위로 조회해 최신 revision을 찾고, 전체 카드 목록을 교체하지 않는다. 초안/사유/input File/미리보기 DOM은 유지하고 사용자 명시 재저장만 PATCH한다. 다른 필터·목록·서버·문서 계약은 변경하지 않는다.
- API 응답은 합성 테스트 fixture. 공유 DB·Browser·runtime·모델은 사용하지 않았다.

## 최소 수정 및 GREEN
- `Standards.tsx`에 실제 편집용 `ReferenceRevisionForm`을 분리했다. 기존 card의 ID key나 과거 행을 억지로 같은 lineage key로 합치지 않았다. 따라서 과거 버전 포함 목록의 중복 key를 만들지 않는다.
- 409의 ‘상태를 다시 확인’은 전체 목록 reload 대신 카테고리/매장 범위 내 `include_inactive=true` 목록의 모든 페이지를 읽고 같은 lineage의 최고 revision/state_version을 선택한다. 저장 대상 id/state_version/version만 갱신하며 초안 textarea·사유·file input·선택 미리보기를 다시 생성하지 않는다.
- 화면에 최신 버전을 확인했고 입력을 유지했음을 안내한다. 조회는 PATCH를 호출하지 않는다. 사용자가 다시 ‘새 Reference 저장’을 누를 때만 최신 ID/state_version과 원래 사진·설명·사유를 보낸다. 다음 경쟁 변경은 서버409로 다시 보호된다.
- `tests/reference-conflict.test.tsx`는 공통 MutationForm만이 아닌 실제 References 페이지를 렌더한다. 기본 활성 목록과 과거 버전 포함 목록 두 경우에서 다른 사람의 새 revision→409→최신조회→사진·설명·사유/미리보기 보존→자동요청0→사용자 재저장 최신ID/state_version/동일File payload를 검증했다.
- jsdom fireEvent는 input.files getter만 설정하고 native FormData 내부 파일 저장소를 갱신하지 않으므로 테스트에서 HTML form의 file input.files를 FormData에 그대로 연결하는 환경 보정만 적용했다. 제품 파일 전송 로직은 바꾸지 않았으며 File 동일성 및 실제 DOM 보존을 별도 assertion으로 확인했다.
- 결과: 해당 실제 컴포넌트2 PASS. 전체 concept04 Vitest4.1.11 **4파일16테스트 PASS**. TypeScript+Vite build PASS. 신규 리그레션 외 MEDIA-CLARIFY·기존 흐름 회귀도 함께 통과.
- 공유 DB·Browser·runtime·모델 호출 없음. 실제 화면 순차 충돌 확인은 root에 인계하며 여기서는 실제 Browser PASS로 쓰지 않는다.
- 상태 REVIEW, 변경 파일: `web-concepts-04/src/ofc-admin/Standards.tsx`, `web-concepts-04/tests/reference-conflict.test.tsx`, 전용 체크리스트/본 이력. 다른 작성자의 MEDIA-CLARIFY 및 테스트 변경은 보존했다.
