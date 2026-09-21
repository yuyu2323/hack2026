# QA01 독립 운영 검증 이력

2026-09-21 root 한정 배정 수신. 계정 `988e8b9b-8ec4-45b3-afff-9937b45ac7c9`, retry job `c5d22c4e-7a26-5961-a04f-79ba8e12e745`를 읽기 전용으로 검증한다. 추가 계정 UI 회귀가 진행 중이므로 우선 재처리 입력·출력·hash·시간을 검증하고 최종 복원 후 계정 조회를 수행한다. 실제 AI·HTTP·서비스·DB 쓰기는 하지 않는다.

- 21:51 KST 재처리 단독 15 PASS. 모델 44,971ms/대기 1,696ms/worker 45,191ms, 저장 입력·출력·파생 지표·사진 관계·hash 정상.
- root 복원 완료 후 v9 계정을 포함하여 최종 22 PASS. owner 은행길 종료1, OFC 푸른언덕 종료2 및 감사 before/after 일치.
- 모델 30초 목표 미달과 과거 fixture 시간 제외를 명시했다. 원래 실패는 새 실제 장애 실험이 아니라 seed 보존 근거다.
- 최종 보고서 independent-operations-review.md, JSON 2개와 재실행 probe를 본인 접두사 경로에만 작성했다.
