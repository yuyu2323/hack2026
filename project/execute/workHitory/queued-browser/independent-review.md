# worker 복원 후 합성 대기 fixture 독립 확인

판정: **PASS — READ ONLY 25항목**. [메타데이터 근거](independent-metadata.json)와 [재실행 probe](independent-probe.py)를 보존했다. root가 수행한 5개 시안 Browser 검수 및 API/worker 중지·복원 이후의 DB 저장 상태 확인이다. 본인은 이번 검수에서 API·AI·Browser·서비스·DB 쓰기를 수행하지 않았다.

## 새 fixture

| 항목 | 읽기 결과 |
| --- | --- |
| submission | `2f9b333f-8a43-5df0-841d-f1c66b213ab3` |
| job | `0d50701f-c61b-5c48-80ea-1df7ca4d2cb4` |
| 상태 | failed / QUEUE_TIMEOUT / is_fixture=true / enqueue_generation=1 |
| 출처 | seed_demo, 질문에 Mock 장기 대기 UI 검수 표시 |
| 합성 대기 시작 | 2026-09-21 21:51:54.764852 KST |
| 대기 기한 | 21:54:54.764852 KST |
| 실제 종료 저장 | 22:13:05.343422 KST |
| 시도 | 최초 1개, `34bfc307-d4cb-4ae8-9097-042326355a5c`, expired / QUEUE_TIMEOUT |
| 시작·점유 | started_at / worker_id / deadline_at / lease_expires_at / heartbeat_at 모두 null |
| 결과 | result_applied=false, ReviewResult 0개 |

snapshot SHA-256은 `7a09aa3f289e307a825a20921522ed3d030004c01e7a5289e9efc4d0cf7ee7e8`이며, **저장 본문·root 실제 apply 기록·생성 감사 after_data 모두 일치**한다. 사진 1개·기준 5개·Reference 3개 입력 메타데이터는 그대로 보존됐다. 생성 감사도 해당 job·seed_demo·is_fixture=true를 유지한다.

queue 기한 이후 `sweep_expired`가 최초 시도 1개를 expired로 남긴 상태와 일치한다. 시도 시작·worker 점유·lease·heartbeat가 없고 결과도 없으므로 실제 AI 처리로 넘어간 흔적이 없다. 모델 서버 로그에서 요청 개수를 직접 세지는 않았으며, 모델 로그 검수까지 수행했다고 주장하지 않는다. 합성으로 10분 이전 시각을 넣은 UI fixture이므로 이 대기 시간을 실제 제출 성능이나 실제로 기다린 시간으로 사용하지 않는다.

## 기존 기록 보존 범위

사전 파일의 snapshot/result hash를 기준으로 기존 실제 AI 기록 **15개**를 다시 조회했다.

- 시안 01/02/04/05 총 12건: snapshot hash 및 result hash 모두 일치, succeeded·real_ai 유지.
- 시안 03의 3건: 사전 root export에 result hash가 없어 snapshot hash와 succeeded·real_ai 상태만 비교했다. 결과 본문의 과거 hash 불변까지 증명한 것으로 쓰지 않는다.
- 위 15건에 포함된 원래 `boundary-pending` 제출 `1dd78a42-e241-52a9-b718-694b8faa0ea1` / job `330bc920-98f9-5bd4-b9ba-3c0e491fede6`은 별도 사전 `existing-metadata.json`과도 대조했다. **succeeded·시도 2개·결과 1개·오류 없음·snapshot hash 그대로**다. 기존 성공 기록을 대기로 되돌리거나 삭제하지 않았다.

비교 근거 파일별 SHA-256과 개별 submission ID는 JSON에 남겼다. 이 표본 이외의 DB 전체가 한 바이트도 바뀌지 않았다는 전수 증명은 아니다. 새로운 fixture의 추가와 worker 만료 상태 변경은 예정된 별도 이력이다.

## 검수 경계

PostgreSQL 연결 기본 read-only와 트랜잭션 READ ONLY를 함께 적용하고 `SHOW transaction_read_only=on`을 확인했다. ORM 추가/변경/삭제 대기 객체도 없다. 원문·비밀·사진은 새 근거에 남기지 않았다. 생성 도구는 본인이 작성했으므로 이 결과는 실제 복원 사건의 메타데이터 대조이며 도구 구현 자체에 대한 독립 소스 리뷰를 대신하지 않는다. 생성 도구의 독립 검토·실제 적용과 Browser 조작은 root의 별도 기록이다.

200% 확대와 UI 재실행은 이번 범위 밖이다. root의 `browser.md`, `queued-initial.json`, `api-outage.json`, `api-recovery.json`, `worker-restored.json`을 수정하지 않았다.
