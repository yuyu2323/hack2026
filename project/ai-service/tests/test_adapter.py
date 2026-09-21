import asyncio
import json
import sys
from pathlib import Path

import pytest

from app.adapters.codex import CodexRunner
from app.config import Settings
from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput


def executable(tmp_path, body):
    path = tmp_path / "fake-codex"
    path.write_text(f"#!{Path(sys.executable).resolve()}\nimport os,sys,json,time\nfrom pathlib import Path\n"
                    "if '--version' in sys.argv:\n print('codex-cli test-double');sys.exit(0)\n" + body)
    path.chmod(0o700)
    return str(path)


def settings_for(tmp_path, path, timeout=2):
    return Settings(_env_file=None, codex_bin=path, ai_temp_root=tmp_path / "requests", ai_model_timeout_seconds=timeout)


@pytest.mark.asyncio
async def test_cli_receives_bytes_with_separate_roles_and_no_app_secrets(tmp_path, context, payload, monkeypatch):
    monkeypatch.setenv("AI_SERVICE_TOKEN", "test-only-private")
    monkeypatch.setenv("DATABASE_URL", "test-only-database")
    fake = executable(tmp_path, """
prompt=sys.stdin.read()
assert 'AI_SERVICE_TOKEN' not in os.environ and 'DATABASE_URL' not in os.environ
assert '--ignore-user-config' in sys.argv and '--ephemeral' in sys.argv
assert 'read-only' in sys.argv
assert 'REFERENCE_IMAGE' in prompt and 'SUBMISSION_IMAGE' in prompt
assert '선반 앞줄' in prompt
images=[sys.argv[i+1] for i,x in enumerate(sys.argv) if x=='--image']
assert [Path(p).read_bytes() for p in images]==[b'submission-bytes',b'reference-bytes']
assert (Path.cwd().stat().st_mode & 0o777)==0o700
Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(""" + repr(json.dumps(payload)) + ")\n")
    runner = CodexRunner(settings_for(tmp_path, fake))
    response = await runner.analyze(AnalysisInput.model_validate(context), [b"submission-bytes"], [b"reference-bytes"])
    assert response["result"]["criteria"][0]["verdict"] == "fail"
    assert response["cli_version"] == "codex-cli test-double"
    assert list((tmp_path / "requests").iterdir()) == []


@pytest.mark.parametrize("body,code", [
    ("sys.stderr.write('authentication required test-only-private');sys.exit(1)\n", "MODEL_AUTH_FAILED"),
    ("sys.stderr.write('network error test-only-private');sys.exit(2)\n", "MODEL_EXECUTION_FAILED"),
    ("pass\n", "EMPTY_RESPONSE"),
    ("Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text('not json')\n", "INVALID_JSON"),
])
@pytest.mark.asyncio
async def test_cli_failures_are_classified_without_raw_output(tmp_path, context, body, code):
    runner = CodexRunner(settings_for(tmp_path, executable(tmp_path, body)))
    with pytest.raises(ContractError) as caught:
        await runner.analyze(AnalysisInput.model_validate(context), [b"p"], [b"r"])
    assert caught.value.code == code
    assert "test-only-private" not in str(caught.value)
    assert list((tmp_path / "requests").iterdir()) == []


@pytest.mark.asyncio
async def test_timeout_terminates_process_and_cleans_workspace(tmp_path, context):
    runner = CodexRunner(settings_for(tmp_path, executable(tmp_path, "time.sleep(30)\n"), timeout=0.1))
    with pytest.raises(ContractError) as caught:
        await runner.analyze(AnalysisInput.model_validate(context), [b"p"], [b"r"])
    assert caught.value.code == "MODEL_TIMEOUT"
    assert list((tmp_path / "requests").iterdir()) == []


@pytest.mark.asyncio
async def test_missing_binary_is_technical_failure(tmp_path, context):
    runner = CodexRunner(settings_for(tmp_path, str(tmp_path / "missing")))
    with pytest.raises(ContractError) as caught:
        await runner.analyze(AnalysisInput.model_validate(context), [b"p"], [b"r"])
    assert caught.value.code == "CLI_UNAVAILABLE"


@pytest.mark.asyncio
async def test_tool_execution_event_is_rejected_and_temporary_input_removed(tmp_path, context):
    body = "print(json.dumps({'type':'item.started','item':{'type':'command_execution'}}),flush=True)\ntime.sleep(30)\n"
    runner = CodexRunner(settings_for(tmp_path, executable(tmp_path, body)))
    with pytest.raises(ContractError) as caught:
        await runner.analyze(AnalysisInput.model_validate(context), [b"p"], [b"r"])
    assert caught.value.code == "MODEL_EXECUTION_FAILED"
    assert list((tmp_path / "requests").iterdir()) == []


@pytest.mark.asyncio
async def test_cancellation_removes_request_directory(tmp_path, context):
    runner = CodexRunner(settings_for(tmp_path, executable(tmp_path, "time.sleep(30)\n")))
    task = asyncio.create_task(runner.analyze(AnalysisInput.model_validate(context), [b"p"], [b"r"]))
    for _ in range(100):
        if (tmp_path / "requests").exists() and list((tmp_path / "requests").iterdir()):
            break
        await asyncio.sleep(0.01)
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert list((tmp_path / "requests").iterdir()) == []


@pytest.mark.asyncio
async def test_timeout_stops_child_that_ignores_termination(tmp_path, context):
    marker = tmp_path / "orphan-was-alive"
    # 3초 정상 종료 유예가 끝난 뒤에도 자식이 살아 있는지 확인한다.
    child = "import signal,time;from pathlib import Path;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(4);Path(" + repr(str(marker)) + ").write_text('alive')"
    body = "import subprocess\nsubprocess.Popen([sys.executable,'-c'," + repr(child) + "])\ntime.sleep(30)\n"
    runner = CodexRunner(settings_for(tmp_path, executable(tmp_path, body), timeout=0.2))
    with pytest.raises(ContractError) as caught:
        await runner.analyze(AnalysisInput.model_validate(context), [b"p"], [b"r"])
    assert caught.value.code == "MODEL_TIMEOUT"
    await asyncio.sleep(1.2)
    assert not marker.exists()
