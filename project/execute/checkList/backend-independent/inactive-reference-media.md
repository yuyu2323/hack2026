# 비활성 Reference 관리 사진 독립 회귀

- 배정: root가 실제 시안03 브라우저에서 찾은, 제출에 사용하기 전 교체된 v1의 사진 실패를 격리 API 테스트로 재현한다.
- 허용 변경: 신규 `server/tests/test_inactive_reference_media.py`, 본 체크리스트·검토 이력. 제품 소스·문서 수정은 root 담당이다.
- [x] 목록/상세의 현재 관리 범위와 원본/썸네일 인가 구현·docs06 대조
- [x] 실제 Reference 등록→사진 교체→미사용 비활성 v1 조회 RED: 4 FAIL/5 PASS, 2.24초
- [x] HQ/지역/OFC 허용 및 점주/운영자/다른 범위/종료 매핑 차단 검증
- [x] 원인·문서 정합 필요·테스트 freeze root 인계, root MEDIA-CLARIFY-2 실제 문서 확인 ACK
- [x] root 수정 후 독립 GREEN 확인: 9 PASS, 1.90초. 허용/거부 조건 소스 대조 PASS.
- [x] MEDIA-CLARIFY-2 등록부의 독립 검증 상태 갱신. 실제 브라우저 재확인은 root 소유로 구분.
- 제한: 공유 DB·브라우저·런타임·Git 변경 금지. SQLite 및 tmp_path 합성 이미지만 사용한다.
