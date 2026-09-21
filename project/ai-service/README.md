# StoreLoop 로컬 AI 서비스

프로젝트 루트에서 실행한다. `server`와 별도의 가상환경을 사용하며 공유 Python 계약은 `packages.review_contract`다.

```sh
PYTHONPATH=. ai-service/.venv/bin/python -m uvicorn app.main:app --app-dir ai-service --host 127.0.0.1 --port 8202 --no-access-log
ai-service/.venv/bin/python -m pytest ai-service/tests -q --tb=short
PYTHONPATH=.:ai-service ai-service/.venv/bin/python -m app.smoke --output execute/workHitory/local-ai/evidence/real-ai-run.json
```

설정은 프로젝트 `.local/runtime.env`를 읽고 OS 환경변수를 우선한다. `AI_SERVICE_TOKEN`은 업무 worker에만 제공하며 비어 있으면 분석 요청을 거절한다. `CODEX_BIN`, `CODEX_MODEL`, `CODEX_REASONING_EFFORT`, `AI_MODEL_TIMEOUT_SECONDS`를 지원한다. 모델 timeout 상한은120초이며 재시도는 업무 서버의 새 attempt로만 수행한다.

`POST /internal/analyze`는 내부 Bearer 인증, metadata JSON과 반복 photos/references 파일을 받는다. 실제 바이트·hash·MIME·크기를 검사하고 요청당0700 임시 폴더에서 Codex를 실행한다. 사용자 config/프로젝트 지시·쉘·웹 검색을 사용하지 않고 프롬프트는 stdin으로 전달한다. subprocess에 DB/내부토큰을 전달하지 않는다. stderr·프롬프트 원문을 로그에 남기지 않는다.

`GET /health`는 CLI 설치 여부, 프로세스, busy, 최근 실제 분석 성공/실패 시각만 제공하며 모델을 호출하지 않는다. 실제 모델 가용성 검증은 smoke 또는 실제 제출로 수행한다.

현재 조기 실제 검증은 `real-ai-early-002.json`: gpt-6-astra / codex-cli0.154.0 / 실제 합성 제출1+Reference1 / schema·참조 PASS / HTTP36.089초. 30초 목표를 초과했으며 브라우저 전체 지연은 별도 검증한다. unit tests의 fake executor는 실제 AI 결과로 표시하지 않는다.
