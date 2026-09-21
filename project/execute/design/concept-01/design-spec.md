# Concept 01 — 관제 데스크 디자인 명세

- 버전 `1.1-review`, `DS01-002`, 2026-09-21.
- 상태: **G1 ACCEPTED** — 독립 문서 검토 및 조정자 확정, 실제 UI 검수는 후속 G4.
- [brief](brief.md) / [공통 화면](../../../docs/04-screens.md) / [검수 기준](acceptance.md).
- 공통 화면의 모든 S-* 기능·4상태·권한을 적용한다. 여기서는 배치·토큰·문구를 구체화한다.

## 1. 룩앤필·토큰

흰 작업 면, 청록의 주요 행동, 짙은 남색 텍스트와 선으로 구획한 표를 사용한다. 진열 사진 자체가 시각적 정보이며 장식 사진·큰 gradient·불필요한 animation을 넣지 않는다.

| 토큰 | 값 | 사용 |
|---|---|---|
| color.canvas | #F4F7F9 | 전체 배경 |
| color.surface | #FFFFFF | 표·폼·결과 패널 |
| color.ink | #142C3D | 제목/본문 |
| color.muted | #526574 | 보조 문구 |
| color.border | #D5DEE5 | 구획/표 행 |
| color.control-border | #7A8994 | input/select/secondary button의 흰 면 경계 (3:1 이상) |
| color.primary | #006C67 | 주요 버튼/선택 링크 |
| color.primary-hover | #005651 | hover/pressed |
| color.primary-soft | #E7F3F1 | 현재 메뉴/선택 row |
| color.pass / pass-bg | #17633B / #E9F5EC | 준수 텍스트/배지 |
| color.fail / fail-bg | #874500 / #FFF3DE | 개선 필요 |
| color.error / error-bg | #AB2332 / #FDECEF | 기술실패/입력오류 |
| color.unknown / unknown-bg | #52616E / #EEF1F4 | 판단 불가/미확인 |
| color.focus | #1A65CF | 3px focus outline, offset 2px |
| font.family | system-ui, -apple-system, BlinkMacSystemFont, "Noto Sans KR", sans-serif | 외부 웹폰트 필요 없음 |
| type.page / section / body / label / meta | 28/36 700, 20/28 650, 16/24 400, 14/20 600, 13/20 400 | px size/line-height weight |
| type.metric | 30/36 700, tabular-nums | 지표; 단위 14px |
| space | 4, 8, 12, 16, 24, 32, 48px | 토큰 배수로 배치 |
| radius.panel / control / badge | 10 / 6 / 4px | 카드 과다 사용 억제 |
| shadow.dialog | 0 8px 28px rgba(20,44,61,.16) | dialog만; 표면은 1px border |

작은 글자 색 대비는 실제 렌더 후 검사한다. 배경이 연한 상태배지 안에 진한 글자와 상태 아이콘/문구를 함께 쓴다. 녹색 성공과 붉은 오류를 색만으로 구별하지 않는다.

## 2. Shell·반응형

### Desktop ≥1200px

- 좌측 224px sidebar, 상단 brand 64px. sidebar는 role별 메뉴만; 현재 메뉴는 primary-soft 면과 좌측 3px 선/aria-current.
- 우측 topbar 높이 64px: 현재 역할·범위, 점주·영업 알림, 사용자·로그아웃(운영자는 영업 알림 제외). 본문 max-width 1440px, 좌우 32px/상하 24px.
- breadcrumb 13px → h1+설명+우측 primary action → 16px 간격 → filter bar → 24px → 핵심 내용.
- 페이지 본문 내부 12-column grid, gap 24px. KPI strip은 4칸(관제), 운영 가용상태는 4칸. 제출상세는 사진 5/평가 7; 상세 보조 기준·이력은 다음 full width 행.

### Tablet 768~1199px

- sidebar 72px 아이콘 rail, accessible label/tooltip 제공. 본문 padding 24px. 긴 메뉴명은 drawer에서 읽을 수 있다.
- KPI 2×2, filter wrap, 사진/평가 1열 전환(≥1024px면 2열 허용). 주요 table은 열 우선순위 유지하고 필요한 열만 좁은 scroll container.

### Mobile <768px

- topbar 56px: 메뉴 버튼·StoreLoop·점주/영업 알림. sidebar는 drawer로 열리고 닫을 때 트리거 초점 복귀.
- 점주 bottom nav 높이 64px + safe-area: 현황/사진 제출/이력/문의, 각 44px 이상. 하단 고정 CTA가 있을 때 nav 위에 배치하고 본문 padding-bottom으로 가림 방지.
- 본문 padding 16px, h1 24/32, 사진/평가/폼 모두 단일 열. KPI 2열, full width action. 점주 제출이력은 표를 상태/날짜/카테고리 row card로 전환.
- 관리자 8열 비교표는 독립 scroll region+“표를 좌우로 이동할 수 있습니다” 안내; 필터는 접기 가능하나 적용조건 summary는 항상 보인다. 기본 작업 버튼을 가로 바깥에 숨기지 않는다.
- 390px 기본, 320px 최소에서 body 가로 스크롤 없음. 200% 확대 시 동일 reflow 규칙.

## 3. 화면별 구체 배치

### 3.1 로그인 (S-A01)

Desktop 420px 폭 form을 중앙 정렬하고 위에 StoreLoop/“관제 데스크”를 둔다. 제목 “매장 운영을 한눈에 확인하세요”는 설명이며 폼에는 ID/비밀번호/로그인만 표시한다. 역할 버튼으로 로그인하지 않는다. 제출 후 오류는 form 상단 summary와 필드 설명으로 연결한다. 비밀번호 보기 버튼은 누를 때만 표시 상태를 바꾸며 값 저장/로그 금지.

### 3.2 점주 홈·이력 (S-O01/O04/O06/C01)

첫 행에 선택 매장 dropdown과 “내 매장 현황”. 이어 primary “사진으로 점검하기”와 3개 상태 요약(분석 중/최근 준수율+판단가능률/확인할 문의). 그 아래 최근 제출 표 열은 `제출 시각 | 카테고리 | 상태 | 준수율/판단 가능률 | 확인`이다. 마지막에 최근 OFC 조치 2~3건과 전체보기. 빈 홈은 촬영가이드+첫 제출 CTA, 연결 없음은 제출 CTA disabled 이유와 연결 안내.

이력은 동일 열·필터(매장/기간/카테고리/상태)와 페이지 이동을 제공한다. parent 관계는 “재제출” 텍스트+연결 링크로 표시하며 들여쓰기 트리로 무한 확장하지 않는다. 문의/알림은 별도 목록으로 읽음·상태를 명시하고 목록 row의 링크와 읽음 버튼을 구분한다.

### 3.3 점주 사진 제출 (S-O02)

Desktop 8/4 grid: 왼쪽 한 페이지 form, 오른쪽 촬영 도움말 및 parent 개선 항목. 단계 wizard로 분할하지 않는다. form 순서는 매장·카테고리 → 사진 영역 → 선택 질문 → 적용 정보 안내 → 제출 CTA. 사진 타일 120×120 썸네일(상세확대 가능), 번호/파일명/용량/제거/앞뒤 이동 control. 모바일 2열 타일, 질문은 textarea 5행, 글자수 0/2,000.

촬영 도움말: “매대 전체와 상품 앞면이 보이게 촬영해 주세요”, “흔들리지 않게 밝은 곳에서 촬영해 주세요”. 사진은 분석 원본을 보존하며 UI crop을 업로드 원본에 적용하지 않는다. 제출 버튼 바로 위 “AI는 1차 검토를 돕습니다. 판단이 어려운 항목은 OFC가 확인합니다.” 안내.

### 3.4 제출 상세·결과·비교 (S-O03/O05/B05)

상단 breadcrumb/매장·카테고리·제출일·상태·생성 이미지 배지. 그 아래 사진/평가 5:7 배치. 사진은 큰 contain image(최소높이 320px)와 번호 있는 thumbnail strip, “사진 n/N”. 평가 상단은 질문 답변 → 요약 → 준수율/판단 가능률/신뢰도 → 기준별 표 순서. 표 열 `진열 기준/버전 | 판정 | 관찰 근거 | 개선 행동`. 행 확장은 사진근거·Reference 비교·limitations를 드러낸다. 주요 개선점은 fail, 확인 필요는 unknown, 우수한 점은 pass 필터로 볼 수 있으나 기본 전체 항목을 제공한다.

진행 상태에서는 평가 영역에 대기/분석 아이콘과 경과 시간·지연 설명을 표시한다. 실패에서는 붉은 panel과 안전 오류, “상태 다시 확인”, “OFC 문의”를 제공하고 가짜 결과 skeleton이 계속 돌아가지 않는다. unknown 성공은 정상 결과 구조를 유지한다.

결과 하단 primary “개선 후 다시 제출”, secondary “OFC에 확인 요청”. 영업 역할에서는 primary “조치 기록하기”. 하단 full width 탭은 `적용 기준·Reference | 제출 이력 | OFC 대응`이며 탭은 키보드 arrow/Home/End와 활성 panel 연결을 지원한다.

비교는 desktop 이전/이후 두 열에 각각 사진·날짜·준수율/판단가능률, 아래 공통 rule_key 변화표. 모바일은 “이전/이번” 선택 탭 또는 세로 2개 섹션, 날짜가 항상 보인다. 기준 버전 차이를 노란 안내문으로 명시한다. Reference는 평가 제출과 별도 “Reference” 라벨을 유지한다.

### 3.5 영업 관제·매장 (S-B01/B02)

첫 화면 뼈대:

```text
범위: 담당 매장 / ○○지역 / 전체 매장        관제 현황
[기간] [지역*] [매장] [카테고리] [적용] [초기화]
담당 매장  | 기간 내 제출 | OFC 확인 필요 | 미해결 문의
-----------------------------------------------------
확인 필요 매장 [상태 필터] [검색]        n개 중 n개
매장 | 제출/완료 | 최근 결과 | 준수/판단률 | 확인 사유 | 열기
...
-----------------------------------------------------
최근 운영 추이 (표본 표시)       미제출/판단 불가 설명
```

`지역*`은 현재 권한에서 가능한 값만 표시한다. KPI 선택은 같은 조건의 목록으로 이동하고 적용 조건 chips를 유지한다. “확인 사유”에는 기술실패/판단불가/미해결문의가 각각 구분된다. 미제출은 중립 상태다. 행 전체 click을 쓰더라도 명시적 “근거 확인” 링크를 제공한다.

매장 페이지는 목록 상단 후보등록(OFC만) secondary action. 후보 모달에는 최소정보만, 등록 후 목록을 다시 읽는다. 매장 상세 header+연결/활성 요약, 아래 `제출 이력/진열 기준/Reference/확인 필요`를 제공한다. 영업용 매장본문에는 계정·운영자 권한 편집을 넣지 않는다.

### 3.6 기준·Reference (S-B03/B04)

기준은 `level/대상/카테고리/rule_key/현재 버전/상태` table, 우측 420px drawer 또는 별도 detail에서 본문·버전 목록을 읽고 새 버전 저장. 본문 textarea는 최소 8행. 저장 버튼은 “새 버전 저장”, 비활성은 별도 사유 dialog. 자신에게 없는 scope는 폼 옵션에 없다. 상위 범위 read 권한과 write 권한이 다르면 “읽기 전용” 표시.

Reference는 160px 이미지 thumbnail+caption/category/대상/수정시각 table/list. 등록 폼은 사진·캡션·카테고리·공통/허용 매장으로 구성. 교체는 새 revision이 됨을 안내하고 이전 평가 사진 유지 문구. 이미지 전면 gallery가 주 탐색인 03과 구별되게 관리 표를 주 영역으로 둔다.

### 3.7 이슈·분석 (S-B06/B07)

이슈는 상태/매장/기간 table→detail. detail 상단 연결 제출·담당·상태, 중앙 chronology(시각/수행자/조치)와 readonly AI 평가 링크, 하단 조치 textarea와 허용 상태 변경. 저장 후 새 action과 updated_at 확인. AI 평가를 직접 수정하는 input은 없다.

분석은 필터 아래 2개 panel(주별 준수율·판단가능률 추이 / Mock 매출 상관 산점도), 하단 기간 집계 table. 각 chart 제목 바로 옆 표본 수·Mock 배지·계산 제한 표시. “표 보기”로 같은 값을 읽을 수 있다. null 구간은 끊고, 표본부족은 빈 chart 축 대신 이유 panel을 사용한다. 인과·예측이라는 문구를 쓰지 않는다.

### 3.8 운영 상태·작업 (S-P01/P04)

상단 “플랫폼 운영”+“계정과 서비스 처리 상태” 부제, 4열 가용상태(API/DB/AI 프로세스/worker), 아래 job 수 strip, 그 아래 실패 목록. AI 프로세스 상태와 최근 모델 실행 상태는 서로 다른 줄. fixture는 명확한 “Mock 장애 사례” 그룹으로 실제 health와 분리한다.

작업 상세는 `job ID/상태/시각/오류 분류/설명` definition list, `attempt ID/대기·시작·종료/기한/상태/반영 여부` 표. UUID는 줄바꿈 또는 copy 버튼; 비밀 값이 아닌 식별자만 복사한다. 질문·사진·모델 결과·CLI stderr 필드는 없다. 실패 종료에서만 primary “실패 작업 재처리”; dialog에 동일 입력 재사용·이전 시도 보존·필수 사유. 진행/성공이면 버튼 disabled+이유. 409는 최신 상태를 읽고 복구한다.

### 3.9 운영 계정·기준 정보·감사·공지 (S-P02/P03/P05/P06)

계정 목록 열 `이름/로그인 ID/역할/소속/연결/상태/수정`. 상세 기본정보+활성/역할·지역+연결목록. 변경 영향 요약에 제거/추가 범위와 기존 로그인에도 반영됨을 표시하고 사유 입력 후 저장. 플랫폼 운영자 역할을 생성/승격하는 옵션 없음. 비밀번호 입력은 새 계정 생성에 필요한 경우만, 저장 후 응답/토스트에 노출 안 함.

기준 정보는 지역/매장/카테고리 탭과 목록·편집 drawer. 사용 중 대상은 삭제 대신 비활성, 과거 기록 유지·신규 선택 제외 설명. 연결 누락은 텍스트 배지+필터. 감사는 actor/target/action/time/result/reason table 및 안전 before/after만. 공지는 제목/기간/활성 table, plain text 본문 편집·미리보기. 유효 공지는 shell 제목 위 정보 strip으로 표시한다.

## 4. 공통 컴포넌트·4상태

- Button: min-height 44px primary/secondary/tertiary, disabled는 비활성 이유를 주변 설명으로 제공. busy는 spinner+현재 행동을 나타내는 문구, width 유지.
- Input/select: 높이 44px, color.control-border 1px 경계, label 14px 위 8px, hint/error 아래 4px. secondary button도 control-border를 사용한다. 필수 별표는 텍스트 “필수”와 함께 설명. 긴 label wrap. 입력 오류는 색+아이콘+텍스트.
- Table: header 40px, row min 56px, padding 12px, tabular numeric, 열 제목 명확. 셀 2줄 이상은 행 높이를 늘린다. 업무 근거는 말줄임만으로 숨기지 않고 펼치기 제공. 20 rows 기본·페이지당 20/50 선택, API page_size 한도 준수.
- Status: label+아이콘, queued “분석 대기”, running “분석 중”, succeeded “분석 완료”, failed “기술 실패”; criterion pass “준수”, fail “개선 필요”, unknown “판단 불가”. 두 종류 상태를 같은 열 이름으로 혼동하지 않는다.
- Empty: small icon+한 문장 이유+허용 CTA. 필터 빈 결과에는 필터 초기화, 연결 없음은 연결 안내, 표본 부족은 데이터 이유.
- Loading: 3~5개 skeleton row(aria-hidden), 영역 aria-busy. 실제 데이터 갱신 시 기존 내용+checked_at 유지. 가짜 수치를 그리지 않는다.
- Error: panel/inline alert, 안전 문구·다시 조회, request_id는 보조 텍스트. 기술실패와 네트워크 조회실패, 정상 unknown을 구분.
- Toast: 저장 성공/알림 읽음 결과만 5초, aria-live polite. 중요한 실패/권한 변화/개선 행동을 일시 toast에만 넣지 않는다.
- Dialog/drawer: 제목, 설명, cancel/confirm, modal focus, Esc, 닫힌 뒤 trigger 복귀. 업무 삭제 dialog 없음.

## 5. 문구·긴 데이터·성능 표시

| 상황 | 실제 문구 |
|---|---|
| 제출 접수 | “사진을 접수했어요. 분석 결과는 제출 이력에서도 확인할 수 있어요.” |
| 30초 지연 | “분석에 시간이 더 필요해요. 이 화면을 나가도 이력에서 확인할 수 있어요.” |
| 판단 불가 | “사진만으로 판단하기 어려운 항목이 있어요. 촬영 안내를 확인하거나 OFC에게 문의해 주세요.” |
| 기술 실패 | “분석을 완료하지 못했어요. 제출 기록은 보관되어 있으며 운영자가 처리 상태를 확인할 수 있어요.” |
| 기준 변경 | “새 버전이 저장되었습니다. 이후 제출부터 적용되며 이전 평가의 기준은 유지됩니다.” |
| 운영 변경 | “변경 사항을 저장했습니다. 기존 로그인에도 현재 접근 범위가 적용됩니다.” |
| 재처리 | “같은 입력으로 다시 분석합니다. 이전 시도 기록은 유지됩니다.” |
| 분석 해석 | “Mock 매출을 사용한 상관관계입니다. 매출 원인이나 예측을 뜻하지 않습니다.” |

기준/질문/관찰 근거는 공백없는 긴 문자열도 overflow-wrap:anywhere. 날짜·지표는 짧게 유지하되 tooltip만으로 핵심을 숨기지 않는다. 업로드~표시 지연은 실제 timestamp로 기록하며 UX spinner의 정해진 시간과 일치시키려 조작하지 않는다. animation은 150ms 이하 단순 전환, prefers-reduced-motion에서 제거한다.

## 6. 인계·검수 증거

모든 폼/목록/결과의 정상·빈·로딩·오류는 공통04 §3을 적용한다. 디자인 검수는 [acceptance](acceptance.md) 기준을 실제 1440×900/390×844 화면에서 확인하고 소스 토큰 확인만으로 PASS를 주지 않는다. 필수 screen capture는 로그인·점주 홈/제출/결과/unknown·영업 관제/근거/기준/이슈/분석·운영 상태/계정/재처리/감사다. 캡처 전 합성 데이터·비밀 미노출 확인. 실제 완성 캡처를 concept01 매뉴얼에만 사용한다.

### DS01-003 / WEB01-004 적용 보완

운영자 상단 영업 알림과 `/platform-admin/notifications`를 제공하지 않는다. 운영 공지 등록·수정과 공통 유효 공지 표시는 유지한다. 조정자 정적 검토의 역할 경계를 반영한 보완이며 원래 운영자 영업 본문 제외 원칙을 구체화했다.
