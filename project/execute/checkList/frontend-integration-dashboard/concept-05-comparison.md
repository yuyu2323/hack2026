# D05-VERSION 비교 기준 버전 체크리스트
root가05 shared/business.tsx Comparison·신규회귀만 단독 이관했다. 기존detail 조회/날짜·사진·rates·조건 URL·기준변경주의를 보존한다.
- [x] 기존parent/current detail이미조회,표버전누락확인.
- [x] 동일rule_key 전후snapshot버전/미적용·실패회복 테스트RED.
- [x] 두버전열·detail오류/재조회 표시,추가API없음.
- [x] 전체테스트/build REVIEW동결.
- [ ] root 실제브라우저·contract_ai 독립 검수.
