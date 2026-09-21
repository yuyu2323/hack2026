# 장기 대기 Browser 검수 준비

- 담당: contract_data. root 배정에 따라 읽기 조사와 실행 전 검토 가능한 합성 fixture 도구만 준비한다.
- [x] 기존 queued 시드의 UUID·현재 상태를 읽기 전용으로 확인한다.
- [x] worker 만료/점유 순서와 Mock 표시·사진 권한을 확인한다(소스/READ ONLY, 실제 UI는 후속).
- [x] 기존 기록 수정·삭제 없이 새 합성 대기 fixture를 추가하는 도구를 작성한다.
- [x] 기본 dry-run, 전용 test DB 제한, worker 정지 확인, 만료된 queue deadline, 추가 전용·멱등 안전 조건을 단위/읽기로 검증한다.
- [x] 계정·5개 URL·실행/후속 정리 방법을 root에게 전달한다.
- [ ] 실제 적용·트랜잭션 commit·재실행 0행·worker 만료·Browser 검수는 root 후속 실행.
- 현재 DB 변경·서비스 중지·새 실제 AI 호출·Browser 조작은 금지한다.
