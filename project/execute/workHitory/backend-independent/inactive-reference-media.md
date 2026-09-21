# 비활성 Reference 관리 사진 독립 회귀

## 사전 확인과 계획
- root는 시안03 HQ Reference 목록에서 미사용 v1이 v2로 교체된 후 사진을 불러오지 못하는 현상을 보고했다. 과거 제출 context에 쓰인 다른 비활성 v1은 정상이다.
- source 확인: guidelines.service의 get_reference/list_references는 manager 역할 및 현재 매장 범위로 비활성 이력 조회를 허용한다. submissions.storage.authorize_media는 활성 Reference 또는 허용된 과거 context만 인정하여 관리 목록의 URL과 불일치한다.
- docs06 §4 목록 include_inactive/과거 revision 보존·동일 인가 요구와 마지막 활성/snapshot-only 문장이 충돌한다. root에게 영업 관리자 현재 조회 범위 안의 비활성 Reference 매체 허용을 명확히 하도록 전달했다. 점주와 운영자 권한 확대는 요청하지 않았다.
- 새 독립 테스트에서 실제 등록·새 사진 교체를 수행하고, 제출 미사용 상태의 원본·썸네일을 검사한다. 합성 사진과 임시 SQLite/미디어만 사용하며 실제 보고 행과 공유 DB를 조회·변경하지 않는다.

## 독립 RED 및 계약 ACK
- 테스트: `server/tests/test_inactive_reference_media.py`. 명령: `server/.venv/bin/python -m pytest server/tests/test_inactive_reference_media.py -q --tb=short`.
- 결과: **4 failed / 5 passed, 2 warnings, 2.24초**. 경고는 기존 테스트 라이브러리 deprecation이며 비밀·실제 자격·원본 사진은 출력하지 않았다.
- 실패4: HQ 전사 공통, HQ 매장 전용, regional 현재 지역, OFC 현재 담당. 첫 Reference 등록→별도 사진으로 v2 교체→제출/AnalysisContext 0건 확인. v1은 비활성 목록·단건200이며 Photo/source_kind 메타데이터도 그대로지만 보호 원본·썸네일이 모두404다. v2 매체는200으로 파일 경로·테스트 구성이 정상임을 확인했다.
- 보호 경계5 PASS: 점주의 미사용 v1은404/활성 v2는200; 운영자는403; 타지역 지역관리자·미배정 OFC·종료된 OFC 매핑은404. 원본·썸네일을 모두 검사했다.
- root가 docs06 §4 MEDIA-CLARIFY-2를 먼저 수정했다. 실제 저장 문구를 읽고 현재 Reference 관리 범위의 영업 관리자만 비활성 이력 사진을 조회한다는 명확화에 ACK를 보냈다. Photo/source_kind/DB 구조·점주 기존 경로·운영자 금지·범위 검사를 유지한다.
- 테스트 freeze와 재현 결과를 root에게 전달했다. 제품 소스 수정자는 root이고, 이 검토자는 수정 후 동일 테스트로 독립 재확인한다.

## root 수정 후 독립 GREEN
- root가 `server/submissions/storage.py` authorize_media를 수정하고 제품 소스 freeze를 전달했다. 독립 검토자는 제품 소스를 변경하지 않았다.
- 소스 대조: require_business가 운영자 접근을 먼저403으로 거부한다. 매 요청의 accessible_store_ids를 사용하며, Reference.photo_id가 요청 media_id와 일치한 행만 검사한다. 관리자 역할은 OFC/regional/HQ로 제한하고 비활성 여부 예외를 적용한다. 매장 전용은 현재 접근 가능한 store_id가 필요하며, 전사 공통은 기존 Reference 목록/단건에서 허용한 관리자 범위를 따른다.
- 점주는 manager=false이므로 활성 Reference 조건이 유지된다. 담당 밖/종료 매핑의 매장 전용 Reference는 이 새 분기에서 허용되지 않는다. 기존 제출 연결 및 현재 허용된 과거 AnalysisContext 경로, 보호 경로 검사, Photo DTO/source_kind는 변경하지 않았다.
- 동일 신규 테스트 독립 재실행: `server/.venv/bin/python -m pytest server/tests/test_inactive_reference_media.py -q --tb=short` → **9 passed, 2 warnings, 1.90초**. RED의 관리자4개는 원본·썸네일 모두200으로 GREEN, 보호 경계5개는 기존 기대값 유지.
- 판정: **MEDIA-CLARIFY-2 독립 기능·권한 검토 PASS**. 실제 브라우저 재확인과 API 재시작은 root 담당이며 이 테스트 결과로 대체하지 않는다. 공유 DB·브라우저·서버 런타임은 조작하지 않았다.
- 등록부 `execute/workHitory/docs/contract-register.md`의 해당 계약 상태를 독립 PASS로 갱신했다.
