# 08. 재현 데이터·시연 계정·이미지 계약

- 버전: DATA-001 / 1.0.0 / 2026-09-21 / G1 ACCEPTED (contract-register 확정)
- 기준: [00](00-vision.md), [01](01-architecture.md), [02](02-development-orchestration.md).
- 연동: [요구·AT ID](03-requirements.md), [DB](05-database.md), [API](06-api.md), [AI](07-ai-processing.md), [검증](09-validation.md), [실행](10-execution.md).
- 시드 소유자와 이미지 생성 담당자는 G2 배정표에서 지정한다. 이 문서는 생성/적재/검수 완료를 뜻하지 않는다.

## 1. 재현성·보존

`server/seed`는 DB 적재 CLI, `scripts/seed`는 합성 시나리오 설명과 `manifest.json`, `scripts/seed/assets/shelves`는 실제 생성 이미지 파일의 정본이다. 자료를 만들기 전에 담당자의 체크리스트를 작성한다. DB는 전용 PostgreSQL 포트 55432이며 브라우저/통합 테스트 DB `storeloop_test`와 `.local/test-media`를 시연 DB/`.local/media`와 분리한다.

시드 버전은 `storeloop-demo-v1`, 의사난수 seed는 `20260921`, 기준 시각은 `2026-09-21T00:00:00Z`. UUIDv5 namespace와 `type:stable_code`로 안정 ID를 만든다. 불변 과거 데이터의 시간은 기준 시각 상대값으로 생성한다. 일반 시드는 새 실행일로 과거 날짜를 이동하거나 새 임의 수치를 생성하지 않는다. 실제 새 제출은 실제 UTC 시각을 사용한다.

프로젝트 루트에서 `server/.venv/bin/python -m server.seed`는 해당 seed namespace의 누락 레코드만 생성하며 기존 사용자/다른 테스트 run 데이터·성공 결과·수정한 기준을 덮어쓰거나 삭제하지 않는다. 시드가 기대값과 충돌하면 `SEED_CONFLICT`를 보고하고 별도 새로운 namespace/DB에서 재현한다. 계정 비밀번호를 재실행마다 바꾸지 않는다. 명시적 개발 리셋은 대상 DB·미디어 경로를 확인한 독립 명령으로만 제공하며 기본 시연 명령에는 포함하지 않는다.

적재는 [05](05-database.md)의 FK 순서를 따른다. 파일은 hash와 실제 디코딩을 검사한 뒤 보호 미디어로 복사하고 DB 관계를 저장한다. 실패 시 새로 복사한 고아 파일만 정리하며 기존 파일을 삭제하지 않는다. 적재 후 생성/기존/충돌/실패 건수와 관계·hash·권한 검증 결과를 비밀 없는 요약으로 기록한다.

## 2. 기준 데이터 및 시연 계정

| 분류 | 결정한 시드 |
|---|---|
| 지역 | `north` 가상 북부권, `south` 가상 남부권 |
| 매장 | 6개: 북부권 봄빛역점·은행길점·푸른언덕점, 남부권 별하천점·노을공원점·새봄로점. 도심/주택가 유형 혼합 |
| 카테고리 | 음료·스낵·간편식·생활용품 4개를 DB 데이터로 등록. 실제 이미지/분석 인수는 음료·스낵 2종 |
| 점주 | `owner.north`, `owner.south` 각 지역 매장 3개 연결. `owner.inactive` 비활성, `owner.unmapped` 활성·연결 없음 |
| OFC | `ofc.north`, `ofc.south` 각 지역 2개 담당. 지역별 남은 1개는 미배정 후보; 영업 본문은 담당 등록 후 접근 |
| 지역 | `regional.north`, `regional.south` 각 지역 전용 |
| 본사 | `hq.demo` 전사 영업 |
| 운영자 | `operator.demo` 운영 전용. 영업 본문 접근 없음, 운영자 승격 UI 없음 |

login_id는 가상 식별자이며 실제 이메일/인물명을 사용하지 않는다. 비밀번호는 실행 시 cryptographic random으로 생성하거나 환경으로 주입한다. Argon2id hash만 DB에 저장하고 원문은 사용자 전용 0600 `.local/demo-credentials`에 최초 한 번 기록한다. 콘솔·소스·시드 JSON·스크린샷·HTML 매뉴얼에 비밀번호를 넣지 않는다. 문서는 로그인 ID와 해당 로컬 파일의 사용법만 안내한다. 세션·CSRF 토큰은 시드하지 않는다.

계정 비활성·역할/매핑 변경 인수 테스트는 고유 run ID의 테스트 계정을 생성한다. 화면 테스트가 공용 시연 운영자/점주 비밀번호와 연결을 변경하지 않도록 한다. 기존 세션에서 즉시 권한 감소를 확인하고 테스트가 끝나도 독립 DB 기록으로만 남긴다.

## 3. 기준·Reference·이력·운영 시나리오

| 시나리오 | 초기 연결과 검증 목표 |
|---|---|
| 4단계 병합 | HQ `label_visibility`, REGION `facing`, STORE `shelf_gap`, CATEGORY `category_grouping`. 일부 rule_key를 상위/하위에 중복해 CATEGORY>STORE>REGION>HQ 유효 기준 선택 검증 |
| 기준 버전 변경 | 음료 `facing` version 1로 과거 평가, version 2로 신규 제출. 과거 snapshot/criteria version 불변 |
| Reference | 음료 2장/스낵 2장, 카테고리 공통 1장+북부 특정 매장 전용 1장. 남부 제출에는 북부 전용 Reference 제외 |
| 개선 루프 | 매장별 과거 제출 3~5개(합계 최소18개), 최소 1개의 parent→child, 시각·매장·카테고리 일치 |
| 판단/결측 | 정상/개선필요/판단불가/실패/처리대기, 최근 선택기간 미제출, 기준·Reference 없음, 표본 부족 사례 |
| 이슈·알림 | open/in_progress/resolved 이슈·조치, 점주 문의/AI 확인 필요, 수신자별 read/unread, 현재 담당 없는 이슈 |
| 운영 | is_fixture=true의 종료된 실패 1개 이상, 과거 실패→재처리→성공 연결 1개, 비활성·연결 누락, 운영 변경 감사 이력 |
| Should 공지 | 활성 점검 안내 1개, 종료 공지 1개. 현재 유효한 것만 사용자 공통 안내에 표시 |

“최근 기간 미제출” 매장에도 기준 시각보다 오래된 이력 3개를 두어 “과거 이력”과 “현재 기간 미제출”을 함께 시연한다. 과거 시드의 성공 평가는 `ReviewResult.source_kind=mock`, `Submission.source_kind=seed_demo`이며 `Mock 데이터`를 명확히 표시한다. 입력 이미지가 생성 이미지일 때 `MediaAsset.source_kind=ai_generated_demo`도 별도로 표시한다.

실제 worker가 새로 분석한 결과만 `ReviewResult.source_kind=real_ai`다. 시드 스크립트가 real_ai 결과를 만들어 넣지 않는다. 과거 Mock 리뷰·작업 지연 수치를 실제 모델 성능/정확도 표본에 섞지 않는다. 장애 fixture는 운영 화면에서 `시연 장애`로 구별하며 실제 서비스의 `up/down/unknown`에 가산하지 않는다. 재처리 시 실서버로 실행한 새 attempt 결과만 실제 처리로 기록한다.

이슈의 created_at은 원본 제출/평가 이후, action은 issue 이후, notification은 대상 사건 이후다. 실패 뒤 재처리의 attempt_number가 증가하고 ended attempt는 불변이다. 기준·사진·매장·질문·결과·조치 연결을 의미적으로 검수한다.

## 4. Mock 매출·재고·집계

6개 매장×2개 시연 카테고리×최근 8주를 기본 축으로 둔다. 주차는 UTC 월요일 시작. 매장/상권별 기본 매출에 작은 고정 난수 변동과 준수도에 따른 의도적 완만한 패턴을 넣되 이 관계는 **시연용으로 만든 것**임을 UI·매뉴얼에 명시한다. 수치의 방향은 모델의 시각 판정 정답이 아니다.

카테고리당 5~10개의 가상 SKU 재고 수량을 만든다. 실제 상품명·실제 매출·실제 점주 정보는 사용하지 않는다. SalesMock/InventoryMock source_kind는 `mock` 고정. 이미지에 보이는 포장 수량을 실제 재고나 매출로 확정하지 않는다.

별도 경계 fixture는 (a) 주차 매출 row 누락, (b) unknown만 있는 평가, (c) valid pair 2개, (d) 일정한 매출 또는 일정 준수율을 포함한다. API는 같은 store/category/week 유효쌍만 계산하고 n<3 또는 분산0이면 r=null과 reason을 반환한다. 결측을 0으로 보정하지 않는다. 평균 준수율·판단 가능률·표본수·제외수를 함께 검증한다.

## 5. 실제 생성 이미지 세트

이미지 담당자는 ImageGen 도구로 실제 raster 파일을 생성한다. 이미지 생성 스킬을 먼저 읽고 지정된 도구를 사용한다. 빈 파일·외부 링크·프롬프트만 남기거나 같은 파일을 Reference/제출로 복제하여 비교 성공을 꾸미지 않는다. 도구가 불가하면 root에 차단 원인·영향·대안을 보고하고 사용자 결정이 필요한 부분만 질문한다.

최소 **10개 파일**: 카테고리별 Reference 2개+평가용 before 1개+동일 구도 after 1개+판단곤란 1개. 실제 프롬프트는 가상 브랜드/읽을 수 있는 큰 범주 라벨, 얼굴·개인정보 없는 편의점 매대, 현실적 조명·선반을 지정한다. 음료는 빈 간격과 불균일 페이싱, 스낵은 범주 혼재와 가려진 선반 라벨을 관찰 후보로 둔다. after는 같은 매대 구도에서 개선한 이미지를 편집 생성한다. 판단곤란은 저조도·가림·흔들림 중 관찰을 실제 방해하는 상태를 생성한다.

| image_id | category_code | purpose | 기대 시각 특징(검수 전 가설) |
|---|---|---|---|
| beverage-reference-01/02 | beverage | reference | 정돈된 음료군, 일정한 페이싱, 보이는 선반 라벨; 서로 다른 사진 |
| beverage-before-01 | beverage | submission_before | 중간 선반의 넓은 빈 간격과 뒤로 들어간 병 |
| beverage-after-01 | beverage | submission_after | before와 같은 구도, 지정 간격/페이싱 개선 |
| beverage-uncertain-01 | beverage | uncertain | 어두움 또는 가림으로 세부 판단 곤란 |
| snack-reference-01/02 | snack | reference | 범주별 묶음과 보이는 라벨; 서로 다른 사진 |
| snack-before-01 | snack | submission_before | 서로 다른 범주 혼재·가린 라벨 |
| snack-after-01 | snack | submission_after | before와 같은 구도, 범주 정리·라벨 노출 |
| snack-uncertain-01 | snack | uncertain | 흐림·가림으로 상품군/라벨 관찰 곤란 |

품질 검수 전에 프롬프트의 의도만으로 기대 정답·점수·AI 정확도를 확정하지 않는다. 생성된 10개 파일 모두 실제로 열어 보고 관찰 가능한 사실을 기록한다. 불일치 이미지는 재생성하거나 시나리오 연결을 수정한다. Golden Case는 이미지 작성자 외 검토자가 관찰 사실을 확인한 후 `golden_approved`로 승격한다. 모델 응답의 정확한 문장이 아닌 식별 가능한 사실/제약·참조를 검사한다.

### 5.1 Manifest 계약

`scripts/seed/manifest.json` 루트는 `{manifest_version:"1.0",seed_version:"storeloop-demo-v1",images:[...]}`이다. 각 image 객체는 다음을 포함한다.

| 필드 | 규칙 |
|---|---|
| `image_id` | 안정적 영문 ID, 위 목록과 대응 |
| `path` | scripts/seed 기준 상대 파일 경로; `..`/절대 경로 금지 |
| `sha256`, `mime_type`, `width`, `height`, `byte_size` | 실제 파일로 계산한 메타데이터 |
| `category_code`, `purpose`, `source_kind` | DB 카테고리와 연결; purpose는 위 표 enum, source_kind=ai_generated_demo |
| `generation_prompt` | 실제 생성에 사용한 프롬프트 전체, 비밀/실제 개인정보 없음 |
| `reference_image_id` | 편집 생성의 원본 image_id 또는 null |
| `guideline_rule_keys` | 연결되는 기준 rule_key 배열 |
| `reference_codes`, `submission_codes` | 적재할 안정 DB seed code 배열. Reference 파일은 submission_codes=[] |
| `observed_features` | 검수로 확인한 사실 배열. 생성 의도와 구별 |
| `review_status` | pending/approved/rejected/golden_approved |
| `reviewer`, `reviewed_at`, `review_notes` | 검수 담당 식별자·UTC·불일치/확인 근거 |

같은 sha256을 Reference와 submission 용도 양쪽에 등록할 수 없다. Reference 원본 변경은 새 image_id·hash·ReferencePhoto 버전으로 만들고 과거의 파일을 덮어쓰지 않는다. 비교의 원본 계보를 metadata로 추적하되 데이터가 하나의 이미지라고 오인시키지 않는다.

## 6. UI·매뉴얼·인수 증거

데이터 badge와 실제 분석 badge는 독립이다. “AI 생성 시연 이미지 · 실제 AI 분석” 조합은 유효하며 “Mock 데이터” 리뷰를 실제 AI로 표시하면 실패다. 운영 fixture의 오류·지연은 실제 가용성과 분리한다. 매뉴얼에 시연 계정 login_id, 비밀 파일 열람 위치, 카테고리/사진 선택 순서, 가상 데이터·모델 한계를 포함한다.

적재 완료 증거에는 seed/manifest 버전·파일 hash, DB migration head, 테이블 개수, 중복 없음, 사진 디코딩·보호 미디어 응답, Reference/제출 hash 중복 금지, 4단계 기준·버전, 부모/자식·시도 시간 순서, 역할별 403/404 접근 검사, empty/unknown/failed/mock 표시 결과를 남긴다. 원문 비밀번호/세션·쿠키·민감 로그는 증거에 넣지 않는다.

주요 인수 연결: AT-05/07/08/09/13/14/16/17/18/19/20/21/23/24, AT-S01. 상세 실행 방법과 결과 상태는 [09](09-validation.md)를 따른다.
