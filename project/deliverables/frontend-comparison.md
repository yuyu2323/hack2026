# StoreLoop 프론트엔드 시안 비교

5개 시안의 사용 설명서를 먼저 읽고 원하는 업무 흐름을 비교할 수 있습니다. 같은 서버와 업무 규칙을 사용하며, 최종 시안은 사용자가 선택합니다. 전체 기능·디자인 인수의 잔여 항목은 별도로 표시합니다.

| 시안 | 정보 배치와 탐색 | 직접 비교할 업무 | 실행 주소 | 독립 디자인 검수 |
|---|---|---|---|---|
| 01 관제 데스크 | 왼쪽 탐색, 지표, 정렬된 기록 표. Reference는160px 썸네일 관리 행 | 여러 매장의 상태를 빠르게 찾고 같은 필터로 사진에 진입 | [5173](http://127.0.0.1:5173/) | [진행 기록](../execute/designReview/concept-01/review-001.md) |
| 02 오늘 할 일 | 검토→조치→후속의3단계 업무 카드, 점주에게 큰 다음 행동 | 오늘 처리할 일을 찾아 담당·조치를 연결 | [5174](http://127.0.0.1:5174/) | [진행 기록](../execute/designReview/concept-02/review-001.md) |
| 03 사진과 근거 | 사진 목록, 원본과 근거를 함께 읽는 분할 화면, Reference 갤러리 | 근거를 눌러 사진의 해당 번호로 이동 | [5175](http://127.0.0.1:5175/) | [진행 기록](../execute/designReview/concept-03/review-001.md) |
| 04 현장 포켓 | 하단 탐색, 큰 행동, 네 단계 사진 제출 | 모바일에서 앞뒤 단계를 오가며 사진과 질문 입력 | [5176](http://127.0.0.1:5176/) | [진행 기록](../execute/designReview/concept-04/review-001.md) |
| 05 탐색과 비교 | 상단 업무 탭, 범위 탐색 패널, 비교 작업 영역 | 조건을 유지하며 전후 기록·조직 연결 비교 | [5177](http://127.0.0.1:5177/) | [진행 기록](../execute/designReview/concept-05/review-001.md) |

위 차이는 각 확정 설계와 현 소스에 근거하며, 최종 배치/접근성 PASS를 의미하지 않습니다. 실행 주소는 해당 시안과 공통 서비스가 켜져 있어야 열립니다. [전체 실행 안내](../README.md)를 참고하세요.

## 매뉴얼과 화면

- [02 사용 설명서](manuals/concept-02/index.html): 점주·OFC·지역·본사·운영자 동선, 상태 대응, 실제 화면, 전체 시연 순서.
- [01 관제 데스크 사용 설명서](manuals/concept-01/index.html)
- [03 사진과 근거 사용 설명서](manuals/concept-03/index.html)
- [04 현장 포켓 사용 설명서](manuals/concept-04/index.html)
- [05 탐색과 비교 사용 설명서](manuals/concept-05/index.html)

매뉴얼별 실제 화면은01 8장·02 7장·03 10장·04 10장·05 12장입니다. 지정1440×900/390×844의 문서·로컬 이미지·표 키보드·본문 건너뛰기와 수정 후 PNG 검수를 완료했습니다. 최신 기능 안내는 본문과 링크를 대조해 갱신했습니다. [독립 문서 재검수](../execute/workHitory/manuals-browser/independent-recheck.md). 실제200% 확대는 사용자 후속 항목이며, OS 네트워크 차단 오프라인·인쇄 검수는 NOT_RUN입니다.

## 현재 확인된 결과와 제한

다섯 시안에서 사진 제출→실제AI→재제출→관리자 조치와 역할별 업무를 확인했습니다. 대기·통신 오류·같은 제출 복구·대기 시간 초과도 실제 UI와 신규20장의 독립 검수로 확인했습니다. 후자는 합성 Mock 대기 사례이며 AI 처리 성능과 구분합니다. 형식/10MiB 초과/6장 차단·정상5장·순서/삭제·질문2000자 제한은 실제 입력 검증을 완료했습니다. [공통 상태 검수](../execute/workHitory/design-review-queued/review-001.md), [입력·복구 기록](../execute/workHitory/input-boundary/browser.md).

시안01·02·04의 Reference409 복구는 입력·사진을 보존하고 최신 내용을 확인한 뒤 사용자가 다시 저장하는 동작을 실제로 확인했습니다. 01·02는 CSRF 오류 입력 보존도 확인했고,01의 기준409 초안 보존과 알려진 복구 경계2건도 수정·재검증했습니다. 전체 목록 상태·나머지 충돌/키보드 등 아직 없는 근거는 [잔여 목록](../execute/workHitory/frontend-comparison/pending-visual-evidence.md)에 유지하며, 문서 전달을 위해 추가 검수 범위를 넓히지 않습니다.


최종 실행 확인도 완료했습니다. 5개 시안의 TypeScript/Vite build, 문서의 setup 재실행, 기본 시연 DB에서 공통 서비스·5개 시안 시작과 같은 start 명령의 중복 실행을 확인했습니다. 최종 preview에서는 점주·본사·운영자 계정으로 세 경로군을 열고 새로고침했으며,새 검수 탭에서 다섯 시안을 차례로 확인한 뒤 조회한 콘솔 warning/error는0건이었습니다. 새 AI 호출은 없었습니다. [5개 build](../execute/workHitory/final-handoff/build-all.log), [setup 재실행](../execute/workHitory/final-handoff/setup-rerun.log), [시작](../execute/workHitory/final-handoff/start.log), [중복 시작](../execute/workHitory/final-handoff/start-idempotent.log), [preview 기록](../execute/workHitory/final-handoff/preview-browser.json). 이 확인은 경로·실행·콘솔에 한정하며 전체 화면의 독립 디자인 PASS를 뜻하지 않습니다. 마지막 stop→종료 확인→restart도 [실행 기록](../execute/workHitory/final-handoff/runtime.md)에서 확인할 수 있습니다.

01 첫 실제 AI 제출은 모델 90.824초/접수→DB 91.132초였고, 화면 표시 관찰은 91.732초였습니다. 마지막 관찰 간격 약 3초를 포함합니다. 후속 제출은 모델 54.601초/접수→DB 55.622초, 화면 표시 최초 확인 상한 69.336초였습니다. 후속 표시는 관찰 간격이 있어 정확한 표시 순간과 구분합니다. 두 표본 모두 30초 목표 미달입니다. 전체 기능/디자인 인수는 진행 중입니다. [01 실제 실행](../execute/workHitory/integration-concept-01/actual-ai.json), [01 브라우저 기록](../execute/workHitory/integration-concept-01/browser.md).

02 실제 AI 인수 사례는 최초 모델51.710초(초기 연결 장애와 수동 복구를 포함한 최초접수→DB결과295.934초), 개선 후 모델47.049초(접수→DB47.060초)였습니다. 이번 사례에서30초 목표는 미달입니다. 브라우저 최종 표시시간과 모델 처리시간을 혼동하지 않습니다. [실제 실행 기록](../execute/workHitory/integration-concept-02/actual-ai.json).

추가로 어둡고 가려진 사진은 모델92.888초/접수→DB94.166초에 완료되었고 판단가능0/5·준수율 계산불가가 표시되었습니다. 제출→화면표시 상한111.334초는 호출 간격을 포함하므로 정확한 표시 순간의 측정값과 구분합니다. [표시시간 기록](../execute/designReview/concept-02/evidence/browser-latency-third.json).

03 첫 실제 AI 제출은 모델 96.072초, 접수→DB 97.227초, 화면 최초 관찰 98.468초였습니다. 브라우저 관찰 간격은 3초이며 30초 목표는 미달입니다. 재제출은 모델 64.730초/접수→DB 66.783초였고 화면 표시는 66.443초의 마지막 대기 관찰과 70.687초의 최초 완료 관찰 사이였습니다. 재제출도 30초 목표 미달이며 전체 인수는 진행 중입니다. [03 실제 실행](../execute/workHitory/integration-concept-03/actual-ai.json), [03 첫 화면 표시 측정](../execute/designReview/concept-03/evidence/first-latency.json), [03 재제출 표시 관찰](../execute/designReview/concept-03/evidence/child-latency.json).

04 첫 실제 AI 제출은 모델 70.973초, 접수→DB 72.692초였습니다. 브라우저는 74.721초에 대기, 74.827초에 완료를 관찰했으며 정확한 표시 순간은 이 0.106초 관찰창 안에 있습니다. 이 스낵 사진 표본은 기준5개·Reference3개로 판정되었고 30초 목표는 미달입니다. 재제출은 모델64.762초/접수→DB65.635초였으며 화면은66.229초의 마지막 대기 관찰과74.371초의 최초 완료 관찰 사이에 표시됐습니다. 관찰창8.142초를 포함하므로74.371초는 정확한 렌더 시간이 아닌 상한입니다. 두 표본 모두30초 목표 미달이며 전체 인수는 진행 중입니다. [04 실제 실행](../execute/workHitory/integration-concept-04/actual-ai.json), [04 브라우저 기록](../execute/workHitory/integration-concept-04/browser.md).

05 첫 실제 AI 제출은 모델60.273초/접수→DB61.422초였습니다. 브라우저는51.315초 대기→63.181초 최초 완료를 관찰했으며11.866초 관찰창을 포함하므로63.181초는 표시 상한입니다.30초 목표는 미달입니다. 재제출은 모델63.876초/접수→DB66.097초였고, 브라우저 대기56.504초 이후 완료 상한94.159초로 기록됐습니다. 타이머 기록 실패로37.655초 관찰창이 있어 정확한 표시시간과 구분합니다. 두 호출 모두30초 목표 미달이며 전체 기능·디자인 인수는 진행 중입니다. [05 실제 실행](../execute/workHitory/integration-concept-05/actual-ai.json), [05 표시 관찰](../execute/designReview/concept-05/evidence/latency-first.json).

사진은 이 작업에서 생성한 가상 매대이며, 새 실제 AI 응답과 Mock 과거 평가·매출을 구분합니다. 이번02 결과50%→100%는 특정 가상사진의 응답이고 일반 정확도나 매출 개선을 보장하지 않습니다.

선택할 때는 표 중심 관제(01), 오늘의 업무 단계(02), 사진과 근거(03), 모바일 제출 단계(04), 범위 탐색과 비교(05) 중 자주 수행할 업무에 맞는 동선을 살펴보세요. 최종 접근성 전체 PASS나 실제 AI 30초 목표 달성을 주장하는 비교표가 아닙니다.

최종 선택은 [시안 선택 기록](../execute/question/frontend-selection/select-concept.md)에 남깁니다.
