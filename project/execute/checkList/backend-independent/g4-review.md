# G4 백엔드·시드 독립 검토
- 상태: 검토 인계 완료; root 후속 Reference 시간 경계 독립 검증 완료
- 검토자: contract_data (root 영업업무·seed·scripts 미구현자)
- 대상: business_common, guidelines/submissions/reviews/issues/notifications/dashboard/analytics, seed, 실행·보안 스크립트
- 제외: 본인 작성 core/accounts/stores/operations/models/migrations의 독립 PASS 판정
- 허용 수정: 본 체크리스트·이력, 신규 tests/test_independent_acceptance.py, docs06의 운영자 알림403 명시만

- [x] 기존 상위계약/AGENTS/배정·독립성 확인
- [x] PD-003 운영자 알림 제외를06에 명시·전파/ACK
- [x] 권한·현재매핑·멱등·이미지·불변스냅샷·버전경합 코드검토
- [x] 대시보드/통계·결측·기간·미해결 드릴다운 검토
- [x] 시드 안정ID·변경보존·연대기·별도PG스키마 재현
- [x] 실행/정지/설치/검증/시크릿방어 스크립트 검토
- [x] 의심결함 재현시험·root 보고·수정후 재검증
- [x] 독립결과·남은제약 인계

- [x] BI-01 미래 기준 참조·BI-02 해결 조치 삭제 RED→root 수정→독립 GREEN
- [x] BI-03 미관리 API/다른 DB 혼합 경로 보고→root 수정→모의 포트 회귀 PASS
- [x] MEDIA-CLARIFY-1 docs06 명시·root 수신, 과거 Reference metadata/hash 불변 독립 PASS
- [x] 신규 독립12개 검증 PASS (8.05초), 실제 Gitleaks stdin·preflight도 실행
- [x] root의 추가 seed 경계 독립 검증; 정정 도구는 후속 구현 배정으로 독립성 분리
- [x] 공유 런타임 보호로 전체 설치/start/stop NOT_RUN 한계를 최종 인계

- [x] BI-04 필터2개·BI-05 대기Attempt/Reference도입시각 root 수정 후 독립 GREEN
- [x] 새 초기32개 포함 최신 독립14 PASS (7.91초)
- [x] 정정 도구 작성 역할 전환·자기검증11 PASS·root 독립 검토 인계

- [x] root의 정정 도구 독립 검토 및 실제 demo/test 적용 결과 수신 (root 소유, 본인 직접 실행·독립 판정 제외)
- [x] root 후속 historical_versions의 미래 Reference 제외·position 재정렬 소스 검토, test_seed 독립1 PASS(3.51초)
