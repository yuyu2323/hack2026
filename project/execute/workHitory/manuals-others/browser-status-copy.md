# MAN-BROWSER-STATUS-001 검수 현황 갱신

상태: REVIEW 동결 — 정적 4개 PASS

root의 실제 문서 검수 인계와 `execute/workHitory/manuals-browser/independent-recheck.md`를 근거로 네 HTML의 문서 브라우저 NOT_RUN/모바일 검수 대기를 갱신했다. 지정 desktop1440×900/mobile390×844에서 로컬 이미지, 키보드 이동 및 본문 건너뛰기를 확인한 범위만 반영했다. 200%는 사용자 후속 검사로, OS 네트워크 차단에 의한 오프라인 검사는 미실행으로 남겼다. 전체 제품 인수 진행 상태를 유지했다.

외부 CDN·스크립트 없음과 모든 로컬 이미지 실제 렌더 PASS를 네 문서에 구분해서 명시했다. README/기록 .md는 HTTP200 확인과 내장 Browser의 Markdown 문서 보기 불가를 구별해 로컬 편집기로 여는 안내를 추가했다. 새 독립 재검수 기록 링크도 연결했다.

시안01 actual-ai.json의 first/child references는 각각2이며 기존 HTML의 첫 분석2개 표기가 이미 정확해 수량은 변경하지 않았다. 시안04의3개도 양쪽 실행 정본과 일치하여 유지했다.

CSS·figure HTML·8/10/10/12개 이미지 byte 불변. 자체 정적 검증기 범위 설명도 최신 실제 검수와 미실행을 구분하도록 갱신했다. `server/.venv/bin/python execute/workHitory/manuals-others/validate_drafts.py` 네 문서 모두 PASS. 최종 SHA-256은 browser-status-copy.json 및 static-validation.json에 있다. 제품 소스·그림 원본·02 매뉴얼·브라우저·서비스/DB는 변경하지 않았다.
