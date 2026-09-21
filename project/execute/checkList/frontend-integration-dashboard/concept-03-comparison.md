# D03-V03 비교 metadata 체크리스트

root가03 Comparison·읽기데이터·신규회귀만 단독 배정. docs04 S-O05/endpoint 표의 원본 detail 날짜·기준 version 요구를 따른다.
- [x] 현재 API 비교side에날짜/버전없음, 별도 SubmissionDetail 조회 계약 확인.
- [x] 날짜/동일rule_key 전후버전·기준변경제한·실패재조회/부모없음 회귀 RED.
- [x] 허용된 부모·현재 detail만 조회, KST제출일시·불변snapshot 버전 표시.
- [x] 기존원본사진·rates·모바일표키보드접근·비교불가 보존.
- [x] 전체테스트/build 후 REVIEW 동결 인계.
- [ ] root실제뷰포트/contract_ai독립재검수.
