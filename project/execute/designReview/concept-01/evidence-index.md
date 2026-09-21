# DR01-001 직접 확인한 실제 화면

본 검수자가 view_image로 직접 읽은 파일만 기록한다. Browser조작/저장/AI실행은 root가 담당하며 아래 시각 관찰은 기능완료를 의미하지 않는다.

| 파일 | 저장 크기 | 관찰 |
|---|---|---|
| [vp-mobile390-owner-home.png](evidence/vp-mobile390-owner-home.png) | 375×812 | 점주 홈390; 주요CTA·2열필터·하단탐색 |
| [vp-desktop1440-hq-dashboard.png](evidence/vp-desktop1440-hq-dashboard.png) | 1425×891 | 본사 관제1440; sidebar·KPIstrip·매장표·Mock표본 |
| [vp-desktop1440-category-v1.png](evidence/vp-desktop1440-category-v1.png) | 1425×891 | 본사CATEGORY 기준v1; 버전·본문·사유·과거보존안내 |

- [vp-desktop1440-reference-list.png](evidence/vp-desktop1440-reference-list.png) (1425×891): 직접 확인, 정상;160px 관리행·출처·버전/편집, D01-P02시각해소.

- [vp-mobile390-preview-keyboard.png](evidence/vp-mobile390-preview-keyboard.png) (375×812): 직접 확인, 정상;1사진 미리보기·질문62/2000·Tab제출초점.

- [vp-mobile390-analysis-running.png](evidence/vp-mobile390-analysis-running.png) (375×812): 직접 확인, 정상;분석중32초/지연안내.

- [vp-mobile390-real-first-top.png](evidence/vp-mobile390-real-first-top.png) (375×812): 직접 확인, 정상;완료·사진출처·91.6초표시/30초목표초과.

- [vp-mobile390-real-first-answer.png](evidence/vp-mobile390-real-first-answer.png) (375×812): 직접 확인, 정상;질문 맥락·실제AI별도출처·답변줄바꿈.

- [vp-desktop1280-category-v2.png](evidence/vp-desktop1280-category-v2.png) (1265×791): 직접 확인, 정상;1280 기준변경·피드백·v2이력표.

- [vp-desktop1280-reference-v2.png](evidence/vp-desktop1280-reference-v2.png) (1265×791): 직접 확인, 정상;새Reference사진·버전2·대상·출처.

- [vp-mobile360-resubmit-preview.png](evidence/vp-mobile360-resubmit-preview.png) (345×767): 직접 확인, D01-V01;미리보기깨진아이콘,로드완료재촬영요청.

- [vp-mobile360-real-child-answer.png](evidence/vp-mobile360-real-child-answer.png) (345×767): 직접 확인, 정상;실제AI새기준/참조답변·비교한계.

- [vp-mobile360-new-snapshot.png](evidence/vp-mobile360-new-snapshot.png) (345×767): 직접 확인, 정상;적용기준탭·목록·표스크롤안내(하단일부미표시).

- [vp-mobile360-old-snapshot-preserved.png](evidence/vp-mobile360-old-snapshot-preserved.png) (345×767): 직접 확인, 정상;이전제출기준탭·목록(하단일부미표시).

- [vp-mobile360-before-after-top.png](evidence/vp-mobile360-before-after-top.png) (345×767): 직접 확인, 정상;mobile세로전후·원본과출처.

- [vp-mobile360-before-after-criteria.png](evidence/vp-mobile360-before-after-criteria.png) (345×767): 직접 확인, 정상;현재100%·날짜·비교표/횡스크롤안내,우측셀추가필요.

- [vp-desktop1440-before-after.png](evidence/vp-desktop1440-before-after.png) (1425×891): 직접 확인, 정상;desktop2열동일크기전후·기준변경주의.

- [vp-desktop1440-ofc-filtered-dashboard.png](evidence/vp-desktop1440-ofc-filtered-dashboard.png) (1425×891): 직접 확인, 정상;은행길점/스낵 범위·관제 지표.

- [vp-desktop1440-filtered-submissions.png](evidence/vp-desktop1440-filtered-submissions.png) (1425×891): 직접 확인, 정상;같은범위 목록·실제20/100·실패와null.

- [vp-desktop1440-ofc-real-result.png](evidence/vp-desktop1440-ofc-real-result.png) (1425×891): 직접 확인, 정상;사진/질문답 두열·실제AI·100/100·5/5.

- [vp-desktop1440-ofc-resolved.png](evidence/vp-desktop1440-ofc-resolved.png) (1425×891): 직접 확인, 정상;해결 상태·담당·해결 내용·저장 피드백.

## QA01 후속 핵심10장

- [vp-qa01-mapped-photo.png](evidence/vp-qa01-mapped-photo.png) (1265×791): 직접 열람. 허용된 QA점주 첫 결과: 스낵 원본과 실제AI 답변을 나란히 표시. 사진·생성 출처/실제AI 출처 구분.

- [vp-qa01-disabled-session.png](evidence/vp-qa01-disabled-session.png) (1265×791): 직접 열람. 비활성화 후 로그인 화면으로 복귀, ID/비밀번호 필드는 비어 있고 이전 사진/질문/평가 본문 없음.

- [vp-qa01-mapping-ended.png](evidence/vp-qa01-mapping-ended.png) (1280×800): 직접 열람. 매핑 종료 후 기록 없음 오류/요청번호/재조회. 이전 사진·질문·평가 제거.

- [vp-qa01-role-denied.png](evidence/vp-qa01-role-denied.png) (1280×800): 직접 열람. OFC 메뉴로 바뀌고 옛 점주 경로는 접근권한 없음·내 업무 이동 표시. 이전 영업 본문 없음.

- [vp-qa01-ofc-claim-refresh-fixed.png](evidence/vp-qa01-ofc-claim-refresh-fixed.png) (1265×791): 직접 열람. F01 최종 정상: 관리목록 총1건, 후보 총0건, 저장성공·페이지상태 확인. 관리행 이름은 화면상단 일부 잘려 전체행 증거로 쓰지 않음.

- [vp-qa01-audit-before-after.png](evidence/vp-qa01-audit-before-after.png) (1265×791): 직접 열람. 감사 시각/actor·대상/행동·사유/succeeded·펼친 변경 전(role ofc/v6 등) 확인. 변경 후는 화면밖이므로 양쪽 전체 시각검수로 세지 않음.

- [vp-retry-success-applied.png](evidence/vp-retry-success-applied.png) (1265×791): 직접 열람. 시도1 기술실패/AI_UNAVAILABLE/미반영과 시도2 분석완료/반영됨, 성공상태 재처리불가 안내를 한 화면에서 확인.

- [vp-owner-resolved-notification.png](evidence/vp-owner-resolved-notification.png) (1265×791): 직접 열람. owner.north의 해결상태·담당OFC·해결내용·관련사진 링크·comment이력 확인. 하단status_change 이력은 일부만 보임.

- [vp-catalog-inactive.png](evidence/vp-catalog-inactive.png) (1265×791): 직접 열람. 기준정보 저장성공/사유입력 폼·영향0/연결0/세션0·신규업무 제한 안내. 변경 대상 비활성행은 화면밖이므로 상태배지 증거 아님.

- [vp-owner-active-notice.png](evidence/vp-owner-active-notice.png) (1265×791): 직접 열람. 점주홈 상단에 QA01 유효 공지와 기존 시연 공지가 표시됨. 사진제출CTA/필터/KPI가 가려지지 않음.

이전 vp-qa01-ofc-claimed/claimed-fixed는 root가 로딩 포착본으로 분류하여 최종 완료 증거에서 제외했다. 원본은 보존하며 이번에 다시 검수하지 않았다.

## DR-QUEUED-001 신규 viewport 직접 검수

이번 제공본만 확인했다. 아래 사용 범위 이외의 화면은 보았다고 주장하지 않는다. 저장 형식은 확장자와 다를 수 있다. hash·소스/입력 기록은 [review-evidence-queued-001.json](review-evidence-queued-001.json).

| 파일 | 저장 크기·형식 | 판정·관찰 |
|---|---|---|
| [vp-mobile390-long-queued.png](evidence/vp-mobile390-long-queued.png) | 375×812 JPEG | PASS: 대기632초·지연/이력 안내, 명시적인 Mock 합성 질문과 생성 사진. 평가 점수 없음. |
| [vp-mobile390-api-outage.png](evidence/vp-mobile390-api-outage.png) | 390×844 JPEG | PASS: 요청 오류와 다시 조회 버튼. 분석 실패나 0점으로 바뀌지 않으며 점주 shell 유지. |
| [vp-mobile390-api-recovered.png](evidence/vp-mobile390-api-recovered.png) | 375×812 JPEG | PASS: 같은 사진·합성 질문·대기1267초로 복귀, 통신 오류 제거. |
| [vp-mobile390-queue-timeout.png](evidence/vp-mobile390-queue-timeout.png) | 375×812 JPEG | PASS: QUEUE_TIMEOUT·분석을 완료하지 못했다는 기술 실패와 운영자 확인 안내. 결과 점수 없음. |
