# BR-001 독립 검토
- root가 contract_data/contract_ai 작성 모듈을 검토. root 업무서비스는 검토 범위에서 제외하여 별도 담당 예정.
- 현재 Session→Account/매핑 DB 재조회, CSRF origin/token, 운영 DTO 필드 제한, 짧은 작업 점유·DB없이HTTP대기·attempt 일치·deadline/lease·완료원자저장·이전시도보존을 확인했다.
- BR-01: API06 고정 operation `analysis.retry`와 worker 실제 `jobs.retry` 불일치 발견. DB/model 변경 없이 확정계약 이름으로 복구하고 실제PG 멱등경쟁 검증 예정. 기존 시연 DB에 실제 재처리 레코드는 없으며 테스트fixture는 격리schema다.
- SEC-오탐: test_analysis_jobs MediaAsset 키워드 긴 한 줄은 generic-api-key 오탐. 줄바꿈만 수정 후 전체소스 스캔 PASS, 전체서버64 PASS. 규칙 완화 없음.

- BR-01 실제PG RED: jobs.retry != analysis.retry. 고정operation 이름으로두호출만수정 후 재처리경쟁/멱등/권한5 PASS. 외부 DTO변경 없음.
