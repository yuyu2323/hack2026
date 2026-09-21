# 합성 이력 정정 도구 구현 — 독립 검토 대상

- 작성자: contract_data. root의 명시적 후속 배정으로 신규 경로 두 개를 구현했다.
- 소유: scripts/repair_seed_fixtures.py, server/tests/test_seed_repair.py.
- 기존 root seed/영업 API 소스는 수정하지 않았다. 실제 demo/public DB 접속·쓰기·백업은 실행하지 않았다.
- 이 문서의 테스트는 작성자의 자기 검증이며 독립 PASS가 아니다. root가 독립 검토와 실제 적용을 소유한다.

## 목적·경계

기존 최초 시드 중 6개 고정 매장×seq1/4의 12개 안정 UUID에 연결된 미래 v2를 당시 v1로 바꾸고, 4개 초기 Reference 등록시각을 BASE−70에서 BASE−65로 바로잡는다. 기존 30개 중 대상 12개 이외의 제출/결과, 사용자 데이터, 실제 AI 결과, 외부 namespace 및 후속 snapshot을 변경하지 않는다.

정정 대상은 AnalysisContext 12개(snapshot/hash), ReviewResult 12개(criteria의 version), CriterionEvaluation 12개(version_id), ReferencePhoto 4개(created_at), 합계40개 행이다. 그 외 본문·점수·질문·이슈·알림·사진·계정·현재 기준은 쓰지 않는다. 삭제가 없다.

## 사전 가드

- namespace/BASE·6개 매장·원래 질문/결과문구·정규화 이미지 지문·버전 텍스트를 고정했다. 향후 seed namespace 변경을 따라가지 않는다.
- 수정 행의 전체 원래 합성 내용 또는 이미 교정된 내용에 정확히 일치해야 한다. snapshot SHA뿐 아니라 질문/사진/Reference/모든 criterion 원문과 결과 지표도 대조한다.
- source_kind=seed_demo 및 mock/seed-v1, 성공 fixture job/attempt 연결, 초기 기준 Version1/2와 Reference lineage/version/state_version/활성/지문/등록시각을 검증한다.
- 수정된 질문·결과·Reference·criterion·hash, real_ai 전환, 외부 후속 제출/previous_review 연결, 누락 레코드 발견 시 전체 fail-closed.
- runtime.env의 demo/test 별칭만 CLI에서 허용한다. localhost:55432, storeloop 사용자, 정확한 storeloop/storeloop_test DB, postgresql+psycopg 및 query 옵션 없음 조건을 확인한다. 실제 URL은 출력하지 않는다.

## 절차·출력

기본은 dry-run이며 행 잠금을 사용한 검증 이후 rollback한다. DB/파일 변경이 없다. --apply에서만 원본40행을 .local/seed-repair-backups/<별칭>의 새0600 JSON에 보존한 후 하나의 DB transaction으로 적용한다. 백업 디렉터리는0700이며 덮어쓰지 않는다. 커밋 실패 때 DB는 rollback하고 원본 백업은 유지한다.

리포트에는 수정 대상의 table/ID/before SHA/after SHA와 개수만 포함한다. 충돌은 안전한 코드와 대상 ID만 출력한다. 내부 DB/연결 오류 원문은 출력하지 않는다. 다시 적용하면 변경0·추가백업0이다.

root 검토 후 사용할 명령:

```sh
server/.venv/bin/python -m scripts.repair_seed_fixtures --database demo
server/.venv/bin/python -m scripts.repair_seed_fixtures --database test
# dry-run 결과와 독립 검토를 확인한 root가 해당 별칭에만 --apply를 추가한다.
```

## TDD 및 자기 검증 증거

1. 신규 모듈 미구현 import RED.
2. 무변경 스텁의 실제 기능 RED: dry-run changed_submissions=0, 기대12 — 1 failed, 2.06초.
3. 구현 후 SQLite8 PASS, 15.18초. dry-run→apply40→반복0·백업0600 및 비대상 user_upload 보존, 변경 snapshot/review/real_ai/reference/criterion/hash/external_child 7종 차단.
4. 전용 PostgreSQL `_test`의 UUID 임시 스키마에서 동일 dry-run/apply/backup/replay 시나리오1 PASS, 2.39초. public 스키마 불변.
5. source namespace/BASE 고정과 별칭 함수 방어 refactor 후 추가2 PASS, 1.99초: flush 이후 인위적 commit 실패에 전체 rollback/원본백업 보존; 외부host/다른port·DB/query/sqlite/임의alias 거절.
6. CLI --help 정상. 실제 demo/test 별칭의 dry-run/apply 실행은 root에 남겼다.

총 자기 검증11개 PASS. 원본 영업백엔드 독립14 PASS와 이11개 자기검증을 구분한다. 최신 소스는 root에 freeze 전달했고 검토·실적용 판단 대기다.
