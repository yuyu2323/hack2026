# D05-VERSION 보완 기록
03 Comparison 동결 후 root배정에 따라05 Comparison의표시만보완한다. 기존parent/current SubmissionDetail을재사용해 context.guidelines rule_key→version을 표시하고 미적용/조회실패/로딩을구분한다. 상세의Load를활용해기존날짜자리에서명시재조회도제공한다. API호출범위·사진·rates·탐색조건URL·기준변경주의는유지한다. 제품소스는shared/business.tsx Comparison만수정.


## RED → GREEN / REVIEW 동결

새회귀2개는v2누락·상세오류누락으로RED였다. Comparison 안에서기존current/parent의snapshot을rule_key로찾아전후버전을표시하고날짜자리를Load로감싸오류/재조회/로딩을보이게했다. 추가API없음,원본사진/수치/탐색URL/기준변경비교불가/모바일표focus유지. 첫GREEN시도에서테스트가current완료후parent비동기완료를기다리지않는실수를확인해행의v1출현을기다리도록고쳤다. 제품추가수정은없다.

최종전체17 PASS,TypeScript/Vite build PASS(index-kGtlCAeC.js). 제품source는05shared/business.tsx Comparison만,새테스트comparison-version.test.ts. REVIEW동결root전달,실제viewport재검수대기. API/DB/공유UI/패키지/브라우저/다른시안무수정.
