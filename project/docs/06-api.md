# 06. 공통 API 계약

- 버전: `CONTRACT-DATA-1.0` (검토 보완 `CONTRACT-DATA-1.0b`), 2026-09-21, 상태 **ACCEPTED**. G1 확정 등록부에 따라 구현한다.
- DB 정본: [05-database.md](05-database.md), AI·처리 정본: [07-ai-processing.md](07-ai-processing.md).
- 모든 시안은 같은 `/api`와 동일 업무 정책을 사용한다. 브라우저는 AI 서비스에 직접 연결하지 않는다.

## 1. 전송·페이지·오류·중복 요청

JSON 요청/응답은 UTF-8 snake_case. UUID는 문자열, 시각은 UTC ISO-8601 `2026-09-21T03:00:00Z`, 날짜는 `YYYY-MM-DD`. 단건 성공은 DTO 객체 자체, 목록은 `{"items":[],"total":0,"page":1,"page_size":20}`다. `page>=1`, `page_size=20`, 최대100, 안정 정렬 `created_at DESC,id ASC` (기준 정보는 name,id). 잘못된 필터는 422이고 권한 밖 명시 ID 필터는 404; 범위 밖 레코드를 total/집계에 포함하지 않는다. 모든 응답에 `X-Request-ID` UUID를 넣는다. 민감 JSON/미디어는 `Cache-Control: private, no-store`.

```json
{"error":{"code":"VALIDATION_ERROR","message":"입력값을 확인해 주세요.","details":[{"field":"question","message":"2000자 이하로 입력해 주세요."}]},"request_id":"00000000-0000-4000-8000-000000000001"}
```

| HTTP | code | 의미 |
|---|---|---|
| 400 | INVALID_REQUEST | 잘못된 JSON/multipart/필터 조합 |
| 401 | UNAUTHENTICATED, SESSION_EXPIRED, ACCOUNT_INACTIVE, INVALID_CREDENTIALS | 세션 만료·폐기·비활성·로그인 실패, 비밀번호 유무/계정 존재 구분 금지 |
| 403 | FORBIDDEN, CSRF_INVALID, ORIGIN_DENIED | 해당 역할 기능 금지, CSRF/Origin 검증 실패 |
| 404 | NOT_FOUND | 없음 또는 현재 권한 범위 밖인 객체/미디어 |
| 409 | VERSION_CONFLICT, IDEMPOTENCY_CONFLICT, ALREADY_ASSIGNED, JOB_NOT_RETRYABLE, INVALID_TRANSITION | 수정 충돌, 키 재사용 차이, 담당 선점, 실행/성공 작업 재처리 |
| 413 | FILE_TOO_LARGE | 이미지 10MiB/장 초과 |
| 415 | UNSUPPORTED_MEDIA | JPEG/PNG 이외 또는 실제 decode 불일치 |
| 422 | VALIDATION_ERROR, INACTIVE_TARGET, GUIDELINE_LIMIT | 필드/역할·매핑 조합 오류, 비활성 대상 신규 업무, 적용 기준 30000자 초과 |
| 503 | SERVICE_UNAVAILABLE | DB/내부 처리 기반 일시 불가, 원시 내부 오류 숨김 |

모든 상태 변경은 CSRF 필수. `POST /submissions`, `POST /operations/jobs/{id}/retry`, `POST /stores/{id}/claim`, `POST /issues`에는 `Idempotency-Key`(16..128자 영숫자와 `-_.:`) 필수, 미지정 422. 계정+operation+key 유니크이며 operation은 경로 template별 고정값(submissions.create,analysis.retry,stores.claim,issues.create)이다. request_hash는 HTTP 메서드·실제 URL 대상 ID(job_id/store_id 등)·정규화 본문·순서별 이미지 hash를 포함한다. 같은 key/같은 reason이라도 다른 대상 URL이면409이며 다른 대상을 원래 응답으로 replay하지 않는다. 동일 내용 재송신은 최초 status와 같은 resource ID를 반환하고 `Idempotency-Replayed:true`; 다른 내용이면409. 새 요청 권한과 CSRF를 매번 먼저 검사한다. TTL 삭제 없이 POC 기간 보존. 수정 PUT/PATCH는 version(Reference는 state_version)과 트랜잭션으로 충돌 보호한다. 로그에 질문/사진/토큰/비밀번호를 남기지 않는다.

### 입력 검증 기본값

모든 JSON/metadata는 추가 필드를 거절한다(`extra=forbid`). 문자열 길이·숫자범위·enum/FK nullable은05 데이터사전을 상속하고 명시된 API 제한이 있으면 더 엄격한 값을 적용한다. 선행/후행 공백을 제거한 뒤 필수 문자열이 비면422. login_id는3..80자의 영문 소문자/숫자/`._-`로 정규화하며 password는12..128자이고 비밀번호의 공백은 임의 제거하지 않는다. q는0..120자다. role·rule_key·code는 명시 enum/영문 식별자이며 rule_key는 `[a-z][a-z0-9_]{0,79}`.

`?` 필드는 생략 가능, 생략하면 기존값(PATCH) 또는 명시 기본값(POST)을 유지한다. null은05에서 NULL 가능한 필드(예: region_id/store_id/parent_submission_id/assignee_id/next_check_at/ends_at)와 명시 null union에만 허용한다. 배열은 전체 교체이며 중복ID를 거절한다. PATCH에 version/reason 같은 제어필드만 있고 실제 변경필드가 없으면422; 값이 같아 실질변경이 없으면200 현재객체 반환·버전/감사 추가 없이 종료한다. 필수 reason은1..500자. 각 레코드 입력의 길이초과·유효하지 않은 타입은 DB오류가 아니라422로 반환한다.

## 2. 인증과 현재 권한

| 메서드·경로 | 요청 | 응답·정책 |
|---|---|---|
| GET /auth/csrf | 없음 | 200 `{csrf_token,expires_at}`. 로그인 전 익명 DB 세션/HttpOnly 쿠키 발급; 유효 세션 존재시 해당 세션의 CSRF를 갱신해 반환 |
| POST /auth/login | `{login_id,password}` + X-CSRF-Token | 200 `{account:AccountMe,csrf_token,expires_at}`; 검증 성공 시 기존 익명/로그인 세션 폐기·새 토큰/CSRF 발급 |
| GET /auth/me | 쿠키 | 200 `AccountMe` |
| POST /auth/logout | `{}` + X-CSRF-Token | 204, DB 세션 revoke와 쿠키 삭제 |

쿠키명 `storeloop_session`, Path=/, HttpOnly, SameSite=Lax, localhost 개발 외 Secure 필수. 익명30분·인증12시간 절대 만료. DB에는 세션/CSRF SHA-256만 저장한다. GET csrf는 무작위 새 CSRF 원문을 반환하고 해시를 교체한다. 공통 클라이언트는 탭별 요청 직렬화를 사용하며 다른 탭이 CSRF를 교체하면 403 후 csrf 갱신·사용자 변경의 명시 재시도(멱등키 재사용)만 허용한다. 비밀을 localStorage에 저장하지 않는다.

상태 변경은 토큰 일치와 Origin 정확 일치; Origin이 없으면 Referer의 origin 정확 일치, 둘 다 없으면403. 허용 origin은 실제 Vite dev/preview 주소만 환경설정으로 나열. 프록시에서 받은 임의 Forwarded host를 신뢰하지 않는다. CORS/쿠키 SameSite는 CSRF 대체 수단이 아니다. 로그인/로그아웃도 예외 없음. GET csrf는 Origin이 있으면 허용목록을 검사하고 cross-site fetch는 거절한다.

`AccountMe={id,login_id,display_name,role,region_id,is_active,version,store_ids:string[],permissions:string[]}`. permission 값은 `submit,manage_guidelines,manage_issues,view_business,operate` 중 현재 역할 허용 목록이며 UI 보조일 뿐 서버 권한을 대체하지 않는다.

매 요청은 Session 유효성 → 현재 Account.is_active/role → 현재 Region/매핑을 DB 조회한다. 세션에 과거 role/store 권한을 고정 저장하지 않는다. 비활성 지역/매장은 신규 입력 차단, 과거 기록 조회는 현재 매핑으로 허용한다.

| 역할 | 영업 조회 범위 | 쓰기 |
|---|---|---|
| store_owner | 현재 매핑된 매장 전체 이력·사진·적용 기준 | 활성 연결 매장 제출, 본인 제출의 후속/문의 |
| ofc | 현재 담당 매장 | 해당 STORE/CATEGORY(store 지정) 기준·Reference, 담당 등록·대응 |
| regional | 현재 소속 지역 매장 | 지역 및 하위 STORE/CATEGORY(store 지정) 기준·Reference·대응 |
| hq | 전사 | 전체 기준·Reference·대응 |
| platform_operator | 없음 | /operations 전용 계정/기준 정보/연결/처리 메타데이터 |

다른 역할 전용 API는403, 허용 역할이 담당 밖 ID에 접근하면404. 운영자는 `/stores`, `/categories`, `/guidelines`, `/references`, `/submissions`, `/jobs`, `/media`, `/dashboard`, `/issues`, `/notifications`, `/analytics` 영업 경로 접근403. 특히 GET /notifications와 POST /notifications/{id}/read는 platform_operator에게403이며 영업 알림 메뉴/라우트도 제공하지 않는다(PD-003). 로그인한 모든 역할의 운영 공지는 유지한다. 운영자 계정 생성/승격/다른 운영자 변경은 UI/API 모두 금지하고 초기 설정만 허용한다. 일반 계정을 플랫폼 운영자로 바꾸는 입력도422.

## 3. 읽기 DTO와 기준 정보·담당 등록

공통 DTO:
- `Region={id,code,name,is_active,version,created_at,updated_at}`.
- `Category={id,code,name,description,is_active,version,created_at,updated_at}`.
- `Store={id,code,name,region_id,region_name,store_type,address,is_active,version,ofc:{id,display_name}|null,owner_count}`. 제출 신규용 목록은 `can_submit:boolean` 포함.
- `Photo={id,media_id,position,mime_type,width,height,source_kind,url,thumbnail_url}`. URL은 보호된 `/api/media/{media_id}`이며 파일경로는 반환하지 않는다.

| 메서드·경로 | 요청·필터 | 응답·정책 |
|---|---|---|
| GET /stores | page,page_size,q,region_id?,is_active? | List<Store>, 현재 범위. q는 이름/code 검색 |
| GET /stores/{id} | 없음 | Store, 현재 범위 |
| GET /categories | page,page_size,is_active? | List<Category>, 영업 역할. 과거 상세는 비활성 category 이름도 반환 |
| GET /regions | page,page_size | List<Region>, ofc/regional은 자기 지역, hq 전사 |
| GET /stores/candidates | page,page_size,q | ofc만, 자기 활성 지역의 활성 미배정 매장. `{id,code,name,region_id,region_name,store_type}`만 반환 |
| POST /stores/{id}/claim | `{reason}` + 멱등키 | 201 Store. 자기 지역 활성 미배정 매장만 행잠금+고유 제약으로 선점, AuditEvent 기록. 이미 타인배정409 |

OFC 후보 조회로 사진·이력 권한을 얻지 않는다. claim 성공 이후 현재 매핑으로만 영업 접근한다. 신규 매장 등록은 운영자의 `/operations/stores`이며 영업 화면은 기존 매장 담당 등록을 사용한다.

## 4. 가이드라인과 Reference

`Guideline={id,rule_key,title,level,region_id,store_id,category_id,is_active,version,current_version,current:{version_id,version,text,change_reason,created_at},created_at,updated_at}`. Guideline 1개는 기준1개, `rule_key` 기준으로 CATEGORY>STORE>REGION>HQ 선택. 상세 우선순위/범위 제약은05. hq는 모든 레벨, regional은 자기 지역 REGION 및 자기 지역 매장의 STORE/CATEGORY, ofc는 담당 STORE/CATEGORY만 변경한다. 공통 CATEGORY(store_id=null)는 hq만 변경한다. 점주는 적용 snapshot 조회만 제공한다.

| 메서드·경로 | 요청 | 응답 |
|---|---|---|
| GET /guidelines | page,page_size,store_id?,region_id?,category_id?,level?,is_active? | List<Guideline>, 영업 관리 역할 조회 가능 후보·자기 권한으로 필터 |
| GET /guidelines/{id} | 없음 | Guideline, 직접 상세/새로고침용·현재 역할/범위 확인 |
| POST /guidelines | `{rule_key,title,level,region_id:null|id,store_id:null|id,category_id:null|id,text,reason}` | 201 Guideline, 최초 version1 원자 생성 |
| GET /guidelines/{id}/versions | page,page_size | List<{version_id,version,text,change_reason,created_at,created_by_id}> |
| POST /guidelines/{id}/versions | `{version,text,reason,title?}` | 201 Guideline, 전달 version은 Guideline 수정 충돌용, 새 GuidelineVersion.current_version+1 |
| PATCH /guidelines/{id} | `{version,is_active,reason}` | 200 Guideline; 비활성화해도 과거 기준 보존 |
| GET /references | page,page_size,category_id?,store_id?,include_inactive=false | List<Reference>, 현재 범위 + 전사 공통. 다른 매장 전용 제외 |
| GET /references/{id} | 없음 | Reference, 현재 범위 또는 허용된 과거 snapshot 참조 |
| POST /references | multipart `metadata` JSON `{category_id,store_id:null|id,caption,reason}`, `photo` 1개 | 201 Reference |
| PATCH /references/{id} | multipart metadata `{state_version,caption,reason}`와 선택 photo | 200 Reference, 새 id/revision 반환, 이전 lineage 버전 보존 |
| PATCH /references/{id}/status | `{state_version,is_active,reason}` | 200 Reference; 다른 활성 lineage 버전과 충돌409 |
| GET /media/{id} | variant=original(default)\|thumbnail | 200 검증된 image/jpeg 또는 image/png bytes, 동일 인가. 비활성 Reference라도 허용된 과거 snapshot에서 사용된 매체는 조회 가능 |

`Reference={id,lineage_id,version,state_version,category_id,store_id,caption,is_active,photo:Photo,created_at}`. Reference.version은 내용revision, state_version은 수정충돌용이다. PATCH는 lineage 최신행 잠금+id/state_version 비교 후 실행하며 오래된 revision 재활성/교체는409다. 상태 변경은state_version+1, 내용교체는 새id/version+1/state_version=1을 반환한다. 파일은 JPEG/PNG decode 검증, 장당10MiB, 확장자/MIME 일치, 가로·세로32..8192 및 총4000만 pixel 이하, EXIF 방향 정규화/불필요 메타 제거, 썸네일 생성. 운영자는 원본·썸네일 모두403. 참조 매체는 활성이고 자신의 사용 가능 범위인 Reference 또는 자기 범위의 과거 AnalysisContext에 포함된 경우 접근한다. MEDIA-CLARIFY-2: 영업 관리자(OFC·지역·본사)는 Reference 관리 이력 조회와 같은 현재 범위 안에서 비활성·교체된 Reference의 원본과 썸네일도 조회할 수 있다. 분석에서 사용된 적이 없는 과거 revision도 포함하며, 점주에게 이 관리 이력 권한을 부여하지 않는다. 점주는 기존 활성 사용 가능 범위 또는 현재 허용된 과거 AnalysisContext 경로만 유지한다. 제출 매체는 현재 권한의 Submission을 통해서만 접근한다. 부모·lineage·media ID를 안다고 범위 검사를 생략하지 않는다.

## 5. 제출·작업·결과·비교

| 메서드·경로 | 요청 | 응답 |
|---|---|---|
| POST /submissions | multipart `metadata` JSON `{store_id,category_id,question:"",parent_submission_id:null|id}`, `photos` 반복 필드 1..5개 + 멱등키 | 202 `{submission_id,job:Job,created_at}`. 활성 연결 매장, 활성 category, 질문2000자/사진10MiB 검증, 스냅샷/작업 원자 생성 |
| GET /submissions | page,page_size,region_id?,store_id?,category_id?,date_from?,date_to?,is_active?,status?,needs_ofc_review? | List<SubmissionSummary>, 현재 범위; 기본 최근28일 |
| GET /submissions/{id} | 없음 | SubmissionDetail |
| GET /jobs/{id} | 없음 | Job, 점주/영업의 현재 제출 범위. 운영자는 전용 DTO 경로 사용 |
| GET /submissions/{id}/comparison | 없음 | `{parent:ComparisonSide|null,current:ComparisonSide,criteria:[{rule_key,before:null|verdict,after:null|verdict,criterion_changed:boolean,change:resolved|unchanged|regressed|unavailable}],narrative:null|string}` |

`Job={id,submission_id,status,queued_at,started_at,finished_at,error_code,error_message,current_attempt_id,attempt_count,elapsed_ms,delayed:boolean}`. status=queued/running/succeeded/failed, delayed는 제출 이후30초 초과이고 미종료. 폴링2초·종료시중단, 네트워크 오류는 서버 실패로 바꾸지 않고 재조회 안내. error_message는 안전한 사용자 안내이며 stderr 제외.

`SubmissionSummary={id,store_id,store_name,category_id,category_name,submitted_by_id,created_at,parent_submission_id,source_kind,photo_count,thumbnail:Photo,job:Job,review_summary:null|{id,compliance_rate,assessable_rate,needs_ofc_review,source_kind},open_issue_count}`.

`SubmissionDetail={...SubmissionSummary,question,photos:Photo[],reference_photos?:Array<{reference_id:UUID,photo:Photo}>,context:AnalysisContextDTO,review:Review|null,parent:null|{id,created_at},children:[{id,created_at}],issues:IssueSummary[]}`. AnalysisContextDTO는 `{schema_version,snapshot_sha256,store,category,question,photos,candidate_guidelines,guidelines,references,previous_review}`로05의 snapshot 필드를 평탄화한다. 프론트는 context.guidelines/context.references를 읽으며 별도 context.snapshot 중첩은 없다. 운영자는 이 객체를 받지 않는다. 기준/Reference가 없을 경우 입력은 허용하되 결과의 한계 및 needs_ofc_review=true 필수.

MEDIA-CLARIFY-1: `reference_photos`는 화면용 읽기 전용 메타데이터이며 기존 Photo DTO의 `source_kind`, 치수, 보호 원본/썸네일 URL을 포함한다. 현재 Submission 조회 범위를 확인한 뒤 해당 불변 context.references의 reference_id/photo_id만 사용해 구성한다. 참조 순서와 대응을 유지하며 참조가 없으면 빈 배열이다. 과거 비활성 Reference도 해당 snapshot에서 사용했다면 원본 메타데이터를 제공한다. 이 필드는 기존 클라이언트 호환을 위해 선택 항목으로 추가하며 신규 서버는 항상 반환한다. 클라이언트는 누락 시 빈 배열로 처리한다. context/snapshot/hash·AI 입력·DB 구조는 변경하지 않으며 임의 Reference 목록 조회 권한을 부여하지 않는다.

`Review={id,submission_id,attempt_id,schema_version,result:ModelResult,compliance_rate:null|number,assessable_rate:null|number,pass_count,fail_count,unknown_count,needs_ofc_review,source_kind,model_name,prompt_version,latency_ms,created_at}`. rate는0..100 소수1자리이고 분모0이면null. 화면에 NULL을 0% 또는 정상으로 표시하지 않는다. `source_kind=real_ai|mock`.

```json
{
  "schema_version":"1.0",
  "question_answer":"질문에 대한 답변",
  "summary":"사진에서 확인한 종합 설명",
  "overall_confidence":"medium",
  "criteria":[{
    "guideline_id":"00000000-0000-4000-8000-000000000010",
    "version_id":"00000000-0000-4000-8000-000000000011",
    "version":1,"rule_key":"facing","verdict":"fail",
    "reason":"앞줄 상품의 정렬 개선이 필요합니다.",
    "evidence":[{"photo_position":1,"observation":"중앙 앞줄 간격이 불규칙합니다."}],
    "actions":["앞줄 상품을 같은 선에 맞춰 주세요."]
  }],
  "reference_comparisons":[{
    "reference_id":"00000000-0000-4000-8000-000000000020",
    "verdict":"different","photo_positions":[1],"observation":"Reference보다 간격이 넓습니다."
  }],
  "limitations":[],"ofc_review_required":false,"follow_up_comparison":null
}
```

ModelResult의 정확한 schema/검증은07. 모든 적용 기준의 ID/version/rule_key와 Reference가 각1회, 사진번호1..N이어야 한다. schema 유효해도 참조가 다르면 INVALID_RESULT 기술 실패다. 모델 unknown, 낮은 신뢰도, 기준/Reference 부재, 모델 ofc 요청은 서버 needs_ofc_review에 반영한다. 불변 Review를 관리자 API로 덮어쓰지 않는다. ComparisonSide=`{submission_id,review_id:null|id,compliance_rate,assessable_rate,photos:Photo[]}`. before/after 없는 기준 또는 version_id가 달라 criterion_changed=true인 기준은unavailable, fail→pass는resolved, pass→fail은regressed, unknown 포함은unavailable, 나머지는unchanged다.

분석 실패코드: `QUEUE_TIMEOUT,MODEL_TIMEOUT,AI_UNAVAILABLE,CLI_UNAVAILABLE,MODEL_AUTH_FAILED,MODEL_EXECUTION_FAILED,EMPTY_RESPONSE,INVALID_JSON,INVALID_RESULT,INVALID_IMAGE,WORKER_INTERRUPTED`. 처리 예산은 queued180초/CLI120초/HTTP130초/lease140초/heartbeat10초. 재시도는 운영자 수동만, 점주 재피드백은 새 제출이다.

## 6. 이슈·조치·알림

`IssueSummary={id,submission_id,store_id,store_name,category_id,category_name,review_id,type,status,priority,title,assignee_id,assignee_name,next_check_at,created_at,updated_at,version}`. `Issue={...IssueSummary,description,resolution,resolved_at,actions:[{id,actor_id,actor_name,action_type,body,from_status,to_status,created_at}]}`. status=open/in_progress/resolved, type=owner_question/ai_review_required.

| 메서드·경로 | 요청 | 응답·정책 |
|---|---|---|
| GET /issues | page,page_size,region_id?,store_id?,category_id?,date_from?,date_to?,is_active?,status?,unresolved?,assignee_id?,priority? | List<IssueSummary>, 현재 매장 범위. unresolved=true는 open+in_progress, false는 resolved; status와 동시 지정422 |
| GET /issues/{id} | 없음 | Issue |
| GET /issues/{id}/assignees | page,page_size | List<{id,display_name,role}>, 영업만·해당매장 현재 담당OFC/소속지역 regional/활성hq 후보; 운영자·비활성·범위밖 계정 제외 |
| POST /issues | `{submission_id,title,description,priority:"normal"}` + 멱등키 | 201 Issue, 점주의 본인 제출 문의 또는 영업 범위의 문의. 초기open, 현재 OFC 배정 |
| PATCH /issues/{id} | `{version,status?,assignee_id?,priority?,resolution?,next_check_at?}` | 200 Issue, 영업만. resolved에 resolution필수, 잘못된 assignee422 |
| POST /issues/{id}/actions | `{body}` | 201 Action, 영업만; 이슈 변경 알림 저장 |
| GET /notifications | page,page_size,unread_only=false | `{items:Notification[],total,page,page_size,unread_count}`, 자신+현재 범위 |
| POST /notifications/{id}/read | `{}` | 200 Notification, 본인만·이미 읽었으면 같은 read_at 유지 |

`Notification={id,kind,title,submission_id,issue_id,read_at,created_at,target:{type:"submission"|"issue",id}}`. 원문본문을 title에 복사하지 않는다. 역할·매핑 변경 후 알림 대상 권한을 다시 확인하며 범위가 사라진 알림은 숨긴다. AI needs_ofc_review에 자동 생성되는 이슈는 같은 제출당1개이고 성공 결과 저장 트랜잭션에서 생성. 외부 알림/실시간 전송은 없다.

## 7. 플랫폼 운영

모든 `/operations/*`는 platform_operator만 허용. 모든 변경에 `reason`(1..500자), PATCH/PUT에 `version` 필수; 감사에 수행자/대상/시각/사유/변경요약/결과를 원자 저장. 비밀번호/해시/토큰/질문/사진/평가본문/매출/원시 stderr는 운영 DTO와 감사에 포함하지 않는다.

| 메서드·경로 | 요청 | 응답 |
|---|---|---|
| GET /operations/accounts | page,page_size,q,role?,is_active? | List<OperatorAccount> |
| GET /operations/accounts/{id} | 없음 | OperatorAccount, 직접 상세/새로고침용 |
| POST /operations/accounts | `{login_id,display_name,role,region_id,password,reason}` | 201 OperatorAccount, 일반 계정만·Argon2id 저장·응답에 password 없음 |
| PATCH /operations/accounts/{id} | `{version,display_name?,role?,region_id?,is_active?,password?,reason}` | 200 `{account:OperatorAccount,impact:ChangeImpact}` |
| PUT /operations/accounts/{id}/mappings | `{version,store_ids:string[],reason}` | 200 `{account:OperatorAccount,impact:ChangeImpact}`. 현재 역할 owner/ofc만, 활성 연결 전체 교체·과거row 종료 |
| GET /operations/regions | page,page_size,q?,is_active? | List<Region> |
| POST /operations/regions | `{code,name,reason}` | 201 Region |
| PATCH /operations/regions/{id} | `{version,name?,is_active?,reason}` | 200 `{region:Region,impact:ChangeImpact}` |
| GET /operations/stores | page,page_size,q?,region_id?,is_active? | List<Store> (영업지표 없음) |
| POST /operations/stores | `{code,name,region_id,store_type,address:"",reason}` | 201 Store |
| PATCH /operations/stores/{id} | `{version,name?,region_id?,store_type?,address?,is_active?,reason}` | 200 `{store:Store,impact:ChangeImpact}` |
| GET /operations/categories | page,page_size,q?,is_active? | List<Category> |
| POST /operations/categories | `{code,name,description:"",reason}` | 201 Category |
| PATCH /operations/categories/{id} | `{version,name?,description?,is_active?,reason}` | 200 `{category:Category,impact:ChangeImpact}` |
| GET /operations/status | 없음 | ServiceDashboard |
| GET /operations/jobs | page,page_size,status?,error_code?,is_fixture? | List<OperationJob> |
| GET /operations/jobs/{id} | 없음 | `{...OperationJob,attempts:OperationAttempt[]}` |
| POST /operations/jobs/{id}/retry | `{reason}` + 멱등키 | 202 OperationJob, failed만; 잠금/멱등 기록/queued Attempt/감사 원자 생성 |
| GET /operations/audit | page,page_size,actor_id?,target_type?,target_id?,date_from?,date_to? | List<AuditEventDTO>, 수정/삭제 없음 |
| GET /operations/announcements | page,page_size,is_active? | List<Announcement> |
| POST /operations/announcements | `{title,body,severity,starts_at,ends_at:null|timestamp,reason}` | 201 Announcement |
| PATCH /operations/announcements/{id} | `{version,title?,body?,severity?,starts_at?,ends_at?,is_active?,reason}` | 200 Announcement |
| GET /announcements | 없음 | List<Announcement>, 로그인한 모든 역할; 현재 노출기간+활성만 |

`OperatorAccount={id,login_id,display_name,role,region_id,is_active,version,store_ids,created_at,updated_at,mapping_status:"ready"|"missing"|"invalid"}`. mapping_status는 owner/OFC 매핑 없으면missing, 지역/역할과 맞지 않으면invalid, 그외ready. 목록에서 누락 필터 `mapping_status`도 지원한다.

`ChangeImpact={ended_mapping_ids:string[],affected_store_ids:string[],active_session_count:number,new_business_blocked:boolean}`. 역할·매핑 변경은 과거 세션 폐기만으로 해결하지 않고 요청마다 현재 권한을 검사한다. 비활성화 이후 기존 세션도401. 비활성 기준 정보는 신규업무가 차단되지만 과거 이력 보존. 운영 변경폼은 원래 version으로409 재조회 안내.

`OperationJob={id,status,created_at,queued_at,started_at,finished_at,error_code,error_message,attempt_count,current_attempt_id,can_retry,is_fixture}`. submission_id,store 이름,question,photos,context,review 제외. `OperationAttempt={id,attempt_number,status,queued_at,started_at,finished_at,deadline_at,lease_expires_at,error_code,error_message,result_applied}`; 원본 입력/출력·worker파일경로 제외. can_retry=status failed이고 현재 활성attempt 없을 때 true. UI 표시와 무관하게 서버 재검증.

`ServiceDashboard={services:[{name,status,checked_at,heartbeat_at,last_success_at,error_code,is_fixture}],jobs:{queued,running,succeeded,failed},fixture_jobs:{queued,running,succeeded,failed},worker_heartbeat_age_seconds:null|number,model:{readiness:"unknown"|"available"|"unavailable",last_success_at,last_failure_at,last_error_code},data_quality:{unmapped_owner_accounts,unmapped_ofc_accounts,unassigned_stores}}`. 실제/fixture 건수를 분리, 모델 readiness는 최근 실제 실행 상태이며 프로세스 health와 구분한다. polling은 실제 모델을 호출하지 않는다.

`AuditEventDTO={id,actor_id,actor_name,action,target_type,target_id,reason,before_data,after_data,outcome,request_id,created_at}`. `Announcement={id,title,body,severity,starts_at,ends_at,is_active,version,created_at,updated_at}`. 공지는 영업 데이터가 아닌 운영 안내이며 Markdown/HTML 실행 없이 일반 텍스트로 표시한다.

## 8. 대시보드·추이·Mock 상관·기간 집계

공통 `BusinessFilter`: `date_from,date_to`는 inclusive UTC 날짜이고 기본 최근28일, 최대366일; region_id?,store_id?,category_id?,is_active? 선택. is_active는 매장 활성상태 필터이며 dashboard 기본true, 제출·이슈 이력목록 기본생략(모두)이다. dashboard가 반환하는 filters와 drilldown에는 적용된 is_active=true를 포함한다. 이슈 date 필터는 연결된 Submission.created_at을 사용하여 대시보드와 같은 모집단을 유지한다. 기간은 `[date_fromT00:00Z,date_to+1T00:00Z)`로 계산한다. 빈 범위는0 counts/null rates/빈 items를 반환한다. 같은 filters 객체를 요약/목록/상세 링크에 보존한다. 기간의 제출상태는 현재 job 상태이고 완료수는 해당 기간 생성 제출 중 succeeded다.

| 메서드·경로 | 응답 |
|---|---|
| GET /dashboard | `{filters,kpis:{store_count,submitted_store_count,submission_count,queued_count,running_count,succeeded_count,failed_count,needs_ofc_review_count,open_issue_count,compliance_rate,assessable_rate},stores:StoreDashboard[],sample_count,mock_review_count}` |
| GET /analytics/trends | `{filters,points:[{week_start,submission_count,review_count,compliance_rate,assessable_rate,unknown_count,mock_review_count}]}` |
| GET /analytics/correlation | `{filters,mock:true,method:"pearson",n,excluded_missing_count,excluded_unassessable_count,r:null|number,reason:null|"insufficient_samples"|"zero_variance",points:[{store_id,category_id,week_start,compliance_rate,sales_amount,review_count,assessable_rate}]}` |
| GET /analytics/report | `{filters,group_by:"store"|"region"|"category",rows:[{id,name,submission_count,review_count,failed_count,open_issue_count,compliance_rate,assessable_rate,mock_sales_amount,mock:true}],generated_at}` |

영업 역할만 조회. report `group_by` query 기본store. 값은 서버 계산, 프론트에서 다른 데이터로 재산출해 권한/점수를 변경하지 않는다.

`StoreDashboard={store_id,store_name,region_id,submission_count,review_count,failed_count,open_issue_count,compliance_rate,assessable_rate,status,latest_submission_id:null|id,latest_job:null|Job,needs_ofc_review_count,drilldown:{region_id,store_id,category_id,date_from,date_to,is_active}}`. status는 제출없음 `not_submitted`, 미해결 이슈 `needs_attention`, 최신 job queued/running `processing`, failed `technical_failure`, review assessable null/0 또는 needs_ofc_review `unassessable`, 그외 `evaluated`. 별도 counts가 상태 혼재를 유지하며 not_submitted를 위반으로 표시하지 않는다. needs_attention 매장도 최신 job 필드와 이슈에서 구체 사유를 보여준다.

counts/분모: store_count는 현재 권한과 적용된 is_active 필터에 해당하는 매장 수다. GET /submissions와 /issues 기본목록 및 이력 상세는 매장 활성 여부와 무관하게 현재 매핑범위의 과거 기록을 조회한다. 대시보드는 기본 활성매장만 집계하며 drilldown은 그 필터를 목록에 명시해 동일 대상을 유지한다. submitted_store_count=기간 제출한 서로 다른 필터 대상 매장 수. kpi rate는 기간 성공 리뷰의 pass/fail/unknown 총합으로 계산(리뷰 평균의 평균 금지). `sample_count`는 성공 리뷰 수, `mock_review_count`는 그중 mock. needs_ofc_review_count는 그러한 리뷰 개수, open_issue_count는 필터된 제출의 open+in_progress 이슈수이며 GET /issues에 동일필터+unresolved=true로 드릴다운한다. rate0..100 소수1자리, 판단가능 분모0은null.

상관은 store/category/UTC월요일 주차별 non-null compliance 평균과 같은 SalesMock 매출을 inner join한다. 결측/판단불가 제외 수를 반환. n<3 또는 어느 축 분산0이면 r=null 및 reason; null을0으로 바꾸지 않는다. r은 -1..1 소수4자리. 과거 mock 리뷰가 포함된 경우 points/review_count와 화면 Mock 배지로 명시. 상관을 원인·예측으로 서술하지 않는다. 정식 export/스케줄링은 제공하지 않는다.

## 9. 내부 구현 인터페이스와 파일 소유권

G1 이후 공통 구현 이름을 다음으로 고정한다. 도메인 모델·Alembic은 db-schema만 수정, root는 도메인 schemas/service/router를 작성한다. 인증/DB Session 의존성·권한은 화면별로 복제하지 않는다.

- `server/core/config.py`: `Settings`, `get_settings()`; DATABASE_URL, MEDIA_ROOT, SESSION_COOKIE_SECURE, ALLOWED_ORIGINS, AI_SERVICE_URL, AI_SERVICE_TOKEN, 기본 기한 설정.
- `server/core/db.py`: `Base`, `engine`, `SessionLocal`, `get_db()` 요청 단위 yield Session. commit은 서비스에 명시, dependency 종료시 commit하지 않음.
- `server/core/security.py`: `hash_password(password)`, `verify_password(password,hash)`, `hash_token(token)`.
- `server/core/auth.py`: `get_current_account(request,db=Depends(get_db)) -> Account`, `require_csrf(request,db=Depends(get_db))`, `require_roles(*roles)` dependency factory. get_current_account가 현재 활성/역할을 확인하며 플랫폼 운영자에게 영업 권한을 부여하지 않는다.
- `server/core/permissions.py`: `accessible_store_ids(db,account)->list[UUID]` (운영자는 빈값), `require_store_access(db,account,store_id,write=False)->Store` (역할 영업 아닌 경우403·범위밖404), `require_business(account)`.
- 모든 모델은 해당 `server/{domain}/models.py`에서 export한다. `server/core/models.py`는 migration을 위한 전체 모델 import registry이며 개별 모델은 정의하지 않는다. Account/AuthSession=accounts, Region/Store/Category/Mapping=stores, Guideline/Version/ReferencePhoto=guidelines, MediaAsset/Submission/Photo/Context=submissions, Review/Criterion=reviews, Job/Attempt/IdempotencyRecord=analysis_jobs, Issue/Action=issues, Notification=notifications, SalesMock/InventoryMock=analytics, Audit/ServiceStatus/Announcement=operations.
- Pydantic DTO는 각 domain/schemas.py, APIRouter는 domain/router.py의 `router`, 업무 로직은 domain/service.py. 업무 API 앱 조립 server/main.py 소유자는 root. JSON 에러 처리 공통 `core/errors.py`의 `ApiError(status_code,code,message,details=None)`.

클래스명/함수 인터페이스 변경 필요시 문서→수신확인→구현 순서로 전파한다. 현재 본 절은 구현 설계이며 함수 실행 증거가 아니다.

## 10. 계약 검증 경계

인증/CSRF 초기화·회전·만료·로그아웃, 기존 세션 비활성/매핑 감소, 목록·상세·집계·원본·썸네일 동일 범위, 운영자 영업본문 금지, 현재 버전충돌, 후보등록 선점, 다중 파일/한도/decode, 같은 key 재송신/상이 payload, 기준 버전/Reference 과거 보존, queued/running/unknown/실패 표시, retry 동시성/성공보존, issue/notification 수신자, missing/표본부족/분산0 집계를 서버 통합검증으로 확인한다. 5개 시안은 같은 API 요청/필수 업무를 실제 브라우저로 각각 검증하며 API 통과만으로 UI 완료 처리하지 않는다.
