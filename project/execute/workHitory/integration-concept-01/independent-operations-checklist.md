# QA01 운영 변경·재처리 독립 메타데이터 검증

- 담당: contract_data. DB READ ONLY, 지정 UUID의 상태·식별자·개수·hash만 보존한다.
- [x] retry job의 최초 실패 시도와 두 번째 성공 적용을 확인한다.
- [x] AI 입력·출력 스키마, 기준/Reference 일치, 저장 파생 지표, snapshot SHA를 확인한다.
- [x] 모델/대기/작업 시간을 별도로 보존하고 관계를 검증한다.
- [x] root 최종 복원 완료 이후 계정 최신 버전·역할·regionNULL·활성 연결0을 확인한다(v9).
- [x] owner 은행길 연결 종료 및 OFC 푸른언덕 두 claim→owner 복원 감사 before/after와 실제 연결을 대조한다.
- [x] 검증·미실행 범위를 별도 기록하고 root에 전달한다.
- 쓰기 범위는 `integration-concept-01/independent-operations-*`뿐이다. 다른 담당의 기존 independent-*와 actual-ai.json은 변경하지 않는다.
- 최초 요청 당시 v7이었으나 root가 추가 검수 후 v9로 복원할 예정이므로 최종 조회는 완료 메시지 이후 수행한다.
