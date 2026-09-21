# QA02 추가 기준·운영 변경 독립 검증

- [x] 현재 qa02_labels HQ/REGION/STORE/CATEGORY 4후보 및 CATEGORY v2 우선 적용을 읽기 전용 make_snapshot으로 확인한다.
- [x] 과거 실제 AI 3건의 snapshot hash와 새 상위 기준 등록 시점을 비교한다.
- [x] QA02 최종 owner/regionNULL/활성 연결0 및 claim 종료·감사 before/after를 확인한다(v7).
- [x] qa02_test_category v1 생성→명칭 변경·비활성 v2를 확인한다(이름 공백 위치의 검증기 오판 별도 교정).
- [x] 결과·한계·후속 공지/기준 정리 미검증을 기록하고 root에게 인계한다.
- [x] root 후속 완료 전달 뒤 공지·상위 3기준 비활성 및 과거 3건 해시를 별도 READ ONLY 14항목으로 확인한다. UI 재실행은 범위 밖이다.
- 소유: 이 디렉터리의 independent-operations-*만. 공유 DB는 READ ONLY이며 API·AI·Browser·서비스 변경은 하지 않는다.
