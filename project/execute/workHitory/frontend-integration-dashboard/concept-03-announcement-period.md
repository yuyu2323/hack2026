# F03-NOTICE-PERIOD 보완
root가실제운영공지에서2026-09-20~2027-09-21이연도없이하루기간처럼읽히는것을확인했다. Announcements목록기간전용formatter를두어연도/월/일/24시간시각과KST를표시한다. 종료null은종료일없음으로표현한다. 다른날짜함수/폼payload/API/CRUD는변경하지않는다. 저영향표시수정이므로새테스트파일없이동일Intl옵션의합성시각검사와build를수행한다.


검증결과: 동일Intl옵션의2026/2027합성UTC입력이 '2026. 09. 20. 09:00 ~ 2027. 09. 21. 09:00 · KST'로표시됨을assert로확인했다. TypeScript/Vite build PASS(index-DwKifTuH.js),root에즉시REVIEW동결/폼작업재개가능전달. 제품변경은Announcements함수내기간formatter와small시간표시뿐이다. 실제UI재확인은root후속.
