# 최소 필수 실행 인계 검증

2026-09-21 · root · **PASS — 확인한 실행 범위**

사용자의 검수 최소화·매뉴얼 우선 요청에 따라 새 경계·AI 검수를 추가하지 않았다. 이 기록은 전체 디자인 인수 PASS를 뜻하지 않는다.

- `./scripts/setup.sh` 최초 실행은 macOS system Python의 인증서 저장소 문제로 Gitleaks 다운로드에서 실패했다. [실패 로그](setup.log).
- `ssl.create_default_context()`에 lock으로 설치된 certifi CA를 추가했다. TLS 인증서·호스트 검증과 고정 SHA-256 검증은 유지한다. setup과 보안 테스트는 준비된 server venv를 사용하며 CI는 같은 고정 certifi를 설치하도록 구성했다. 원격 CI 실행은 NOT_RUN이다.
- 설치기 회귀 2개 RED→GREEN, [독립 검토](independent-installer.md) PASS. TLS 검증과 체크섬 불일치 시 기존 파일 보존을 검사했다.
- 같은 setup 명령 재실행 exit0. 의존성·보안 검사기·마이그레이션·합성 시드 완료, 기존 seed 263개 보존. 기존 DB 초기화나 삭제 없이 재현했다. [로그](setup-rerun.log).
- 최종 소스로 5개 `tsc --noEmit && vite build` 모두 PASS. [빌드 로그](build-all.log), [JS hash](build-files.json).
- 문서의 모든 시안 start 명령 exit0, 두 번째 실행은 8개 서비스를 모두 이미 실행 중으로 확인했다. [시작](start.log), [중복 시작](start-idempotent.log).
- 관리된 dev 5개를 종료하고 문서의 `npm run preview --workspace=@storeloop/concept-0N`으로 각 고정 포트에서 실행했다. 일반 시연 DB에서 점주·본사·플랫폼 운영자 3경로군×5 시안의 직접 접속/로그인 및 새로고침을 확인했다. 각 경로의 역할과 화면 렌더를 확인했으며 일부 즉시 스냅샷은 업무 데이터 로딩 상태를 포함한다. 전 기능 재검증으로 확대하지 않는다. 확인 시 새 검수 탭 콘솔 warn/error는 0건이었다. [브라우저 원시 근거](preview-browser.json).
- preview 5개 종료 후 stop 실행, 기록된 모든 관리 PID 종료 확인, PostgreSQL 유지. [종료 로그](stop.log), [종료 확인](stop-result.json).
- 다시 문서 start 명령으로 API·AI·worker·dev 5개를 실행했다. 현재 일반 `storeloop` 시연 DB를 사용하며 기존 실제 AI 인수 결과는 `storeloop_test`에 보존한다. [재시작](start-final.log), [최종 실행 확인](runtime-final.json).

추가 실제 모델 호출은 0회다. 200% 확대는 사용자 후행 선택이며, 미확인 디자인·키보드·목록 세부 근거와 전체 최종 인수는 별도로 남긴다. [독립 상태 대조](independent-completion-audit.md).

## 마지막 보안 확인

보안 회귀 11개 PASS. 전체 추적 후보 검사에서 이전 검증 보고서의 파일명과 인접한 SHA-256 4개를 일반 API 키로 오탐했다. 두 실제 소스의 현재 해시와 일치함을 확인했고, source_before/source_after의 모든 해시 값을 보존한 채 명시적인 sha256 필드로 기록 형식만 바꿨다. 원본은 사용자 전용 로컬 백업으로 보존했다. 검사 규칙·허용 예외·검증 강도는 변경하지 않았다. [원인·수정 근거](security-resolution.json), [최종 검사 결과](security-final.json), [보안 테스트](security-tests.log).
