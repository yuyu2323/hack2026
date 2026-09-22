# 시안 02 Vercel 배포 소스 준비

## 변경
- Vercel Build Output API로 BACKEND_ORIGIN 환경변수를 빌드 시 외부 API 프록시로 반영. 실제 origin 미정 상태에서도 비밀이나 예시 주소를 고정하지 않음.
- API 경로/메서드 유지, 비캐시 응답, 정적 파일 우선 및 역할 화면 SPA 새로고침 지원.
- prepare_env.py의 선택적 --backend-origin으로 프론트 허용 Origin과 Caddy TLS 주소를 분리. 기존 CLI 동작 및 기존 파일 덮어쓰기 금지 유지.
- Vercel 업로드 제외 파일 및 생성 산출물 Git/Docker 제외, README 및 전용 단계별 가이드 추가.

## 검증
- npm run test:vercel: 3 PASS (URL 검증·API 전달 경로·SPA 분리).
- BACKEND_ORIGIN=https://backend.example.com npm run build:vercel: TypeScript/Vite 빌드 및 .vercel/output 생성 PASS. 예시 도메인으로 네트워크 요청 없음.
- 임시 디렉터리에서 환경 생성 단일/분리 origin, 0600 파일 권한, AI 비활성 기본값, 기존 파일 보존 PASS.
- 첫 빌드 호출은 저장소 루트에서 실행해 npm script를 찾지 못했으며, project 디렉터리에서 재실행하여 위 결과 확인.
- 독립 검토자: 라우팅/쿠키/CSRF 설정 차단 사항 없음, 설정 테스트 3 PASS.
- 외부 Vercel 배포 및 실제 Origin/쿠키/사진 업로드: NOT_RUN. 외부 서버·Vercel 주소 설정 후 확인 필요.
- 유료 OpenAI 호출: NOT_RUN (사용자 직접 테스트 방침).
