# F03-NOTICE-PERIOD 체크리스트
root한정소유:03 platform-admin/pages.tsx Announcements목록기간표시만.
- [x] 연도생략으로2026→2027기간이하루처럼읽히는증상확인.
- [x] 목록만 연도포함 KST 기간·종료없음 표시,공통date/CRUD/데이터무변경.
- [x] 합성跨年시각표시확인/build REVIEW동결.
저영향표시문구변경으로새회귀파일은만들지않고format출력검사/기존타입·build로검증한다.
