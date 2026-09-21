# CMD-01 실행·검증 문서 반영

- 상태: 문서 반영·자기 검증·독립 문서 재검토 PASS, 동결. 문서 반영 담당 contract_data, 독립 검토자 contract_ai.
- 변경 이유: [독립 대조 CMD-01~09](command-document-review.md)에서 G1 예정 명령과 실제 runner·fixture·프로세스 운영의 불일치를 확인했다. root가 구체 수정안을 수락했다.
- 영향: README와 docs09/10의 실행 안내만 변경한다. API/DB/업무 동작, 상위00/01/02와 E01~E08의 요구는 변경하지 않는다. 별도 저장소 Playwright CLI 미제공과 실제 in-app Browser 검증의 차이를 명시한다.
- 검증 계획: 원본00/01/02 및 docs09 필수 인수 시나리오 구간 해시 보존, 상대 링크·명령 구문·실제 pytest 수집 및 preview 설정 근거 대조. 현재 서비스 종료·DB 변경·실제 모델 재호출은 하지 않는다. 종료 확인 예시는 실제 프로세스 대신 격리 double로 성공/대기/시간 초과 경계를 검사한다.
- 수신: root 반영 배정 수신. 독립 검토 요청과 재검증 결과는 아래에 추가한다.

## 반영 내용

- README: Node22.12/npm10, setup 전체 범위, 04 ‘현장 포켓’·05 ‘탐색·비교 작업대’, 매뉴얼5개 직접 링크와 최종 검수 대기, preview 동일 포트/dev 종료, foreground 테스트 분리와 안전한 종료 절차 링크.
- docs09: 현재 pytest/프론트/verify 명령, 정확한 테스트 DB 변수·스키마 수명, 실제 HTTP smoke와 worker→AI→DB 검사 분리, 실제 Browser E01~E08 절차와 저장소 Playwright CLI 미제공 상태, 현재 결과 정본 링크.
- docs10: 현재 setup/start/verify 범위, 최소 버전, PID 기록을 보존한 종료 확인→DB 중지 예시, foreground API/AI/worker/Vite 각각의 실행 터미널과 종료 순서. RUNTIME-01의 공개 명령 불변 설명.
- 원본00/01/02 및 docs09 §2~6(AT 추적·단위·PG·실제AI·E01~E08/뷰포트·접근성)은 편집 전후 SHA-256 동일하다. 요구 축소 없음.

## 실제 검증

- [command-document-checks.json](command-document-checks.json): 상대 링크·anchor39개, shell 코드블록 구문9개, 원본/필수 구간 해시4개 확인. 종료 예시 Python AST와 격리 double3건(이미 종료, 대기 후 종료, 시간 초과) PASS. 시간 초과에는 DB stop을 요청하지 않았다.
- `server/.venv/bin/python -m pytest server/tests/test_analysis_jobs.py --collect-only -q --tb=short -m real_ai`: 실제 worker 테스트1/20 수집,19제외, exit0. 실행·DB fixture·모델 호출은 하지 않았다.
- `ai-service/.venv/bin/python -m pytest ai-service/tests --collect-only -q --tb=short -m real_ai`:0수집/39제외, exit5. 기존 잘못된 명령에는 실제AI 테스트가 없음을 재확인했다. 프레임워크 deprecation warning이 있으며 기능 실패와 구분한다.
- Node `resolveConfig` 독립 재확인:5개 preview 각각5173~5177,host127.0.0.1,strictPort=true,proxy/api→8000 모두 PASS. 실제 preview 기동/브라우저 로그인은 이 작업에서 NOT_RUN이다.
- 현재 서비스·공유DB·브라우저·실제 모델·외부 설치/전송은 조작하지 않았다. doc 예시의 실제 SIGTERM/DB stop도 실행하지 않았다.

## 전파

- root: 수정 범위와 안전한 종료 확인 설계 착수 메시지 전달.
- contract_ai: 세 문서·등록부 CMD-01을 동결하고 실제 scripts 및 상위 필수 범위와 독립 대조 요청. 수신 후 실제 setup/verify/preflight/services/worker/fixture/smoke·package를 직접 대조하고 문서 해시를 독립 재계산하여 PASS 회신했다. 미해소 결함 없음.
- 독립 근거: [문서 검토](../local-ai/command-doc-independent.md), [해시·판정](../local-ai/command-doc-independent.json). 종료 절차와 foreground 예외, E01~E08/실제 UI·AI/독립 디자인·매뉴얼 요구 보존을 확인했다. 서비스/DB/AI/브라우저 실행 없는 문서 정합성 PASS로 한정한다.
- 등록부 CMD-01의 상대 근거 링크5개도 재검사 PASS. 세 제품 문서는 독립 검토 이후 추가 편집하지 않는다. root에 완료·미실행 범위를 전달한다.
