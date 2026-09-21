# AI-TIME-READ-001 · 시안05 재처리 시간 기준 대조

상태 REVIEW_COMPLETE. contract_data가 독립 읽기 검증 중 전달한 job `aa73ad7e-9d08-5a5b-b035-96941a217621`의 adapter50,635ms/worker UTC48,786ms, 차이1,849ms를 코드와 대조했다. DB 원본 시각 검증은 contract_data가 소유하며 이 검토는 소스 읽기만 수행했다.

- `ai-service/app/adapters/codex.py`의 analyze는 요청 로컬 `time.monotonic()`을 임시 이미지 파일 작성 직전에 읽고 CLI 실행·출력 계약 검증 후 차이를 정수ms로 반환한다. CLI 버전 조회·finally 정리/HTTP 왕복은 제외한다. 모델 서비스 추론만의 순수 시간은 아니다.
- `server/analysis_jobs/service.py`의 claim은 `utcnow()`를 started_at에 저장한다. complete_attempt는 소유 잠금을 얻은 후 UTC now를 읽고 이를 finished_at에 저장하므로 검증/후처리/commit 완료 이후 시각 자체는 아니다. 별도 최종 deadline 검사는 commit 전에 다시 수행한다.
- `server/core/base.py`의 utcnow는 datetime.now(timezone.utc)다. 생산 worker 경로는 now를 주입하지 않는다. 테스트의 now 인자/monkeypatch는 테스트 프로세스에 한정된다.
- AI 결과·duration 캐시는 없다. 캐시는 CLI 버전 문자열뿐이다. worker는 응답 job/attempt/submission ID를 검증하므로 다른 시도 응답의 기간을 선택하는 경로를 발견하지 않았다.

안정된 시계라면 worker의 포함 구간은 adapter 구간보다 길어야 한다.1,849ms 역전은 정수 반올림이나 현재 두 구간의 시작/끝 범위만으로 설명되지 않는다. 벽시계와 monotonic 기록의 관측 불일치로 보존하되 NTP·사용자 시계 변경·특정 OS 원인은 증거 없이 확정하지 않는다. 현재 시점의 시계 샘플만으로 과거 원인을 복원할 수 없다.

이 재처리는 과거 Mock 장애 fixture로 이미 정상 신규 제출 성능 집계에서 제외됐다. 원시 값을 교정하거나 같은 모델 호출을 반복하지 않는다. 실제 성공/첫 실패 보존/결과반영의 시각 검수와 시간 원인 조사는 구분한다. 작업자/모델 서비스·DB·설정/비밀은 변경하지 않았다.
