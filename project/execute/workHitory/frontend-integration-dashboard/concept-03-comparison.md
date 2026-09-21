# D03-V03 보완 기록

독립 검수 contract_ai가 Comparison 화면의 날짜/기준version 누락을 확인했다. docs04의S-O05 및 endpoint 표에 따라 비교API side는 그대로 두고 parent/current SubmissionDetail을 읽어 created_at/context.guidelines의version을 표시한다. DB/API계약변경없이 현재로그인 범위검사를 받는 GET /submissions/{id}만 추가한다. 버전은 context.snapshot이아닌평탄context.guidelines 정본에서 rule_key로 찾으며 조회실패/미적용을추정하지않는다.

새회귀는 실제 React Comparison 렌더에 합성API를 주입해 날짜·전후버전·사진/rates·기준변경비교불가·상세실패재조회·부모없음추가조회없음을검증한다. 브라우저/서비스/DB/다른제품파일수정없음.


## 검증 완료 · REVIEW 동결

신규3회귀 중 날짜2개누락/상세오류누락2 RED, 부모없음기존동작1 PASS였다. current/parent의 GET상세를useResource로읽고 사진위 KST제출일시(time datetime 포함), 기준별변화표에 이전/현재version열을추가했다. rule_key는동일하게대응하고 조회실패/불러오는중/미적용을구분한다. Resource의기존오류/재조회동작과 기준변경비교불가·rates/원본사진·모바일가로표키보드포커스를보존한다.

GREEN3개,전체28 PASS,TypeScript/Vite build PASS(index-ujIs0mzD.js). 기본성공GET은comparison+parentdetail+currentdetail3개뿐이며점주Reference/API별도조회없음. 원래parent없는경우detail조회없음. 원본값못읽으면추정없음. 제품수정은03store-owner/pages.tsx Comparison만,신규회귀comparison-detail.test.ts. 실제브라우저기하/비교화면재촬영·독립시각재검수는root/contract_ai후속. REVIEW동결즉시인계후05별도작업으로전환.
