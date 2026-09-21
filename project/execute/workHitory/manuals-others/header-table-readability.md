# D-MAN-H01 및 표 로그인 ID 가독성

상태: REVIEW 동결 — 정적 4개 PASS, root 및 독립 검토자에게 최종 hash 인계

실제 desktop 렌더에서 14px 헤더 메타 문구의 대비 2.047:1이 확인돼 네 HTML의 `header .compact`만 #e1edef로 변경했다. #173c48 배경 대비는 9.886:1이며, print의 기존 검정 선택자에 `header .compact`를 추가해 밝은 색이 인쇄에 남지 않도록 했다. 본문 .compact 색상은 유지했다.

root/contract_data의 모바일 표 로그인 ID 중간 분할 보고에 따라 `.table code{white-space:nowrap;overflow-wrap:normal;word-break:normal}`만 추가했다. 기존 `.table{overflow:auto}`와 표 최소 폭을 유지한다. 페이지/표 이외 code 및 본문 줄바꿈 규칙은 변경하지 않았다.

검증은 WCAG 대비 수식 계산, CSS 외 HTML 원문 불변, 8/10/10/12개 이미지 byte 불변, `server/.venv/bin/python execute/workHitory/manuals-others/validate_drafts.py` 네 문서 PASS다. selectors와 수정 전후 SHA-256은 header-table-readability.json에 기록했다. 제품 소스·원본 PNG·02 매뉴얼·브라우저·서비스는 변경하지 않았다. 이번 한정 소유는 네 HTML 및 검사 기록이므로 초안 생성기는 변경하지 않았다.

실제 desktop/mobile 재촬영은 root·contract_data가 진행한다. 200% 검수는 사용자 후속 확인으로 NOT_RUN이며 본 소스/정적 검사로 대체하지 않는다.
