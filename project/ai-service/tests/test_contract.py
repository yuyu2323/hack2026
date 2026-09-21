import copy
import json

import pytest

from packages.review_contract.errors import ContractError
from packages.review_contract.validation import derive_metrics, parse_result, validate_result


@pytest.mark.parametrize("text", ['{"x":1,"x":2}', '{"x":NaN}', '```json\n{}\n```', '{} trailing'])
def test_strict_json_rejects_unsafe_or_ambiguous_input(text):
    with pytest.raises(ContractError) as caught:
        parse_result(text)
    assert caught.value.code == "INVALID_JSON"


def test_unknown_output_field_is_rejected(payload):
    payload["invented_score"] = 100
    with pytest.raises(ContractError) as caught:
        parse_result(json.dumps(payload))
    assert caught.value.code == "INVALID_RESULT"


@pytest.mark.parametrize("mutation", ["version", "duplicate", "missing", "photo", "reference", "empty_evidence", "empty_actions", "parent"])
def test_semantic_validation_rejects_invalid_reference(payload, context, mutation):
    if mutation == "version": payload["criteria"][0]["version"] = 2
    if mutation == "duplicate": payload["criteria"].append(copy.deepcopy(payload["criteria"][0]))
    if mutation == "missing": payload["criteria"] = []
    if mutation == "photo": payload["criteria"][0]["evidence"][0]["photo_position"] = 2
    if mutation == "reference": payload["reference_comparisons"][0]["reference_id"] = context["submission_id"]
    if mutation == "empty_evidence": payload["criteria"][0]["evidence"] = []
    if mutation == "empty_actions": payload["criteria"][0]["actions"] = []
    if mutation == "parent": payload["follow_up_comparison"] = "이전보다 개선되었습니다."
    with pytest.raises(ContractError) as caught:
        validate_result(payload, context)
    assert caught.value.code == "INVALID_RESULT"


def test_valid_result_roundtrip_and_metrics(payload, context):
    parsed = parse_result(json.dumps(payload))
    validate_result(parsed, context)
    metrics = derive_metrics(parsed, context)
    assert metrics == {"compliance_rate": 0.0, "assessable_rate": 100.0, "needs_ofc_review": False,
                       "pass_count": 0, "fail_count": 1, "unknown_count": 0}


def test_unknown_is_success_with_null_compliance(payload, context):
    criterion = payload["criteria"][0]
    criterion.update(verdict="unknown", reason="사진이 흐려 정렬을 판단할 수 없습니다.", evidence=[], actions=[])
    validate_result(payload, context)
    metrics = derive_metrics(payload, context)
    assert metrics["compliance_rate"] is None
    assert metrics["assessable_rate"] == 0.0
    assert metrics["needs_ofc_review"] is True


def test_no_guidelines_or_reference_requires_review(payload, context):
    context.update(guidelines=[], references=[])
    payload.update(criteria=[], reference_comparisons=[], limitations=["적용 기준과 Reference가 없습니다."])
    validate_result(payload, context)
    metrics = derive_metrics(payload, context)
    assert metrics["compliance_rate"] is None
    assert metrics["assessable_rate"] is None
    assert metrics["needs_ofc_review"] is True
