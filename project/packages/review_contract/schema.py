from packages.review_contract.models import ReviewResultPayload


def result_json_schema() -> dict:
    return ReviewResultPayload.model_json_schema()
