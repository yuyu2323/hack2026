# QA01 운영 이력·재처리 독립 메타데이터 검증

판정: **PASS — 22개 검사**. 2026-09-21 21:51 KST에 root의 최종 복원 완료 메시지 후 PostgreSQL `storeloop_test`를 `REPEATABLE READ` + `SET TRANSACTION READ ONLY`로 조회했다. [최종 근거 JSON](independent-operations-metadata-20260921T125136Z.json)에 식별자·개수·hash·상태·시각만 남겼다. 계정 변경 전 별도 재처리 15개 PASS 근거도 [보존](independent-operations-metadata-20260921T125118Z.json)했다.

## 계정·연결 변경

계정 `988e8b9b-8ec4-45b3-afff-9937b45ac7c9`는 최종 **v9 / 활성 점주 / region null / 활성 owner 연결 0 / 활성 OFC 연결 0**이다. 최초 요청의 v7에서 추가 UI 회귀 후 v8 OFC→v9 점주 복원이 실제 감사 이력과 일치한다.

- 은행길점 owner 연결 `c5ed234d-7de2-40ff-af9c-99a6ead039a9`: v2 연결, v5 종료. `accounts.mappings`의 before 매장 포함→after 빈 목록 및 `ended_mapping_ids`가 실제 종료 행과 일치한다.
- 푸른언덕점 최초 OFC 연결 `caffefaf-5fe3-462c-92de-e4edc2f86606`: v6 북부 OFC에서 본인 claim, v7 점주 복원 때 종료. 감사 전/후 역할과 종료 ID 일치.
- 같은 매장의 추가 회귀 OFC 연결 `e87e8409-6809-4ad3-bdf3-844f930b61ab`: v8 북부 OFC에서 본인 claim, v9 점주·region null 복원 때 종료. 감사 전/후 매장 포함→빈 목록 및 종료 ID 일치.
- 계정 감사 v1~v9가 연속이며 성공 상태·사유·request ID가 존재한다. 두 claim 감사는 미담당 상태에서 해당 계정으로 바뀌고, 각 실제 연결 생성 및 종료 시각과 일치한다.

## 재처리

| 항목 | 확인 값 |
| --- | --- |
| job | `c5d22c4e-7a26-5961-a04f-79ba8e12e745` |
| submission | `e3488415-6745-56a8-be69-7d3010521033` |
| review | `4b9a1331-abc5-4e17-9c12-350123e6c09d` |
| 실패 시도 1 | `b432cd96-a1ec-5284-b42a-51b2e9180157`, failed / AI_UNAVAILABLE / 결과 미반영 |
| 성공 시도 2 | `6f336626-ae76-446a-84a7-024f8908ac5c`, succeeded / 결과 반영 |
| 입력·출력 개수 | 사진 1, 기준 4, Reference 1 / 결과 기준 4, 비교 1 |
| 출처 | submission seed_demo, job is_fixture=true, 새 결과 real_ai |
| 모델·계약 | gpt-6-astra / storeloop-review-v1 / schema 1.0 |

최초 실패는 원래 시드의 UUID와 대기 2026-09-09 09:00:00 KST·시작 09:00:01·종료 09:00:12까지 일치한다. 기존 실패를 덮어쓰지 않았고 성공 시도 2만 현재 job·review에 연결돼 있다. 재처리 감사는 실패 시도 1→queued 시도 2를 기록한다. 이 첫 실패는 합성 과거 fixture이며 이번 검수에서 실제 장애를 유발한 증거로 취급하지 않는다.

엄격한 `AnalysisInput`에 실제 worker와 동일하게 내부 `media_id`를 제외한 사진 메타데이터를 투영해 검증했다. 저장 결과를 `validate_result`로 재검증하여 모든 기준 ID/version/rule_key와 Reference ID 대응을 확인했다. 사진 연결·미디어 hash, 정규화된 기준 평가 행·근거/조치, 파생 지표도 저장 결과와 일치한다. 준수율 25.0%, 판단 가능률 100.0%, pass 1/fail 3/unknown 0이다.

- snapshot SHA-256: `3e438fda1ea1a520e1ad65be3cc516c1af0723b5e54d1558eb3af819ea62059c`
- result SHA-256: `54a58b67fdc40edeea729f1a54794ee6894262ba0f9929b2283961f2bf5d305b`

snapshot은 저장 본문과 hash가 일치함을 확인했다. 본 검수 이전의 별도 snapshot 기준 파일과 변경 전후 비교를 한 것은 아니며, 저장 무결성 확인과 불변성의 과거 비교 증명을 구분한다.

## 시간과 범위

대기 **1,696ms**, worker 처리 **45,191ms**, AI adapter 구간 **44,971ms**다. worker 구간이 220ms 길어 포함 구간 순서가 일관된다. adapter 값은 사진 준비·CLI 실행·출력 검증을 포함한 monotonic 구간이며 순수 추론 시간과 같지 않다. worker 시각은 UTC wall-clock이다. 이번 데이터에 역전은 없지만 서로 다른 시계라는 제한은 유지한다. **30초 목표는 미달**이며, 과거 fixture이므로 최초 제출부터 결과까지의 정상 신규 제출 시간 통계에서 제외한다.

이번 PASS는 지정 메타데이터 검증이다. root가 보고한 실제 UI 성공 표시·재처리 폼 제거·F01 목록 갱신 경쟁 수정은 본인이 Browser로 재실행하지 않았다. 새로운 실제 AI 호출, HTTP 세션 생성, 서비스 중지, 업무 DB 변경, 원문/비밀/사진 출력은 없다. 다른 담당의 `independent-*`와 root `actual-ai.json`은 수정하지 않았다. 원시 HTTP AI 응답 envelope는 별도 보관되지 않으므로 저장 모델/프롬프트/스키마/latency 및 코드의 수용 검증과 구분한다.
