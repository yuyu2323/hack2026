import json
from decimal import Decimal, ROUND_HALF_UP

from pydantic import ValidationError

from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput, ReviewResultPayload


def _invalid_json(*args):
    raise ContractError("INVALID_JSON", "분석 결과 형식을 확인할 수 없습니다.")


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _invalid_json()
        result[key] = value
    return result


def strict_json_loads(text: str | bytes):
    try:
        return json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_invalid_json)
    except (ValueError, UnicodeError, TypeError, RecursionError) as exc:
        raise ContractError("INVALID_JSON", "분석 결과 형식을 확인할 수 없습니다.") from None


def _as_result(result) -> ReviewResultPayload:
    try:
        return result if isinstance(result, ReviewResultPayload) else ReviewResultPayload.model_validate(result)
    except (ValidationError, TypeError, ValueError):
        raise ContractError("INVALID_RESULT", "분석 결과를 검증하지 못했습니다.") from None


def parse_result(text: str | bytes) -> ReviewResultPayload:
    if not text or not text.strip():
        raise ContractError("EMPTY_RESPONSE", "분석 결과를 받지 못했습니다.")
    if len(text.encode("utf-8") if isinstance(text, str) else text) > 512 * 1024:
        raise ContractError("INVALID_RESULT", "분석 결과 크기를 초과했습니다.")
    return _as_result(strict_json_loads(text))


def _as_context(context) -> dict:
    return context.model_dump() if isinstance(context, AnalysisInput) else context


def validate_result(result, context) -> ReviewResultPayload:
    result = _as_result(result)
    data = _as_context(context)
    expected = {(g["guideline_id"], g["version_id"], g["version"], g["rule_key"]) for g in data["guidelines"]}
    actual = [(g.guideline_id, g.version_id, g.version, g.rule_key) for g in result.criteria]
    photo_positions = {p["position"] for p in data["photos"]}
    reference_ids = {r["reference_id"] for r in data["references"]}

    def require(condition):
        if not condition:
            raise ContractError("INVALID_RESULT", "분석 결과의 입력 참조를 검증하지 못했습니다.")

    require(len(actual) == len(expected) and set(actual) == expected)
    for criterion in result.criteria:
        require(all(e.photo_position in photo_positions for e in criterion.evidence))
        require(criterion.verdict == "unknown" or bool(criterion.evidence))
        require(criterion.verdict != "fail" or bool(criterion.actions))
    compared_ids = [r.reference_id for r in result.reference_comparisons]
    require(len(compared_ids) == len(reference_ids) and set(compared_ids) == reference_ids)
    for compared in result.reference_comparisons:
        require(all(p in photo_positions for p in compared.photo_positions))
        require(len(set(compared.photo_positions)) == len(compared.photo_positions))
        require(compared.verdict == "unknown" or bool(compared.photo_positions))
    require(data.get("previous_review") is not None or result.follow_up_comparison is None)
    require((data["guidelines"] and data["references"]) or bool(result.limitations))
    return result


def derive_metrics(result, context) -> dict:
    result = validate_result(result, context)
    data = _as_context(context)
    counts = {verdict: sum(c.verdict == verdict for c in result.criteria) for verdict in ("pass", "fail", "unknown")}
    assessable = counts["pass"] + counts["fail"]
    total = len(result.criteria)

    def percent(numerator, denominator):
        if not denominator:
            return None
        return float((Decimal(numerator) * 100 / Decimal(denominator)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))

    return {
        "compliance_rate": percent(counts["pass"], assessable),
        "assessable_rate": percent(assessable, total),
        "needs_ofc_review": bool(counts["unknown"] or not data["guidelines"] or not data["references"]
                                 or result.overall_confidence == "low" or result.ofc_review_required),
        "pass_count": counts["pass"], "fail_count": counts["fail"], "unknown_count": counts["unknown"],
    }
