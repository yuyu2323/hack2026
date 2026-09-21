# 합성 장기 대기 fixture 복원 후 독립 검증

- [x] root 적용 근거의 생성 시 snapshot hash를 확보한다.
- [x] 새 job QUEUE_TIMEOUT, 최초 expired 시도 1개·시작 없음·결과 미반영을 확인한다.
- [x] ReviewResult 0개 및 snapshot hash 보존을 확인한다.
- [x] 사전 근거가 있는 기존 기록의 상태·개수·hash 보존을 확인한다(기존 AI15건, 결과hash12건·snapshot만3건).
- [x] READ ONLY 범위와 비교 가능한 기존 기록의 범위를 구체적으로 기록한다.
- 소유: queued-browser/independent-*만. DB/서비스/Browser 변경·새 AI 호출 금지.
