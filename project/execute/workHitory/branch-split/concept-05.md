# 시안 05 독립 브랜치

사용자 승인: main을 변경하지 않고 시안별 backend·AI·공유 패키지·프론트만 유지하여 commit/push.
기준 커밋: edb64ba1f977804d5254806ee40337a457b5e60a.

- [ ] 대상 외 프론트·매뉴얼 제거
- [ ] workspace/lockfile/실행 설정/문서 정합화
- [ ] 독립 설치·테스트·빌드·API/프론트 실행 확인
- [ ] 독립 검토·보안 훅 통과

포트: frontend 5185, API 8105, AI 8205, PostgreSQL 55445. 원래 main의 서비스는 유지한다. 실제 AI 추가 호출은 이번 분리 검증에 포함하지 않는다.

## 검증 결과

- fresh `./setup.sh`: 가상환경·npm ci·별도 PostgreSQL·마이그레이션·시드 성공.
- backend(PostgreSQL 포함)/AI/runtime/security/client/frontend/UI/build: 모두 exit 0. `validation-05.json` 참조.
- `./start.sh` 기본 실행: API·AI health, 실제 DB의 세 역할 로그인과 Vite 프록시 인증 응답, HTML 역할 경로 200 및 관리 프로세스 4개 확인. `runtime-05.json` 참조.
- start 직후 일부 Vite가 아직 준비되지 않은 시점에 검사하여 최초 연결 거부가 발생했다. 검사 도구에 HTTP 준비 대기를 적용하여 재검증 통과했으며 제품 오류로 숨기지 않는다.
- 관리 서비스 정상 종료 확인. 이번 검증은 HTTP 실행·테스트·빌드 검증이며 새 브라우저 디자인 검수나 실제 AI 호출 검증을 의미하지 않는다.
- 독립 검토: branch_split_review가 5개 worktree의 의존성·포트·쿠키·문서를 읽기 전용으로 재검토. AI 및 05 프론트 README의 포트 누락을 수정한 뒤 차단 결함 없음 확인.
- docs00~02는 main과 동일. 이전 main의 후행 검수와 실제 AI 증거는 역사 자료로 유지.
- 커밋 및 원격 전송은 이 기록 작성 이후 root가 보안 훅을 거쳐 수행한다. 실제 결과는 Git 이력을 기준으로 확인한다.
