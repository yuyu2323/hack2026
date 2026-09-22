# 진행 기록

- 기존 배포 실패는 잘못된 FastAPI 감지와 repository root 선택 때문임을 확인했다.
- 사용자가 외부 서버 없음 및 무료 범위만 사용을 지정했다. 상시 Docker 서버 대신 Vercel Python 함수와 Neon Free를 사용한다.
- OpenAI 프로모션 크레딧 등록을 확인했으며 사용자 승인으로 Responses 전용 30일 만료 키를 생성했다. 키 값은 기록하지 않는다.
- Neon 약관 동의는 사용자에게 받은 후 진행했다. 무료 플랜만 선택했다.

## 2026-09-22 운영 배포 확인

- 원격 codex/concept-02에 8a1669b2170c7257e824afb6280e9d7690433002 반영.
- Vercel Production 추적 브랜치를 codex/concept-02로 변경하고 신규 운영 빌드를 실행했다.
- 배포 B6ve6f17TbbkfMZG6EYCSu878rjU: Ready, 35초. 빌드 로그에서 신규 DB 초기화 완료 확인.
- 운영 주소: https://hack2026-iota.vercel.app
- 리소스 화면에서 Python 3.12 함수 /fastapi, 45.5 MB 확인.
- Neon Free PostgreSQL 및 Production 비밀 환경변수 연결 완료. 키/비밀번호/DB 연결 값은 기록하지 않았다.
- 로컬 프론트 빌드 및 관련 단위 테스트 통과는 앞선 구현 기록 참조.
- 운영 브라우저는 Chrome ERR_BLOCKED_BY_CLIENT로 접속이 막혔다. 사용자에게 직접 브라우저 차단 설정 확인을 요청했다.
- 실제 운영 로그인, 사진 업로드, OpenAI 응답 검증은 미완료이며 배포 성공과 구분한다.
- 사용자가 직접 연 운영 페이지에서 실제 FastAPI 404를 확인해 브라우저 차단과 별개의 프론트 경로 누락을 식별했다.
- index.py에 API 뒤 정적 파일 mount(check_dir=False)를 추가하고 public 파일을 함수 패키지에 포함했다. 기존 SPA rewrites 유지.
- 독립 검토 backend_deploy_review 완료. TestClient로 HTML root 200, health API 우선순위, .env 404 통과.
