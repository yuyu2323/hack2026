# DEP-002 테스트 의존성 보안 갱신
- npm audit: Vitest3.2와 @vitest/mocker2.1~4.1.10의 GHSA-82fw-gwwq-j7x9 moderate 발견.
- 기능 축소 없이01/02/04의 테스트 의존성만4.1.11 고정. 세 package.json 해당키는root 통합소유로잠시회수,04작성자통지.
- npm install/audit/관련테스트·빌드 재검증 예정.

- 설치 완료: npm audit 0취약점. 01 policy6/UI6,02 UI8 Vitest4.1.11 PASS. 04 작성자 최종시험 후 결과통합예정.

- 04 Vitest4.1.11 9PASS/buildPASS 작성자확인. CI 테스트·빌드 workflow 추가: 공식actions API로 setup-node v4 commit49933ea..., setup-python v5 commita26af69... 확인 후 고정. 읽기전용권한,Python3.13.3/Node22.12.0,고정lock·실제AI제외·5앱test/build. 원격push/실행은범위밖이라NOT_RUN.
