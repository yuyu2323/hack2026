기존 결과 계약은 유지하고 검증 완료 후 최소 사용량 메타데이터만 기록한다.
성공 usage JSON1줄 구현: model, input/output/total tokens, req/resp/job IDs, 허용패턴 project/org 헤더, API키 SHA25612자 fingerprint. 값 누락/비정상 메타는 null; 결과 계약 불변. mockHTTP+capsys20개 PASS, 키원문·원본본문·사진·질문 미로그 확인. 실제 API 호출 없음.
실패 계측 수정: strict JSON dict 파싱 직후 usage를 기록하여 완료상태·결과schema·참조 검증에서 실패한 유료응답도 계측. 별도 failure event는 job_id와 고정 stage/code만 기록. incomplete/schema/reference 실패 모의 테스트 추가, 총23개 PASS. 기존 실응답 원인이 미확정이므로 추측성 prompt 변경 안함.
