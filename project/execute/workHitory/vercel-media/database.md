Vercel 임시 파일 시스템 대신 선택형 DB 사진 저장소를 추가한다. 기존 계약과 파일 저장 기본값은 유지한다. PostgreSQL 트랜잭션 advisory lock으로 저장량 경쟁을 막는다.

구현: media_blobs 모델/0005 마이그레이션, DB·파일 선택 저장과 읽기, 원본 해시/크기 검증, 시드 사진 영속화 및 SEED_CREDENTIAL_FILE 지원. POST 제출/GET 작업 조회에 승인된 요청 기반 분석 훅 추가.
검증: 신규 SQLite 미디어 테스트 5개 통과. 기존 업무 API·미디어 권한·모델 등 선택 회귀 21개 통과, PostgreSQL 1개 미실행. HTTP 작업자 9개는 Windows 대형 파라미터 ID 문제를 짧은 ID 테스트 플러그인으로 우회하여 통과. 실제 AI/외부 PostgreSQL은 호출하지 않음.
후속 범위: VITE_HOSTED_UPLOAD_LIMIT=true일 때 공유 사진 선택기에서 큰 사진을 JPEG로 축소, 최대 선택 개수 기준 총 3.5MiB 제한. 원본 10MiB 제한 유지, 미리보기는 실제 전송본. TS/Vite 빌드 통과.
