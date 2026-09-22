# 07. AI 입력·평가·처리 계약

- 버전: AI-001 / 1.0.0 / 2026-09-21 / G1 ACCEPTED (contract-register 확정)
- 기준: [00](00-vision.md), [01](01-architecture.md), [02](02-development-orchestration.md).
- 연동: [DB](05-database.md), [API](06-api.md), [데이터](08-data.md), [검증](09-validation.md), [실행](10-execution.md).
- 소유자: local-ai. DB 모델·마이그레이션 소유자는 db-schema이며 이 문서는 구현 완료 증거가 아니다.

## 1. 경계와 고정 결정

브라우저는 업무 API만 호출한다. 업무 API는 제출·사진·적용 기준을 저장하고 작업을 접수한다. 독립 worker가 PostgreSQL에서 작업을 점유하고 `127.0.0.1:8010`의 AI 서버를 내부 토큰으로 호출한다. AI 서버는 DB나 독자 대기열 없이 한 요청의 실제 제출 사진·질문·기준·Reference 사진을 Codex CLI로 분석한다. Codex 프로세스와 HTTP 서버가 로컬이며 모델 서비스는 인증·네트워크가 필요하다.

`unknown`은 관찰 근거 부족에 대한 **성공한 분석**이다. 기술 실패를 unknown이나 시드 답변으로 바꾸지 않는다. 기준 문장·사진 속 문자·질문·Reference 캡션은 신뢰하지 않는 데이터다. 도구 실행이나 지시 변경 요청으로 해석하지 않는다.

원문 모델 출력에 점수·작업 ID를 생성하도록 맡기지 않는다. 검증된 기준별 판정에서 서버가 점수를 계산하고 신뢰된 호출 metadata의 job/attempt/submission ID를 응답에 붙인다.

## 2. 내부 HTTP와 입력

| 경로 | 요청 / 응답 |
|---|---|
| `GET /health` | loopback 내부 전용. 프로세스 가용성·CLI 설치 여부·마지막 성공/실패 시각만 반환. 모델 요청을 실행하지 않음 |
| `POST /internal/analyze` | `Authorization: Bearer <내부 토큰>`과 multipart. 동시 실행 기본 1건. 빈 슬롯 없으면 `409 AI_BUSY`, 내부 대기열 생성 금지 |

multipart part는 `metadata`(UTF-8 JSON 문자열) 1개, `photos`(반복되는 제출 파일), `references`(반복되는 Reference 파일)다. 각 배열의 position 순서와 파일 순서를 맞춘다. 경로나 URL은 입력으로 받지 않는다. 내부 인증 실패는 401, 잘못된 metadata/개수·제약은 422, 총 본문 초과는 413이다. 내부 오류 응답은 `{error:{code,message,request_id}}`이며 안전한 고정 message만 반환한다.

`metadata`의 모든 객체는 알 수 없는 필드를 거절하며 다음 필드만 허용한다.

| 필드 | 타입·검증 |
|---|---|
| `schema_version` | 리터럴 `1.0` |
| `job_id`, `attempt_id`, `submission_id` | UUID 문자열, 실제 DB 관계는 worker에서 검증 |
| `question` | 문자열, 0~2,000자. 비어 있으면 전체 점검 요약으로 답함 |
| `guidelines` | 아래 유효 기준 배열. 본문 합계 30,000자, 최대 100개 |
| `photos` | 1~5개 `{photo_id,position,mime_type,sha256}`. photo_id=SubmissionPhoto.id, position=1부터 연속·고유, sha256=소문자 64자리 |
| `references` | 0~3개 `{reference_id,photo_id,position,caption,mime_type,sha256}`. photo_id=MediaAsset.id, position은 Reference끼리 1부터 연속·고유, caption 최대 2,000자 |
| `previous_review` | null 또는 `{submission_id,review_id,criteria}`. 부모 제출의 검증된 criteria만 전달하며 현재 매장·카테고리가 동일해야 함 |

`guidelines[]`는 `{guideline_id,version_id,version,level,rule_key,text}`다. UUID ID, version 양의 정수, level=`HQ|REGION|STORE|CATEGORY`, rule_key 1~80자, text 1~10,000자다. `previous_review.criteria`는 §4의 criterion 구조를 사용한다. 부모 결과가 없으면 null이며 현재 결과의 이전/이후 수치를 추측하지 않는다.

### 2.1 이미지 검증·스냅샷

- JPEG/PNG만 허용하며 파일 확장자·신고 MIME·실제 디코딩 포맷을 일치시킨다. 장당 10MiB, 제출+Reference 최대 8장/80MiB, metadata와 multipart 오버헤드를 포함한 전체 요청 최대 82MiB.
- Pillow로 완전히 디코딩하고 width/height 각각 32~8,192, 총 40,000,000 pixel 이하로 제한한다. 손상 이미지·압축 폭탄·동영상·SVG·경로 대체 입력을 거절한다. EXIF 방향을 정규화하고 위치 등 불필요한 메타데이터를 제거한 저장본을 분석한다. `sha256`은 **분석에 전달하는 저장본** 바이트 기준이다.
- 요청마다 worker와 AI 서비스 양쪽이 파일 개수·순서·hash·mime를 검증한다. 임시 이름은 서버가 생성한다. 사용자 파일명을 경로로 사용하지 않는다.
- 업무 API가 제출을 접수할 때 GuidelineVersion ID·본문과 Reference ID·캡션·원본 미디어 ID/hash를 AnalysisContext에 고정한다. 이후 변경·비활성화나 장애 재처리는 스냅샷을 다시 계산하지 않는다.
- DB/API 담당과 합의한 `rule_key`가 같은 후보는 `CATEGORY > STORE > REGION > HQ` 순으로 하나만 적용한다. 같은 레벨·동일 적용 범위·rule_key는 DB 고유 제약으로 중복 생성 금지. 모든 후보와 제외 근거는 snapshot에 보존하고 AI에는 effective_guidelines만 전달한다. CATEGORY 동순위는 매장 전용 > 전사 공통, 나머지 동순위는 category 지정 > 공통 순이며 최종 기준은 rule_key 순서다. 다른 rule_key 사이 의미상 충돌은 자동 해결하지 않고 limitations/OFC 검토로 남긴다.
- Reference는 해당 카테고리의 해당 매장 전용 우선, 전사 공통 다음. 다른 매장 전용 자료는 제외. 동일 계보 최신 활성 버전만 선택하고 `(store 우선, created_at 내림차순, id 오름차순)`으로 최대 3장 고정한다.
- 기준 또는 Reference가 0개인 입력도 분석 가능하다. 기준 0개면 criteria=[], Reference 0개면 reference_comparisons=[]이며 누락 사실을 limitations에 넣고 OFC 검토 대상으로 만든다.

## 3. Codex 어댑터

2026-09-21 로컬 읽기 조사 결과 `/opt/homebrew/bin/codex`, `codex-cli 0.154.0`, ChatGPT 로그인 상태다. CLI 도움말에서 이미지 첨부·스키마·최종 응답 파일·임시 세션·사용자 config 미사용 옵션을 확인했다. 인증 원문은 읽지 않았다. 실제 이미지+모델 성공과 사용 가능한 모델은 G2 조기 검증으로 확인한다.

새 temporary directory(권한 0700)에 `submission-01.png` … `reference-01.png`, `schema.json`, 결과 파일을 두며 0600으로 생성한다. shell=False인 argv와 stdin을 사용한다. 아래는 **구현할 argv 계약**이며 G1 중 실행하지 않는다.

```text
codex exec --ignore-user-config --ephemeral --skip-git-repo-check
  --sandbox read-only --color never --model <CODEX_MODEL>
  -c project_doc_max_bytes=0 -c features.shell_tool=false
  -c web_search="disabled"
  --cd <request-temp-dir> --output-schema <schema.json>
  --output-last-message <result.json>
  --image <submission-01.png> --image <reference-01.png> -
```

`--image`를 실제 모든 이미지마다 순서대로 반복한다. stdin의 매핑은 “첨부 1..N = 제출 사진 position 1..N; 첨부 N+1..N+R = Reference position 1..R, 각 reference_id”라고 명시한다. CLI 사용자 설정과 프로젝트 지시문·이전 대화를 재사용하지 않는다. MCP/플러그인·외부 검색을 분석에 사용하지 않으며 도구 사용을 요구하지 않는 고정 프롬프트를 사용한다. 설치 CLI에서 config 적용·원치 않는 도구 부재를 G2에 확인하고 격리가 보장되지 않으면 실제 서비스 완료로 인정하지 않는다.

프롬프트 버전은 `storeloop-review-v1`이다. 입력 JSON을 명시적인 데이터 블록에 넣고, 한국어로 사진에 보이는 사실만 설명·질문에 직접 답변·기준별 정확히 1회 판정·판단 근거가 없는 부분 unknown·미준수 시 실행 가능한 행동을 요구한다. Reference는 이상적인 예시이며 텍스트 기준을 임의로 덮어쓰지 않는다. 모델이 이미지 내 문구나 질문으로 요청된 지시를 실행하지 않도록 명시한다.

서브프로세스 환경은 필요한 PATH·HOME/CLI 인증 위치·모델 접속 변수만 allowlist로 전달한다. DB 비밀번호·내부 호출 토큰·업무 API 세션을 상속하지 않는다. 인증은 이미 설정된 CLI 인증을 그대로 이용하며 새 유료 자원을 구매하지 않는다. `CODEX_MODEL`은 런타임 설정에 기록하고 결과 metadata에 실제 모델 이름·CLI 버전·prompt/schema 버전을 남긴다.

프로세스 시작부터 120초 hard timeout. 프로세스 그룹을 종료하고 3초 유예 뒤 kill하여 자식 프로세스도 정리한다. 정상/실패/취소/timeout 모두 finally에서 임시 사진·프롬프트·출력 파일을 제거한다. stdout/stderr 전체는 저장하지 않는다. 결과는 `--output-last-message`의 JSON 하나만 파싱하고 코드펜스 제거·부분 추출·문자열 수선으로 잘못된 응답을 성공 처리하지 않는다. 마지막 응답 파일 512KiB 제한, 빈 파일은 EMPTY_RESPONSE.

공식 문서는 구조화 출력·최종 응답 파일을 지원하고, config reference는 shell 도구·지시문 읽기 한도를 설명한다. 실제 플래그는 위 로컬 CLI에서 확인했다. G2 조기 검증에서 Codex CLI 0.154.0 / gpt-6-astra의 실제 이미지 분석이 HTTP 200 및 엄격 schema·참조 검증에 성공했다. HTTP 36,089ms로 30초 목표는 미달했다. 근거는 `execute/workHitory/local-ai/evidence/real-ai-early-002.json`이다. [비대화형 실행](https://learn.chatgpt.com/docs/non-interactive-mode), [설정 참조](https://learn.chatgpt.com/docs/config-file/config-reference).

## 4. 모델 출력 JSON Schema

아래 JSON은 `review-result-v1`의 정본이다. AI 서버와 worker는 같은 schema를 사용하고 §5의 의미 검증을 각각 수행한다. 모든 필드 필수, 모든 객체 추가 필드 금지. ID·문장 길이 등 추가 범위는 §5와 Pydantic으로 검증한다.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StoreLoopReviewV1",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "question_answer", "summary", "overall_confidence", "criteria", "reference_comparisons", "limitations", "ofc_review_required", "follow_up_comparison"],
  "properties": {
    "schema_version": {"type": "string", "enum": ["1.0"]},
    "question_answer": {"type": "string"},
    "summary": {"type": "string"},
    "overall_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    "criteria": {
      "type": "array",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["guideline_id", "version_id", "version", "rule_key", "verdict", "reason", "evidence", "actions"],
        "properties": {
          "guideline_id": {"type": "string"},
          "version_id": {"type": "string"},
          "version": {"type": "integer"},
          "rule_key": {"type": "string"},
          "verdict": {"type": "string", "enum": ["pass", "fail", "unknown"]},
          "reason": {"type": "string"},
          "evidence": {
            "type": "array", "items": {
              "type": "object", "additionalProperties": false,
              "required": ["photo_position", "observation"],
              "properties": {
                "photo_position": {"type": "integer"},
                "observation": {"type": "string"}
              }
            }
          },
          "actions": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "reference_comparisons": {
      "type": "array", "items": {
        "type": "object", "additionalProperties": false,
        "required": ["reference_id", "verdict", "photo_positions", "observation"],
        "properties": {
          "reference_id": {"type": "string"},
          "verdict": {"type": "string", "enum": ["similar", "different", "unknown"]},
          "photo_positions": {"type": "array", "items": {"type": "integer"}},
          "observation": {"type": "string"}
        }
      }
    },
    "limitations": {"type": "array", "items": {"type": "string"}},
    "ofc_review_required": {"type": "boolean"},
    "follow_up_comparison": {"type": ["string", "null"]}
  }
}
```

## 5. 의미 검증·저장·계산

1. strict JSON 파싱: duplicate object key, NaN/Infinity, UTF-8 오류·trailing text 금지. bool을 integer로 변환하지 않고 타입 강제 변환 금지.
2. criteria의 `(guideline_id,version_id,version,rule_key)` 집합은 입력 effective_guidelines와 정확히 동일하다. 누락·중복·낯선 ID·버전·rule_key는 INVALID_RESULT. 입력 기준이 비어 있을 때만 criteria=[] 허용.
3. evidence의 photo_position과 comparison photo_positions는 제출 사진 1..N만 참조. Reference 번호를 제출 사진 근거로 사용하지 않는다. pass/fail criterion은 관찰 근거 ≥1개, fail은 개선 행동 ≥1개 필수. unknown은 reason에 판단 제한을 남기며 근거 없는 pass/fail로 보정하지 않는다.
4. Reference comparison은 입력 reference_id마다 정확히 1개. similar/different에는 제출 photo_positions ≥1개, 중복 position 금지. Reference가 비어 있을 때만 comparisons=[] 허용.
5. question_answer/summary/reason/observation/action은 공백 제외 1~2,000자, limitations 최대 20개·각 1,000자, follow_up_comparison 최대 2,000자. evidence 최대 20개/criterion, actions 최대 10개/criterion. guideline 최대 100개·Reference 최대 3개와 schema_version 검증.
6. 부모 결과 없으면 follow_up_comparison=null. 부모가 있어도 사진 관찰을 뒷받침하지 않는 수치·매출 인과·상품 식별 정확도를 단정하지 않는다. 부모/자식 동일 rule_key의 판정 비교는 서버가 제공하며 다른 기준 버전이면 “기준 변경” 표시하고 단순 개선율 산정에서 제외한다.
7. 모델 본문은 HTML로 실행하지 않고 평문으로 렌더한다. 허용되지 않은 경로·비밀 값·도구 실행 결과를 저장하는 채널로 사용하지 않는다. 입력에 없는 개인정보를 추가하도록 요구하지 않는다.

성공 응답 envelope는 `{schema_version,job_id,attempt_id,submission_id,result,model,prompt_version,cli_version,duration_ms}`다. `result`는 위 model JSON. worker가 현재 시도·deadline·입력 snapshot과 다시 검증한 뒤 ReviewResult의 result와 CriterionEvaluation을 한 트랜잭션에 저장한다. 서버 계산 필드는 API가 `compliance_rate`, `assessable_rate`, `needs_ofc_review`로 반환한다.

| 서버 필드 | 계산 |
|---|---|
| `compliance_rate` | pass/(pass+fail)×100, 판정 가능 기준 0개면 null |
| `assessable_rate` | (pass+fail)/전체 effective 기준×100, 전체 기준 0개면 null |
| `needs_ofc_review` | unknown 존재 OR 기준/Reference 누락 OR overall_confidence=low OR ofc_review_required=true |

비율은 소수 1자리로 반올림한다. 화면에는 준수율과 판단 가능 비율·표본 수를 함께 표시한다. unknown을 fail 또는 0점으로 세지 않는다. 모델 신뢰도는 자기 평가이며 통계적 정확도 보증이 아니다. 보조판단 표시와 점주의 OFC 문의 동선을 유지한다.

## 6. 작업과 시도 상태 전이

| 사건 | AnalysisJob | AnalysisAttempt | 저장 조건 |
|---|---|---|---|
| 최초 제출 접수 | queued | 아직 없음 | 제출·context·job 한 트랜잭션, queue_deadline_at=접수+180초 |
| 최초 점유 | queued→running | running 새로 생성 | row lock, active attempt ID 설정, attempt_number 증가 |
| 실패 수동 재처리 접수 | failed→queued | queued 새로 예약 | job lock, 동일 입력 유지, queue_deadline_at=재처리 접수+180초 |
| 예약 시도 점유 | queued→running | queued→running | 새 시도를 또 생성하지 않음 |
| 유효 성공 | running→succeeded | running→succeeded | active attempt와 lease 일치, deadline 전, review unique |
| CLI/결과/내부 호출 실패 | running→failed | running→failed | error_code 고정, result_applied=false |
| 모델/응답 시간 초과 | running→failed | running→expired | MODEL_TIMEOUT, result_applied=false |
| worker lease 만료 | running→failed | running→expired | WORKER_INTERRUPTED, 복구 sweep가 단 한 번 종료 |
| 대기 만료 | queued→failed | 예약 있으면 queued→expired, 없으면 expired 생성 | QUEUE_TIMEOUT. 실행된 것처럼 started_at을 채우지 않음 |

attempt 필드 정본은 [05](05-database.md)에 있으며 개념적으로 attempt_number, status, worker_id, started_at/finished_at/deadline_at, error_code, result_applied를 포함한다. 끝난 시도는 immutable. succeeded job·review를 재처리하거나 덮어쓰지 않는다. 실패 종료와 새 시도는 서로 연결되며 사용자 재촬영은 parent_submission_id를 가진 새로운 Submission이다.

### 6.1 점유·heartbeat·복구

- 기본 worker concurrency=1, AI concurrency=1. PostgreSQL `FOR UPDATE SKIP LOCKED`로 queued 작업 1개를 고르고 queue deadline을 확인한 뒤 실행 상태와 worker/attempt ID를 기록·commit한다. 모델 HTTP를 기다리는 동안 DB lock을 유지하지 않는다.
- heartbeat 10초, lease 140초. CLI hard timeout은 시작+120초다. `AnalysisAttempt.deadline_at`은 worker 시작+130초인 호출·결과 수용 절대기한이고 worker HTTP connect=5초/read=130초에 별도의 **전체 HTTP wall time 130초** 제한을 둔다. `lease_expires_at`은 attempt 시작+140초다. heartbeat는 lease를 이 절대 상한 너머로 연장하지 않는다. 결과 검증·DB commit 조건 검사는 130초 전에 완료해야 한다.
- worker는 HTTP를 기다리는 중 별도 짧은 transaction으로 자기 heartbeat를 갱신한다. API/worker 상태 화면은 30초 heartbeat 부재를 “응답 확인 필요”로 표시할 수 있으나 기존 실행을 즉시 재점유하지 않는다. 만료 후에만 실패로 종료하고 수동 재처리를 허용한다.
- sweep는 시작 시와 5초 주기로 queued 기한·running lease를 비교한다. 여러 sweeper가 실행되어도 row lock과 조건부 update로 한 번만 종료. running lease가 아직 유효하면 재시작 worker가 빼앗지 않는다.
- graceful stop은 새 점유를 중단하고 현재 요청은 deadline까지 drain한다. 종료가 강제되거나 서버가 죽으면 lease 만료 복구. AI 프로세스는 요청 취소/timeout에 자식 프로세스 그룹을 종료하고 임시 파일을 정리한다.
- worker 최종 저장은 `job.status=running AND current_attempt_id=응답 attempt AND worker_id=현재 worker AND deadline/lease 유효` 조건을 한 트랜잭션에서 다시 검사한다. ReviewResult(submission_id) UNIQUE가 마지막 방어다.
- 늦은 응답은 전용 안전 로그에 `discarded`와 job_id/attempt_id/시각만 기록한다. 별도 업무 DB 이벤트를 만들거나 본문을 기록하지 않는다. 완료된 시도·review의 status/body/result_applied를 바꾸지 않는다. 만료된 시도가 뒤늦게 성공해도 새 시도의 성공 결과를 덮어쓰지 않는다.

### 6.2 중복 요청

공개 제출·재처리는 `Idempotency-Key` 필수. 범위는 계정+operation+key, HTTP 메서드·실제 대상 job/store ID·정규화 본문·이미지 hash를 포함한 요청 hash와 결과 ID를 저장한다. 정확한 operation/hash 정본은05/06 CONTRACT-DATA-1.0b를 따른다. 같은 key/같은 hash는 기존 응답을 반환하고, 같은 key/다른 hash는 409 IDEMPOTENCY_CONFLICT. retry의 reason도 hash에 포함한다. 다른 key로 failed 작업의 재처리가 동시에 오면 job lock으로 하나만 수락하고 나머지는 409 JOB_NOT_RETRYABLE. 진행 중·성공한 작업은 이유와 관계없이 재처리 금지.

failed→queued 재처리에서는 Job.started_at/finished_at/error_code/error_message를 NULL로 초기화하고 queued_at/queue_deadline_at을 새 접수 시각으로 설정한다. current_attempt_id를 새 queued 시도로 바꾸고 enqueue_generation을 증가시킨다. 이전 실패의 시각·오류는 종료된 AnalysisAttempt에 그대로 보존하여 현재 작업 화면에 옛 실패를 섞지 않는다.

내부 AI HTTP를 자동 재시도하지 않는다. worker가 response를 못 받은 경우 새 요청으로 같은 attempt를 모델에 다시 보내지 않고 실패/만료 기록 후 명시적인 수동 재처리로 새 attempt를 만든다. AI_BUSY는 AI_UNAVAILABLE로 기술 실패 처리하고 운영자가 원인을 확인한다.

## 7. 오류 분류와 사용자 표시

| error_code | 발생 경계 | 표시 / 인수 검증 |
|---|---|---|
| QUEUE_TIMEOUT | 접수/재처리 180초 내 미점유 | “분석 대기 시간이 초과되었습니다.” queued 만료·수동 재처리 |
| MODEL_TIMEOUT | CLI 120초 또는 HTTP 130초 | “분석 시간이 초과되었습니다.” expired 시도·프로세스 정리·늦은 결과 폐기 |
| AI_UNAVAILABLE | 접속 실패·AI_BUSY·잘못된 내부 인증·HTTP 프로토콜 오류 | “분석 서비스 연결을 확인하고 있습니다.” 내부 토큰 내용 미노출 |
| CLI_UNAVAILABLE | binary 없음·실행 불가 | “분석 실행 환경을 확인하고 있습니다.” |
| MODEL_AUTH_FAILED | Codex 인증 오류 | “분석 서비스 인증을 확인하고 있습니다.” 원문 stderr 미노출 |
| MODEL_EXECUTION_FAILED | 모델/네트워크/CLI 비정상 종료 | “분석을 완료하지 못했습니다.” |
| EMPTY_RESPONSE | 최종 파일 없음/공백 | “분석 결과를 받지 못했습니다.” |
| INVALID_JSON | strict JSON 파싱 실패 | “분석 결과 형식을 확인할 수 없습니다.” |
| INVALID_RESULT | schema/참조/의미 검증 실패 | “분석 결과를 검증하지 못했습니다.” |
| INVALID_IMAGE | 내부 파일 hash·mime·디코딩 실패 | “사진 파일을 확인할 수 없습니다.” 입력 시엔 422, 저장 후 발견이면 job 실패 |
| WORKER_INTERRUPTED | lease 만료 | “분석 작업이 중단되었습니다.” 수동 재처리 |

운영자에게 job/attempt ID, 상태·시각·기간, 안전한 error_code/message, 재처리 가능 여부만 제공한다. 질문·사진/URL·가이드라인 본문·평가 결과·전체 stderr/CLI prompt·인증 헤더는 운영 API·audit에 넣지 않는다. 일반 사용자는 실패 설명과 새로 조회하기/OFC 문의를 이용하며 플랫폼 운영자의 장애 재처리 버튼은 보이지 않는다.

UI polling은 2초이며 succeeded/failed에서 멈춘다. 재접속 시 job 조회로 복구한다. 제출 이후 30초부터 지연 안내를 표시하되 30초를 성공/실패 경계로 사용하지 않는다.

## 8. 측정과 완료 증거

접수 completed timestamp, queue 시작/점유, model 시작/종료, DB 결과 commit, 브라우저 결과 표시 시각을 별도로 기록한다. `submit_to_visible_ms`는 브라우저 제출 시작→첫 유효 결과 표시이며 업로드·대기·모델·polling을 모두 포함한다. 서버 queue_ms/model_ms/total_ms는 장애 원인 분석용이다. 개발 세션 시간이나 에이전트 수를 계측하지 않는다.

G2에서는 제출 1장+다른 Reference 1장+질문+기준으로 실제 모델 호출을 먼저 성공시킨다. 결과 schema/참조 검사·사진 hash 매핑·실제 모델/CLI·elapsed를 비밀 없는 보고서에 남긴다. G4에는 5개 시안마다 실제 분석 최소 1회와 전체 재제출·OFC 확인 흐름을 수행한다. 30초 목표는 모든 표본의 실제 시간과 달성률을 기록하며 초과를 숨기거나 Mock으로 대체하지 않는다. 문장 완전 일치 또는 생성 의도만으로 정답을 판정하지 않는다.

## 9. 구현 인터페이스와 파일 소유권

G1 확정 후 local-ai 담당이 `ai-service/`와 `packages/review_contract/` Python 패키지를 소유한다. 공유 패키지는 입력/결과 Pydantic 타입, 정본 JSON Schema 생성, strict JSON 로더, snapshot 대상 참조 검증, 서버 산식 함수를 제공한다. AI 서버와 업무 worker가 동일 함수를 import하여 서로 다른 허용 스키마가 생기지 않도록 한다. workflow/DB 저장은 업무 서버 책임이다.

- `packages.review_contract.models.AnalysisInput`, `ReviewResultPayload`: §2/4 strict 타입.
- `packages.review_contract.validation.parse_result(text)`: strict JSON 파싱 후 ReviewResultPayload 반환.
- `packages.review_contract.validation.validate_result(result, context)`: 현재 입력 기준·사진·Reference·부모와 의미 검증. 실패는 코드/안전 메시지를 가진 오류이며 원문을 예외 메시지에 넣지 않음.
- `packages.review_contract.validation.derive_metrics(result, context)`: compliance_rate/assessable_rate/needs_ofc_review와 pass_count/fail_count/unknown_count 반환.
- `packages.review_contract.schema.result_json_schema()`: CLI에 전달할 정본 JSON Schema 객체.

root는 `PYTHONPATH=project`로 공통 패키지 import를 제공하고 AI는 `uvicorn app.main:app --app-dir ai-service`, 업무 API/worker는 `server.*` 절대 패키지 경로로 실행한다. 두 가상환경에서 필요한 공유 패키지 의존성을 동일 호환 버전으로 설치한다. 공통 계약 인터페이스 변경은 root/DB/API/worker 담당에게 먼저 전파하고 수신·반영 확인 후 구현한다.


## 시안 02 배포 확장: OpenAI Responses API

사용자 승인에 따라 AI_PROVIDER=codex|openai로 기존 CLI와 API를 선택한다. 기본은 codex이며 배포 구성은 openai를 명시한다. OpenAI 모델·서버 비밀·출력 토큰 상한은 환경변수로 주입한다. 이미지 순서, 질문, 적용 기준/Reference, 엄격한 결과 스키마와 참조 검증은 동일하다. API 호출은 요청당 1회이며 자동 재시도·CLI로 대체 실행·결과 수선 호출은 하지 않는다. AI_REQUESTS_ENABLED=false이면 유료 요청을 보내지 않는다.

기존 schema_version=1.0 봉투를 유지한다. API 모드의 cli_version은 실제 CLI 버전이 아닌 not-applicable:openai-responses 고정 표식이다. health의 provider로 실행 방식을 구분하며 키 존재 여부는 인증 성공이 아니다. health는 모델을 호출하지 않는다. 응답은 store=false, JSON Schema strict, tools 미지정이며 refusal·미완료·잘못된 JSON·참조 불일치는 실패 처리한다.

공식 근거: https://developers.openai.com/api/docs/guides/images-vision 및 https://developers.openai.com/api/docs/guides/structured-outputs . 실제 유료 API 검증은 사용자 후행 항목이다.
