# MAN-RUNTIME-001 실행 안내 정합화

상태: REVIEW — 정적 4개 PASS, root와 독립 검토자에게 hash 인계 완료

root의 실제 문서 렌더에서 발견한 Node 22+ 표현을 README/docs/10 CMD-01과 맞춰 Node 22.12 이상·npm 10 이상으로 정정했다. stop.sh는 SIGTERM 후 반환하므로 DB 중지 전에 해당 실행 프로세스 종료를 확인하고, stop 전 README의 관리 PID 기록 절차를 읽도록 안내했다. 별도 터미널의 서버는 프롬프트 복귀를 확인하도록 명시했다.

대상은 네 매뉴얼 HTML과 자체 초안 생성기의 동일 문구다. CSS·figure HTML·로컬 이미지 byte는 불변이며, 제품 소스·원본 PNG·타 담당 매뉴얼·브라우저·서비스·DB는 변경하지 않았다. 재현성을 위해 runtime-copy.json에 수정 전후 HTML SHA-256을 보존했다. 실제 브라우저/200%/오프라인 인수는 root 담당으로 별도 상태를 유지한다.

검증: `server/.venv/bin/python execute/workHitory/manuals-others/validate_drafts.py`에서 네 문서 모두 PASS. 이미지 수 8/10/10/12와 모든 로컬 링크·anchor·alt·caption을 보존했으며 외부 리소스 의존성과 비밀 값 노출은 없다. 현재 HTTP8088 문서 렌더는 root가 이어서 수행한다.
