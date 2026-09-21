# 최종 보안 독립 검토

- 담당: product_design. root의 명시 배정으로 core/accounts/stores/operations와 AI/worker·실행/CI를 독립 검토한다.
- 상태: REVIEW_COMPLETE / PASS · 지정 범위 내 열린 확인 결함 없음
- 기존 참고: backend-independent/g4-review.md, backend-review/independent.md, repository-security/initial-audit.md. 기존 PASS를 이번 독립 실행으로 재표기하지 않는다.
- 확인 한계: 실제 전체 setup/start/stop은 root 후속. 원격 CI NOT_RUN, branch protection HTTP403 플랜 제약은 확정된 외부 상태. 본 검토는 원격 설정을 변경하지 않는다.
- 코드 또는 로컬환경 비밀 값을 출력하지 않고, 공유 서비스·DB·브라우저를 변경하지 않는다. 테스트는 새 결함 재현이 필요할 경우 격리한 메모리/임시 경계만 사용한다.

## SR-01 · 내부 상태조회 환경 프록시 경유 · P1 · RED

- 위치: `server/operations/service.py::service_dashboard`, `httpx.get(ai_service_url+'/health', ..., headers={'Authorization': ...})`.
- 조건: 운영자 서비스 상태 조회, HTTP_PROXY가 설정되고 NO_PROXY에서 loopback을 제외하지 않은 환경.
- HTTPX 기본 `trust_env=True` 때문에 localhost AI 상태조회도 HTTPProxy transport를 선택하며, 내부 분석 토큰 헤더가 환경 프록시 경로로 나갈 수 있다. worker의 실제 분석 HTTP 경로는 이미 trust_env=False이며 이 상태조회만 누락되었다.
- 새 독립 재현: `server/tests/test_security_final_review.py`. 임시 SQLite DB, 합성 내부 토큰, mock HTTPTransport만 사용. 소켓/외부 네트워크/실제 비밀/공유 DB는 사용하지 않았다.
- 명령: `server/.venv/bin/python -m pytest server/tests/test_security_final_review.py -q --tb=short`.
- 결과: 1 FAIL (0.16초). ConnectionPool 기대에 HTTPProxy 실제 선택. 기존 라이브러리 deprecation warning 2개.
- root/contract_data에게 보고. root가 구현 수정 소유를 수락했다. 내부 건강조회 trust_env=False 및 불필요한 health 인증 헤더 제거를 요청했다. 실제 비밀이 유출되었다는 증거는 없으며 합성 환경에서 경유 가능성을 확인한 것이다.

## SR-02 · merge 전용 변경의 이력 검사 누락 · P1 · RED

- 위치: `scripts/security_guard.py::pushing`, 각 commit `diff-tree` 및 scanner `--log-opts=<revision>`.
- 처음에는 정적 후보로 root에 보고했다. root가 이 검증에 한해 임시 `/tmp` 저장소의 합성 commit/merge를 명시 허용하고 `tests/security/test_merge_history.py` 신규 파일 소유를 배정했다. 실제 프로젝트 Git 변경 권한을 확대하지 않았다.
- 두 분기를 합친 merge에서만 표본을 추가하고, 다음 merge에서만 제거했다. 현재 HEAD에는 표본이 없다. 일반 단일 부모 commit은 표본 추가/제거를 포함하지 않는다.
- 금지 `.env` 파일(일반 합성 설정)과 외부에서 유효하지 않은 합성 토큰 표본 두 사례에서 모두 push 검사 returncode=0으로 허용했다.
- 명령: `python3 -m unittest discover -s tests/security -p test_merge_history.py`.
- 결과: 2 FAIL, 1.942초. 실제 사용자 저장소/원격/인증 값을 사용하지 않았다. 임시 저장소는 테스트 종료 시 삭제했다.
- 기존 보안 7개 회귀는 단일 부모 이력을 검증하며 이 경계를 다루지 않았다. root에 테스트 freeze를 전달했고 guard 구현은 root가 수정한다. 경로 및 내용 검사 모두 merge 각 부모 diff를 포함해야 한다.

## 독립 소스 검토 범위

| 경계 | 확인한 구현 | 판정과 제한 |
|---|---|---|
| 로그인/세션 | Argon2id, 불투명 무작위 토큰, DB SHA-256, 로그인시 세션 교체, HttpOnly/SameSite=Lax, 로컬 쿠키설정, 익명30분/인증12시간 | 소스 정합. 공개 운영배포는 범위 밖이며 Secure=false는 loopback 구성만 전제로 함 |
| CSRF | 변경요청에서 정확한 Origin 또는 Referer origin, cross-site 거절, 세션 결합 토큰 상수시간 비교, 만료/폐기 확인 | 모든 accounts/stores/operations 변경 경로 dependency 대조. 무토큰 요청 성공 경로 없음 |
| 현재 권한/범위 | get_current_account DB 재조회·비활성401, 현재 매핑/지역 재조회, 운영자 영업403, 범위 밖404, OFC 후보 최소 DTO·지역·활성 제한 | 기존 세션이 정적 역할/매핑을 보유하지 않음. 비활성 지역은 과거 조회 허용/새 업무 제한 |
| 운영 변경 | 일반역할 enum, 운영자 승격/운영자 계정 수정 금지, 활성 FK·version·행 잠금, 매핑 종료 이력, 전체교체·OFC 단일담당 | 기존 DB/업무 검토 증거와 소스 교차확인. 새 DB 경합 테스트는 중복 실행하지 않음 |
| 오류/감사/운영 DTO | password/hash/session 원문 미직렬화, validation 입력 제외, SQL hide_parameters, 변경 감사 whitelist, job/attempt에서 질문·사진·제출본문 제외 | 감사 호출의 업무본문 배제도 읽어 확인. SR-01 외 직접적인 비밀 출력 경로를 발견하지 않음 |
| AI 내부 HTTP | loopback 실행, 내부 analyze 토큰 필수/빈설정503, 전체본문 제한, multipart 개수/MIME/hash/치수 확인, 단일슬롯, health 모델호출 없음 | health 공개 정보는 프로세스/준비 메타데이터이며 docs07과 일치 |
| AI CLI | 직접 argv 실행, ignore-user-config·ephemeral·read-only·도구/웹 비활성, 신뢰하지 않는 데이터 표시, 0700 임시디렉터리/0600 입력·결과, 환경 allowlist, 원문 stdout/stderr 미기록 | 프롬프트만으로 보안 경계를 대체하지 않고 도구 이벤트 차단·프로세스그룹 종료를 병행. 실제 모델 인수는 root 증거 |
| worker | 실제 보호 파일/hash·불변 snapshot, HTTP trust_env=False/redirect=False, 응답상한·오류 whitelist, DB 외부에서 HTTP, attempt/worker/deadline/lease 재확인 후 원자 저장 | unknown은 정상 결과, 기술실패는 failed. 늦은결과 본문 저장·기존성공 덮어쓰기 없음 |
| 실행 도우미 | loopback host/strictPort, 관리 PID marker+프로젝트경로, 전체 포트 사전충돌, 기존 설정 보존·파일권한, 버전 출력만 preflight | 전체 setup/start/stop은 공유 런타임 보호 때문에 NOT_RUN. root의 후속 실제실행 필요 |
| CI/보안 훅 | read-only workflow 권한, checkout/setup SHA 고정, scanner 버전/다운로드 SHA 검증, 무원문 출력 fail-closed, 새 branch 전체 이력, private 파일 제외 | SR-02 merge 경계 수정 전 최종 보안 PASS 불가. 원격 CI 실행 NOT_RUN, 보호설정403 제약 유지 |

현재 소스는 수정하지 않았다. 신규 회귀 2개 파일과 본 검토기록만 추가했다. 미해소 결함을 해소한 뒤 해당 검사만 다시 실행하고 결과를 갱신한다.

## 수정 후 독립 GREEN · 검토 종료

- root가 SR-01에 `trust_env=False`를 추가했다. 같은 운영 상태조회 경로가 환경 프록시를 우회하는지 새 독립 재현을 그대로 실행했다.
- `server/.venv/bin/python -m pytest server/tests/test_security_final_review.py -q --tb=short` → **1 passed, 0.10초**, 기존 라이브러리 deprecation warning 2개. 모의 HTTPX transport는 ConnectionPool, 실제 네트워크 사용 없음.
- root가 SR-02 경로 검사에 `diff-tree -m`, 내용 검사에 `--log-opts=-m <revision>`을 추가했다. 두 부모 기준 변경을 포함하도록 실제 소스도 확인했다.
- `python3 -m unittest discover -s tests/security -p test_merge_history.py` → **2 passed, 1.765초**. merge에서만 도입/제거한 금지파일·합성 비밀 모두 차단. 임시 저장소만 사용, 실제 프로젝트 Git/원격 불변.
- root의 확장 회귀 operations 11 PASS/PG1 PASS, security9 PASS 및 테스트 API 반영은 담당자의 별도 실행 증거다. 본 검토자는 위3개 결함 재현을 독립 재실행했고 전체 검사를 중복 실행하지 않았다.
- 실제 `.local`/logs/pids 0700, runtime.env/postgres-password/demo-credentials 0600을 읽기 전용 stat으로 확인했다. 파일 본문은 읽거나 출력하지 않았다. 증거: `local-permissions.json`.
- 현재 지정 범위에서 미해소 확인 결함은 없으며 **독립 보안 검토 PASS**로 종료한다. SR-01의 환경 프록시 조건이나 SR-02의 merge 표본에서 실제 사용자 비밀이 노출되었다고 주장하지 않는다.
- 최종 검토 소스 식별: `reviewed-source-sha256.json`. 버전 식별용이며 비밀 파일의 hash는 포함하지 않는다.

### 남은 프로젝트 인수와 명확한 제한

- 실제 신규환경 전체 setup/start/stop 재현은 root가 후속 진행한다. 본 검토의 소스/격리 PASS는 이를 대신하지 않는다.
- 원격 CI 실제 실행은 NOT_RUN. 비공개 저장소 branch protection은 기존 조사 HTTP403·플랜 제약이며 원격 설정을 변경하지 않았다.
- 실제 모델 분석과 5개 UI 전체 동선/디자인/완성 캡처/매뉴얼 인수는 각 담당자의 증거를 따른다. 보안 PASS가 해당 기능검증을 대신하지 않는다.
- 로컬 loopback 실행을 전제로 검토했다. 외부 운영 배포는 요청 범위에 없고 인증/배포 구성을 이 검토로 승인하지 않는다.
