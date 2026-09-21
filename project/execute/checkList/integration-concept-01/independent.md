# AI-HTTP-INDEPENDENT-01

- 담당 contract_ai / 상태 REVIEW_COMPLETE. root browser.md 및 원본 checklist는 변경하지 않는다.
- [x] PostgreSQL REPEATABLE READ/READ ONLY에서 실제 입력·엄격 schema/참조·저장집계·버전/부모 보존 확인
- [x] 제출/Reference의 실제 MediaAsset ID·파일 hash와 수량 대조
- [x] 별도 HTTP 세션의 점주 정상200/hash/썸네일200 → 운영자403/다른지역404 검증
- [x] 원본 export와 불일치/제약·비밀 없는 증거/보고서 작성
- AI 추가호출·DB 업무 변경·Browser·서비스 변경 금지. 로그인/CSRF/logout만 새 검사 세션으로 수행한다.
