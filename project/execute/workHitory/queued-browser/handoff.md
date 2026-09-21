# 5개 시안 장기 대기 UI 검수 인계

상태: 도구 준비 완료, **실제 적용·Browser 검수·worker 재개 후 timeout 확인은 NOT_RUN**. root가 독립 코드 검토 후 적용한다. contract_data는 기존 test DB를 READ ONLY로만 조회했고 기존 기록·서비스·파일·실제 AI를 변경하지 않았다.

## 기존 기록을 재사용하지 않는 이유

원래 `boundary-pending`의 제출은 `1dd78a42-e241-52a9-b718-694b8faa0ea1`, job은 `330bc920-98f9-5bd4-b9ba-3c0e491fede6`이다. 2026-09-21 21:39 KST 읽기 관측에서 이미 `succeeded`, 시도 2개·결과 1개이며 현재 queued job은 0개였다. 이 성공 기록을 대기로 되돌리지 않는다. [메타데이터](existing-metadata.json)에 본문·비밀 없이 보존했다.

## 추가할 합성 fixture

- 제출: `2f9b333f-8a43-5df0-841d-f1c66b213ab3`
- job: `0d50701f-c61b-5c48-80ea-1df7ca4d2cb4`
- 계정: `owner.north`. 비밀번호는 기존 `.local/demo-credentials`에서 담당자가 확인하며 이 기록에 복사하지 않는다.
- 매장/카테고리: 현재 연결된 봄빛역점 / 음료.
- 사진: 기존 AI 생성 시드 `beverage-uncertain-01`. 원본 파일 SHA-256과 DB 메타데이터를 대조하며 새 사진 파일을 만들지 않는다.
- `Submission.source_kind=seed_demo`, `AnalysisJob.is_fixture=true`. 질문 첫머리에 **[Mock 장기 대기 UI 검수]**를 표시하고 실제 제출/AI 결과가 아님을 명시한다. 5개 상세 화면 모두 질문을 표시하는 소스를 확인했다. 화면 상단 별도 Mock 배지 노출은 UI 실제 검수에서 확인할 사항이다.
- 새 Submission/SubmissionPhoto/AnalysisContext/AnalysisJob/AuditEvent 총 5행만 추가한다. 결과/시도/이슈/알림은 만들지 않는다. 감사 사유도 합성 UI 검수임을 명시한다.
- 제출·job 생성·대기 시각은 실행 시점 10분 전, queue deadline은 실행 시점 7분 전이다. `delayed=true`가 즉시 보이고, worker 재개 시 만료 처리 대상이다. 합성 시각이라는 점을 성능 측정/실제 AI 인수와 구분한다.
- 현재 기준에서 10분 전까지 존재한 버전을 `historical_versions`로 선택하고 미래 Reference를 제외한다. snapshot hash를 저장한다.

## root 실행 순서

프로젝트 루트 `hack2026/project`에서 실행한다. 기존 Browser QA용 API/AI/Vite는 유지한다. **전체 `stop.sh`를 사용하지 말고 root가 관리하는 해당 worker만 종료 요청한 뒤 프로세스 종료까지 확인한다.** 처리 중 작업이 있다면 먼저 종료를 기다린다. 이 도구는 worker를 정지시키지 않는다.

1. 사전 읽기 계획을 확인한다.

```sh
server/.venv/bin/python execute/workHitory/queued-browser/prepare_fixture.py
```

2. root가 worker 종료를 확인한 뒤 명시 적용한다.

```sh
server/.venv/bin/python execute/workHitory/queued-browser/prepare_fixture.py --apply --worker-stopped
```

안전장치: 로컬 55432의 `storeloop_test`만 허용, 연결 문자열 query 거부, public schema 고정, `--worker-stopped` 명시, 실제 프로세스 argv의 production/browser 두 worker 진입점 탐색, INSERT 직전 재확인, 다른 queued/running job이 있으면 거부, PostgreSQL 트랜잭션·advisory lock, 기존 행 UPDATE/DELETE/DDL 거부. 기존 fixture ID 묶음이 있으면 무결성을 확인하고 보존한다. 일부 ID만 있거나 변경됐으면 fail-closed한다. 오류 원문/DB URL/본문/비밀번호를 출력하지 않는다.

3. `owner.north`로 동일 제출을 5개 시안에서 확인한다.

| 시안 | URL |
| --- | --- |
| 01 | http://127.0.0.1:5173/store-owner/submissions/2f9b333f-8a43-5df0-841d-f1c66b213ab3 |
| 02 | http://127.0.0.1:5174/store-owner/submissions/2f9b333f-8a43-5df0-841d-f1c66b213ab3 |
| 03 | http://127.0.0.1:5175/store-owner/submissions/2f9b333f-8a43-5df0-841d-f1c66b213ab3 |
| 04 | http://127.0.0.1:5176/store-owner/submissions/2f9b333f-8a43-5df0-841d-f1c66b213ab3 |
| 05 | http://127.0.0.1:5177/store-owner/submissions/2f9b333f-8a43-5df0-841d-f1c66b213ab3 |

대기/30초 초과 안내, 이력 이동 후 돌아오기, 새로고침, 재조회와 결과 없음 표시를 검수한다. 이 기록을 정상 첫 제출→결과 지연 측정에 포함하지 않는다. 실제로 10분 기다렸다는 근거로도 사용하지 않는다.

## 이후 정리

삭제나 상태 초기화를 하지 않고 합성 검수 이력으로 보존한다. root가 기존과 동일한 test DB 설정으로 worker를 재개한다. 기존 전용 실행 방법은 별도 터미널의 아래 명령이다(이미 worker가 있으면 중복 실행하지 않는다).

```sh
server/.venv/bin/python scripts/browser_test_runtime.py worker
```

worker는 heartbeat → `sweep_expired` → `claim_next_job` 순서로 처리한다. 이 fixture는 이미 만료됐으므로 `failed / QUEUE_TIMEOUT`, 최초 `expired` 시도 1개, `started_at=null`, `result_applied=false`, 결과 0개가 예상된다. `claim_next_job` 자체도 미래 deadline만 점유하므로 이 fixture로 새 AI를 호출하지 않는다. **운영자 재처리 버튼을 누르면 실제 AI 분석이 실행될 수 있으므로 이 검수의 정리 방법으로 사용하지 않는다.** 다른 대기 작업이 새로 만들어졌다면 worker 재개 시 그 작업은 정상 처리될 수 있으며 본 도구의 무호출 보장은 이 fixture에 한정한다.

## 검증 근거

- `test_prepare_fixture.py`: 미구현 모듈 수집 실패를 초기 RED로 기록한 뒤 안전 경계 7개 PASS(기능 동작 RED와 구분). 전용 DB 제한, worker 두 진입점 검출, 만료된 Mock 추가 계획, hash/시각/관계, 기존 성공 보존, 부분 충돌, SQL 수정·삭제/DDL 거부, 적용 명시 요구를 DB 연결 없이 검증했다.
- 실제 PostgreSQL 기본 dry-run: `read_only=true`, `other_active_job_count=0`, `insert_count=0`, `planned_insert_count=5`, `status=ready`. [결과](dry-run.json).
- 실제 INSERT/commit 및 재실행 0행, worker 재개 후 timeout, 실제 Browser는 root 후속 검증이다. 본 준비 단계에서 PASS로 표시하지 않는다.
