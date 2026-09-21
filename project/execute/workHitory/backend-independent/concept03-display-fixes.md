# 시안03 표시 결함 후속 수정
- root 명시 배정: shared/ui.tsx FileImage/ContactSheet, store-owner/pages.tsx FilePreview 표시 및 신규 tests만.
- 이전 seed 읽기 검토보다 우선한다. 편집 시작을 root에게 전달했다.
- 새 역할은 제한 UI 구현이며 독립 PASS 판정이 아니다. root 실제 브라우저 인수와 구분한다.
- 계획: 빈 src 초기 렌더/실패 상태 오표시를 의미 테스트 RED로 확인 → 해당표시만 수정 → 신규 및 기존17개 테스트·build → freeze 인계.
- 브라우저·DB·런타임·다른 시안·Git은 변경하지 않는다.

## TDD 실행 증거
- 신규 파일: `web-concepts-03/tests/display-state.test.ts`. FileImage 초기 마크업, FilePreview 파일 선택/삭제 및 URL 해제, 실패 ContactSheet, 대기/성공 ContactSheet를 검사한다.
- 테스트 준비 중 프로젝트 루트에서 직접 node를 실행하면 시안 tsconfig가 선택되지 않아 React 식별자 오류가 발생했다. 시안 workspace 실행으로 고쳤다. 파일 입력 label도 설명을 포함하므로 정규식으로 찾도록 고쳤다. 이 준비 오류는 기능 RED 증거에 포함하지 않는다.
- 의미 RED: 올바른 workspace에서 기존17개+신규4개 실행 결과 18 PASS / 3 FAIL. 빈 src 경고 두 경로와 실패 상태의 대기 문구가 각각 실패했다.
- GREEN 변경: FileImage와 FilePreview는 URL이 준비된 경우에만 img를 렌더한다. ContactSheet는 review_summary가 없고 job.status=failed이면 ‘기술 문제로 분석하지 못했어요. 운영자에게 재처리를 요청해 주세요.’를 표시한다. 기존 성공 결과와 queued/running 대기 표시는 그대로다.
- REFACTOR 검토: 공통 인터페이스·CSS·URL 생성/해제 수명주기는 변경할 필요가 없어 지정 표시 조건만 유지했다.
- 검증 명령: `npm test --workspace @storeloop/concept-03 && npm run build --workspace @storeloop/concept-03`.
- 최종 결과: **21 passed / 0 failed**, 1038ms. `tsc --noEmit` PASS, Vite7.3.6 build PASS(34 modules, 475ms). 빈 src 경고 없음.
- root에게 지정 소스 freeze와 결과를 전달했다. 브라우저·DB·실행 중 서버를 조작하지 않았다. 이 결과는 제한 UI 구현의 자기검증이며 root의 실제 브라우저 독립 인수를 대체하지 않는다.
