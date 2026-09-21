# 로컬 비밀 차단 장치 및 원격 적용 상태
- 담당: root (추후 독립 검토자 배정)
- 상태: RUNNING — 로컬 보안 검사 완료·최종 산출물 독립 검토 대기
- 입력: 02 §12, docs/10 v1 초안
- 수정 범위: hack2026/.gitignore, project/.githooks, project/scripts/security*, hack2026/.github/workflows, project/.gitleaks.toml

- [x] Gitleaks 고정 버전 설치·해시/버전 확인
- [x] 환경/토큰/인증 상태/DB/미디어/로그 추적 제외
- [x] staged 스캔 + 금지 경로 검증 pre-commit
- [x] pre-push 전체 전송 이력/신규 브랜치 검사
- [x] 도구 오류 시 차단, 마스킹 출력
- [x] 합성 fixture 임시 Git 저장소에서 commit/push 차단 검증
- [x] 실제 checkout 훅 설치 확인
- [ ] 최소 권한 CI 보안·테스트·빌드 설정
- [x] 원격 보호 상태 읽기 확인, 미적용 이유 기록
- [ ] 실제 source/bundle/캡처 비밀 노출 독립 검토

원격 push/설정 변경을 임의로 수행하지 않는다. 작업 범위 밖 사용자 자료는 자동 추적하지 않는다.
