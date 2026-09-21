# 시안04 저장 이력·권한 실제 HTTP 독립 보조 검증

- 상태: PASS. 검토자 contract_data. root가 실행한 E01/E02/E03/E05의 저장 메타데이터와 별도 실제 HTTP 권한 검증이다. 브라우저 E04 및 전체 시안 인수의 대체 결과가 아니다.
- 재현: 프로젝트 루트에서 `server/.venv/bin/python execute/workHitory/integration-concept-04/independent-probe.py`. DB와 시안04 Vite가 실행되어 있어야 하며, 명시 배정된 검사 세션만 생성·폐기한다.
- 결과: 정정 재검증한 [메타데이터·HTTP 증거](independent-metadata-http.json)의 확인67개 모두 PASS, 실제 GET16개 모두 기대 상태와 일치. [검사 코드](independent-probe.py)에는 비밀 기본값이 없다.

## 미디어 대상 오류 정정

최초64개/14개 보고는 북부 사진 경로에 snapshot의 `photo_id`(SubmissionPhoto 연결 ID)를 사용했다. 보호 미디어 URL은 `media_id`(MediaAsset ID)를 요구하므로 당시 지역 관리자404는 존재하지 않는 경로 응답이었고, **그 미디어 범위 검증은 무효**다. DB·상세·Reference hash 관찰과 구분하여 [기존 기록](independent-metadata-http-incorrect-media-target.json)을 `PARTIALLY_INVALIDATED`로 보존했다. root가 independent-* 재개를 승인한 뒤 검사 도구와 기록을 정정했다.

최신 검사는 실제 `media_id=2e2c314d-0a13-404d-8627-5ecff861ebcc`의 DB 존재와 snapshot 원본 hash를 확인한다. 같은 ID에서 북부 점주 원본200(image/png·hash일치), 썸네일200(image/jpeg)을 정상 대조하고, 운영자 두 경로403·남부 지역 두 경로404를 확인했다. 따라서 아래 최신 미디어 판정은 존재하는 보호 사진의 정상·거부 응답을 함께 검증한 결과다. 제품 결함 수정이나 업무 데이터 변경은 없었다.

## 저장된 실제 분석

DB 연결의 `default_transaction_read_only=on`과 트랜잭션의 `SET TRANSACTION READ ONLY`를 함께 설정하고 `SHOW transaction_read_only=on`을 확인했다. 공유 테스트 DB에는 SELECT만 실행했다. 질문·기준 본문·사진 바이트·AI 서술 응답은 증거에 저장하지 않았다.

| 대상 | 제출 ID | 사진/기준/Reference 수 | 판정 |
|---|---|---|---|
| 첫 제출 | e447d4e9-54c0-4c85-a0d6-20597b92d0ba | 1 / 5 / 3 | succeeded·real_ai·1번 성공 적용 |
| child | 80d35004-ef2b-4d18-8618-f2199b6878a2 | 1 / 5 / 3 | succeeded·real_ai·1번 성공 적용 |
| 재처리 | a24ff9dd-8389-5d8b-9234-0d4cfa98e9d8 | 1 / 4 / 1 | succeeded·real_ai·2번 성공 적용 |

재처리 job `667d69ab-2eca-565b-b5d7-7b2736b2b57c`는 위 재처리 제출에 연결된다. 1번 시도 `31657b64-1e9e-5281-86ca-dd60956812c8`은 `failed / AI_UNAVAILABLE / result_applied=false`로 보존돼 있다. 2번 시도 `7c2d9f2a-65b2-45e8-9eaf-f4f02774d50a`는 `succeeded / error_code=null / result_applied=true`이며, job의 current_attempt와 review의 attempt가 모두 이를 가리킨다. 새 실제 AI 요청은 보내지 않았다.

세 snapshot의 canonical SHA-256을 재계산해 DB 저장 hash와 대조했고, 첫 제출·child는 root가 이미 기록한 `actual-ai.json`의 hash와도 일치했다. 결과는 JSON 계약·기준ID/버전·사진 번호·Reference ID 참조 검증을 통과했으며 저장 집계와 재계산 집계가 일치한다. 최초·현재 AI 서술 본문을 과거 원문과 대조했다는 주장은 하지 않는다. 이번 result SHA-256은 독립 관찰 시점의 기록이다.

## 기준·Reference·parent 보존

- `qa04_labels`는 첫 제출의 CATEGORY v1, child의 같은 guideline CATEGORY v2로 연결된다. 두 snapshot 모두 같은 키의 HQ/REGION/STORE/CATEGORY 후보4개 중 CATEGORY만 선택됐다. 각 버전은 제출 이전에 생성됐고 저장된 immutable 버전 본문과 일치한다.
- child의 parent ID는 첫 제출이다. child snapshot의 previous_review는 첫 review ID 및 criteria와 정확히 일치한다. HTTP comparison에서도 `qa04_labels`는 `criterion_changed=true / change=unavailable`이다.
- Reference lineage `457b506e-2f2d-47b9-8186-73546e7cea3d`는 v1→v2로 교체됐다. 현재 v1은 비활성, v2는 활성이다. 각 snapshot의 photo ID/hash는 해당 DB 미디어와 일치한다.
- v1 원본 SHA-256: `8458f5510458ede7ef6e2173e5584a182a77dea321f3e9d83eb96e35a1954c8f`.
- v2 원본 SHA-256: `15708f4baec41748dc579a017cd2479b044f2a45efc88ee9578b69dd744b63fa`.
- 북부 점주 새 HTTP 세션에서 과거 v1과 현재 v2의 보호 원본을 각각200으로 읽고 응답 바이트 hash까지 snapshot과 대조했다. 사진 바이트는 메모리에서 검사 후 폐기했고 파일로 저장하지 않았다.

## Vite5176 경유 실제 HTTP 권한

| 검사 세션 | 대상 | 실제 상태 |
|---|---|---|
| operator.demo | 첫 제출 상세·제출 원본·썸네일·notifications | 각각403 |
| owner.north | 첫 제출·child 상세, 제출 원본·썸네일, 두 Reference 원본, child 비교 | 각각200 |
| owner.north | 현재 담당 밖 남부 제출 상세 | 404 |
| regional.south | 남부 제출 상세 정상 대조 | 200 |
| regional.south | 첫 북부 제출 상세·원본·썸네일 | 각각404 |

403/404는 오류 envelope와 기대 코드만 반환하고 영업 본문이 없음을 확인했다. 남부 합성 제출 사진은 동일 MediaAsset이 북부 제출에도 연결된 자료다. 따라서 그 사진을 북부 점주의 범위 밖 미디어로 간주하는 검사는 수행하지 않았다. 북부 점주의 범위 밖 **상세** 차단과 남부 지역 관리자의 북부 **상세·미디어** 차단을 구분해 보고한다.

각 계정은 브라우저 쿠키를 가져오지 않고 새로운 httpx client에서 CSRF200→login200→검사→logout204를 완료했다. 정정 재검증의 새 세션3개도 모두 logout204를 확인했다. 기존 로그인·매핑·계정 상태는 변경하지 않았으며 새로운 검사 세션만 폐기했다. HTTP_PROXY 환경을 사용하지 않는 `trust_env=False`로 Vite에 연결했다. 실제 브라우저 직접 API 탐색을 수행한 결과로 보고하지 않는다.

## 보존과 제한

- 원본 snapshot/result/시도·업무 데이터·공유 미디어·현재 서버/worker/설정은 수정하지 않았다. 직접 DB 쓰기는 READ ONLY로 차단했다. HTTP의 유일한 상태 변경은 검사 세션의 CSRF/login/logout이다.
- 기존 root의 browser.md/actual-ai.json은 읽기만 했고 증거는 independent-*에만 작성했다.
- 저장 JSON과 검사 코드를 Gitleaks stdin으로 검사하여 모두 PASS했다. 자격값·cookie·CSRF·Authorization 및 업무 본문은 출력·저장하지 않았다.
- 실제 지연, 시각적 근거의 타당성, UI의 오류 상태·반응형·접근성, 세션 중 권한 변경을 실제 브라우저에서 조작하는 E04 전체 인수는 이 검사 범위가 아니다. root의 시안별 브라우저 기록과 독립 디자인 검수에서 별도로 판정한다.
