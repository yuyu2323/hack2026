# 시안05 첫 실제 제출 독립 메타데이터 검수

- 상태: FIRST_SUBMISSION_PASS. root 브라우저 인수와 별도의 READ ONLY DB 보조 검수이며 child·전체 시안 검증 완료를 뜻하지 않는다.
- 후속: root가 child ID를 인계한 뒤 [첫 제출·child 재검수35개 PASS](independent-pair-review.md)를 별도로 기록했다. 이 첫 baseline은 덮어쓰지 않았다.
- 대상: `3fdb0cf3-61da-4008-84c1-79e2a58cde05`. 근거는 [첫 메타데이터](independent-first-metadata.json), 재현 코드는 [independent-probe.py](independent-probe.py)다. 확인15개 PASS.
- 연결: job `d9f18dfb-ceae-45f3-8776-991383794be8`, review `4625a155-3c9c-4d7a-b2d5-988d26dbb8b0`. 첫 성공 시도가 current_attempt/review와 연결되고 적용 결과는1개다. `succeeded / real_ai / is_fixture=false`, parent 없음.
- 입력: 사진1장·기준5개·Reference2개. 실제 worker와 같은 photo 필드 projection으로 strict AnalysisInput을 구성했고, 결과 JSON Schema·모든 기준/버전/rule_key·사진 번호·Reference 참조·집계가 일치한다. 제출 시점보다 나중에 생긴 기준 버전을 입력으로 사용하지 않았다.
- `qa05_labels`는 HQ/REGION/STORE/CATEGORY 후보4개 중 CATEGORY `1750bc1d-332f-472e-9f0f-528d5f632844` v1만 선택했다. root가 현재 기준을v2로 변경한 이후의 독립 관찰에서도 첫 snapshot은v1이다.
- 첫 Reference `dd5e826b-618a-4f55-8777-34eb3d9e81db` v1은 현재 비활성이지만 첫 snapshot의 photo ID와 원본 SHA-256 `63c02dac9d0410a8e2b6a03b6668d5b3070baebd76f452cefecbef47964bb5aa`를 보존한다. child에서 새v2를 사용했는지는 후속 ID 인계 후 검증한다.
- snapshot SHA-256 `328e242f70db0b606c9cb1f05ff507408440c80fea4dd6d5e4ca9c51e53fccab`, result SHA-256 `2ed952ff398fd14a8ac1e6445013028849d81f88e79cd1a1ea94ca280eb2e8e1`를 독립 baseline으로 보존한다. 후속 결과에서는 이 값들이 바뀌지 않았는지도 확인한다.
- 모델60,273ms·제출→DB61,422ms다. 30초 목표 미달이며 브라우저 표시 시간은 이 DB 검사에서 측정하지 않았다. root exporter의 모델·DB 관찰값과 일치한다.

## 도구 보완·증거 구분

첫 probe는 snapshot.photos의 DB 연결용 `media_id`까지 AI strict 입력에 그대로 넣어 extra-field 검증이 실패했다. 실제 worker의 `analysis_input`은 네 필드(photo_id/position/mime_type/sha256)만 보낸다. 이 projection에 맞춰 검사 도구만 수정한 뒤15개 PASS를 확인했다. [초기 도구 실패](independent-probe-adapter-mismatch.json)는 보존하며 제품·모델 실패로 집계하지 않는다.

`scripts/export_acceptance_evidence.py`는 지정한 제출들의 안전한 처리 메타데이터를 `actual-ai.json`에 저장하며 같은 파일을 덮어쓴다. root가 첫 제출·child·재처리 대상 전체를 함께 전달해 기존 항목을 보존해야 한다. 본 검수는 그 도구를 실행하거나 root 파일을 덮어쓰지 않고 별도 READ ONLY 연결·independent-*에만 기록했다. exporter 자체의 존재와 DB 메타데이터만으로 실제 브라우저 동작·그림의 의미·실제 CLI 전송을 새로 관찰했다고 주장하지 않는다.

연결은 로컬 `storeloop_test`로 제한하고 `default_transaction_read_only=on` 및 `SET TRANSACTION READ ONLY`를 적용했다. HTTP 세션·업무 쓰기·서비스 종료/설정·사진 파일 변경·새 AI 호출은 없다. 자격값과 질문/기준/AI 서술 원문은 출력·저장하지 않았고 JSON 증거 Gitleaks 검사 PASS다.
