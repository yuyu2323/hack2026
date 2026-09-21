# 시안05 첫 제출·child 독립 메타데이터 재검수

- 상태: PASS, 확인35개. 근거 [independent-pair-metadata.json](independent-pair-metadata.json). 첫 제출 단독15개 기록과 그 이후 생성된 child를 함께 대조했다.
- 재현: `server/.venv/bin/python execute/workHitory/integration-concept-05/independent-probe.py b0dbd6a2-3b6c-4442-8b57-902448539127`.
- 범위: 지정된 두 제출의 READ ONLY DB 메타데이터. 브라우저, HTTP 권한·업무 조작, 신규 AI 호출, 서비스·파일·데이터 변경은 없다.

| 대상 | submission | job | review |
|---|---|---|---|
| 첫 제출 | 3fdb0cf3-61da-4008-84c1-79e2a58cde05 | d9f18dfb-ceae-45f3-8776-991383794be8 | 4625a155-3c9c-4d7a-b2d5-988d26dbb8b0 |
| child | b0dbd6a2-3b6c-4442-8b57-902448539127 | 04c30a57-8766-44d8-b4c9-e24ce7d5f590 | c5d74287-167a-4167-a2fb-771c6432770d |

두 제출 모두1사진/5기준/2Reference, `succeeded / real_ai / is_fixture=false`다. 각 성공 시도는 해당 job의 current_attempt와 review에 연결되고 적용 결과는1개다. 실제 worker의 입력 projection·strict schema·결과 기준/버전/사진/Reference 참조·저장 집계가 일치한다.

child의 parent_submission은 첫 제출이며 snapshot.previous_review의 review ID와 criteria는 첫 결과와 정확히 같다. 최초 독립 baseline과 재조회한 첫 제출의 job/review ID, snapshot SHA-256, result SHA-256이 모두 동일하다. 따라서 child 생성 뒤에도 해당 첫 입력과 결과가 바뀌지 않았음을 독립 전후 관찰로 확인했다.

`qa05_labels`는 같은 CATEGORY guideline `1750bc1d-332f-472e-9f0f-528d5f632844`의 v1→v2다. 두 입력 모두 HQ/REGION/STORE/CATEGORY 후보4개 중 CATEGORY만 선택했다. snapshot의 버전 본문은 immutable DB version과 일치하고 해당 제출 이전에 생성됐다.

Reference lineage `dd5e826b-618a-4f55-8777-34eb3d9e81db`의 첫 입력은 비활성된v1, child 입력은 활성v2 `881d5e08-0690-41c4-8f6d-cf67a5d744fc`다. 각 snapshot의 미디어 ID·hash는 DB와 일치하며 교체 전후 원본 hash가 다르다. 원본 사진 바이트를 이 검수에서 HTTP로 읽거나 저장하지 않았으므로 이미지 실제 로드는 root의 UI 증거와 구분한다.

첫 모델60,273ms/제출→DB61,422ms, child 모델63,876ms/제출→DB66,097ms로 root의 actual-ai.json과 일치한다. 모두30초 목표를 넘었다. 브라우저 표시 시간을 새로 측정하지 않았고, 이 두 실제 신규 표본을 이전 시드·재처리 기간과 섞지 않는다.

검사 코드와 최종 JSON의 Gitleaks 검사 PASS. 자격값·질문·기준 본문·AI 서술 본문·사진 바이트는 증거에 저장하지 않았다. [첫 probe의 도구 구성 오류와 보완](independent-first-review.md#도구-보완증거-구분)은 숨기지 않고 보존한다. 시안05 전체 E01~E08·독립 디자인·매뉴얼 최종 인수는 root와 담당자의 별도 결과를 따른다.
