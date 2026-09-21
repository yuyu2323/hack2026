# 공통 긴 대기와 통신오류
root / RUNNING. 실제Browser+기존테스트서비스의통제된중단·복원. 기존fixture수정/삭제안함.
- independent prepare_fixture.py root소스검토완료: 전용testURL·INSERT전용guard·stableUUID·ps worker종료확인·READONLY기본·既存기록보존. timestamp합성10분전/expireddeadline은Mock질문과source_kind로표시. worker재시작시실제AI호출없이QUEUE_TIMEOUT예정.

- worker session2117 Ctrl-C→worker_stopped/exit0확인. root검토한prepare_fixture --apply --worker-stopped 실행,기존활성job0/INSERT5행/AI0. 새submission2f9b333f-8a43-5df0-841d-f1c66b213ab3,job0d50701f-c61b-5c48-80ea-1df7ca4d2cb4,sha7a09aa3f289e307a825a20921522ed3d030004c01e7a5289e9efc4d0cf7ee7e8.합성queued12:51:54Z/deadline12:54:54Z.
- 5시안390x844/문서375. 경과618~624초·queued와추가지연안내·기존이력으로재확인안내확인,실제결과생성없음. queued-initial.json에원시DOM,각vp-mobile390-long-queued.png.
- API root session93576 Ctrl-C→shutdowncomplete/process58971exit0확인. worker계속정지,AI8010유지.03 수동 버튼 클릭을 시도했으나 자동 접속정보 오류로 이미 사라져 실패했고, 같은 호출의 05 클릭은 실행되지 않았다. 5개 모두 자동 조회 오류를 실제 확인했다.

- API 중단 시 01/04/05는 오류 안내와 재조회, 02는 기존 queued 내용과 통신 오류, 03은 접속 확인 오류를 표시했다. 실제 분석 실패나 점수로 바뀌지 않았다. api-outage.json 및 각 vp-mobile390-api-outage.png 보존.
- API 재시작은 sandbox 포트 bind 거부 후 승인된 명령으로 완료: session24525/process42139. 같은 브라우저 탭에서 01/03/04는 자동 조회/포커스 복구, 02·05는 실제 재조회 버튼으로 복구했다. 04 수동 클릭 시도는 자동 복구로 버튼이 사라져 실행되지 않았다. 03은 복구 도중 같은 detail URL에서 로그인 폼이 일시 보였으나 새 로그인 없이 원래 detail로 돌아왔다. full reload/새 로그인 없이 5개 모두 queued·사진·기준 회복, 오류 없음. api-recovery.json 및 vp-mobile390-api-recovered.png.
- worker 정상 재시작 session40156. 5개 화면에서 기술 실패·대기 시간 초과·운영자 복구 안내를 확인했다. 03 시도1회, 01/02/05 QUEUE_TIMEOUT 코드 표시. 실제 결과·점수 없음. worker-restored.json 및 vp-mobile390-queue-timeout.png. 독립 DB 사후 검토 진행 중.
- 실제 200% 확대는 사용자 후행 선택으로 NOT_RUN이며 이번 390x844 검증으로 대신하지 않는다.

- 독립 사후검토25PASS: 최초expired시도1,started/worker/lease/heartbeat NULL,결과0,snapshot불변. 이전15건 snapshot/사전hash있는12건결과 보존. 상세independent-review.md. API·worker·AI·5개Vite 정상복원.
