# 시안 02 Vercel 배포

## 현재 배포: Vercel Python + Neon Free

외부 유료 서버 없이 실행하도록 현재 배포는 Vercel FastAPI 함수와 Neon Free로 변경했다.
아래 기존 Docker 프록시 절차는 외부 서버를 사용하던 이전 배포 방식의 참고다.
현재 설정은 Root `project`, Framework `FastAPI`(vercel.json), Node 22,
`npm ci`, `npm run build:vercel`, Output Directory override 없음이다.
`BACKEND_ORIGIN`은 필요하지 않다. `index.py`가 업무 API와 빌드된 `public/` 정적 파일을 제공한다.

Production 환경에 Neon이 연결한 `DATABASE_URL`, `DATABASE_URL_UNPOOLED`와 다음 값을 저장한다:
`MEDIA_STORAGE=database`, `MEDIA_DATABASE_MAX_BYTES=209715200`,
`VERCEL_REQUEST_ANALYSIS=true`, `AI_PROVIDER=openai`, `OPENAI_MODEL=gpt-4.1-mini`,
`AI_REQUESTS_ENABLED=true`, `SESSION_COOKIE_SECURE=true`, `SESSION_COOKIE_NAME=storeloop_concept_02_session`.
`OPENAI_API_KEY`와 신규 DB 시연 계정 생성에 쓸 24자 이상 `DEMO_PASSWORD`는 Secret으로 저장한다.
기존 계정이 있으면 빌드 초기화는 비밀번호·시연 데이터를 변경하지 않는다.
Origin은 Vercel이 제공한 `VERCEL_PROJECT_PRODUCTION_URL`을 사용하며 필요하면 `ALLOWED_ORIGINS`로 지정한다.

인증된 제출·상태 조회·명시적 재처리에서 해당 분석 작업만 ASGI background task로 실행한다.
외부 무한 루프 worker와 공개 AI 엔드포인트는 필요하지 않으며 기존 작업 소유권·lease·결과 검증은 유지한다.
함수는 180초, AI는 120초 이내로 제한한다. 중단된 작업은 후속 인증 조회에서 만료 처리하며 유료 자동 재시도를 하지 않는다.
사진은 권한 검사 후 DB에서 읽고, 200MiB 저장 상한을 적용한다. 무료 DB의 다른 테이블도 공간을 사용한다.
Vercel 업로드 제한 때문에 배포 빌드에서는 브라우저가 사진을 축소하여 전체 3.5MiB 이하로 보낸다.
실제 AI 호출은 프로모션 크레딧을 소비한다. 무료 자원 한도 초과 시 유료로 자동 전환하지 않고 사용을 중단하거나 자료를 정리한다.

## 공개 시연과 동시 역할 탭

기본값은 비활성이다. 명시적인 공개 시연 승인 후 Production에
`DEMO_MULTI_ROLE_ENABLED=true`, `DEMO_PUBLIC_ACCESS_ENABLED=true`를 설정하고 재빌드한다.
빌드 스크립트가 비밀이 아닌 두 플래그만 프론트에 전달한다.
다른 PC에서도 최초 접속 시 시연 계정 세션을 자동 발급하고 점주·영업·운영자 탭을 함께 사용할 수 있다.
세 역할은 별도 HttpOnly 쿠키를 사용하며 서버 역할 검사와 CSRF/Origin 검사를 유지한다.
비밀번호와 API 키는 프론트 소스나 브라우저 저장소에 포함하지 않는다.

공개 모드에서는 계정·매장·기준·운영 설정 변경을 차단한다.
사진 신규 제출과 실패 작업 재처리는 전체 방문자 합계 UTC 하루 20건으로 제한한다.
이 제한은 기존 대기 작업의 실행 횟수 제한은 아니며 무료 서비스의 전체 비용 상한도 아니다.
공개 시연 사진과 제출 결과는 같은 시연 계정을 사용하는 방문자 사이에 공유된다.
실제 개인정보·민감한 매장 사진을 넣지 않는 별도 시연 DB에서만 활성화한다.
공개 접근을 중단하려면 두 플래그를 false로 변경하고 재배포한다.

## 이전 외부 Docker 서버 배포 방식

Vercel은 세 역할의 정적 프론트와 /api 프록시를 담당한다. 외부 Linux 서버의 기존 Docker Compose가 Python API·AI·worker·PostgreSQL·사진 볼륨을 실행한다. 서버와 API 주소는 아직 발급되지 않았으며 이 문서는 신규 배포 절차다. main은 변경하지 않는다.

## 1. 준비

- GitHub 저장소 yuyu2323/hack2026의 codex/concept-02 브랜치 접근 권한.
- Vercel 프로젝트 생성 권한. 요금제는 팀 이용 조건에 맞게 선택한다.
- Docker Engine/Compose v2, Git, Python 3가 설치된 Linux 서버와 공개 HTTPS 도메인.
- 서버 DNS A 레코드 연결, 외부 TCP 80/443 허용. PostgreSQL·AI 포트는 공개하지 않는다.
- 실제 OpenAI API 키는 서버 .local/deploy.env에만 저장한다. Vercel/VITE_*에 넣지 않는다.

이하 backend.example.com 및 PROJECT.vercel.app은 예시이며 실제 주소로 교체한다. 프론트는 Vercel 기본 도메인을 사용할 수 있다.

## 2. 외부 서버 시작

서버 터미널에서:

```sh
git clone --branch codex/concept-02 --single-branch https://github.com/yuyu2323/hack2026.git storeloop
cd storeloop/project
python3 deploy/prepare_env.py --origin https://backend.example.com
nano .local/deploy.env
docker compose --env-file .local/deploy.env -f deploy/compose.yaml up -d --build
docker compose --env-file .local/deploy.env -f deploy/compose.yaml ps
```

편집기에서 OPENAI_API_KEY를 채우고 AI_REQUESTS_ENABLED=false를 유지한다. init은 정상 완료 후 종료된다. 나머지 서비스는 실행되어야 한다. 기존 Caddy 프론트 컨테이너는 HTTPS/API 진입점으로 그대로 유지한다. 서버 전체 설명은 [11-deployment.md](11-deployment.md)를 따른다.

Vercel 주소를 이미 알고 있다면 처음부터 분리하여 생성할 수 있다:

```sh
python3 deploy/prepare_env.py --origin https://PROJECT.vercel.app --backend-origin https://backend.example.com
```

기존 환경 파일이 있으면 위 명령은 덮어쓰지 않는다. 기존 값은 nano로 필요한 항목만 수정한다.

## 3. Vercel 가져오기

Vercel → Add New → Project → GitHub 저장소 가져오기. 아래 값을 적용한다.

| 설정 | 값 |
| --- | --- |
| 배포할 브랜치 | codex/concept-02 |
| Root Directory | project |
| Framework Preset | Other |
| Install Command | npm ci |
| Build Command | npm run build:vercel |
| Output Directory | Override 끔; 직접 지정하지 않음 |
| Node.js | 22.x |
| Environment Variables | BACKEND_ORIGIN=https://backend.example.com |

BACKEND_ORIGIN을 Production에 설정한다. Preview도 필요하면 해당 환경에 별도 설정하되 아래 Origin 허용과 운영 데이터 주의사항을 따른다. 주소에는 /api 경로를 넣지 않는다. 키나 비밀번호를 넣지 않는다.

project/vercel.json이 설치/빌드 설정을 제공한다. 기존 대화의 일반 Vite 설정과 달리 이 구현은 **Other + Build Output API**를 사용한다. Vite 자체 빌드는 그대로 사용하며 .vercel/output/static에 정적 파일, config.json에 환경변수로 확정한 프록시 경로를 생성한다. Output Directory를 web-concepts-02/dist로 강제하면 프록시 구성이 누락될 수 있다. 이전 설정이 남아 있다면 위 값으로 교체한다.

BACKEND_ORIGIN이 없거나 잘못된 URL이면 빌드를 실패시킨다. 환경변수를 변경하면 반드시 Redeploy한다. 빌드 중 백엔드나 GPT를 호출하지 않는다.

Settings → Environments → Production → Branch Tracking에서 codex/concept-02를 지정한다. GitHub 기본 브랜치를 바꾸거나 main에 merge하지 않는다. 첫 가져오기가 main으로 시작됐다면 브랜치를 수정한 뒤 시안 02로 새 Production 배포를 실행한다.

## 4. 최종 Vercel 주소 연결

프로젝트의 고정 Production 주소를 확인하고 서버의 .local/deploy.env를 편집한다:

```dotenv
PUBLIC_ORIGIN=https://PROJECT.vercel.app
SITE_ADDRESS=backend.example.com
SESSION_COOKIE_SECURE=true
AI_REQUESTS_ENABLED=false
```

```sh
docker compose --env-file .local/deploy.env -f deploy/compose.yaml up -d api worker
```

PUBLIC_ORIGIN은 브라우저에서 여는 Vercel origin으로 ALLOWED_ORIGINS에 전달된다. SITE_ADDRESS는 백엔드 TLS 인증서 도메인이다. 둘을 혼동하지 않는다. Cookie Domain은 추가하지 않는다. 현행 host-only Secure/Lax 쿠키 및 CSRF 토큰을 그대로 사용한다.

Preview URL은 자동 허용되지 않는다. 테스트가 꼭 필요하면 정확한 origin을 PUBLIC_ORIGIN에 쉼표로 추가하고 재시작한다. 모든 *.vercel.app을 허용하지 않는다. Preview도 같은 백엔드를 지정하면 운영 데이터에 접근하므로 심사용은 고정 Production URL만 공유하는 것을 권장한다.

## 5. 심사 계정과 실제 AI

Settings → Deployment Protection에서 Production URL이 심사위원의 Vercel 로그인 없이 열리는지 확인한다. StoreLoop 자체 로그인은 유지한다.

| 화면 | 경로 | 시연 계정 |
| --- | --- | --- |
| 점주 | /store-owner | owner.north |
| 영업관리 | /ofc-admin | hq.demo 또는 ofc.north |
| 플랫폼 | /platform-admin | operator.demo |

비밀번호는 서버에서 다음 명령으로 확인하고 심사위원에게만 전달한다:

```sh
docker compose --env-file .local/deploy.env -f deploy/compose.yaml exec api cat /app/.local/demo-credentials
```

실제 AI 테스트는 사용자가 진행한다. 그때만 서버 환경의 AI_REQUESTS_ENABLED=true로 변경하고 적용한다:

```sh
docker compose --env-file .local/deploy.env -f deploy/compose.yaml up -d ai
```

비활성 상태에서는 실제 분석이 실행되지 않는다. 키 유효성·실제 품질·과금은 이 배포 소스 준비로 검증되지 않는다. 비용은 Vercel·외부 서버·OpenAI 사용량이 별도다.

## 6. 검증과 업데이트

로컬에서 유료 호출 없이 빌드 산출물을 확인할 수 있다:

```sh
npm ci
npm run test:vercel
BACKEND_ORIGIN=https://backend.example.com npm run build:vercel
```

위 예시 주소는 빌드 구조 확인에만 사용하며 실제 배포에는 실제 서버 주소가 필요하다. 생성된 .vercel은 Git 제외다.

외부 배포 후 최소 확인: 외부 네트워크의 시크릿 창에서 로그인, 세 역할 URL 새로고침, 사진 업로드/조회, 로그아웃 확인. 사용자가 AI 1회 검증. 프록시의 대용량 업로드·Origin/쿠키 전달은 실제 Vercel 환경에서 확인해야 한다. 로컬 라우팅 테스트는 이를 대신하지 않는다.

| 증상 | 확인 |
| --- | --- |
| 빌드 BACKEND_ORIGIN 오류 | Production 환경에 공개 HTTPS origin 설정 후 Redeploy |
| 로그인/저장 403 | PUBLIC_ORIGIN이 접속 중인 Vercel 주소와 일치하는지 확인 |
| API 502/504 | 서버 실행, DNS/TLS, 방화벽, BACKEND_ORIGIN 확인 |
| 새로고침 404 또는 API가 HTML 반환 | Other/빌드 명령/Output Directory override 및 배포 브랜치 확인 |
| Vercel 로그인 화면 | Production Deployment Protection 확인 |
| AI 비활성 | 팀 테스트 시작 시 AI_REQUESTS_ENABLED 활성화 |

프론트는 codex/concept-02 push로 갱신된다. 백엔드 변경은 서버에서 아래를 별도로 실행한다:

```sh
git pull --ff-only origin codex/concept-02
docker compose --env-file .local/deploy.env -f deploy/compose.yaml up -d --build
```

DB와 사진은 Docker 볼륨에 저장된다. down -v는 데이터를 삭제하므로 업데이트에 사용하지 않는다.

공식 근거: [Build Output API](https://vercel.com/docs/build-output-api), [라우팅 설정](https://vercel.com/docs/build-output-api/configuration), [외부 rewrites](https://vercel.com/docs/routing/rewrites), [Git 배포](https://vercel.com/docs/git).
