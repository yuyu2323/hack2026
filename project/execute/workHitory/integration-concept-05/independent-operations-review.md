# 시안05 운영 변경·재처리 독립 메타데이터 검수

- 판정: **기능·이력15개 PASS / 시간 관계 이상 확인, 원인 미확정**. 단일 전체 PASS로 합치지 않는다.
- 증거: [READ ONLY 메타데이터](independent-operations-metadata.json), [검사 코드](independent-operations-probe.py). 재현 명령은 프로젝트 루트에서 `server/.venv/bin/python execute/workHitory/integration-concept-05/independent-operations-probe.py`다.
- 계정·카테고리·재처리·첫/child를 SELECT만으로 대조했다. 실제 AI/HTTP 세션/업무 쓰기/서비스 변경은 없다.

## 계정·담당 연결 감사

계정 `b979fd3d-661c-45eb-8c4d-f3c1dd155aa9`는 현재v8, 활성 store_owner, region_id=null이다. 과거 점주 연결1개와 OFC 연결1개는 모두 종료되어 현재 연결0개다.

- v6 `accounts.update`: 점주→OFC, 남부 region 지정. 당시 연결 없음.
- `stores.claim`: 계정 자신이 새봄로점 `ae43dd9f-2dfa-5bc0-8e1e-ce1106c5d01d`를 담당 등록. 해당 사건은 v6와v7 감사 사이에 있다.
- v7 `accounts.update`: OFC→점주. `ended_mapping_ids`는 OFC 연결 `1b0354d0-2023-47d9-b366-de87f29a0672` 하나이며 DB 종료 시각과 일치한다. 점주로 자동 연결되지 않는다.
- v8 `accounts.update`: 점주·활성을 유지하고 region_id를null로 변경, 종료할 추가 연결 없음.

각 감사의 actor/target/time/outcome·request_id와 사유 존재를 확인했다. 감사 사유나 사용자 표시명 원문은 증거에 저장하지 않았다.

## 카테고리

`qa05_test_category`는 ID `b14e0298-9fb3-4fc5-bba7-d80a13e3786c`, 현재v2·비활성이다. `categories.create` v1 활성과 `categories.update` v2의 이름 변경·비활성 감사가 남아 있다. 현재 이름의 검증완료 표시를 확인했고 코드는 유지됐다.

## 실제 재처리와 과거 보존

job `aa73ad7e-9d08-5a5b-b035-96941a217621`는 submission `96165c7c-53c9-5ded-9f99-f9ee67ec2c86`, review `29c615ba-5396-4f31-9d70-12a4b203c973`에 연결된다.

- 시도1: 과거 Mock 장애 시드의 `failed / AI_UNAVAILABLE / result_applied=false`, 대기1,000ms·실행11,000ms를 보존했다. 이11초를 이번 실제 장애 실험의 실측으로 보고하지 않는다.
- 시도2: `succeeded / error_code=null / result_applied=true`. current_attempt와 review가 모두 시도2를 가리키고 성공 결과는1개다. review는 real_ai, job은 is_fixture=true를 유지한다.
- snapshot canonical hash, 결과 schema/기준/Reference/사진 참조 및 저장 집계가 일치한다.
- 첫 실제 제출과 child의 snapshot/result SHA-256도 이전 독립 baseline과 모두 동일하다. 운영 변경과 재처리가 두 평가를 바꾸지 않았다.

## 시간 관계 이상 — 값을 정정하지 않음

| 값 | 실제 저장·재계산 |
|---|---:|
| 시도2 queued_at | 2026-09-21 21:14:56.443952 +09:00 |
| 시도2 started_at | 2026-09-21 21:14:56.963490 +09:00 |
| 시도2 finished_at | 2026-09-21 21:15:45.749933 +09:00 |
| 대기시간 | 520ms |
| UTC 시각 차 기반 시도 실행시간 | 48,786ms |
| AI adapter monotonic 기반 duration_ms | 50,635ms |
| 실행시간−AI시간 | **−1,849ms** |

exporter의 계산 실수나 표시 반올림 문제가 아니다. 원본 타임스탬프 차와 export의48,786ms가 일치한다. AI adapter는 요청마다 `time.monotonic()`으로 이미지 임시파일 생성 직전부터 CLI 종료·결과 검증까지 측정한다. 순수 모델 추론만의 시간이 아니며 finally 정리·HTTP 반환은 제외된다. worker 시작은 `utcnow()`, 성공 종료는 `complete_attempt` 진입 후 검증/commit 전의 `utcnow()`다. 두 시각 모두 Python `datetime.now(timezone.utc)` 기반이다.

작성자 contract_ai도 [시간 계산 경로 읽기 검토](../local-ai/timing-read-review.md)에서 생산 worker의 now 주입·기간 캐시가 없고 응답 job/attempt/submission ID가 일치 검증된다는 점을 확인했다. 안정된 시계라면 worker 구간이 그 안의 AI adapter 구간보다 길어야 하므로 위1.849초 역전은 계측 구간 차이만으로 설명되지 않는다.

분류는 `CLOCK_BASIS_ANOMALY_UNRESOLVED`다. 벽시계 조정은 가능한 원인이지만 당시 벽시계와 monotonic 동시 표본 또는 시스템 시계 변경 증거가 없으므로 NTP/시계 보정으로 확정하지 않는다. 원시 시간값·완료 데이터는 수정하지 않았다. 모델과 실행시간을 같은 시계의 포함 구간으로 합산·대소 비교하는 성능 근거로 쓰지 않는다.

이 건은 이미 과거 fixture 재처리이므로 원래 제출일부터의994,545,750ms를 정상 신규 제출→결과 지연에 포함하지 않는다. 실제 재처리의 모델50,635ms 자체는30초를 넘었다. 첫 제출/child의 정상 신규 표본과 별도 표시하며 기능 성공과 계측 제약을 함께 인계한다. 새 monotonic worker 측정이나 모델 재호출은 이번 읽기 검수 범위에서 수행하지 않았다.

검사 코드와 JSON Gitleaks PASS. 본문·비밀번호·토큰·사진 바이트를 저장하지 않았으며 타 담당 문서·원본 실제AI export·공유 데이터·프로세스는 변경하지 않았다.
