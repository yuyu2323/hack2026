# 시안05 실제 HTTP 권한 독립 보조 검증

- 상태: PASS. 확인23개, Vite5177 경유 실제 GET15개. [원본 증거](independent-live-http.json), [재현 검사](independent-http-probe.py).
- 재현: 프로젝트 루트에서 `server/.venv/bin/python execute/workHitory/integration-concept-05/independent-http-probe.py`. root가 명시 배정한 기존 합성 계정의 새 세션만 사용한다.
- 실제 미디어 ID: `3111f4ec-d4d5-4f14-9bf8-7ecd2552f9f5`. SubmissionPhoto 연결 ID `b4b0b665-3ec5-4f45-80b0-6281e46aaa78`와 구분했다.
- 원본 SHA-256: `86d21c85c15d0328e6942a82c7fe0d797d1dbc4584bb320fab4bd80e7e7f4329`.

| 검사 세션 | 대상·정상 대조 | 기대·실제 |
|---|---|---|
| owner.south | 첫 제출/child 상세, child 이슈 | 모두200 |
| owner.south | 실제 사진 원본·썸네일 | 모두200, image/png·image/jpeg, 원본 응답 hash가 저장 snapshot과 일치 |
| operator.demo | 첫 제출·child·이슈 본문, 같은 원본·썸네일 | 모두403/FORBIDDEN, 영업 본문 없음 |
| regional.north | 북부 e447d4e9… 상세 정상 대조 | 200 |
| regional.north | 남부 첫 제출·child 이슈, 같은 원본·썸네일 | 모두404/NOT_FOUND, 영업 본문 없음 |

owner.south 상세의 context snapshot hash가 독립 DB baseline과 같고 photos가 실제 media_id에 연결된 것을 확인했다. 같은 사용자의 정상 응답으로 대상이 존재함을 확인한 뒤 역할·범위 밖 거부를 판정했다. child 이슈 `c4ecb6f5-d284-42f4-bf90-d641e71097e3`의 submission_id도 child `b0dbd6a2-3b6c-4442-8b57-902448539127`과 일치한다. 존재하지 않는 UUID의404를 권한 증거로 사용하지 않았다.

세 세션 모두 CSRF200→login200→검사→logout204를 완료했다. login 응답 역할도 store_owner/platform_operator/regional과 대조했다. 브라우저 cookie/인증 저장소를 사용하지 않고 `trust_env=False`인 독립 httpx client로 검사했다. 저장 JSON에는 상태·대상 식별자·hash와 판정만 남겼으며, 질문/평가/이슈 본문·사진 바이트·비밀번호·cookie·CSRF를 출력하거나 저장하지 않았다. 검사 코드·JSON Gitleaks PASS다.

현재 서비스·DB 설정·매핑·계정·업무 데이터는 변경하지 않았고 root가 생성 중인 qa05 신규 계정은 조회/변경하지 않았다. HTTP 상태 변경은 새 검사 세션의 CSRF/login/logout에 한정된다. 이번 실제 HTTP 보조 검증은 root의 브라우저 E04 조작이나 기존 세션의 권한 변경 UI 검사와 구분한다.
