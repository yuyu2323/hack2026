기존 결과 계약은 유지하고 검증 완료 후 최소 사용량 메타데이터만 기록한다.
성공 usage JSON1줄 구현: model, input/output/total tokens, req/resp/job IDs, 허용패턴 project/org 헤더, API키 SHA25612자 fingerprint. 값 누락/비정상 메타는 null; 결과 계약 불변. mockHTTP+capsys20개 PASS, 키원문·원본본문·사진·질문 미로그 확인. 실제 API 호출 없음.
