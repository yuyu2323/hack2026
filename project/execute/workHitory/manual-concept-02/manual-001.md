# MANUAL02-001 작성 이력
- 상태 RUNNING / contract_ai
- 최종 UX가 확인되는 시안02부터 작성한다. 다른 시안은 실제 캡처와 최종 소스 동결 전 완료 매뉴얼을 만들지 않는다.
- 한 시안 한 접속 주소(02: http://127.0.0.1:5174), 5역할, 로컬 자격 안내 위치만 설명하고 비밀번호 원문은 읽거나 복사하지 않는다.
- v0.9 한국어 오프라인 HTML 작성, 역할5·실제 경로/메뉴·점주/영업/운영·오류·실제AI와Mock·실측 한계·전체 시연 순서 포함. 실제 사용 가능한 PNG4장 상대경로 복사. 정적 링크/목차/alt/UTF8 확인 통과(static-check.json), Browser 렌더 검수 대기.

- 현재 실제 화면 7장과 선택 기록 링크를 반영했다. MEDIA-CLARIFY-2에 따라 영업 관리자의 현재 범위 내 교체·비활성 Reference 이력 사진 조회, 점주의 활성/허용된 과거 점검, 운영자의 사진 접근 금지를 구분해 설명했다. 본 안내는 권한 계약을 설명하며 브라우저에서의 수정 검증 완료를 의미하지 않는다.

- S-O05 비교 날짜/버전 보완 소스 인계 후 매뉴얼에 KST 제출 일시·적용 기준 펼침·항목별 전후 버전 읽기를 추가했다. 변경된 비교 화면의 최종 캡처와 Browser 문서 렌더는 root 인계 후 확인한다.

- 최근 비교 날짜/기준버전 및 MEDIA-CLARIFY-2와 본문을 재대조했다. 내용 모순 없음. 현재7장 가운데 비교사진 교체·Browser 문서 렌더는 그대로 대기한다.

## CMD-01 시작 환경·종료 절차 정합화

root의 한정 요청에 따라02의 준비 절에 Python3.11/Node22.12/npm10/PostgreSQL14 최소환경과 setup 역할, 전체README 링크를 추가했다. DB 종료는 stop 전에 PID기록→stop 종료요청→기록 프로세스 종료확인→db.sh stop 순서이며,즉시반환/timeout시DB유지/별도터미널프롬프트복귀 및 처리중worker의API·AI·DB유지를 설명한다. 상세 명령은 docs10의 검증된 종료 절차앵커로 연결하여 중복 명령을 새로 만들지 않았다.

정적 검수 PASS: UTF8/lang ko·목차참조12개/로컬경로21개·신규Markdown절앵커·중복ID없음·외부의존없음·기존7장hash불변. Gitleaks stdin exit0. HTML SHA-256 e648f314a009d83bf60b7c552eb34935f5682f5bfeff394bc62bee572d359ee4로 REVIEW 동결한다. 실제 서비스를 실행/중단하지 않았고 다른매뉴얼/README/docs10을 수정하지 않았다. Browser 렌더는 root 인계 후 검수한다.

## D-MAN02-01 표 키보드 접근 보완

root 실제 Browser 검수에서 발견한7개 표의 이름/키보드진입 누락을 보완했다. .table-wrap에 내용별 aria-label·role region·tabindex0을 추가하고 focus-visible3px #b85424/offset4px로 현재 위치를 표시한다. 기존 CSS 배치/폭/본문·7개이미지는 그대로다. 변경한 속성과초점규칙을 제거한 문자열이 직전CMD-01반영본과 정확히 같음을 확인했다.

정적 검사7개 모두PASS/고유 이름·tabindex/region·기존내용불변/Gitleaks0, 근거 table-a11y-check.json. 최종HTML SHA6065e1fa38470d33f81a17ac56050e8962d3615e5b0166bed3e071ca79229887로 REVIEW 동결하고 root의 실제모바일Tab/ArrowRight 재검수를 요청했다. 소스 PASS를 실제조작 PASS로 표기하지 않는다.

## D-MAN02-02 모바일 로그인ID 줄바꿈

root가 인계한 실제390 표 캡처를 직접 확인했다. 표의 code가 overflow-wrap:anywhere를 상속해 owner.north/regional.north 등을 중간분할한다. 표 안 code에만 nowrap/overflow-wrap:normal/word-break:normal을 추가하여 식별자를 한 줄로 유지했다. 표 영역의 가로스크롤·명명region·초점과 표 밖 긴경로 줄바꿈은 유지했다. 추가 CSS 규칙을 제거한 문자열이 기존 HTML과 정확히 일치하고 7개 이미지 해시도 불변이다. 새 HTML SHA-256 `50421f5b5e5fab2f074af7f0537d36354998c325ffba86684fa2533d7ddfa9b3`. 실제 모바일 너비/표 내부 스크롤/식별자 표시는 root와 독립검토자의 재촬영을 기다린다.

## 실제 문서 렌더 상태 갱신

root 실제 Browser와 contract_data 독립 재검수에서1440×900/390×844 문서·7이미지·키보드/본문건너뛰기·식별자표시가 확인되었다. 해당 범위만 문구로 갱신했다.200% 사용자후속·OS차단오프라인·인쇄 NOT_RUN 및 전체제품인수진행은 유지한다. Markdown 링크HTTP200과내장문서보기불가를구분해 편집기로읽는방법을안내했다. CSS/figure/7이미지해시불변·로컬경로22개확인. 해시와 근거는browser-status-copy.json이다.

- 매뉴얼 우선 사용자 지시: CSRF/Reference409의 초안·사진 보존과 명시재저장, 통신/대기시간초과·입력 경계 완료를 본문에 반영. CSS/figure/7이미지 불변, 링크 검사 PASS. 새로운 Browser 검수는 하지 않음. manual-priority-update.json 참조.
