# StoreLoop · Concept 01 관제 데스크

단일 React 앱 안에서 점주·OFC·지역·본사·플랫폼 운영자 업무를 제공합니다. 공통 API 외에 다른 시안의 소스를 공유하지 않습니다.

## 실행

프로젝트 루트에서 공통 서버를 8000 포트에 실행한 뒤:

```sh
npm install
npm run dev --workspace=@storeloop/concept-01
npm run build --workspace=@storeloop/concept-01
npm run preview --workspace=@storeloop/concept-01
```

dev와 preview는 `http://127.0.0.1:5173`이며 `/api`를 `127.0.0.1:8000`에 전달합니다. 동일 포트에서 dev와 preview를 동시에 실행하지 않습니다. 시연 계정은 루트의 런타임 `.local/demo-credentials` 안내를 따릅니다. 비밀번호를 이 문서나 캡처에 복사하지 않습니다.

## 주요 흐름

- 점주: 내 매장 현황 → 사진 제출 → 결과·사진 근거 → OFC 확인 요청 / 개선 후 다시 제출 → 이전 사진과 비교.
- OFC·지역·본사: 매장 관제의 동일 필터 지표 → 건별 사진·기준 → OFC 조치. 관리 매장에서 후보 담당 등록(OFC), 진열 기준의 새 버전과 Reference 관리, 추이·Mock 분석.
- 운영자: 서비스 상태 → 계정·연결 / 기준 정보 → 작업 상세·실패 재처리 → 감사 이력. 영업 사진·질문·평가를 조회하지 않습니다.
- 운영 공지는 모든 역할의 상단 안내에 표시됩니다. 필터와 페이지는 URL에 남아 브라우저 뒤로 가기로 복원됩니다.

## 검증

```sh
npm run test --workspace=@storeloop/concept-01
npm run test:ui --workspace=@storeloop/concept-01
npm run build --workspace=@storeloop/concept-01
```

정책 및 UI 단위 검증은 실제 AI·브라우저 인수를 대체하지 않습니다. 실제 분석, 독립 기능·디자인 검수, 실제 화면이 들어간 HTML 매뉴얼은 오케스트레이터의 후속 증거에 따라 확정합니다.

## 데이터 표현

판단 불가는 정상 평가 결과의 제한이며 기술 실패와 다릅니다. 준수율과 판단 가능률을 함께 표시하고 null은 `—`로 표시합니다. Mock 평가·매출, AI 생성 시연 사진에는 출처를 표시합니다. 매출 상관관계는 인과관계나 예측을 의미하지 않습니다.
