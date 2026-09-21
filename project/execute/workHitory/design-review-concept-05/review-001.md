# DR05-001 작업 이력
- 상태 RUNNING / contract_ai
- 시안탐색과 비교의 설계·구현 및 root 기능 인수와 독립하여 검수한다.
- 명세와 현재 소스 읽기 사전검토 완료. 실제 PNG가 없는 항목은 NOT_RUN으로 유지하며 소스 존재만으로 디자인 PASS를 주지 않는다.
- 최종 수정은 root가 지정한 통합 작성자가 담당한다. UI 변경 후 소스 hash와 최종 캡처를 다시 연결한다.
- HTML 매뉴얼은 UI 확정/최종 증거 수신 후 이 시안 전용 화면으로 작성한다. 다른 시안 캡처를 대체 사용하지 않는다.
- 통합 작성자 수정 소스 재확인: 모바일 .identity button min-height44px. D05-P01 소스 보완 확인, 실제 캡처 재검수 대기. build PASS 보고 수신.

- 첫 실제9장 직접 검수:1440 범위탐색/행렬·기준/Reference,390 이력·형식오류·미리보기·2000자·처리/지연. D05-01 PASS, 나머지 부분 증거는 BLOCKED/NOT_RUN 유지. review-evidence-005.json 해시와 원본치수 보존.

- 실제 viewport51장 직접 열람(흰 first-result1장 제외/정상fixed 대체 포함). review-evidence-005~019.json에 원본hash·저장치수·관찰범위를 보존했다. D05-01/03/04/07 PASS, 나머지는 최종 증거에 따라 BLOCKED/NOT_RUN이다. 주요360/390/1280×800/1440 화면과 실제60→100·OFC조치/점주알림·운영/권한/재처리·Mock unknown/기술실패 구분 확인. 파일명과 실제 상태/보이는 구간을 구분했다.
- 매뉴얼05 최신12장은 별도 독립 내용/정적검수 PASS이며 작성자는 product_design이다. Browser문서렌더/200%/통신·충돌/최종preview는 미완료다.

- DR-QUEUED-001: 신규 viewport 4장 직접 검수·해시/decoded 치수 기록. 대기→통신 오류→복구→시간초과 구분 PASS, 전체 시안 완료 아님. [결합 보고서](../design-review-queued/review-001.md).
