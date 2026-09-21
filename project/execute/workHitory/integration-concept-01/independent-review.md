# 시안01 기존 실제 AI·원본·HTTP 권한 독립 대조

- 판정: **저장 메타데이터 53개 PASS / 실제 HTTP 37GET·검사 46개 PASS**. 기능 전체 E01~E08 또는 최종 디자인 완료를 뜻하지 않는다.
- 입력: [DB READ ONLY 결과](independent-ai-metadata-20260921T124354Z.json), [HTTP 결과](independent-live-http-20260921T124615Z.json), [DB 검사기](independent-probe.py), [HTTP 검사기](independent-http-probe.py).
- 실제 모델 추가 호출·Browser·서비스·업무 데이터 변경 없음. PostgreSQL REPEATABLE READ 안에서 READ ONLY를 명시하고 SHOW로 확인했다. HTTP는 별도 CSRF/login/logout 세션만 생성·종료했다.

## 실제 입력과 불변 자료

| submission_id | 제출사진 | 적용기준 | Reference |
|---|---:|---:|---:|
| 17f959e5-831a-4ff7-842d-22575e6cfad5 | 1 | 5 | 2 |
| 2b0e717c-c161-4caa-8d1e-f1b7c9c88106 | 1 | 5 | 2 |

01 첫 평가와 child는 모두 **Reference 2개**다. 첫 평가는 매장 전용 v1 한 개와 공통 v1 한 개이며, child는 같은 매장 lineage의 v2와 같은 공통 v1이다. “등록한 v1 + 기존 공통2장”은 실제 입력3개로 읽히는 기록상 오류이며 원본 export의2가 맞다. root에 정정 요청했고 본 검토자는 원본 browser.md/actual-ai.json을 수정하지 않았다.

첫 평가의 두 Reference는 ID/MediaAsset은 다르지만 같은 정규화 이미지 SHA-256이다. 입력 슬롯은2개이며 서로 다른 시각 예시2개라고 해석하지 않는다. child의 매장 전용v2는 다른 hash이고 공통v1은 그대로다. 두 snapshot 모두 qa01_front 후보 HQ/REGION/STORE/CATEGORY4개와 CATEGORY만선택 상태를 보존하고, 적용 CATEGORY 내용버전v1→v2를 확인했다.

모든 대상은 real_ai/succeeded이며 실제 성공 review가1개이고 반영 attempt도1개다. 저장 snapshot의 canonical hash, 질문의 DB 값/길이/hash, 적용·후보 GuidelineVersion 본문/ID/버전/생성시각, Reference ID/캡션/미디어 hash를 대조했다. 사진의 SubmissionPhoto ID와 MediaAsset ID를 구분하고 해당 원본 파일의 바이트 수·SHA-256을 검사했다.

실제 worker와 동일한 strict 입력 필드로 재구성해 AnalysisInput 및 결과 schema/기준·사진·Reference 참조 검증을 실행했고 서버 집계값과 일치했다. 자식의 frozen previous_review ID/기준결과는 부모 결과와 일치한다. 원본 export snapshot hash·job/review ID·모델시간·수량도 그대로다. 이번에 result_sha256을 최초 독립 baseline으로 남겼으며, 과거에 없던 응답전체 hash가 이미 기록되어 있었다고 주장하지 않는다. 네트워크 원시 AI 요청이나 프롬프트를 새로 캡처하지 않았다.

## 실제 HTTP 권한 기준

`owner.north`의 실제 제출 상세와 저장 snapshot/media 연결을 확인한 뒤, **모든 대상 원본200 + SHA-256 일치 / 썸네일200**이 먼저 통과해야 거부 검사를 진행했다. 같은 실제 MediaAsset ID에서 `operator.demo`는 상세·원본·썸네일 모두403이며 오류 envelope 외 영업본문은 없다.

`regional.south`는 실제 남부 평가를200으로 읽는 정상 기준을 먼저 확인하고, 북부 대상 제출·제출사진·매장전용 Reference 원본/썸네일은404로 차단된다. **공통 Reference는 현재 허용 범위이므로200/hash 일치가 올바른 기대값**이다. 존재하지 않는 UUID를404로 받은 결과를 권한 PASS로 사용하지 않았다. 세 검사 계정은 모두 logout204로 세션을 종료했다. 비밀번호·CSRF·쿠키·응답본문·사진바이트는 증거에 저장하지 않았다.

## 검사 시도와 범위

일반 sandbox의 로컬 연결 오류는 검사0개로 보존했고, 명시적 권한 검토 후 같은 localhost 읽기 검사가 성공했다. 01 HTTP 최초 시도는 공통 Reference까지404로 기대해 이미지 응답을JSON으로 파싱한 **검사기 오류**다. 해당 부분 실패 산출물을 보존하고 docs06의 공통 Reference 범위에 맞춰200으로 분리했다. 제출/매장전용Ref의404 기준은 그대로 유지했다.01 수정 후 검사와02 검사는 위 최종 결과다.

이번 검토는 DB 저장 증거와 API/보호 이미지 범위의 독립 보완이다. 화면에서 계정 변경·운영 재처리를 조작한 것, 실제 시안 최종 렌더/키보드,02 4단계 UI등록 등 원래 남은 Browser 인수를 대신하지 않는다. 원시 지연값을 정정하거나 새로운 성능표본으로 추가하지 않았다.

## 후속 export의 fixture 추가

root가 actual-ai.json에 과거fixture재처리 e3488415-6745-56a8-be69-7d3010521033을3번째행으로추가했다. 기존first/child의job/review/snapshot hash·모델시간·수량·attempt상태/반영여부를기존독립근거와다시대조해모두같음을확인했다. 추가행은다른검토자의independent-operations-review.md22개PASS이며,앞선53개DB/46개HTTP검사대상에소급포함하지않는다.

검사기가향후export추가행을자동포함하지않도록01최초2개/02기존3개UUID로대상을고정했다.선택목록/필드투영만바뀌었고실제DB/HTTP는재실행하지않았다.새exporthash와비교필드는independent-index.json이다.
