# DR02-001 · 시안 02 「오늘 할 일」 독립 디자인 검수

- 최신 기록: **DR-FINAL-001 후속 증거 검수 동결**. 전체 디자인 완료와 구분하며, 과거 대기 문구는 최신 기준별 표/마지막 절로 정정한다.
- 상태: RUNNING — 전체 페이지 캡처 교체 및 누락 상태 증거 대기. 최종 디자인 완료 판정 아님.
- 검수자: contract_ai. 시안02의 기획·디자인·프론트 구현 및 root 기능 인수와 독립.
- 기준: docs00→01→02, docs03/04/09/10, DS02-001 v1, PD-003, MEDIA-CLARIFY-1.
- 구현: web-concepts-02 v1.0.0, C02-QA-001 보완 후 13 test/build PASS 보고 수신. 현 시점 소스·계약·캡처 SHA256은 [review-source-001.json](review-source-001.json). 캡처 당시 소스 대응은 root 확인 대기. 이후 대비 수정 및 vp 캡처 기록은 [review-source-002.json](review-source-002.json), 직접 확인한 파일별 사용 범위는 [evidence-index.md](evidence-index.md).
- 실행 환경: macOS, 실제 Vite 5174·공통 API8000·AI8010, 별도 storeloop_test/.local/test-media(root 기능 QA 기록). root가 모바일 innerWidth=390/clientWidth=375/innerHeight=844/DPR=1을 확인했다. 15px 차이는 스크롤바 폭이다. Browser 빌드·desktop viewport 메타데이터는 확인 대기.
- 증거 방법: root가 실제 페이지를 촬영하고 본 검수자가 PNG를 직접 시각 검사한다. 공유 로그인·DB·브라우저를 변경하지 않는다. 소스/DOM 존재만으로 디자인 PASS를 부여하지 않는다.

## 1. 증거 품질과 관찰

`mobile-analysis-delayed.png`(375×812)와 `desktop-reference-preview.png`(1425×891)는 일반 화면으로 읽을 수 있다. 전자는 지연 상태·질문 맥락·기술 실패와 구별되는 분석 중 문구·초점 테두리를, 후자는 라벨·필수표시·실제 Reference 미리보기와 원본 비율 보존을 확인했다.

나머지 fullPage 캡처는 실제 저장 폭 대비 UI가 약 50% 폭에 렌더링되고 오른쪽 공백 및 하단 중복 카드/푸터 조각을 포함한다. 대표적으로 [mobile-submit](evidence/mobile-submit.png), [desktop-ofc-priority-board](evidence/desktop-ofc-priority-board.png)에 나타난다. 이는 캡처 파이프라인 오류 후보이며, 제품 자체의 축소/중복 UI로 확정하지 않았다. 글자 크기·화면 밀도·overflow 최종 판정 및 매뉴얼에는 사용하지 않는다. 원본을 보존하고 `fullPage:false`로 주요 구간을 다시 촬영하도록 요청했다.

재촬영한 `vp-mobile-qa-owner-home.png`, `vp-mobile-account-revoked.png`, `vp-desktop-account-inactive.png`는 직접 시각 확인했으며 축소·중복 문제가 없다. 모바일 홈에서 큰 다음 행동, 5개 업무 탭, 시연 출처 공지가 읽히고 본문 가로넘침은 보이지 않는다. 계정 비활성화 저장 화면에는 사유와 기존 로그인 접근 차단 안내가 있고, 별도 점주 화면은 업무 데이터 없이 로그인으로 돌아간 상태다. 이 세 화면은 증거로 사용할 수 있으며 아직 촬영되지 않은 상태 전체를 대체하지 않는다. 이어서 `vp-mobile-mapping-revoked.png`의 접근 제한·업무 데이터 제거·명확한 돌아가기 및 초점 테두리와 `vp-desktop-audit.png`의 운영 전용 메뉴·공지·필터·변경 사유를 직접 확인했다. 감사 펼침 상세는 아직 확인하지 않았다.

## 2. 발견 사항

| ID·중요도 | 재현·기대 | 관찰·영향 | 담당·조치 |
|---|---|---|---|
| D02-001 · P1 증거 차단 | 실제390×844/1440×900의 일반 캡처로 명세 배치·크기를 확인 | fullPage 증거에 절반 폭 축소·큰 공백·중복 조각. 원본 UI와 캡처 오류 분리 필요 | root: viewport 구간별 재촬영, browser/viewport/DPR/zoom/소스 대응 기록 |
| D02-002 · P2 대비 · 소스 수정 확인 | docs04 §5 컨트롤 경계 3:1, 작은 글자4.5:1 | 기존 경계2.93:1·null 글자4.05:1. root가 #7b9080과 #56644d로 수정했고 재계산3.42:1·6.31:1로 통과 | 소스 대비 결함 해소. 최신 입력/결측 차트 시각 증거 확인까지 전체 접근성 BLOCKED |
| D02-003 · P2 증거 누락 | 상태·5역할·접근성·모바일/확대 모두 검증 | 홈/계정/권한 철회 캡처 수신. 감사, unknown/null 결과, 키보드 이동,200% 확대,360/1280 좁은 화면 증거는 대기 | root: 추가 촬영/조작 기록. 해당 기준 BLOCKED 유지 |

## 3. DS02-001 기준별 진행 판정

| 기준 ID | 역할·화면·상태 | 기대 / 실제 | 결과 | 증거·후속 |
|---|---|---|---|---|
| DS02-01 | 영업 첫 화면 desktop | 지역3/HQ6 범위와 검토/조치/변화3단계 lane 정상 첫 viewport 확인 | PASS | regional-home/hq-home-final, 옛 fullPage 제외 |
| DS02-02 | 점주 홈/제출 mobile | 기존390홈 CTA와360 제출/초점, 신규390 매장·카테고리·사진 선택 폼을 직접 확인 | PASS | 기존 §5 및 photo-order-boundary; 새 캡처 아래 순서버튼은 화면 밖 |
| DS02-03 | 운영 첫 화면 desktop | 복구/연결/상태와 안전 메타데이터, 업무 본문 없음 | BLOCKED | operations 재촬영 필요 |
| DS02-04 | 5역할 메뉴/직접 경로 | root 현재권한/직접경로 기능 완료, 신규 preview3경로군도 완료. 다섯 역할 전체 메뉴의 독립 시각 대조는 부분적 | BLOCKED | 운영 알림 제외 유지; 역할 기능을 반복할 필요 없음 |
| DS02-05 | 사진 선택/미리보기/오류 | 기존360 사진번호/순서·삭제·질문/제출 초점과 root5장·형식/용량/개수·2000자 실제 검증을 결합 | PASS | input-boundary; 신규390은 폼 상단만 보인다는 제한 유지 |
| DS02-06 | queued/running/지연/실패/unknown/성공 | 기존 실행/완료·지연 및 신규 queued/통신 오류·복구/기술 실패, 실제 unknown —/0·이유를 구분 | PASS | DR-QUEUED-001 및 기존 실제 unknown 결과 |
| DS02-07 | 결과 본문 | unknown/null/근거/행동 확인. Reference 순서 소스 수정 확인 | BLOCKED | D02-004 새 캡처 재검수 필요 |
| DS02-08 | 생성/Mock/실제 출처 | 기존 실제AI/Mock unknown/생성사진 구분과 신규Reference v3 카드 AI생성 시연 이미지 배지를 확인 | PASS | reference-conflict-saved; 관리카드 사진번호와 결과snapshot번호는 다른 대상 |
| DS02-09 | 재제출/비교 | 부모 연결·전후 사진/날짜·5개 기준 버전/판정·비교한계 확인 | PASS | comparison-dates-final/versions-final, D02-005 해소 |
| DS02-10 | 영업 보드→근거→조치 | 기능 QA 성공 보고와 별도로 시각 계층 검수 필요 | BLOCKED | priority/photo/resolved 재촬영 |
| DS02-11 | 기준/Reference 관리 | root4단계 관리·Reference교체/비활성 기능, CSRF/409 입력·파일 보존→명시v3 저장 완료. 신규v3 카드 확인 | BLOCKED | 나머지 관리이력/역할별 옵션의 독립 시각 구간만 남음 |
| DS02-12 | 운영 계정/연결/기준 정보 | 비활성 영향·사유/연결 및 펼친 감사 before/after 확인. 충돌/나머지 기준 정보 추가 필요 | BLOCKED | account-inactive, audit-role-restored-after |
| DS02-13 | 실패 재처리 | 실제 실패 시도1·미반영과 성공 시도2·반영 표시 확인. guard 안내 전체는 화면 밖 | BLOCKED | retry-success-preserved-final, guard 필요 구간만 후속 |
| DS02-14 | 추이/상관/표 | Mock/표본/계산불가 및 서버 값 | BLOCKED | analytics-empty 재촬영, 정상 표본 추가 |
| DS02-15 | 알림/공지 | 공통 공지 관찰, 점주 알림·읽음 링크 별도 | BLOCKED | notification 재촬영, 운영 공지 소스 유지 |
| DS02-16 | 라벨/44px/초점/키보드 | 라벨·지연 h1 초점 관찰. 대비 소스 수정 계산 통과, 키보드/결측 시각 증거 필요 | BLOCKED | D02-002 소스 해소, 포커스/결측 캡처 대기 |
| DS02-17 | mobile/200%/overflow | 390/1440 및360/1280,200% 확대 주요동선 | BLOCKED | D02-001/003 |
| DS02-18 | 4상태/재조회/권한 철회 | 권한철회·통신복구·queued 및 root 기준0/Reference없음 기능 완료. 새no-criteria PNG는 Mock완료 상단만 보임 | BLOCKED | 기준없음본문은 화면 밖; 목록 최초/갱신/빈 상태의 미확인 구간은 별도 |
| DS02-19 | URL필터/페이지/뒤로가기 | 동일 작업 맥락 보존 | NOT_RUN | root 실제조작 기록·연결 캡처 필요 |
| DS02-20 | build/test/실제AI 독립 증거 | 구현13test/build PASS, root 실제AI2건 성공 기록 있음. 디자인 PASS를 대체하지 않음 | PASS | 기능 증거 actual-ai.json, 구현 이력 |

## 4. 매뉴얼 반영 원칙

02의 메뉴·경로·단계별 행동을 소스와 캡처에 맞춰 작성한다. 현재 캡처 결함이 있는 이미지는 완성 화면 예시로 배포하지 않는다. 명세상의 구현 예정 화면·다른 시안 캡처를 대체 사용하지 않는다. 최종 캡처가 오면 대응 소스 hash와 함께 업데이트한다.

실제 AI02 원본은 모델51.710초, 장애 복구 포함 접수→DB결과295.934초, 재제출 모델47.049초/접수→DB결과47.060초다. 30초 목표는 이 사례에서 미달이며 브라우저 표시시간의 완전한 측정값으로 부르지 않는다. 원본50%→재제출100%는 이번 가상사진의 실제 응답 사례이고 일반 정확도/개선 보장으로 표현하지 않는다.

## 5. 좁은 모바일·키보드 증거 추가

`vp-mobile360-submit.png`와 `vp-mobile360-preview-keyboard.png`를 직접 확인했다. root 측정은 innerWidth360/clientWidth345/scrollWidth345로 본문 가로넘침이 없다. 제출 상단의 부모 연결·매장 고정, 하단의 미리보기·파일명/용량·순서/삭제·질문78/2000자·제출 행동이 읽힌다. Tab으로 제출 버튼에 도달한3px 초점은 배경/버튼과 구별되고 화면에 가려지지 않는다. 이 한 동선의 관찰은200%/전체 역할 키보드/오류 상태 검수를 대체하지 않는다.

## 6. 실제 unknown·새 기준 결과 증거

실제 모델3번째 제출의 `vp-mobile360-real-unknown-top.png`, `vp-mobile360-real-unknown-metrics.png`, `vp-mobile360-new-snapshot.png`를 직접 확인했다. 정상 분석 완료와 생성 이미지/실제AI 배지가 구분되며, 준수율은—·판단가능률0%·판단 가능한 기준0/5로 표시되고 계산불가 이유를 별도 안내한다. unknown을 기술 실패나 준수0%로 표현하지 않는다. 이전 제출 연결 및 제출 당시 기준 버전 목록도 보인다. 기준별unknown/Reference 본문 전체와 비교 경고는 추가 캡처가 필요하다.

root 실제AI 기록: 모델92.888초, 접수→DB94.166초. `browser-latency-third.json`의 제출→화면표시111.334초는 heading 대기와 도구 호출 간격을 포함한 상한 측정값이며 정확한 표시 순간이 아니다. 이 표본도30초 목표 미달이다.

## 7. 변경 기준 비교와 실행 재확인

`vp-mobile360-changed-criteria-compare.png`에서 현재 사진·생성 출처·준수율—/판단률0%와 명시적인 기준 차이 주의 문구, 항목별 준수→판단불가/비교불가 표시를 직접 확인했다. root는 전체5항목 및 qa02_labels의 버전 변경 표시를 기능 조작으로 확인했다고 보고했다. 사진 전후 전체 배치/날짜와 하단5항목 모두의 시각 증거는 별도로 확인한다.

root가 기존 개발 HMR 세션에서09:20~09:55UTC createRoot 중복/removeChild NotFoundError 기록을 발견하여 시안02 작성자에게 수정·확인을 배정했다. 이 기록만으로 동결된 preview의 오류를 확정하지 않는다. 최종 동결 버전에서 신규 탭/preview 콘솔이 깨끗한지 확인하고 변경된 소스 hash와 build/test 증거를 연결해야 한다.

## 8. Reference 순서 표시 보완 요청

`vp-mobile360-unknown-evidence.png`에서 기준별 판단불가, 근거 사진1 관찰, 재촬영 행동, 낮은 신뢰도/OFC확인 안내가 서로 구분됨을 확인했다.

D02-004 · P2: `vp-mobile360-reference-snapshot.png`는 서로 다른 Reference 카드가 모두 “비교 Reference1”로 표시된다. `Owner.tsx/SnapshotReference`가 top-level 실제 Photo metadata의 position=1을 그대로 전달하고 `Photos`가 이를 우선 사용하기 때문이다. 실제 URL/source_kind는 유지한 채 표시 순서를 context.references.position으로 맞추도록 root에 요청했다. 다른 사진을 동일 번호로 오해할 수 있으므로 해당 부분은 수정 후 재촬영한다. 새 캡처는 문제의 증거로 보존하고 매뉴얼의 정상 결과 예시로는 아직 사용하지 않는다.

C02-HMR-001 수정 기록을 읽었다.5개 entry만 기존 React root를 재사용하도록 수정했고02회귀15/15와5개build PASS 보고가 있다. JSX/화면 배치는 유지된다. 마지막 fresh preview 콘솔 재검수는 root 증거 대기다.

D02-004 소스 재검수: 작성자가 context reference.position 또는 배열index+1을 SnapshotReference에 별도로 전달하고, 실제 Photo를 복사한 뒤 표시용 position만 덮도록 수정했다. URL/source_kind·원본 DTO/context는 변경하지 않는다. 해당 코드를 직접 확인했고 전체16/16·build PASS(index-CQdY1g6y.js) 보고를 수신했다. 현재 소스 원인은 해소되었으며 새 PNG에서Reference1/2 구별을 확인하기 전 전체 항목은 BLOCKED이다.

현재 소스 hash 추가 기록: [review-source-003.json](review-source-003.json). HMR root 재사용 보완과 인계된 현재 수정을 추적한다. 앞선 캡처와 같은 빌드라고 소급 단정하지 않으며 최종 캡처/신규 페이지 콘솔 검수는 root 실행 기록과 함께 확인한다.

## 비교 정보 누락 · D02-005

docs04 S-O05/§6/endpoint 표의 비교 날짜·기준 version 표시 요구를 소스와 대조했다. Comparison은 날짜와 적용 기준 버전을 모두 표시하지 않는다. root가 단독 보완 소유를 배정했다(02/04 contract_data,05 product_design). 상세로 이동하는 링크만으로 비교 화면의 필수 정보를 대체하지 않는다. 수정 회귀·build와 실제 날짜/버전 화면을 재검수할 때까지 관련 비교 항목의 최종 PASS를 보류한다.

S-O05 보완 독립 소스 재검수: 현재 허용된 전후 detail의 날짜와 rule_key별 불변 기준 버전을 사용하며 로딩·실패·미적용을 구분하고 기존 사진·rate·변경 한계를 유지한다. 작성자 테스트/build 통과 인계를 수신했다. 소스 검토 PASS, 현재 hash는 [review-source-004.json](review-source-004.json). 실제 새 화면 전에는 비교 시각 항목을 PASS로 확정하지 않는다.

## DR-QUEUED-001 공통 대기·통신 오류·복구 추가 검수

신규390 viewport4장을 직접 확인했다. 대기·추가 지연·통신 오류·복구 후 대기·worker 재시작 후 QUEUE_TIMEOUT 기술 실패가 서로 구분되며, 통신 오류나 기술 실패를 평가0점으로 표시하지 않는다. 이번 대기는 과거 시각을 넣은 별도 Mock fixture이고 실제 AI 호출/성능 측정이 아니다. 원본 질문에도 합성 검수임을 명시한다. 보이는 구간에서 새 명백한 겹침·글자 절단·본문 가로넘침은 발견하지 않았다.

root의 실제 조작 기록과 별도 READ ONLY 사후25PASS를 참조했다. 신규 시도는 expired·결과0·점유 없음, snapshot 보존이다. 기존15건 snapshot과 사전 결과hash가 있는12건의 결과 보존을 확인한 범위이며 DB 전수/모델 로그 검증으로 확대하지 않는다. 본인은 추가 Browser·DB·AI·서비스 조작을 하지 않았다. 화면 이탈 시 polling 종료, 목록 전체4상태, 입력/충돌/키보드/200%는 이번4장으로 완료 처리하지 않는다. 파일별 제한은 [evidence-index.md](evidence-index.md), 결합 보고서는 [DR-QUEUED-001](../../workHitory/design-review-queued/review-001.md).

## DR-QUEUED-001 시안02 보완9장 판정

지역/HQ 3단계 업무 첫 화면은 정상 viewport로 확인했다. 전후 KST 날짜 및 전체5개 기준 버전·판정·비교불가가 명확하여 D02-005는 시각 해소한다. qa02_labels의 정확한 표시는 이전 미적용→현재v2이며, 기존 기록의 포괄적인 ‘버전 변경’을 이전v1이 있었다는 뜻으로 해석하지 않는다. 실제 unknown —/0%·표본0/5·이유, 감사 before/after, 실패 시도1과 성공 시도2의 보존도 직접 확인했다.

`vp-mobile390-reference-number-fixed.png`에는 Reference 사진/번호가 화면 밖이고 기준 accordion까지만 보인다. root의 번호1·2·3 기능 확인은 수신했으나 이 파일만으로 D02-004 시각 PASS를 주지 않는다. root가 후속 필요 구간을 한 번만 촬영할 예정이며 전체 정상 화면 재촬영은 필요 없다. 재처리 캡처도 시도 보존은 확인하지만 화면 위쪽 guard 문구 전체까지 확인한 것으로 기록하지 않는다. 세부 관찰/파일hash는 `review-evidence-queued-001.json`에 고정했다.

## DR-FINAL-001 · 기존 증거 최소 후속 검수

2026-09-21, 검수자 contract_ai. 이전 발견·촬영 기록은 당시 이력으로 보존하며, 최신 판정은 위 표와 이 절을 따른다. [통합 근거·파일 식별·필수 잔여](../../workHitory/final-handoff/design-evidence-reconciliation.md)를 정본으로 연결한다. 본 후속 검수는 기존 PNG 열람과 기록 대조만 수행했다. 새 Browser·테스트·DB·AI·서비스 조작, 구현/매뉴얼 변경은 없다. 기능 PASS와 독립 시각 PASS를 구분하며, 화면 밖이라는 이유만으로 제품 결함을 추가하지 않는다.

최종 5개 build/setup/start/중복 시작/stop→restart 및 점주·본사·운영자 3경로군×5 preview 직접 접속·새로고침은 root 실행 기록으로 완료되었다. 하나의 새 검수 탭에서 순차 확인했고 마지막 콘솔 조회의 warning/error는 0건이다. 전체 내부 화면이나 다섯 역할의 모든 동선을 새로 검수했다는 뜻은 아니다. HTML 매뉴얼의 지정 desktop/mobile 렌더·링크·이미지·키보드 표 이동은 기존 독립 기록에 따라 완료다. 실제 200%는 사용자가 후행으로 정한 NOT_RUN이며 전체 디자인 완료로 올리지 않는다.

신규 사진 선택 폼에서 매장·카테고리·파일 제약·순서 설명이 읽히지만 아래 순서/삭제 버튼은 화면 밖이다. 앞서 본360 미리보기/키보드 화면과 root 입력 경계를 결합했다. CSRF 보존 캡처는 caption/reason 폼이 보이는 범위만 시각 확인했으며 오류 문구와 파일명은 화면 밖이다. 새 Reference v3 활성카드의 원본·보존 설명·생성 출처는 직접 확인했다. root의 CSRF→409→최신v2 조회→명시v3 저장 성공과 독립 소스 회귀는 별도 근거다.

no-criteria-reference-final은 Mock·완료 상단만 보인다. 기준0/Reference없음·—/— 기능은 root가 실제 확인했지만 이 PNG가 본문 시각 증거가 되지는 않는다. D02-004의 결과 Reference번호1/2/3 역시 기존 캡처에서 화면 밖이므로 해소하지 않았다. 관리카드의 사진번호와 해당 결함을 혼동하지 않는다. 남은 필수는 결과 Reference번호·관리/원본근거/운영·분석 중 미검토 구간, URL 작업맥락·목록 상태·접근성/200%의 구체 근거이며 이미 완료한 실제AI·권한·복구를 재실행하지 않는다.
