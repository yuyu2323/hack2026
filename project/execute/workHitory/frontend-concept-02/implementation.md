# Concept02 구현 이력
- 담당 concept02 / RUNNING / 적용 DS02-001 v1
- 공통 계약 G1 ACCEPTED 수신. context는 평탄화, Reference는 state_version, 모든 운영 변경은 reason/version, 멱등 대상 요청은 같은 payload 재시도에 같은 키를 사용한다.
- 2026-09-21: 구현 전 체크리스트 작성. 정보구조를 상단 역할 메뉴 + 우선순위 업무 카드 + 단계 lane으로 결정. 관제01의 KPI/테이블 첫 화면과 구분한다.
- 변경 DS02-001: 신규 상세 디자인이며 공통 업무·API 계약 변경 없음. root에 전달하고 독립 QA/매뉴얼 배정 시 읽도록 요청한다.
- 브라우저·실제 AI 인수 및 독립 디자인 검수는 NOT_RUN; 구현 단위검증과 별도로 보고한다.
- TDD RED: workflow.test.tsx 실제 실행, 지연 안내·안전 실패 설명이 없는 초기 JobStatus 때문에 2 assertion FAIL (환경 오류 아님), null/역할 복귀 경계2 PASS.
- GREEN: JobStatus에 queued/running/failed/succeeded와 지연/안전복구 문구 구현 후 4/4 PASS. 명령 npm test --workspace @storeloop/concept-02 -- --reporter=dot.

## 자체 검증 / REVIEW 인계
- 전체 역할 앱 구현: 점주 다음 행동·제출·이력·결과·재제출·비교, 영업 3-lane·담당 등록·기준4단계/버전·Reference·이슈·분석, 운영 복구/계정/매핑/기준정보/작업/감사/공지 및 공통 알림.
- 모든 데이터는 공통 API 클라이언트로 읽고 저장. 실패 시 고정 샘플 평가 fallback 없음. 클라이언트 비밀 저장·노출 없음.
- `npm run build --workspace @storeloop/concept-02` PASS. 단일 dist에 모든 역할 포함. dev/preview5174, /api proxy8000.
- `npm test --workspace @storeloop/concept-02 -- --reporter=dot` 8/8 PASS. 지연/실패 RED2→GREEN, return URL 경로 정규화 회귀 RED1→GREEN, 수정 충돌 복구 행동 RED1→GREEN. 사진 장수/MIME 입력 경계도 PASS. 초기 사진 테스트의 jsdom URL API 누락은 환경 오류로 구분하고 테스트 환경 stub 후 실행했다.
- 수정 충돌에서 입력값을 유지하고 최신 정보 다시 읽기 버튼으로 API를 재조회하도록 구현. 멱등키는 대상+본문별로 보존하고 성공 후 초기화한다.
- 폼 schema 대조: issue priority normal/high, 빈 resolution null, 공지 severity info/maintenance, 제목160자. API contract 변경 없음.
- source formatting은 임시 캐시의 prettier3.6.2로 자기 소스만 수행. 루트 package/lockfile 변경 없음.
- root 인수 지적: 점주 /references/{id} 금지. SnapshotReference 추가 조회를 제거하고 context.photo_id 보호 미디어를 직접 사용하도록 수정. snapshot에 source_kind가 없을 경우 생성 이미지로 추정해 표시하지 않는다. Reference 관리 화면은 DTO photo.source_kind를 그대로 표시한다.
- 2026-09-21 root 요청으로 UI 소스 동결, 상태 REVIEW. 독립 기능/실제 AI/디자인 QA는 root 및 별도 검수자 수행 중이며 자체 PASS로 대체하지 않는다.
- 디자인 기준 DS02-001 v1과 모든 변경을 root에 전달했다. 이후 결함별 수정 요청으로 작업을 재개한다.

## 독립 검수 후 보완 C02-QA-001 (2026-09-21)
- 상태 RUNNING. root 지정 범위: 운영자 알림 직접 경로 차단, 기술 unavailable 문구 분리, 분석 표의 사용자용 매장/매대 이름, 읽기 전용 reference_photos 출처 메타데이터 반영.
- PD-003/NOTIFY-CLARIFY-1 docs03/04/06 확인: 영업 알림은 점주·영업만. 운영자 메뉴·라우트·API 요청 모두 제외하고 운영 공지 유지.
- MEDIA-CLARIFY-1 docs06 확인: optional SubmissionDetail.reference_photos를 context.reference_id 순서에 대응. 불변 snapshot/hash/AI 입력은 그대로. 필드 누락 시 보호 URL fallback, 출처 추정 금지, 점주 Reference API 금지.
- 영향은 02 소스·회귀 테스트·기록. 공통 DB/브라우저 조작 및 package/lock 수정 없음. root의 vitest4.1.11 잠금 변경 수신.
- 검증 계획: 운영자 직접 경로에서 영업 fetch 0건·운영 공지 유지, 모델 unavailable 표시, 상관표 이름·누락 표현, Reference 출처/순서/fallback React 테스트 후 build/test.
- TDD RED: 독립 검수 재현 테스트5개 추가 후 기능4개 FAIL, 기존8+Reference fallback1 PASS. 실패 이유는 운영자 직접경로 미차단/사용 불가 문구 없음/UUID 출력/출처 메타데이터 미반영이며 환경 오류 아님.
- GREEN/REFACTOR: 13/13 PASS (Vitest4.1.11), `npm run build --workspace @storeloop/concept-02` PASS. formatter는 기존 임시 캐시에서 offline 실행했고 변경된 자기 소스만 정리했다.
- 운영자 직접 경로는 역할별 canonical route 허용 검사 전에 업무 컴포넌트를 생성하지 않아 영업 API 0호출. 공통 운영 공지 조회는 유지한다. 주어진 회귀에서 `/platform-admin/notifications` 및 API 호출 목록을 확인했다.
- 서비스 전용 ServiceState에서 unavailable=사용 불가, unknown=미확인. 비교 결과의 unavailable=비교 불가 의미는 유지한다.
- 상관 표는 현재 범위 `/stores`, `/categories`의 이름을 매핑한다. 일치 정보가 없으면 매장/매대 정보 없음으로 표시하며 UUID는 사용자 화면에서 제거했다.
- Reference는 context.references 순서를 유지하며 reference_photos의 reference_id를 찾는다. 대응 Photo DTO source_kind로만 생성 배지를 표시하고 optional 필드 누락 시 context.photo_id 보호 URL로 표시한다. snapshot·본문·AI 입력은 변경하지 않았다. 추가 Reference API 호출 0건 회귀 PASS.
- 선택 의견의 rule_key 영어 제목은 이번 수정 범위에서 유지했다. 정본 context.guidelines/ModelResult.criteria에는 title이 없고 사용자 정의 rule_key가 가능하므로 임의 한글 이름을 생성하지 않는다. 동일 화면의 기준 text·근거 reason·행동 actions는 원문 한국어를 제공한다.
- 상태 REVIEW로 재인계. 공유 DB/브라우저/루트 package/lockfile은 수정하지 않았다. 최종 브라우저 캡처·독립 검수 재확인은 root가 수행한다.

## D02-P2 · Reference 사진 번호 표시
- 상태 RUNNING / 독립 디자인 검수 증거 vp-mobile360-reference-snapshot.png, contract_ai에 직접 ACK.
- 원인: reference_photos의 개별 Photo.position=1이 화면 순서보다 우선되어 모든 Reference가 1로 표시된다.
- 변경 계획: context.references를 원래 순서로 순회하며 reference.position, 누락 시 index+1을 표시용 복사본의 position에만 적용한다. Photo URL/source_kind와 원본 context/DTO는 그대로 유지한다.
- 범위: 시안02 Owner.tsx·관련 회귀·기록만. 타시안/API/DB/브라우저 조작 없음. 변경 후 root가 새 캡처를 수행한다.
- TDD RED: 실제 메타데이터처럼 두 Photo.position을 모두1로 둔 fixture에서 context position 존재/누락 2경우 모두 화면 alt가 [1,1]로 나타나 [1,2] 기대 assertion FAIL.
- GREEN: SnapshotReference 표시용 복사본에서만 position을 override. metadata가 역순이어도 reference_id 대응과 context 순서 유지, Photo URL/source_kind 유지, JSON 원본 DTO/context 불변 및 추가 Reference API 0호출 확인.
- 회귀 전체16/16 PASS (Vitest4.1.11), `npm run build --workspace @storeloop/concept-02` PASS, JS artifact index-CQdY1g6y.js. 원본·출처 필드·API·타시안 변경 없음.
- root와 contract_ai에 수정/검증 결과 및 소스 동결을 직접 전달. 최종 화면 캡처·독립 디자인 재검수는 root/contract_ai 진행. 상태 REVIEW.

## C02-RECOVERY-001 · 입력 보존 복구
- 상태 RUNNING. 독립 source검토: CSRF_INVALID가 다른403과 같이 forbidden으로 이동해 초안이 사라짐; Reference409 뒤 edit.id/state_version이 유지되어 재시도도 충돌.
- 범위는02 컴포넌트·회귀·전용기록만. 공유브라우저/runtime/DB/모델 호출·API계약 변경 없음.
- 검증 계획: 실제 App 제출폼에서 CSRF403 후 같은 질문/사진/멱등키 보존 및 사용자 명시 재전송; Reference 폼에서409 후 최신 lineage id/state_version 반영·caption/reason/File 보존. 근거와 필요한 edge case를 독립 reviewer product_design에게 요청.
- 실제 컴포넌트 RED3: App 제출폼 CSRF_INVALID 이후 /forbidden 이동으로 오류/질문/사진 폼 제거; Reference 내용revision 충돌 후 ref-old 전송; 상태충돌 후 state_version1 전송(기대2). 환경 오류 없이 해당 assertions FAIL.
- 수정: CSRF_INVALID만 accessFailure의 권한철회 이벤트에서 제외하고 ErrorBox에 입력유지·명시 재전송 안내. 공통 API 클라이언트의 기존 CSRF 초기화/다음 변경 요청 갱신을 사용하며 자동 재전송하지 않는다. 기존 401/기타403/404 권한 차단은 유지.
- Reference의 최신정보다시읽기는 target category/store, include_inactive=true, page_size100 및 페이지 순회로 같은 lineage의 최신 version/state_version을 찾는다. 현재 edit 대상만 갱신하고 caption/reason/File은 보존한다. 최신 서버 설명과 재저장 안내를 보여 주며 다른 편집 대상을 연 뒤 늦게 도착한 복구 응답은 무시한다. 신규 API나 mutation 자동재실행 없음.
- 독립 reviewer product_design은 페이지 밖/비활성 최신 Reference도 확인해야 함을 전달했고 해당 조회 범위·순회에 반영했다. 브라우저·동시 서버 조작은 root 전담으로 유지.
- GREEN/REFACTOR: 신규3/3 및 기존 포함22/22 PASS(5 test files, Vitest4.1.11). CSRF 재전송의 질문/사진/File identity/멱등키 동일 및 Reference 최신 id/state_version·설명/사유/File 보존·명시 재저장 확인.
- `npm run build --workspace @storeloop/concept-02` TypeScript·Vite PASS. JS index-C6hz82zD.js. 공통 client/package/lock/DB/runtime/모델 호출 변경 없음.
- root의 실제 Reference 새등록 /forbidden 사례는 CSRF 분기와 양상이 일치하지만 응답코드·HMR 영향 증거 없이 원인을 단정하지 않음. root가 최종 브라우저 복구 확인을 계속 수행한다.
- root/product_design에 변경·검증·소스동결 직접 전달. 상태 REVIEW.
