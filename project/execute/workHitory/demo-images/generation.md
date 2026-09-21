# generation: 실제 매대 시연 이미지

- 담당: product_design / demo-images
- 상태: REVIEW
- 체크리스트: [generation](../../checkList/demo-images/generation.md)
- 계약: DATA-001 1.0.0 및 G1 ACCEPTED.

## IMG-001 — 생성 전 계획 (2026-09-21)

- imagegen SKILL.md를 읽고 내장 image_gen 도구를 사용한다. CLI/API fallback은 요청되지 않았으며 사용하지 않는다.
- 우선 beverage-reference-01(정돈된 기준 사진)과 beverage-before-01(간격/페이싱 관찰용)을 독립 생성한다. 같은 파일을 용도만 바꿔 복제하지 않는다.
- 다음 beverage-reference-02/after/uncertain과 snack 5장을 생성한다. after는 해당 before를 직접 확인 후 edit target으로 사용하며 선반·카메라 구도·제품 외형을 유지하고 지정 개선만 반영한다.
- 산출물은 도구가 실제 생성한 파일을 scripts/seed/assets/shelves에 원본 복사한다. 각 파일을 view_image로 직접 열고 생성 의도와 실제 관찰을 구분해 manifest에 기록한다.
- manifest의 JSON 필드/ID는 계약 영문 식별자, generation_prompt/observed_features/review_notes는 한국어. source_kind=ai_generated_demo, 자체 검수 approved, 독립 검수 전 golden_approved 금지.
- 검증: 이미지 decode/크기/hash 메타 계산, 10개 존재, reference와 제출 sha256 교집합 없음, 경로 탈출 없음, after 계보 일치. 코드/프론트/Git/DB 적재는 담당하지 않는다.

## 계약 확정 수신

03/04 및 concept01 헤더를 G1 ACCEPTED로 반영한다. 내용·범위·검수 기준은 변경하지 않는다. 근거는 [등록부](../docs/contract-register.md)의 G1 결정이며 실제 구현 인수를 의미하지 않는다.

## IMG-001 — 조기 AI용 2장 생성·검수

- beverage-reference-01.png: 1254×1254, 2,298,206 bytes, SHA-256 a96648449ff2fc1d5266965669cd44ee051539d6db565795e8c2587d0550f986.
- beverage-before-01.png: 1254×1254, 2,304,719 bytes, SHA-256 8e72ae4f11c60a58b8ab0b0fb03e307082945bac56aa44c28d60a7983b61c3b7.
- 도구 원본을 복사하고 두 프로젝트 파일을 각각 view_image로 열었다. Reference의 일정한 앞줄·보이는 라벨과 before 중간 빈공간·앞뒤 불균일을 관찰했다. hash가 다르며 용도 재사용 없음.
- 두 항목의 실제 프롬프트/관찰사실/자체검수 상태 approved를 manifest에 먼저 저장했다. 나머지8개는 아직 생성 중이다. 독립 검수 전 golden_approved 아님.

## IMG-001 — 전체10장 생성·실제 시각 검수 완료

- 생성/편집은 모두 내장 image_gen만 사용했다. 원본PNG를 프로젝트로 복사했으며 다른 도구로 픽셀·밝기·해상도를 수정하지 않았다. Python은 PNG 헤더 차원·바이트수·SHA-256 계산에만 사용했다.
- 음료·스낵 각각 Reference2장, before1장, before를 입력으로 편집한 after1장, uncertain1장. 모든 최종 파일을 각각 view_image로 열어 확인했다.
- 음료 after는 같은 정면 흰 선반·라벨·뒷판을 유지하고 중간 빈 공간 채움과 앞줄 정렬 변화가 보인다. Reference02는 회색 선반 사선 구도다. uncertain은 저조도·수평흔들림·우하단 상자 가림으로 세부 관찰이 제한된다.
- 스낵 before 초안은 라벨 글자가 가려지지 않아 추가 image_gen 편집으로 봉지를 문자 위치로 옮겼다. 최종본에서 상단 글자 윗부분·중간 글자 일부 가림을 확인했다. 초안은 최종manifest에 넣지 않았다. 모든 실제 프롬프트는 최종 항목에 보존했다.
- 스낵 after는 before와 같은 흰 선반 구도에서 노란봉지/갈색상자/파란파우치가 선반별로 분리되고 라벨이 드러난다. 합성편집의 세부 포장·수량 차이는 재고/모델점수 정답으로 사용하지 않는다. uncertain은 흐림·흔들림·앞쪽상자 가림을 확인했다.
- 최종manifest: scripts/seed/manifest.json, manifest_version1.0/seed storeloop-demo-v1. 각 reference_codes/submission_codes는 image_id 안정코드다. Reference01 공통·02 북부매장 전용 연결은 데이터 담당이08에 따라 적재한다.
- 자체검수 approved10개, 독립 golden_approved0개. 모델 결과를 미리 확정하지 않았다.

### 파일 증거

모든 파일은 scripts/seed/assets/shelves/<image_id>.png, image/png, 1254×1254다.

| image_id | bytes | SHA-256 |
|---|---:|---|
| beverage-after-01 | 2,127,066 | `48e58986409fd98419ed59aacced93a4b5f72cbe0df941b640fd1e81c7f38f19` |
| beverage-before-01 | 2,304,719 | `8e72ae4f11c60a58b8ab0b0fb03e307082945bac56aa44c28d60a7983b61c3b7` |
| beverage-reference-01 | 2,298,206 | `a96648449ff2fc1d5266965669cd44ee051539d6db565795e8c2587d0550f986` |
| beverage-reference-02 | 2,139,454 | `c41d47d219ba263ceb30ef04545b4734e10fee65526ac1717a7c4727e0930135` |
| beverage-uncertain-01 | 1,623,460 | `6efa3fb467b33aebd5ecbe5f8fd4dfb0105ec9bc3a97b949aeea021e7f4318af` |
| snack-after-01 | 1,940,888 | `1668005c877d14660c17c2028bf310399e28fe68153637f9bfc62ff7f91246c4` |
| snack-before-01 | 1,979,627 | `7be49d046c4e03d539a59d112d877cc3e76bb17a1e40595c3c43754e26d5d410` |
| snack-reference-01 | 2,143,557 | `2f0bce5ed1645713e53154bd51c8ef3cc134bef752baf7a9b79938d8f9aadece` |
| snack-reference-02 | 2,046,369 | `1920ac33b9a49f343d0d1d6cbec9019e1ffb97eef0a3971006e3da9ad94e5db9` |
| snack-uncertain-01 | 1,434,126 | `0501b44e28fb4ecb92d095f4f7b286a14ad0fcbee29e95890a133a867119246c` |

### 검증 결과

- Python 표준 hashlib/struct/Path로10개 실제 PNG의 signature·차원·hash·byte_size 계산: PASS. 장당 최대2,304,719 bytes로10MiB 제한 이내. 합계20,037,472 bytes.
- 저장 manifest를 다시 읽어 실제 메타데이터와 대조하는 functions JavaScript 검증: PASS. 기대ID10개, Reference4/제출6, hash10개 고유, metadata 일치, 경로탈출 없음, Reference/제출코드 재사용 없음, 두 after 부모계보 일치, 프롬프트/관찰사실/검수정보 모두 존재.
- 실제 이미지 시각검수 완료는 자체검수다. DB 적재/보호미디어 API/실제 AI 판정·브라우저 인수는 본 작업 범위에서 NOT_RUN이며 각 담당자가 수행한다.

### 인계

- root와 contract_ai에 조기2장 경로/hash를 이미 전달했다. 최종10장과 manifest·관찰사실을 전달하고 독립 Golden Case 검수 배정을 요청한다.
- 사진 원본이나 역할 연결을 변경할 때는 새image_id/hash 및 Reference 버전으로 기록하며 본 최종 자산을 무단 덮어쓰지 않는다.
- 현재 상태 REVIEW. 최종 승인/DB 적재 통합은 root가 판정한다.
