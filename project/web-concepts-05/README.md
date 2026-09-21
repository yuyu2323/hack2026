# StoreLoop 05 — 탐색과 비교

각 역할이 현재 범위와 기간을 유지하며 매장·이력·기준·연결을 탐색하는 독립 React 앱이다. 상단 업무 탭, 접을 수 있는 범위 탐색 패널, 이전/이후 비교 작업영역을 사용한다.

## 실행

프로젝트 루트의 `scripts/setup.sh`로 의존성과 로컬 설정을 준비하고, 공통 API·AI·worker를 실행한 뒤 사용한다. 상세 절차는 상위 README와 docs/10-execution.md를 따른다. 브라우저 요청은 `/api` 프록시를 통해 업무 API `127.0.0.1:8105`으로만 보낸다.

```sh
npm run dev --workspace @storeloop/concept-05
npm test --workspace @storeloop/concept-05
npm run build --workspace @storeloop/concept-05
npm run preview --workspace @storeloop/concept-05
```

접속: `http://127.0.0.1:5185/`. dev와 preview를 동시에 같은 포트에서 실행하지 않는다. 각 명령은 한 앱 안에서 모든 역할을 제공한다. 로그인 자격은 런타임의 사용자 전용 로컬 파일을 사용하며 소스·문서에 실제 비밀번호를 넣지 않는다.

## 업무 시작

- 점주 `/store-owner`: 지역·매장·카테고리·UTC 기간으로 이력을 탐색하고 사진 제출, 결과·기준, 개선 재제출·비교, OFC 문의, 내 알림으로 이동한다.
- OFC·지역·본사 `/ofc-admin`: 매장 비교 행렬에서 이력/이슈로 이동하고, 담당 등록, 4단계 진열 기준·버전, Reference, 추이·Mock 상관·기본 리포트를 다룬다. 상위 공통 기준/Reference는 허용 역할만 변경한다.
- 플랫폼 운영자 `/platform-admin`: 상태·계정/조직 연결, 기준 정보, 실패 작업·시도 이력, 감사·공지를 다룬다. 영업 알림·사진·평가·매출 화면을 제공하지 않는다.

## 상태와 보존

필터는 URL에 보존되며 현재 탐색 주소를 복사할 수 있다. 401/권한 오류 시 업무 화면을 비우고 로그인/접근 불가로 전환한다. CSRF 갱신 오류에는 사용자 명시 재시도만 제공한다. 기준/Reference의 409는 초안을 보존하고 최신 수정 버전으로 재시도한다. Reference 계보 충돌은 최신 revision을 조회한다. 사진의 동일 제출 재송신은 동일 중복 키를 유지하며 본문/사진순서가 바뀌면 새 키를 사용한다.

AI는 queued/running/succeeded/failed를 표시하고 2초 간격으로 조회한다. 완료·실패에서 주기 조회를 멈추며 30초 초과에는 지연을 알린다. 판단 불가를 기술 실패나 0%로 바꾸지 않는다. 결과는 원문 평문과 서버 산식을 그대로 표시한다.

`MEDIA-CLARIFY-1`의 `reference_photos`로 snapshot 순서에 맞춘 보호 URL과 출처를 표시한다. 구 서버의 선택 필드 누락은 기존 photo_id URL로 호환하되 출처를 추정하지 않는다. 점주가 `/references` 목록을 추가 호출하지 않는다.

## 검증 경계

작성자 자체 정책·UI 15개와 TypeScript/Vite 빌드 PASS. 실제 브라우저·PostgreSQL·실제 AI·독립 디자인 검수는 root의 별도 인수 증거를 확인해야 한다. 단위/UI 테스트는 합성 응답이며 실제 AI 성공을 뜻하지 않는다. 상태와 체크리스트는 `execute/checkList/frontend-concept-05` 및 `execute/workHitory/frontend-concept-05`에 기록한다.
