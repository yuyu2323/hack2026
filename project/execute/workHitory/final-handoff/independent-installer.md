# Gitleaks 설치 TLS 수정 독립 보안 검토

- 검수자 contract_ai / 시각 2026-09-21T13:36:15.962228+00:00
- 판정: **PASS — 요청한 최소 수정 범위에서 발견된 보안 결함 없음**.
- 대상: 설치기와 실제 루트 setup.sh, 신규 두 회귀. scripts/setup.sh는 루트 setup.sh로 위임하는 진입점임을 읽기 확인했다. 제품 파일은 수정하지 않았다.

## 확인 내용

1. `ssl.create_default_context()`를 사용하고 certifi CA를 `load_verify_locations`로 추가한다. 인증서 검증과 호스트명 검증을 끄는 옵션이나 비검증 context가 없다.
2. setup은 서버 lock 의존성 설치가 끝난 뒤 `server/.venv/bin/python scripts/install_security.py`를 실행한다. 시스템 Python 대신 이미 준비된 환경에서 certifi를 읽는 순서다.
3. 고정 HTTPS 배포 경로에서 받은 전체 archive의 SHA-256이 코드에 고정한 값과 일치해야 파일을 추출하고 설치한다. 불일치는 설치 경로 쓰기 이전에 종료한다. archive 전체를 임의 경로로 풀지 않고 지정된 gitleaks 내용만 읽는다.
4. 기존 binary 보존은 checksum 불일치 경로에 대해 검증했다. 실제 네트워크·실제 배포물의 독립 checksum 출처 확인이나 모든 설치 실패의 원자성을 이번 검토로 주장하지 않는다.

## 실행 근거

`server/.venv/bin/python -m unittest discover -s tests/security -p test_install_security.py -v` — **2/2 PASS, exit0**.

- TLS context: CERT_REQUIRED, check_hostname=true, CA 포함을 확인하고 올바른 fixture archive만 설치.
- 잘못된 checksum: SystemExit이며 기존 binary bytes 유지.

테스트 다운로드는 합성 stub이고 설치 위치는 임시 폴더다. 테스트 출력의 설치 완료는 실제 GitHub 다운로드 성공을 뜻하지 않는다. setup 실제 재실행은 root의 별도 증거이며 본인은 수행하지 않았다. 새 경계·테스트·AI·Browser·서비스 조작을 추가하지 않았다.

## 검토한 파일 SHA-256

| 파일 | SHA-256 |
|---|---|
| `scripts/install_security.py` | `94bceb74581483545eaea33d7c218d831b1c4accca1c41dd81c0a644e42a9761` |
| `setup.sh` | `e5a851df21ffd20f24fb5c8ec4adcc0ce1bc680d00b968818cc7c14def65b3a0` |
| `tests/security/test_install_security.py` | `408a1154213b7b35f66ff6ba41208ac7e38bbe8f80821a9c6151c9d45171eb80` |
