# 분석 작업자

프로젝트 루트에서 `PYTHONPATH=. server/.venv/bin/python -m server.analysis_jobs.worker`를 실행한다. `--once`는 만료 복구와 작업 최대 1건 처리 후 종료한다. PostgreSQL과 AI 서버가 먼저 실행되어야 한다. 설정은 환경변수 우선이며 `.local/runtime.env`에서 나머지를 읽는다.

SIGTERM/SIGINT를 받으면 신규 점유를 중단하고 현재 분석을 130초 수용 기한 안에 마무리한다. 강제 종료된 시도는 140초 lease가 지난 후 새 작업자의 sweep가 `WORKER_INTERRUPTED`로 종료한다. 운영자가 실패 작업을 재처리하면 새 queued 시도를 예약한다. 자동 모델 재호출이나 성공 결과 덮어쓰기는 하지 않는다.

사진 원본은 snapshot의 연결·MIME·hash와 저장 파일 hash를 대조한 뒤 실제 multipart bytes로 전달한다. 모델을 기다리는 동안 DB 세션과 잠금을 보유하지 않는다. 10초 heartbeat는 존재 확인용이며 절대 lease를 연장하지 않는다. 결과는 job/attempt/worker 소유권·130초 수용 기한·엄격 JSON·참조를 다시 확인하여 Review/Criterion/Issue/Notification과 함께 commit한다.

검증 명령:

```sh
PYTHONPATH=. server/.venv/bin/python -m pytest server/tests/test_analysis_jobs.py server/tests/test_worker_http.py -q --tb=short
```

실제 모델 검증은 별도 명시적 실행이다. 전용 `_test` DB 임시 schema와 `scripts/seed/assets/shelves/beverage-before-01.png`, `beverage-reference-01.png`를 사용하며 인증된 Codex 모델 서비스에 해당 합성 이미지·테스트 질문·기준을 전송한다.

```sh
STORELOOP_RUN_REAL_AI=1 PYTHONPATH=. server/.venv/bin/python -m pytest server/tests/test_analysis_jobs.py::test_real_worker_generated_images_to_postgres -q --tb=short
```

실제 호출이 실행되어야 `execute/workHitory/analysis-jobs/evidence/real-worker-001.json`이 생성된다. 이 파일이 없거나 FAIL이면 실제 모델과 DB 저장의 통합 인수는 미완료다. 일반 회귀 테스트의 synthetic 응답을 실제 모델 성공으로 취급하지 않는다.
