# 보안 초기 조사
- 담당 root, 구현 전 조사. 체크리스트 local-controls.md.
- 내부 Git origin: github.com/yuyu2323/hack2026, 기본 브랜치 main, private.
- 2026-09-21 GitHub API 읽기 결과: security_and_analysis=null (적용 상태 정보 없음. 활성/비활성으로 단정하지 않음). 현재 인증 계정은 admin 권한을 보고하나, 사용자의 로컬 구현 요청은 원격 설정 변경 지시가 아니므로 설정은 변경하지 않는다.
- 원격 push/PR/merge/배포 실행 없음. 기존 3개 기준 문서만 추적됨. 사용자 미추적 자료 보존.
- Gitleaks v8.30.1 고정 예정. 공식 release 및 README 확인: https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1 , https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md
- git/dir/stdin 모드 사용. 출력 redaction, staged 검사·신규 브랜치 전체 이력 검사, 도구 부재시 차단을 구현한 뒤 합성 fixture로 검증할 계획. 현재 설치/차단 검증은 NOT_RUN.
- 브랜치 보호 조회: HTTP 403, GitHub가 비공개 저장소에서 Pro 또는 공개 전환 필요라고 응답. 현재 플랜에서 미지원으로 기록. 구매/공개 전환은 요청하지 않았고 수행하지 않음. 로컬 차단 및 CI 구성은 계속 진행한다.

- 개발 중 PostgreSQL sandbox 연결 실패의 pytest traceback에 프로젝트 전용 생성 DB 자격값이 포함된 사실을 담당자가 보고. 원문은 기록하지 않음. root가 실제 로컬 DB role 비밀번호와 보호환경 파일을 회전, 담당자는 --tb=short 및 안전한 연결오류 메시지로 전환한다. 기존 값은 폐기하며 raw traceback을 산출물로 보존하지 않는다.

## SEC-002 실제 훅과 전체 소스 검사
- `python3 -m unittest discover -s tests/security`: 7 PASS. 실제 임시Git pre-commit과 로컬bare 목적지 pre-push가 합성 탐지 표본을 차단하며 원격전송은 없었다.
- `security_guard.py files`: PASS. test_analysis_jobs.py의 한 줄에 연속된 storage_key/thumbnail_key 키워드가 generic-api-key 오탐을 일으켜 키워드별 줄바꿈만 적용. 검사규칙·allowlist는 변경하지 않았다. 포맷 뒤 전체서버64 PASS, 실제AI는제외.
- CI `.github/workflows/security.yml` 추가: 읽기권한/고정checkout SHA/고정scanner공식SHA/전체이력검사/보안회귀. 아직 원격미실행.
- 최종 프론트번들·캡처·매뉴얼과 독립보안검토는 남음.
