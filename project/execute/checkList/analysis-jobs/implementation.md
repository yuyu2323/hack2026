# 분석 작업자·재처리 구현

- 담당: contract_ai / analysis-jobs
- 상태: REVIEW
- 선행: G1 ACCEPTED, AI 실제 조기 HTTP 검증 PASS, 공유 계약 구현
- 소유: server/analysis_jobs/service.py, worker.py, 해당 작업 테스트. models.py는 contract_data 소유.
- 기준: 05/06 CONTRACT-DATA-1.0b, 07 AI-001, 09 QA-001
- 목표: 영속 큐·시도·재처리·점유·시간초과·중단·늦은결과·성공원자저장과 PostgreSQL 증거

- [x] 모델·DB/session·멱등/audit·후처리 helper 확인
- [x] PostgreSQL 점유/중복재처리/큐만료/중단/늦은결과 RED
- [x] 독립 worker CLI·HTTP·heartbeat·sweep 구현
- [x] Review/Criterion/Issue/Notification 원자 저장·성공 불변
- [x] 실제 PostgreSQL GREEN 및 worker→AI 통합
- [x] 운영자 retry 인터페이스·안전 상태·이력 인계

PostgreSQL/HTTP 28개 PASS, 기본 실제 모델 테스트 1개 SKIP. 사용자의 명시 승인 후 실제 worker→AI→DB 통합 1개 PASS, 25,805ms. 앞선 자동 검토 거절과 해결 경위는 이력에 보존한다. 독립 구현 검토와 브라우저 인수는 root 후속 게이트다.
