# Vercel 전체 배포

- 요청: codex/concept-02 프론트·API·AI를 무료 DB와 기존 Vercel 프로젝트로 배포한다.
- 기존 로컬 변경을 보존하기 위해 최신 원격 커밋의 별도 worktree에서 작업한다.
- Neon Free PostgreSQL에 사진을 함께 저장하고, 인증된 요청의 유한 background 작업으로 분석을 실행한다.
- API 키·DB 연결 문자열·시연 비밀번호는 배포 환경변수만 사용한다.
- 검증: DB 마이그레이션·시드, 서버/AI 단위 테스트, 프론트 빌드, 실제 배포/로그인/사진/AI 1회 확인.
- 소유권: root 배포/설정/초기화, backend_deploy_review 분석 실행, db_media_storage 미디어 모델/마이그레이션.
