# 매뉴얼01·03·04 실제 렌더 검수 위치

root에게 전달한 검사 위치. 현재 문서 정적 서버 origin은 확인되지 않아 임의 포트를 제시하지 않는다. 아래 path는 프로젝트를 정적 루트로 제공할 때 사용한다. 파일로 직접 열 때는 project/deliverables/manuals/... 경로를 사용한다. 서비스 시작/Browser 조작은 root가 수행한다.

| 시안 | URL path | 이미지 대표 앵커 |
|---|---|---|
|01|/deliverables/manuals/concept-01/index.html|#screen-preview, #screen-dashboard, #screen-reference|
|03|/deliverables/manuals/concept-03/index.html|#screen-first, #screen-comparison_versions, #screen-operator_retry|
|04|/deliverables/manuals/concept-04/index.html|#screen-preview, #screen-business, #screen-evidence, #screen-retry|

공통 앵커: #start(실행 명령/계정표), #navigation(역할표), #mobile, #data(실측·보안), #evidence(검증 경계), #compare(상대 링크).

실제390px 및200%에서 상단 내비게이션/본문 건너뛰기, 앵커 초점, 긴 코드/표의 내부 스크롤과 본문 가로넘침, 그림/alt/캡션, 원본 링크를 확인한다. 오프라인에서는 로컬 그림과 다른 시안·비교·선택 문서 링크를 확인한다. 단순 정적 PASS로 실제 렌더 PASS를 대신하지 않는다. HTTP origin/실측 결과는 root가 실제 검수 후 별도로 기록한다.
