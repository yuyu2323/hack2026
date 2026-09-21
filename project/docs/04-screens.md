# 04. 공통 화면·라우트·상태 계약

- 버전 `1.1-review`, 변경 `PD-002`, 2026-09-21, 소유 product-design.
- 상태: **G1 ACCEPTED** — API 세부 경로·필드 교차 반영 및 독립 지적 재확인 PASS, [확정 기록](../execute/workHitory/docs/contract-register.md). 화면 구현 완료를 의미하지 않는다.
- 근거: [03 요구사항](03-requirements.md), [01 구조](01-architecture.md), [02 실행](02-development-orchestration.md), [10 실행 계약](10-execution.md).
- 공통 데이터 표현은 snake_case, UUID, UTC ISO 시각을 사용한다. UI는 한국어 날짜·시간과 시간대를 표시한다. 목록은 `{items,total,page,page_size}`, 단건은 직접 JSON, 오류는 `{error:{code,message,details},request_id}`를 따른다.

## 1. 패키지·라우팅·권한

각 `web-concepts-01`~`05`는 독립 React/TypeScript/Vite 소스와 한 dev/build/preview 진입점을 갖고, 포트 5173~5177을 사용한다. dev/preview의 `/api` proxy로 같은 업무 API를 호출한다. `packages/api-client`만 공통 세션/CSRF/타입/전송을 담당하며 AI 서버를 직접 호출하지 않는다.

| 소스 영역 | 경로 | 허용 역할 |
|---|---|---|
| src/app | `/login`, `/forbidden`, `/not-found` | 로그인은 공개, 오류 화면은 최소 안내 |
| src/store-owner | `/store-owner/*` | store_owner |
| src/ofc-admin | `/ofc-admin/*` | ofc, regional, hq |
| src/platform-admin | `/platform-admin/*` | platform_operator |

로그인 직후 역할별 루트로 이동한다. 루트가 각 시안의 고유 첫 화면이다. 아래 하위 라우트는 동일 업무의 canonical 경로로 사용하며 시안이 보드/사진 패널/탐색기 배치를 선택할 수 있다. 어떤 시안도 업무 기능을 생략하거나 다른 역할 화면을 공용 메뉴에 섞지 않는다. 직접 URL·새로고침·뒤로가기를 지원한다. 미허용 role은 `/forbidden`, 세션 만료는 `/login`으로 이동하며 로그인 후 return URL은 같은 role prefix의 안전한 경로만 허용한다.

모든 페이지는 최초 사용자 세션 확인 이후 필요한 데이터를 읽는다. 현재 세션/권한 오류가 발생하면 민감한 Query 캐시·열린 이미지 URL을 즉시 폐기한다. 401은 로그인 안내, 403/범위 밖 404는 접근 불가 안내를 제공하고 이전 데이터가 남지 않게 한다. 클라이언트 가드는 편의 기능이며 API/미디어 권한 검사로 대체할 수 없다.

## 2. 화면·업무·데이터 계약

아래 `API 리소스`는 /api 아래 기능별 계약의 연결점이다. 정확한 메서드/요청·응답/오류는 [06 API](06-api.md) 정본에 따른다. 기준·작업 상태의 이름을 화면에서 별도로 정의하지 않는다. §7에 CONTRACT-DATA-1.0 기준 endpoint를 연결한다. 아직 작성자 수정 중인 추가 경로는 그 상태를 명시한다.

| ID / 역할·라우트 | 사용자의 행동·정상 내용 | 필요한 데이터 | API 리소스 / 요구 |
|---|---|---|---|
| S-A01 전체 `/login` | ID·비밀번호로 로그인, 한국어 필드 오류, 역할별 자동 진입 | CSRF·현재 사용자 id/display_name/role/is_active 및 접근 범위; 비밀번호는 메모리 폼에만 | auth csrf/login/me/logout / M02·03 |
| S-O01 점주 `/store-owner` | 연결 매장 선택, 최근 결과·확인할 조치, “사진으로 점검하기”, 알림 | 접근 가능한 store id/name/region/category, 최근 submission/job/review, 미해결 이슈·읽지 않은 알림 수 | stores/categories/submissions/issues/notifications / M09·13·17 |
| S-O02 점주 `/store-owner/submit` | 매장·카테고리→사진 1~5장·질문→제출; parent가 있으면 개선 전 항목 표시 | 활성 store/category, File·사진 순서·선택 질문; parent_submission_id; 접수 submission/job | submissions 생성 / M09·13 |
| S-O03 점주 `/store-owner/submissions/:id` | 대기/분석/실패를 표시, 성공 시 평가·사진·기준·개선 행동, 문의/재제출 | submission photos/question/created_at/parent, job state/timestamps/error, review/기준 snapshot/Reference, children·issues | submissions/jobs/reviews/media/issues / M10~14 |
| S-O04 점주 `/store-owner/history` | 매장·기간·카테고리·상태 검색→상세; 재제출 묶음 표시 | SubmissionSummary, parent_submission_id, job.status, review_summary nullable·source_kind | submissions 목록 / M13 |
| S-O05 점주 `/store-owner/submissions/:id/compare` | 이전/이후 사진·판정·개선 항목 비교→재제출/문의 | parent+child의 사진/날짜/기준 version/criteria·rates·AI follow_up_comparison; 비교 한계 | submissions/reviews/media / M13 |
| S-O06 점주 `/store-owner/issues` | 자기 문의 상태·OFC 대응 읽기, 결과에서 문의 작성 | review/submission 연결, issue status/assignee/action·시각; 사유 | issues / M14 |
| S-B01 영업 `/ofc-admin` | 범위/기간/카테고리 필터→요약·확인 필요 매장→원본; 컨셉별 첫 배치 | scope summary, counts, compliance/assessable·sample, unresolved, no_submission/unknown/failed 분리 | dashboard/stores/categories / M15 |
| S-B02 영업 `/ofc-admin/stores` 및 `/:id` | 담당 목록·최소정보 후보 등록(OFC), 매장 상세·연결·이력/이슈·기준 | store name/region/type/is_active/current assignment; 후보는 id/name/region/type만; 상세 scoped summaries | stores/candidates/claim/submissions/issues / M05·06·13 |
| S-B03 영업 `/ofc-admin/guidelines` 및 `/:id` | level/scope/category/rule 필터, 기준 등록·새 버전·비활성·이력 | id/rule_key/level/scope IDs/version/version_id/text/active/effective metadata; write scope | guidelines/versions / M07 |
| S-B04 영업 `/ofc-admin/references` | 대상 매장/공통·카테고리·캡션·이미지 업로드, 교체/비활성·등록 이력 | Reference(id,lineage_id,version,state_version,caption,category_id,store_id,is_active,photo); photo.source_kind; protected media | references/media / M08 |
| S-B05 영업 `/ofc-admin/submissions` 및 `/:id` | 필터 검색·사진 근거·기준/Reference snapshot·전체 이력·문의 조치로 이동 | O03와 동일 scoped 업무본문 및 store/owner 표시; API 공개 제한 준수 | submissions/jobs/reviews/media/issues / M10~15 |
| S-B06 영업 `/ofc-admin/issues` 및 `/:id` | 확인 필요 목록→담당/조치/상태 변경→후속 결과 확인 | status, reason/type, linked submission/review, assignee, comments/actions chronological, updated_at | issues / M14 |
| S-B07 영업 `/ofc-admin/analytics` | 기간·지역·매장·카테고리 비교, 추이/산점도/표, 기본 기간 집계 | filters, points, review_count, compliance_rate, assessable_rate, n, r nullable, reason, mock, excluded_missing_count, excluded_unassessable_count | analytics / M16 |
| S-P01 운영 `/platform-admin` | API/DB/AI/worker 상태·작업 수→실패/연결 오류 | component availability/checked_at, worker heartbeat, recent model outcome, job counts·fixture origin | operations status/jobs / M18 |
| S-P02 운영 `/platform-admin/accounts` 및 `/:id` | 일반 계정 생성·검색, 활성·역할·지역·연결 변경, 사유 입력·영향 확인 | id/login/display_name/role/is_active/region/mappings/version·safe change summary; create secret 입력은 저장 후 재표시 안 함 | operations accounts/mappings / M04·20 |
| S-P03 운영 `/platform-admin/catalogs` | 지역·매장·카테고리 탭, 등록·수정·비활성, 연결 누락 정정 | master id/name/is_active/region, relation IDs·counts, safe version | operations regions/stores/categories/mappings / M05·20 |
| S-P04 운영 `/platform-admin/jobs` 및 `/:id` | status/error_code/is_fixture 필터→실패 분류·attempt 이력→사유 입력 후 재처리 | OperationJob(id,status,created_at,queued_at,started_at,finished_at,error_code,error_message,can_retry,is_fixture); attempts deadline_at/lease_expires_at/result_applied/error_message | operations jobs/retry / M18·19 |
| S-P05 운영 `/platform-admin/audit` | 대상·수행자·기간 검색, 결과와 안전한 before/after 요약 | AuditEventDTO(actor_id,actor_name,target_type,target_id,action,reason,outcome,created_at,before_data,after_data,request_id) | operations audit / M20 |
| S-P06 운영 `/platform-admin/announcements` | 게시 기간·제목·안내·활성 상태 등록·수정, 게시 미리보기 | announcement ID/title/body/start/end/active/version | operations announcements / S01 |
| S-C01 점주·영업 `<prefix>/notifications` | 수신 알림 목록→읽음→현재 허용 대상 이동 | Notification(id,kind,title,target,read_at,created_at), unread_count; 운영자는 영업 알림 메뉴·라우트·API 요청을 제공하지 않음(운영 공지는 별도 유지) | notifications / M17 |
| S-C02 로그인 후 각 shell | 현재 유효 공지 확인, 닫기(현재 화면 세션 수준) | title/body/start/end; HTML 실행 금지 plain text | announcements / S01 |

OFC·지역·본사의 화면 이름은 동일하되 범위 헤더는 각각 “담당 매장”, “○○ 지역”, “전체 매장”이다. 서버 허용 범위만 선택기에 제공한다. HQ 기준 생성은 HQ, 지역 기준은 해당 regional/HQ, 매장·매대 기준/Reference는 담당 OFC 및 상위 범위 영업 역할만 표시·허용한다. 플랫폼 기준 정보는 진열 가이드라인과 별개 화면이다.

## 3. 모든 화면의 정상·빈·로딩·오류 상태

`N/E/L/X`는 아래 화면군별로 모두 구현한다. 빈 값과 오류 값을 숫자 0으로 바꾸지 않는다. 저장 성공 후 서버 결과를 다시 읽고 해당 목록/상세/요약 캐시를 무효화한다.

| 화면군 | N 정상 | E 빈 상태 | L 로딩 | X 오류·복구 |
|---|---|---|---|---|
| 로그인 | 필드/로그인 버튼 | 입력 전 설명 | 로그인 버튼 busy·중복 방지 | 자격 오류는 계정 존재 여부 노출 없이 공통 안내, CSRF 갱신·재시도 |
| 점주 홈/매장·카테고리 선택 | 선택 범위+최근 작업 | 연결 매장 없음: 운영자에게 연결 요청 안내; 카테고리 없음: 제출 불가 이유 | 선택기 skeleton·disabled | 조회 재시도, 캐시된 타 계정 데이터 금지 |
| 제출·Reference 업로드 | 실제 미리보기·이름·용량·제거·순서 | 촬영 가이드와 파일선택 | 업로드 표시·제출 잠금, 브라우저 지원시 전송률 | MIME/디코딩/장수/용량/질문 필드 오류; 값/사진을 유지; 타 범위/비활성 시 선택 재조회 |
| 제출 상세·분석 | 사진·결과·기준·이력 | 기준/Reference 없음 이유; 평가 없는 작업은 상태 표시 | queued/running 문구·실제 경과, 30초 후 지연 안내 | failed 안전한 오류/운영자 복구 안내; polling 네트워크 실패는 분석실패로 바꾸지 않고 “상태를 다시 확인” |
| 평가·비교 | 항목별 판정·근거·행동 | 결과 없음/비교 부모 없음/판단가능 기준 없음 | 사진 비율을 보존한 placeholder·결과 skeleton | 미디어 실패는 다시보기; unknown은 정상 카드+제한/재촬영/OFC 문의 |
| 목록·검색·알림·이슈 | 행·필터·페이지·상세 이동 | “조건에 맞는 항목이 없습니다”+필터 초기화, 최초 없음은 적절한 생성 CTA | 처음 skeleton, 갱신은 기존 rows+갱신중 표시 | retry 및 request_id; 성공 후 새 권한 상태 재검증 |
| 기준·계정·master 폼 | 필드·권한별 변경·변경 사유 | 최초 등록 안내; 연결 누락 배지 | 저장 busy·중복 방지 | version 충돌은 최신정보 다시읽기·사용자 입력 유지, 데이터 강제덮어쓰기 금지 |
| 영업 관제·분석 | 지표→필터 동일 목록, 차트와 표 | 미제출/표본 부족/분산 0/결측 사유 | 지표 skeleton, 가짜 0/100% 금지 | 섹션별 오류 범위 표시, 잘못된 집계로 대체 금지 |
| 운영 상태·jobs | 실제 체크시각·heartbeat·attempts | 최근 작업 없음; 미확인 상태는 unknown | 갱신중, 이전 체크시각 유지 | API down·AI unavailable·worker stale 분리, 재시도; 모델 호출을 health로 자동 재실행 금지 |
| 재처리·비활성·연결 변경 | 영향 요약+필수 사유+실행 | 재처리할 실패 없음 | 요청 진행중 버튼 잠금 | 409는 현재 state 재조회; 재시도 가능 여부 새로 판단; idempotency 유지 |
| 운영 감사/공지 | 안전 요약·게시 기간 | 이력/유효 공지 없음 | 목록/폼 상태 | 권한 오류 즉시 비우기, 업무 본문/원시 stderr 노출 금지 |

오류 응답의 원시 stack/CLI stderr를 화면·개발자용 확장 패널에 넣지 않는다. 화면은 `error.message` 안전 문구와 필요시 `request_id`만 보여 준다. 프론트가 실패를 숨기려고 seed나 고정 평가로 fallback하지 않는다.

## 4. 결과 및 비동기 UX 상세

AI-001 결과는 SubmissionDetail.review.result의 ModelResult이며 필드는 `schema_version`, `question_answer`, `summary`, `overall_confidence(high|medium|low)`, `criteria[{guideline_id,version_id,version,rule_key,verdict(pass|fail|unknown),reason,evidence[{photo_position,observation}],actions}]`, `reference_comparisons[{reference_id,verdict(similar|different|unknown),photo_positions,observation}]`, `limitations`, `ofc_review_required`, `follow_up_comparison`이다. `compliance_rate/assessable_rate/pass_count/fail_count/unknown_count/needs_ofc_review/source_kind`는 모델 텍스트가 아닌 Review 외곽의 서버 검증·집계 값이다.

- 사진 번호는 1부터 시작하며 화면 미리보기·근거·Reference 비교에서 동일하다. Evidence 선택은 해당 사진으로 초점을 옮길 수 있으나 모델이 제공하지 않은 bounding box를 꾸며 표시하지 않는다.
- 서버의 `compliance_rate`와 `assessable_rate`를 같이 표시하고 판단 가능한 수/전체 수를 읽을 수 있게 한다. null은 `—`와 이유. unknown·낮은 신뢰·기준/Reference 누락·모델 요청을 합친 서버 `needs_ofc_review`에 따라 OFC 확인 CTA를 제공한다.
- “판단 불가”는 회색 중립, “개선 필요”는 주황, “준수”는 녹색과 텍스트를 함께 쓴다. 모델 신뢰도는 확률로 바꾸지 않는다. AI 원문 수정 기능은 없다.
- job은 queued→running→succeeded/failed, attempts는 과거 기록을 보존한다. 2초 polling, 성공/실패/권한 철회에서 정지, background 복귀 시 즉시 재조회. 같은 제출 재접속은 기존 job을 조회하며 새 작업을 생성하지 않는다.
- 30초 초과는 “분석에 시간이 더 필요해요. 이 화면을 나가도 이력에서 확인할 수 있어요.”로 표시한다. 목표를 확정 완료시간처럼 약속하지 않는다. 대기 180초, 모델 120초, worker HTTP 130초와 lease 규칙은 처리 계약을 따른다.
- 네트워크 타임아웃 후 사용자가 전송 재시도할 때 동일 제출 payload/중복 키를 유지한다. 성공 응답 수신 전 새 키로 반복 제출하지 않는다. parent 재피드백은 새 제출·새 키이며 원본 job 재처리와 다르다.
- 비교는 photo/date/기준 version/항목별 변화가 주 대상이다. 적용 기준이 달라졌으면 “적용 기준이 달라 단순 점수 비교에 주의가 필요합니다”를 표시하고 공통 rule_key의 근거를 확인한다.

## 5. 공통 접근성·반응형·문구

- 문서 언어 ko, 한 화면 h1 하나, semantic nav/main/form/table, 입력 label/description/error 연결, 아이콘만 있는 버튼은 accessible name 필수.
- 키보드로 로그인→필터→사진선택→제출→결과→이슈/재제출에 접근 가능. 파일 선택에는 일반 input 대안을 둔다. drag-and-drop만 요구하지 않는다. dialog는 제목·초점 가두기·Esc·트리거로 복귀, route 이동은 h1/주요 내용 초점 처리.
- 일반 본문 대비 4.5:1 이상, 큰 글자/상태 아이콘/컨트롤 테두리 3:1 이상 목표. 색만으로 판정·상태·차트 계열을 구분하지 않는다. 키보드 focus는 2px 이상 분명한 외곽선.
- 점주 주요 조작은 최소 44×44px. 데스크톱 보조 아이콘은 최소 32×32px이며 44px 터치 영역을 확보한다. 200% 확대와 390×844/1440×900에서 주요 업무 사용 가능. 페이지 전체 가로 스크롤은 금지하고 큰 비교표만 제목/안내가 있는 수평 영역으로 제한한다.
- 사진은 원본 비율 유지, 분석 근거 화면은 object-fit:contain. 목록의 정사각 썸네일은 상세에서 전체 이미지 확인 가능해야 한다. 이미지의 alt는 카테고리/용도/사진번호·촬영시각 등 메타데이터로 작성하고 AI 판정을 정답처럼 쓰지 않는다.
- chart는 요약과 데이터 표를 제공하고 null 구간은 연결해 정상 추세로 만들지 않는다. 필터/범례는 명칭과 상태가 읽혀야 한다.
- async 상태에는 aria-live=polite를 쓰며 2초마다 같은 문구를 읽지 않는다. 오류 요약은 제출 후 한 번 초점을 받는다. 단순 배경 갱신으로 초점을 빼앗지 않는다.
- 업무 용어: “진열 기준”, “Reference”, “제출 사진”, “판단 불가”, “기술 실패”, “OFC 확인 필요”. 운영 “기준 정보”는 지역·매장·카테고리라는 부제를 붙인다.
- 버튼 문구는 “사진 제출하기”, “개선 후 다시 제출”, “OFC에 확인 요청”, “변경 저장”, “실패 작업 재처리”. 실패 업무와 새 현장 사진 제출을 같은 “다시 시도”만으로 표시하지 않는다.
- 생성 이미지와 Mock 매출/과거 fixture는 각각 “AI 생성 시연 이미지”, “Mock 데이터” 배지. 실제 분석의 source 표시와 별개다. 운영 fixture에는 “Mock 장애 사례” 표시하며 실제 서비스 상태와 섞지 않는다.

## 6. 시안별 독립 정보 구조와 완료 범위

| 시안 | 첫 화면/탐색/데이터 표현 | 점주·영업·운영 동선 차별화 | 상세 디자인 정본 |
|---|---|---|---|
| 01 관제 | 고정 사이드바, 상단 범위필터, KPI 스트립, 밀도 있는 table→근거 detail | 점주 최근상태 표에서 제출; 영업 지표→담당매장→사진; 운영 상태표→실패 attempt | [brief](../execute/design/concept-01/brief.md), [design](../execute/design/concept-01/design-spec.md), [acceptance](../execute/design/concept-01/acceptance.md) |
| 02 오늘 할 일 | 우선순위 queue/단계 lane, 업무 카드, 오늘 처리할 항목 먼저 | 점주 다음 행동 카드; 영업 검토→조치→후속; 운영 연결 오류/실패 복구 할일 | 전담 디자이너 작성 예정, 미확정 |
| 03 사진과 근거 | 사진 contact sheet→분할 이미지/근거 inspector, visual timeline | 점주 사진·판정 연결; 영업 Reference/제출 비교; 운영에는 사진 대신 요청/attempt 관계 타임라인 | 전담 디자이너 작성 예정, 미확정 |
| 04 모바일 현장 | 큰 터치·짧은 단계·진행표시, bottom navigation | 점주 매장→사진→질문→확인; 영업 검토 카드별 안내; 운영 변경/재처리 단계별 확인 | 전담 디자이너 작성 예정, 미확정 |
| 05 탐색과 비교 | region/store/category 탐색 panel, 저장 가능한 filter 상태, 비교 workspace | 점주 이력 탐색→다시제출; 영업 여러 대상 추이/근거비교; 운영 조직/계정 연결 탐색 | 전담 디자이너 작성 예정, 미확정 |

5개 시안 모두 §2의 모든 화면·권한·상태를 제공한다. 색/폰트/로고만 바꾸거나 동일 페이지의 테마 selector로 대체하면 AT-01/22 실패다. 공통 API·접근 가능한 basic controls는 공유해도 각 시안의 페이지 구성·스타일·탐색은 독립 소스여야 한다.

## 7. 실제 API 연결표

아래는 `/api` prefix를 생략한 CONTRACT-DATA-1.0b 교차표다. 독립 검토에서 발견한 상세/후보/필터 누락과 Reference 수정충돌 버전을 작성자 수정본으로 재확인했다. 상세 검토는 별도 독립 보고를 참조한다.

| 화면 | 메서드·경로 | 반환 및 변경 후 재조회 |
|---|---|---|
| A01·모든 shell | GET /auth/csrf, POST /auth/login, GET /auth/me, POST /auth/logout | AccountMe·회전된 CSRF, 로그아웃/권한 철회시 업무 캐시 폐기 |
| O01/O02/B02 | GET /stores, /stores/{id}, /categories, /regions | List<Store/Category/Region>, Store; roles/scope는06 정본 |
| B02 담당 등록 | GET /stores/candidates, POST /stores/{id}/claim | 후보 List 최소정보, Store; stores/dashboard/me 무효화 |
| O02/B04 파일 | POST /submissions, POST /references | multipart metadata+photos(반복) 또는 photo; 파일/질문 한도 검증 |
| O03/O04/B05 | GET /submissions, /submissions/{id}, /jobs/{id} | SubmissionSummary/Detail·Job; detail 안 context/review/parent/children/issues |
| O05 | GET /submissions/{id}/comparison | parent/current/criteria/narrative; side 추가 날짜/버전은 원본 detail로 조회 |
| O03/O05/B04/B05 | GET /media/{id}?variant=original 또는 thumbnail | 권한 검증 이미지 bytes; URL 원문 아닌 ID 기반 |
| B03 기준 관리 | GET/POST /guidelines, GET /guidelines/{id}, GET/POST /guidelines/{id}/versions, PATCH /guidelines/{id} | List<Guideline>/Guideline/versions; list/detail 무효화, 과거 review 유지 |
| B04 Reference | GET/POST /references, GET /references/{id}, PATCH /references/{id}, PATCH /references/{id}/status | Reference; 교체는 새 revision ID, 목록 무효화 |
| O06/B06 | GET/POST /issues, GET/PATCH /issues/{id}, GET /issues/{id}/assignees, POST /issues/{id}/actions | IssueSummary/Issue/Action·배정 후보; issues/detail/notifications/dashboard 무효화 |
| C01 (점주·OFC·지역·본사) | GET /notifications, POST /notifications/{id}/read | List+unread_count/Notification; 읽음 시각은 재요청에도 유지 |
| B01 | GET /dashboard | filters/kpis/stores/sample_count/mock_review_count; 같은 조건 drilldown |
| B07 | GET /analytics/trends, /analytics/correlation, /analytics/report | points 또는 rows·rates·n/r/reason, mock 표시 |
| P02 | GET/POST /operations/accounts, GET/PATCH /operations/accounts/{id}, PUT /operations/accounts/{id}/mappings | OperatorAccount 또는 account+impact; accounts/catalog/audit 무효화 |
| P03 | GET/POST /operations/{regions\|stores\|categories}, PATCH /operations/{regions\|stores\|categories}/{id} | master 또는 master+impact; catalog/accounts/audit 무효화 |
| P01/P04 | GET /operations/status, /operations/jobs, /operations/jobs/{id}; POST /operations/jobs/{id}/retry | ServiceDashboard, OperationJob+attempts; jobs/status/audit 무효화 |
| P05 | GET /operations/audit | List<AuditEventDTO>, 수정/삭제 없음 |
| P06/C02 | GET/POST /operations/announcements, PATCH /operations/announcements/{id}, GET /announcements | Announcement 목록/단건; 공지·감사 무효화 |

변경은 X-CSRF-Token과 허용 Origin을 사용한다. 제출/담당등록/문의생성/재처리는 Idempotency-Key를 유지하고 일반 PATCH/PUT에는 조회한 version을 넣는다. Reference만 내용 revision인 version과 수정용 state_version을 분리하므로 PATCH metadata/status에 state_version을 보낸다. Reference 교체 후 반환된 새 id/version/state_version으로 갱신하고 과거 revision 수정409는 최신 lineage 조회로 복구한다. 재처리 POST는 reason+키다. 로그인 전에도 CSRF를 발급한다. 권한·버전·멱등 오류 처리는 06 §1~2를 따른다.

`BusinessFilter`의 date_from/date_to는 UTC inclusive 날짜이며 화면 필터에 “조회 기준: UTC 날짜”를 명시한다. 표시 시각은 Asia/Seoul임을 함께 설명한다. dashboard 기본 활성매장 조건(is_active=true)을 포함한 반환 filters/drilldown을 submissions/issues에 그대로 전달한다. 이슈 날짜는 연결된 제출의 생성시각 기준이다. 미제출 KPI는 제출목록이 아닌 매장표의 not_submitted 상태로 연결한다. 미해결 이슈 KPI는 동일필터와 unresolved=true로 GET /issues를 조회해 open+in_progress 모집단을 유지한다. unresolved와 status는 함께 전송하지 않는다(422). 현재 검토 이력은 [독립 데이터 검토](../execute/workHitory/product-design/independent-data-review.md)에서 관리한다.

## 8. 구현·검수·매뉴얼 인계

프론트 담당자는 03/04 및 해당 concept 디자인 버전을 체크리스트에 적고 G1 확정 후 구현한다. 단위/UI 테스트의 Mock 화면은 개발용으로 표시하며 완료 전에 실제 API로 연결한다. 기능 QA는 AT-01~24/S01~02를 시안별로 실행하고 실제 AI 필수 경로를 확인한다. 디자인 QA는 작성/개발/기능QA와 별도 담당자가 실제 페이지로 §5 및 concept acceptance를 검수한다.

매뉴얼 담당은 각 role 루트·실제 메뉴/버튼·경로·오류·빈 상태·unknown 및 운영자 영업 접근 제한, 사진/기준/이력 연결을 캡처한다. 적어도 점주 mobile(홈/제출/결과), 영업 desktop(관제/근거/기준/이슈/분석), 운영 desktop(상태/계정/재처리/감사) 화면을 해당 시안에서 확보한다. 최종 수정 후 캡처를 갱신하고 비밀번호/세션/실제 영업정보가 없는지 별도 확인한다.

### PD-003 / WEB01-004 운영자 영업 알림 경계

2026-09-21 조정자 독립 검토를 반영했다. `/platform-admin/notifications`는 화면 계약에 포함하지 않으며 운영자 shell에도 영업 알림 링크가 없다. 점주·영업 알림 및 공통 운영 공지는 유지한다.
