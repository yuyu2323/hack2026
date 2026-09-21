import copy
import asyncio
import hashlib
import io
import json

import pytest
import httpx
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app
from app.services.images import validate_image
from packages.review_contract.errors import ContractError


def png_bytes(size=(80, 60)):
    image = Image.new("RGB", size, "lightblue")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def metadata_for(data):
    return {"mime_type": "image/png", "sha256": hashlib.sha256(data).hexdigest()}


@pytest.mark.parametrize("case", ["hash", "mime", "filename", "corrupt", "dimensions"])
def test_image_verification_rejects_mismatches(case):
    data = png_bytes((8, 8)) if case == "dimensions" else png_bytes()
    metadata = metadata_for(data)
    filename = "photo.png"
    if case == "hash": metadata["sha256"] = "0" * 64
    if case == "mime": metadata["mime_type"] = "image/jpeg"
    if case == "filename": filename = "photo.svg"
    if case == "corrupt": data = b"not an image"
    with pytest.raises(ContractError) as caught:
        validate_image(data, metadata, filename)
    assert caught.value.code == "INVALID_IMAGE"


def test_internal_authorization_is_required():
    client = TestClient(create_app(Settings(_env_file=None, ai_service_token="local-test-only-internal-token")))
    response = client.post("/internal/analyze")
    assert response.status_code == 401
    assert "local-test-only-internal-token" not in response.text


def test_missing_configured_secret_fails_closed():
    client = TestClient(create_app(Settings(_env_file=None, ai_service_token="")))
    response = client.post("/internal/analyze")
    assert response.status_code == 503


class FakeRunner:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    async def analyze(self, context, photos, references):
        self.calls.append((context, photos, references))
        return {"result": self.payload, "model": "test-double", "prompt_version": "test-v1", "cli_version": "test", "duration_ms": 1}


def request_parts(context):
    data = png_bytes()
    context = copy.deepcopy(context)
    for image in context["photos"] + context["references"]:
        image.update(metadata_for(data))
    return {"metadata": json.dumps(context)}, [("photos", ("photo.png", data, "image/png")), ("references", ("reference.png", data, "image/png"))]


def test_valid_multipart_preserves_ids_and_actual_bytes(context, payload):
    runner = FakeRunner(payload)
    client = TestClient(create_app(Settings(_env_file=None, ai_service_token="local-test-only-internal-token"), runner))
    data, files = request_parts(context)
    response = client.post("/internal/analyze", data=data, files=files, headers={"Authorization": "Bearer local-test-only-internal-token"})
    assert response.status_code == 200
    body = response.json()
    assert body["attempt_id"] == context["attempt_id"]
    assert body["result"]["question_answer"] == payload["question_answer"]
    assert len(runner.calls) == 1
    assert runner.calls[0][1][0] == png_bytes()


def test_no_model_call_for_invalid_metadata(context, payload):
    runner = FakeRunner(payload)
    client = TestClient(create_app(Settings(_env_file=None, ai_service_token="local-test-only-internal-token"), runner))
    context["unexpected"] = "do something"
    data, files = request_parts(context)
    response = client.post("/internal/analyze", data=data, files=files, headers={"Authorization": "Bearer local-test-only-internal-token"})
    assert response.status_code == 422
    assert runner.calls == []


def test_health_does_not_call_model(payload):
    runner = FakeRunner(payload)
    client = TestClient(create_app(Settings(_env_file=None), runner))
    response = client.get("/health")
    assert response.status_code == 200
    assert "cli_available" in response.json()
    assert runner.calls == []


def test_ambiguous_metadata_is_a_client_error(payload):
    runner = FakeRunner(payload)
    client = TestClient(create_app(Settings(_env_file=None, ai_service_token="local-test-only-internal-token"), runner))
    response = client.post("/internal/analyze", data={"metadata": '{"x":1,"x":2}'},
                           headers={"Authorization": "Bearer local-test-only-internal-token"})
    assert response.status_code == 422
    assert runner.calls == []


@pytest.mark.asyncio
async def test_streamed_body_limit_cannot_be_bypassed_without_content_length(payload):
    runner = FakeRunner(payload)
    app = create_app(Settings(_env_file=None, ai_service_token="local-test-only-internal-token", ai_max_request_bytes=128), runner)

    async def content():
        yield b"x" * 100
        yield b"x" * 100

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/internal/analyze", content=content(), headers={"Authorization": "Bearer local-test-only-internal-token"})
    assert response.status_code == 413
    assert runner.calls == []


@pytest.mark.asyncio
async def test_second_analysis_is_rejected_without_an_internal_queue(context, payload):
    started, release = asyncio.Event(), asyncio.Event()

    class BlockingRunner(FakeRunner):
        async def analyze(self, *args):
            started.set()
            await release.wait()
            return await super().analyze(*args)

    runner = BlockingRunner(payload)
    app = create_app(Settings(_env_file=None, ai_service_token="local-test-only-internal-token"), runner)
    data, files = request_parts(context)
    headers = {"Authorization": "Bearer local-test-only-internal-token"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        first = asyncio.create_task(client.post("/internal/analyze", data=data, files=files, headers=headers))
        await asyncio.wait_for(started.wait(), 1)
        second = await client.post("/internal/analyze", data=data, files=files, headers=headers)
        assert second.status_code == 409
        assert second.json()["error"]["code"] == "AI_BUSY"
        release.set()
        assert (await first).status_code == 200
    assert len(runner.calls) == 1
