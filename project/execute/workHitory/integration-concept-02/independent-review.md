# 시안02 기존 실제 AI·원본·HTTP 권한 독립 대조

- 판정: **저장 메타데이터 70개 PASS / 실제 HTTP 46GET·검사 56개 PASS**. 기능 전체 E01~E08 또는 최종 디자인 완료를 뜻하지 않는다.
- 입력: [DB READ ONLY 결과](independent-ai-metadata-20260921T124410Z.json), [HTTP 결과](independent-live-http-20260921T124627Z.json), [DB 검사기](independent-probe.py), [HTTP 검사기](independent-http-probe.py).
- 실제 모델 추가 호출·Browser·서비스·업무 데이터 변경 없음. PostgreSQL REPEATABLE READ 안에서 READ ONLY를 명시하고 SHOW로 확인했다. HTTP는 별도 CSRF/login/logout 세션만 생성·종료했다.

## 실제 입력과 불변 자료

| submission_id | 제출사진 | 적용기준 | Reference |
|---|---:|---:|---:|
| 8259ce47-90ce-4a85-8496-8ed27edeb375 | 1 | 4 | 2 |
| bca082c1-56fe-4bd4-9c0f-9b7ce1ed0ee9 | 1 | 4 | 2 |
| e9fd4f27-0d3e-42a1-9e58-9c255f49d703 | 1 | 5 | 3 |

02 첫 평가와 child는 **4기준·2Reference**, 이후 어둡고 가려진 세 번째 실제 결과는 **5기준·3Reference**다. 세 번째 snapshot에는 qa02_labels CATEGORY v2와 새 Reference v2가 포함되며, 첫/child의4기준·2Reference snapshot은 원본 export hash와 그대로 일치한다. 첫 제출 attempt1 failed/AI_UNAVAILABLE/미반영, attempt2 succeeded/반영이 함께 남고 review/current_attempt는성공시도를 가리킨다.

E01의 “4단계 기준 UI 신규 등록”은 이 메타데이터로 증명되지 않는다. 첫/child의 qa02_* 후보는 없고 세 번째의 qa02_labels는 CATEGORY1개다. 실제 적용기준4개라는 개수와 HQ/REGION/STORE/CATEGORY4단계 등록은 구분해야 한다. 이 제한을 root에 전달하며 기존 실제 AI 성공을 취소하거나 새 호출로 대체하지 않는다.

모든 대상은 real_ai/succeeded이며 실제 성공 review가1개이고 반영 attempt도1개다. 저장 snapshot의 canonical hash, 질문의 DB 값/길이/hash, 적용·후보 GuidelineVersion 본문/ID/버전/생성시각, Reference ID/캡션/미디어 hash를 대조했다. 사진의 SubmissionPhoto ID와 MediaAsset ID를 구분하고 해당 원본 파일의 바이트 수·SHA-256을 검사했다.

실제 worker와 동일한 strict 입력 필드로 재구성해 AnalysisInput 및 결과 schema/기준·사진·Reference 참조 검증을 실행했고 서버 집계값과 일치했다. 자식의 frozen previous_review ID/기준결과는 부모 결과와 일치한다. 원본 export snapshot hash·job/review ID·모델시간·수량도 그대로다. 이번에 result_sha256을 최초 독립 baseline으로 남겼으며, 과거에 없던 응답전체 hash가 이미 기록되어 있었다고 주장하지 않는다. 네트워크 원시 AI 요청이나 프롬프트를 새로 캡처하지 않았다.

## 실제 HTTP 권한 기준

`owner.north`의 실제 제출 상세와 저장 snapshot/media 연결을 확인한 뒤, **모든 대상 원본200 + SHA-256 일치 / 썸네일200**이 먼저 통과해야 거부 검사를 진행했다. 같은 실제 MediaAsset ID에서 `operator.demo`는 상세·원본·썸네일 모두403이며 오류 envelope 외 영업본문은 없다.

`regional.south`는 실제 남부 평가를200으로 읽는 정상 기준을 먼저 확인하고, 북부 대상 제출·제출사진·매장전용 Reference 원본/썸네일은404로 차단된다. **공통 Reference는 현재 허용 범위이므로200/hash 일치가 올바른 기대값**이다. 존재하지 않는 UUID를404로 받은 결과를 권한 PASS로 사용하지 않았다. 세 검사 계정은 모두 logout204로 세션을 종료했다. 비밀번호·CSRF·쿠키·응답본문·사진바이트는 증거에 저장하지 않았다.

## 검사 시도와 범위

일반 sandbox의 로컬 연결 오류는 검사0개로 보존했고, 명시적 권한 검토 후 같은 localhost 읽기 검사가 성공했다. 01 HTTP 최초 시도는 공통 Reference까지404로 기대해 이미지 응답을JSON으로 파싱한 **검사기 오류**다. 해당 부분 실패 산출물을 보존하고 docs06의 공통 Reference 범위에 맞춰200으로 분리했다. 제출/매장전용Ref의404 기준은 그대로 유지했다.01 수정 후 검사와02 검사는 위 최종 결과다.

이번 검토는 DB 저장 증거와 API/보호 이미지 범위의 독립 보완이다. 화면에서 계정 변경·운영 재처리를 조작한 것, 실제 시안 최종 렌더/키보드,02 4단계 UI등록 등 원래 남은 Browser 인수를 대신하지 않는다. 원시 지연값을 정정하거나 새로운 성능표본으로 추가하지 않았다.
