# 시안 02 GPT API 및 배포 준비

사용자 요청: codex/concept-02에서 Python 백엔드·3역할 프론트·AI 서버 배포. 환경변수로 Codex CLI/OpenAI API 선택. 실제 유료 API 호출은 사용자가 검증하며 에이전트는 호출하지 않는다. main 변경 금지. 전달된 키 원문은 문서·소스·로그에 기록하지 않는다.

작업: AI 어댑터/모의 테스트 → 컨테이너·환경설정·배포 문서 → 독립 검토 → 로컬 무료 검증 → 배포 가능한 경로 확인.
Sites는 Worker ESM/정적 출력 대상이며 기존 Python·PostgreSQL·작업자 전체 호스팅은 별도 환경이 필요하다. 사용자에게 배포 서버와 제공된 키의 용도를 질문했고 그 외 작업은 진행한다.

## 구현·검증 결과

- AI_PROVIDER=codex/openai 선택과 OpenAI Responses 어댑터, 단일 요청·store=false·출력 토큰 상한·비활성화 스위치 구현.
- AI 테스트 57개 PASS(신규 모의 API 테스트 18개 포함). 런타임 테스트 5개 PASS. 백엔드 인증·작업 관련 비PostgreSQL 테스트 6개 PASS/20 deselected.
- 컨테이너 이미지 3개(backend/AI/frontend) Linux 빌드 및 PostgreSQL/init/API/AI/worker/frontend 시작 성공. 세 역할 HTML·로그인·세션 HTTP 확인 성공.
- 첫 Docker 빌드에서 init/api가 동일 이미지 태그를 동시에 내보내 충돌. build를 api에만 남겨 재빌드 성공.
- Sites Worker 앞단 프로젝트와 비밀 쿠키 분리/같은 origin 프록시 테스트 3개 PASS. 실제 사이트 등록·배포는 하지 않음: 외부 Python 서버 origin 미제공.
- 독립 읽기 전용 검토(api_deploy_review): 이미지·결과 계약, 비용 제어, 영속 볼륨, 라우팅 확인. DB 비밀번호는 prepare_env.py의 hex 생성으로 URL 안전성 확보.
- 전달된 OpenAI 키는 gitignore된 .local/container-check.env(0600)에만 보관하고 AI 서버에 적용. AI_REQUESTS_ENABLED=false 유지. 실제 키 인증 유효성·모델 품질·비용 검증은 NOT_RUN. 유료 모델 호출 0회.
- 로컬 컨테이너 http://localhost:8082는 실제 외부 배포 URL이 아니다. 신규 외부 서버/호스팅 계정과 도메인을 기다림. main의 파일·커밋은 변경하지 않음.
