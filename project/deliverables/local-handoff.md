# StoreLoop 로컬 시연 인계

2026-09-21 · 사용자 승인 범위 인계 완료

[사용자 매뉴얼 목차](manuals/index.html)에서 5개 시안의 역할별 사용법, 실제 화면 47장, 제출·재제출·관리자 조치·운영 복구 안내를 볼 수 있다. [시안 비교](frontend-comparison.md)로 탐색 방식의 차이와 확인 범위를 비교한다.

## 현재 실행 상태

공통 FastAPI·PostgreSQL·worker·Codex CLI AI 서버와 5개 React 시안이 구현되어 있다. 모든 시안은 점주·영업·플랫폼 운영자 영역을 포함한다. 일반 시연 DB를 사용하는 서버를 켜 두었으며 01~05 주소는 각각 http://127.0.0.1:5173 ~ http://127.0.0.1:5177 이다.

프로젝트 폴더에서 처음 준비할 때 `./scripts/setup.sh`, 실행할 때 다음 명령을 사용한다.

```sh
./scripts/start.sh --concept 1 --concept 2 --concept 3 --concept 4 --concept 5
```

비밀번호는 사용자 전용 `.local/demo-credentials`에서 확인한다. 점주 `owner.north` → OFC `ofc.north` → 본사 `hq.demo` → 운영자 `operator.demo` 순서로 로그아웃·로그인하여 시연한다. 점주는 before 사진 제출·결과 확인·after 사진 재제출을, OFC는 해당 문의·조치를, 운영자는 계정·처리 상태를 확인한다. 기존 Mock 기록으로 먼저 둘러볼 수 있으며 새 제출은 실제 AI를 호출한다. 종료와 DB 종료 순서는 [실행 안내](../docs/10-execution.md)를 따른다.

## 검증 근거와 제한

- 5개 시안의 실제 AI 제출·재제출과 핵심 관리자 흐름, 권한·미디어 경계, 결과·과거 적용 기준 보존을 확인했다. [통합 상태와 근거](../execute/checkList/orchestration/master.md).
- 이전 전체 검증 258개 PASS 후 변경한 01/02/04 복구는 영향 테스트와 독립 검토로 확인했다. 최종 5개 build 및 preview 3역할 경로군×5의 직접 접속·새로고침, 문서 setup·start·stop 재현은 [최종 실행 기록](../execute/workHitory/final-handoff/runtime.md)에 있다.
- 문서 설치 중 확인한 macOS 인증서 문제를 TLS 검증 유지 상태로 수정했다. 기존 DB·비밀번호·설정을 보존했다. 이번 최소 실행 검수에서 추가 모델 호출은 0회다.
- 실제 AI 지연은 30초 목표를 넘었다. 측정값과 세부 증거는 각 시안 매뉴얼에 있으며 목표 달성으로 보고하지 않는다.
- 200% 확대는 사용자 후행 선택이다. 일부 독립 디자인·키보드·목록 세부 확인, OS 네트워크 차단·인쇄 검수 등은 미실행이다. [미확인 범위](../execute/workHitory/frontend-comparison/pending-visual-evidence.md). 따라서 전체 최종 인수를 PASS로 표시하지 않는다.
- 사용자 요청에 따라 반복·추가 경계 검수를 확대하지 않았다. 최종 시안은 사용자가 선택한다. 외부 배포·원격 반영은 하지 않았고 원격 CI 실행도 미확인이다.

실제 AI 인수 기록은 별도 테스트 DB에 보존되어 있으며 현재 일반 시연 DB와 구분된다. 자료는 합성 사진·가상 매출이며, Mock 과거 기록과 실제 AI 결과를 구분해 표시한다.

최소 검수 정리에서는 기존16장의 독립 시각 검토를 마쳤고 새 명백한 제품 결함은 발견하지 않았다. [요구사항26개별 근거](../execute/workHitory/final-handoff/requirements-evidence.md)와 [시안별 필수 잔여](../execute/workHitory/final-handoff/design-evidence-reconciliation.md)를 인계한다. 사용자가 “남은 검수는 후행으로 넘기고 목표 마무리”를 명시적으로 선택했다. 따라서 이번 목표는 종료하며, 위 미검수 항목은 후행 인계 목록에 그대로 보존한다.
