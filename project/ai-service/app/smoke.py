"""실제 생성 이미지와 Reference로 로컬 AI HTTP 경로를 검증한다."""

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx

from app.config import PROJECT_ROOT, get_settings
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import derive_metrics, validate_result


def identifier(name):
    return str(uuid5(NAMESPACE_URL, "storeloop:real-ai-smoke:" + name))


def prepare_input():
    base = PROJECT_ROOT / "scripts" / "seed" / "assets" / "shelves"
    submission_path = base / "beverage-before-01.png"
    reference_path = base / "beverage-reference-01.png"
    submission, reference = submission_path.read_bytes(), reference_path.read_bytes()
    context = AnalysisInput.model_validate({
        "schema_version": "1.0", "job_id": identifier("job"), "attempt_id": identifier("attempt"),
        "submission_id": identifier("submission"),
        "question": "가운데 선반의 빈 공간과 앞줄 정렬을 어떻게 개선하면 좋을까요? Reference와 비교해 주세요.",
        "guidelines": [{
            "guideline_id": identifier(key), "version_id": identifier(key + ":1"), "version": 1,
            "level": "CATEGORY", "rule_key": key, "text": text,
        } for key, text in [
            ("facing", "같은 구역의 상품 앞면을 선반 앞 가장자리와 평행한 일정한 앞줄로 정렬한다."),
            ("shelf_gap", "상품 구역 안에 넓은 빈 공간을 두지 않고 상품 사이 간격을 일정하게 유지한다."),
        ]],
        "photos": [{"photo_id": identifier("photo"), "position": 1, "mime_type": "image/png", "sha256": hashlib.sha256(submission).hexdigest()}],
        "references": [{
            "reference_id": identifier("reference"), "photo_id": identifier("reference-photo"), "position": 1,
            "mime_type": "image/png", "sha256": hashlib.sha256(reference).hexdigest(),
            "caption": "앞줄과 간격이 정리된 가상 음료 매대 Reference",
        }], "previous_review": None,
    })
    return context, submission, reference


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8204")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    settings = get_settings()
    context, submission, reference = prepare_input()
    started = time.monotonic()
    report = {
        "test_id": "AT-10-EARLY", "source_kind": "real_ai", "image_source_kind": "ai_generated_demo",
        "started_at": datetime.now(timezone.utc).isoformat(), "status": "FAIL",
        "input": context.model_dump(), "transport": "actual_local_http", "model_configured": settings.codex_model,
    }
    try:
        with httpx.Client(timeout=httpx.Timeout(130, connect=5), trust_env=False) as client:
            response = client.post(
                args.url + "/internal/analyze",
                headers={"Authorization": "Bearer " + settings.ai_service_token},
                data={"metadata": context.model_dump_json()},
                files=[("photos", ("submission.png", submission, "image/png")),
                       ("references", ("reference.png", reference, "image/png"))],
            )
        report["http_status"] = response.status_code
        body = response.json()
        if response.status_code == 200:
            result = validate_result(body["result"], context)
            report.update(status="PASS", response=body, metrics=derive_metrics(result, context))
        else:
            report["error_code"] = body.get("error", {}).get("code", "UNKNOWN_HTTP_ERROR")
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        report["error_code"] = getattr(exc, "code", "HTTP_OR_VALIDATION_FAILURE")
    report["http_elapsed_ms"] = int((time.monotonic() - started) * 1000)
    report["within_30_second_target"] = report["status"] == "PASS" and report["http_elapsed_ms"] <= 30000
    report["browser_latency_measured"] = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ["test_id", "status", "http_elapsed_ms", "within_30_second_target"]}))
    if report.get("error_code"):
        print(json.dumps({"error_code": report["error_code"]}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
