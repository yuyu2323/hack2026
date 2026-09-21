# frontend-concept-05 이력
2026-09-21: root 전담 배정 수신. 소유 파일만 수정, 공유 DB/브라우저/lock 변경 없음. DS05-001을 구현 전에 작성했다. PD-003 ACK: 운영자에게 notifications 링크/라우트/API가 없고 전체 역할 공지는 유지한다. CONTRACT-DATA-1.0c flat context/assignees pagination 반영. 실제 AI/브라우저/독립 디자인은 작성자 완료 선언 대상이 아니다.

## MEDIA-CLARIFY-1 수신·변경 계획
2026-09-21 root 전파를 수신하고 docs06의 선택형 reference_photos 계약을 확인했다. 불변 context.references 순서는 유지하며 reference_id로 화면 Photo 메타데이터를 대응한다. source_kind로 생성 배지를 표시하고 보호 URL을 사용한다. 필드가 없는 구 서버에서는 photo_id URL만 사용하고 출처를 추정하지 않는다. 점주 /references API 조회는 추가하지 않는다. snapshot/AI 입력 변경 없음. UI 회귀에서 순서·정확한 URL·배지·추가 조회 없음·필드 누락 호환을 검증한다.

## 자체 구현·회귀 결과 / WEB05-001
- 상태: **REVIEW / 소스 동결**. root의 독립 브라우저·실제 AI·디자인 검수 대기. 런타임 서버/공유 DB/공유 브라우저 변경 없음.
- React19 / Vite7.3.6 / TypeScript5.9 호환, 독립 package @storeloop/concept-05, dev/preview5177. root가 npm lock 의존성을 설치했다.
- 점주: 탐색·파일 1~5장 미리보기/삭제/순서·질문·중복키·지연/poll·기준/reference snapshot·평가·문의·parent 재제출·비교·알림.
- 영업: 현재 범위 매장 행렬/동일 필터 drilldown·담당 후보 등록·계층 기준/버전/비활성·Reference lineage/상태·이슈 배정/상태/조치·주간 추이/산점도/표/Mock 기본 리포트.
- 운영: 구성요소/모델/worker·실제/fixture 작업 구분·계정/역할/지역/매핑·3종 기준 정보·실패 재처리와 과거 attempt·감사·공지와 미리보기. 영업 알림/사진/평가/매출 미노출.
- 디자인: DS05-001 상단 탭 + 범위 패널 + 비교 영역. 모바일 패널 접기, 44px 주요 조작, 표 자체 스크롤, 원본 사진 contain, 의미있는 label와 helper aria-describedby. 일반/배경 읽기 오류는 초점 유지, 명시 변경 오류 요약은 초점 이동.

### RED → GREEN
1. 정책 테스트 5개를 먼저 만들고 정책 모듈 부재 RED 확인 후 구현, 5 PASS.
2. UI 회귀에서 OFC에게 본사 기준 수정 버튼 노출 RED 재현 → 읽기 전용 구분 → PASS. 공통 Reference도 같은 역할 경계를 적용했다.
3. 입력 label에 도움말이 섞이는 회귀 실패 → label/aria-describedby를 분리 → 질문/사진 CSRF 보존·동일키 재시도 PASS.
4. 기준 409 후 입력 보존·version2 재시도, Reference 409 후 최신 lineage id/state_version·사진/캡션 초안 보존 PASS.
5. 현재 세션 401 후 업무 행 폐기·로그인, 운영자 알림 직접 URL API 미조회, 홈 탐색 return URL 유지와 외부 URL 거절 PASS.
6. MEDIA-CLARIFY-1 보호 URL 불일치 RED 확인 → reference_id 대응 Photo 메타데이터 적용 → 순서/배지/추가조회없음/구서버 fallback PASS.

### 최종 실행
- `npm test --workspace @storeloop/concept-05`: **15 PASS** (정책5 + UI10), 합성 API 응답 사용.
- `npm run build --workspace @storeloop/concept-05`: **PASS** (tsc noEmit + Vite). JS 311.16KB / gzip92.91KB, CSS16.43KB.
- `.local/bin/gitleaks dir web-concepts-05 --no-banner --redact --config .gitleaks.toml`: **PASS / no leaks found**, 약462KB 소스·테스트·산출물 검사. 실제 비밀을 소스/브라우저 저장소에 기록하지 않았다.
- 실제 Browser / 실제 모델 / 독립 최종 디자인: **NOT_RUN (root 담당)**. 작성자 단위 테스트를 해당 증거로 대체하지 않는다.
- 상위 docs00/01/02, 공통 API·DB·스키마·루트 lock·다른 시안 코드 수정 없음. PD-003 및 MEDIA-CLARIFY-1 수신·구현 반영 완료.

### 독립 QA 인계 포인트
- `/store-owner`는 첫 화면 이력 탐색이며 모바일에서 `범위 탐색` summary를 열어 필터를 조정한다.
- 제출 당시 기준/Reference는 결과 왼쪽의 접이식 `제출 당시 적용 기준`에서 확인한다.
- 기준/Reference/계정은 목록-상세 탐색, `← 탐색 조건으로`가 필터 URL을 복원한다.
- 운영 `사용 불가`/`미확인`은 모델/서비스 상태이며 비교 화면 `비교 불가`와 구분한다.
- Reference 수정 충돌은 최신 계보 정보를 안내하고 사용자의 선택 사진·설명은 유지한다.
- 한 호스트 쿠키를 공유하므로 실제 브라우저의 역할 로그인은 root가 직렬 실행한다.
