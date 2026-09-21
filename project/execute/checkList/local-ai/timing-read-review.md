# AI-TIME-READ-001 시간 계측 기준 읽기 검토

- 담당 contract_ai / 상태 REVIEW_COMPLETE.
- 요청: contract_data의 시안05 retry 모델50,635ms와 작업자 UTC차48,786ms 관측 대조.
- [x] adapter duration 산출 구간과 clock 확인
- [x] worker started/finished 시각 및 생산 now 주입 여부 확인
- [x] 결과 캐시·ID 연결 검증 확인
- [x] 관측 사실과 원인 추정 분리, root/검증자 전달
- 새 모델 호출·DB 변경·서비스 재시작·사용자 시계 변경은 수행하지 않았다.
