# MEDIA-CLARIFY-1 통합 반영

- 담당: product_design / root 임시 소유권 이관
- 상태: REVIEW 동결
- 대상: 시안01·03·04 Reference 화면 메타데이터, 시안03 운영자 알림 직접 경로 정책
- 계약: docs06 top-level reference_photos 선택 배열. snapshot 순서·reference_id로 대응하며 실제 Photo의 보호 URL과 source_kind를 표시한다. 누락은 context.photo_id URL만 사용하고 출처를 추정하지 않는다. 점주 GET /references 요청을 추가하지 않는다.
- 범위: 세 시안의 필요한 소스·검증 및 각 체크리스트 추가. package/lock·공유서버·DB·브라우저 변경 없음.
- 검증 계획: 역순 metadata와 무관 metadata 포함·정상 source 배지·누락 fallback/출처 비추정·점주Reference API 요청 없음 RED→GREEN. 시안03은 기존 메뉴/route 분기를 검토하고 직접 URL 정책 회귀 검증. 이후 각 기존 전체 테스트와 build.

## 통합 검증 및 추가 디자인 소유권

- TDD RED: 01 metadata URL/출처1, 03 metadata URL/출처1+운영자 notifications 경계1, 04 metadata URL/출처1을 실제 assertion 실패로 확인했다. 누락 fallback 테스트는 기존 동작에서 PASS했다.
- 01/03/04는 context.references 순서를 유지하고 reference_id로 metadata의 photo를 연결했다. 일치하지 않는 metadata는 표시하지 않는다. 실제 source_kind=ai_generated_demo만 해당 배지를 표시하며 값이 없는 Reference에 사용자 업로드/AI 생성 출처를 부여하지 않는다. 세 시안 모두 점주 GET /references를 추가하지 않았다.
- 03 operationMenu에 영업 알림이 없고 Routes에도 operator 제외 분기가 이미 존재했다. root guard canVisit에 /platform-admin/notifications 및 하위경로 제외를 더해 직접 진입·로그인 return 경계를 명시했다. 운영 공지 경로는 허용한다.
- root·독립 디자인 담당이 01 Reference 관리의 행 목록, 04 입력 대비, 03 필터 터치영역, 05 모바일 로그아웃 터치영역 보완을 추가 배정했다. 문서 기준을 낮추지 않았다.
- 01 Standards.tsx를 3열 gallery에서 160px 썸네일+카테고리/설명/범위/버전/활성/동작을 갖춘 한 행 목록으로 변경했다. 모바일은 같은 목록행 내부를 세로로 재배치한다. 원본 사진 열기와 출처, 수정·비활성 동작은 유지한다. 실제 편집 state_version PATCH 회귀 RED→GREEN.
- 04 input/select/textarea, secondary/pagination 버튼의 경계를 --control #65796b로 변경했다. 밝기공식 계산: white4.666:1, canvas #f5f3ee 4.208:1, secondary-hover #edf2ec 4.113:1, confirm #f4f0dd 4.078:1, plain-hover #e7ede4 3.918:1. 모두3:1 이상. 패널 구획선은 기존값 유지.
- 03 .filters input/select·button·text-link의 같은 42px 최소높이 규칙을44px로 일치화했다. root의 필터 min-height CSS 이관 범위에서 관련 컨트롤의 높이만 변경했다.
- 05 root가 별도 이관한 모바일 .identity button의 min-height36→44만 변경했다.
- 04 첫 build의 callback 안 s.data nullable TS18047을 optional 접근으로 수정했다. UI 동작은 동일하며 수정 후 관련검증을 재실행한다.
- 03 기존 recovery 테스트에서 빈 img src 경고2회가 남는다. 모든 assertion은 PASS이며 이번 metadata 테스트에서는 발생하지 않았다. 이관 밖의 기존 미리보기 초기값 경고로 root에게 별도 전달한다.


## 최종 실행 결과 / 인계

| 시안 | 명령 | 결과 |
|---|---|---|
| 01 | npm run test --workspace=@storeloop/concept-01 | 정책6 PASS |
| 01 | npm run test:ui --workspace=@storeloop/concept-01 | UI9 PASS (metadata2/행목록편집1 포함) |
| 01 | npm run build --workspace=@storeloop/concept-01 | TypeScript/Vite PASS |
| 03 | npm run test --workspace=@storeloop/concept-03 | 17 PASS (metadata2/알림정책1 포함) |
| 03 | npm run build --workspace=@storeloop/concept-03 | TypeScript/Vite PASS |
| 04 | npm run test --workspace=@storeloop/concept-04 | 11 PASS (metadata2 포함) |
| 04 | npm run build --workspace=@storeloop/concept-04 | TypeScript/Vite PASS |
| 05 | npm run build --workspace=@storeloop/concept-05 | TypeScript/Vite PASS (승인된 CSS규칙만 수정) |

- 01/04는 root가 고정한 Vitest4.1.11을 그대로 사용했다. package/lock/서버/DB/브라우저 변경 없음.
- 01 적용점: shared/business.tsx SnapshotReferences 및 호출부; Standards.tsx의 Reference 관리 목록, styles.css의 해당 목록 규칙; tests/ui.test.tsx.
- 03 적용점: store-owner/pages.tsx의 적용 Reference 사진·배지, shared/policy.ts의 운영자 영업알림 경계, app/style.css의 필터 min-height; tests/policy.test.ts 및 reference-metadata.test.ts.
- 04 적용점: store-owner/Owner.tsx Reference metadata, shared/ui.tsx의 없는 출처 배지 제거, shared/style.css의 control 대비; tests/flows.test.tsx.
- 05 적용점: src/styles.css의 모바일 .identity button min-height 규칙 단독.
- root와 contract_ai에 변경 위치·증거·기존 경고를 전달하고 REVIEW 동결했다. 실제 브라우저 기능 QA와 최종 PNG 촬영은 root, 독립 디자인/시각 재검수는 contract_ai가 담당하며 본 단위 검증으로 대체하지 않는다.
