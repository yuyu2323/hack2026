# 시안 02 서버 배포

이 브랜치는 공통 Python API·worker·PostgreSQL·독립 Python AI 서비스·시안 02 프론트(점주/영업관리/플랫폼 운영자)를 배포한다. 기존 main과 다른 시안 브랜치는 변경하지 않는다.

## GPT API 선택과 비용 제어

AI 서버의 `AI_PROVIDER=codex`는 기존 로컬 Codex CLI, `AI_PROVIDER=openai`는 OpenAI Responses API를 사용한다. API 방식에서는 서버에 Codex CLI나 사용자 로그인 파일이 필요 없다. 입력 사진과 Reference의 실제 바이트, 질문, 적용 기준, 이전 결과를 보내며 기존 결과 스키마·참조 검증을 유지한다.

| 환경변수 | 의미 |
|---|---|
| AI_PROVIDER | `codex` 또는 `openai`; 로컬 기본 codex, 컨테이너 openai |
| OPENAI_API_KEY | AI 서버 전용 비밀. 프론트 `VITE_*`나 Git에 넣지 않는다 |
| OPENAI_MODEL | 기본 `gpt-4.1-mini`, 이미지와 Structured Outputs 지원 모델 사용 |
| OPENAI_MAX_OUTPUT_TOKENS | 기본 6000; 출력 상한 초과 시 실패, 자동 추가 호출 없음 |
| AI_REQUESTS_ENABLED | 배포 기본 `false`; 사용자가 실제 검증할 때만 `true`로 변경 |
| AI_MODEL_TIMEOUT_SECONDS | 모델 호출 전체 제한, 기본 120초 |
| AI_SERVICE_TOKEN | 백엔드/worker와 AI 간 내부 인증; OpenAI 키와 별개 |

`health`, 설치, 빌드, 자동 테스트는 GPT API를 호출하지 않는다. 분석 요청당 API 요청 1회, 자동 재시도·CLI fallback·JSON 수선 재호출이 없다. `store=false`를 사용한다. 출력 토큰 제한은 계정 전체 달러 예산 제한과 다르며 입력 이미지·텍스트에도 비용이 발생한다. 실제 인증·모델 품질·과금 검증은 사용자가 진행한다.

근거: [Responses 이미지 입력](https://developers.openai.com/api/docs/guides/images-vision), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini).

## 신규 Linux 서버에 전체 배포

Docker Engine 및 Compose v2, 도메인의 DNS가 서버로 연결된 환경을 전제로 한다. 80/443만 공개하고 DB·API·AI는 Compose 내부 네트워크로 통신한다. 서버 자원이나 계정은 이 저장소가 자동 구매하지 않는다.

```sh
git clone --branch codex/concept-02 --single-branch https://github.com/yuyu2323/hack2026.git storeloop
cd storeloop/project
python3 deploy/prepare_env.py --origin https://YOUR_DOMAIN
```

생성된 `.local/deploy.env`는 0600 권한이며 Git과 Docker build context에서 제외된다. 해당 파일의 `OPENAI_API_KEY`만 실제 키로 채운다. 아직 `AI_REQUESTS_ENABLED=false`를 유지한다. 비밀번호·내부 인증 값은 hex로 생성하므로 DB URL에서 안전하게 사용할 수 있다. 임의로 기호가 포함된 DB 비밀번호를 넣으려면 URL 인코딩까지 맞춰야 한다.

```sh
docker compose --env-file .local/deploy.env -f deploy/compose.yaml up -d --build
docker compose --env-file .local/deploy.env -f deploy/compose.yaml ps
```

초기화 서비스가 마이그레이션 후 `SEED_DEMO=true`일 때 합성 시연 계정을 생성한다. 계정의 비밀번호는 API 컨테이너의 `/app/.local/demo-credentials`에만 저장된다. `docker compose ... exec api`로 컨테이너에 접속하여 본인 터미널에서 확인한다. 계정은 점주 `owner.north`, 영업 본사 `hq.demo`/OFC `ofc.north`, 플랫폼 운영자 `operator.demo`다. `SEED_DEMO=false`인 신규 DB에는 로그인 계정이 없으므로 별도 운영 계정 초기화가 필요하다.

접속 경로는 동일 도메인의 `/store-owner`, `/ofc-admin`, `/platform-admin`이다. 프론트 Caddy가 HTTPS를 제공하고 `/api/*`를 Python API로 프록시하므로 기존 쿠키·CSRF 방식이 유지된다. 사진/계정 생성 파일은 application 볼륨, DB는 database 볼륨에 영속화된다. 볼륨을 삭제하는 `down -v`는 데이터를 지운다.

실제 GPT 테스트를 시작할 때 `.local/deploy.env`에서 `AI_REQUESTS_ENABLED=true`로 설정하고 AI 컨테이너만 갱신한다.

```sh
docker compose --env-file .local/deploy.env -f deploy/compose.yaml up -d ai
```

테스트를 끝내면 false로 되돌리고 같은 명령으로 적용한다. 실패한 기존 요청은 자동 재처리하지 않으며 플랫폼 운영자에서 명시적으로 처리한다.

## Sites 배포 경계

Sites는 프론트 정적 출력 또는 Cloudflare Worker ESM을 배포한다. 현재 Python ASGI 프로세스·상시 worker·PostgreSQL을 그대로 실행하는 Docker 호스트를 제공하지 않는다. 따라서 Sites만 연결한 상태로 전체 배포 완료를 선언할 수 없다.

Sites를 프론트에 사용할 경우 Python 서버를 먼저 외부 HTTPS 주소로 배포하고, Sites Worker의 같은 origin `/api/*` 프록시를 해당 서버로 연결한다. 브라우저에서 외부 API 주소를 직접 호출하도록 바꾸면 현재 CSRF/쿠키 정책과 충돌하므로 단순 VITE_API_URL 교체만으로 배포하지 않는다. Python `ALLOWED_ORIGINS`에는 실제 Sites origin을 추가하고 `SESSION_COOKIE_SECURE=true`를 유지한다. OpenAI 키는 Sites 프론트가 아닌 Python AI 서비스에만 둔다.

현 단계에서는 외부 Python 호스팅 계정·서버·도메인 입력을 기다린다. 별도 계정 없이 임의 유료 서버를 만들거나 로컬 컴퓨터를 공개 터널로 노출하지 않는다.

## 검증 경계

AI 어댑터 모의 응답 테스트는 인증 실패·429·미완료·refusal·JSON/참조 오류·타임아웃·호출 비활성화·자동 재시도 없음·이미지 순서를 확인한다. 실제 유료 API는 호출하지 않는다. 컨테이너 로컬 검증 결과와 외부 배포 여부는 `execute/workHitory/api-deployment/concept-02.md`에 기록한다.

### Sites 앞단 연결 파일

`deploy/sites`는 별도 Sites 소스로 등록할 수 있는 Worker 프로젝트다. 컨테이너 프론트와 API를 같은 HTTPS 서버로 올린 뒤 Sites의 `BACKEND_ORIGIN`에 그 origin을 지정한다. 이 Worker는 세 역할 화면과 정적 파일 및 `/api/*`를 같은 origin으로 제공한다. 호스팅 로그인 쿠키·Authorization은 외부 서버로 전달하지 않고 StoreLoop 앱 세션만 전달한다. 공개 Python 서버의 `ALLOWED_ORIGINS`에는 Sites의 실제 origin을 추가해야 한다. API 서버 주소가 없으면 503을 반환하며 임의 목업 성공으로 대체하지 않는다.

호스팅 순서는 외부 컨테이너 서버 준비 → Sites 신규 등록 및 project_id 설정 → BACKEND_ORIGIN 설정 → Sites 공식 소스·빌드·저장·private 배포 절차다. Worker build는 `npm run build`, 로컬 모의 테스트는 `npm test`이며 네트워크를 호출하지 않는다. `.openai/hosting.json`은 실제 등록 결과의 project_id만 사용하며 임의 ID를 저장하지 않는다.

## Vercel을 프론트로 사용

현재 선택한 Vercel 구성은 [12-vercel-deployment.md](12-vercel-deployment.md)를 따른다. Sites 등록은 필요 없다. `prepare_env.py --origin https://PROJECT.vercel.app --backend-origin https://backend.example.com`으로 프론트 허용 Origin과 백엔드 TLS 주소를 분리할 수 있다.
