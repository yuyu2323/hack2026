import copy
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ai-service"))


@pytest.fixture
def context():
    return {
        "schema_version": "1.0",
        "job_id": "00000000-0000-4000-8000-000000000001",
        "attempt_id": "00000000-0000-4000-8000-000000000002",
        "submission_id": "00000000-0000-4000-8000-000000000003",
        "question": "선반 앞줄을 어떻게 정리하면 좋을까요?",
        "guidelines": [{
            "guideline_id": "00000000-0000-4000-8000-000000000010",
            "version_id": "00000000-0000-4000-8000-000000000011",
            "version": 1, "level": "HQ", "rule_key": "facing", "text": "상품 앞줄을 정렬합니다.",
        }],
        "photos": [{
            "photo_id": "00000000-0000-4000-8000-000000000020",
            "position": 1, "mime_type": "image/png", "sha256": "a" * 64,
        }],
        "references": [{
            "reference_id": "00000000-0000-4000-8000-000000000030",
            "photo_id": "00000000-0000-4000-8000-000000000031",
            "position": 1, "mime_type": "image/png", "sha256": "b" * 64,
            "caption": "정돈된 앞줄",
        }],
        "previous_review": None,
    }


@pytest.fixture
def payload(context):
    guideline = context["guidelines"][0]
    return {
        "schema_version": "1.0", "question_answer": "앞줄을 선반 끝선에 맞춰 주세요.",
        "summary": "사진 중앙의 상품 간격을 정리하면 좋겠습니다.",
        "overall_confidence": "medium",
        "criteria": [{
            **{key: guideline[key] for key in ["guideline_id", "version_id", "version", "rule_key"]},
            "verdict": "fail", "reason": "앞줄 간격이 고르지 않습니다.",
            "evidence": [{"photo_position": 1, "observation": "중앙에 빈 간격이 보입니다."}],
            "actions": ["앞줄을 정렬해 주세요."],
        }],
        "reference_comparisons": [{
            "reference_id": context["references"][0]["reference_id"],
            "verdict": "different", "photo_positions": [1], "observation": "Reference보다 간격이 넓습니다.",
        }],
        "limitations": [], "ofc_review_required": False, "follow_up_comparison": None,
    }
