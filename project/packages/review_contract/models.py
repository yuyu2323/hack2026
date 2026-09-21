from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints, model_validator


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("공백만 있는 문장은 허용하지 않습니다.")
    return value


Identifier = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")]
Digest = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
Text = Annotated[str, StringConstraints(min_length=1, max_length=2000), AfterValidator(_not_blank)]
RuleKey = Annotated[str, StringConstraints(min_length=1, max_length=80), AfterValidator(_not_blank)]
Limitation = Annotated[str, StringConstraints(min_length=1, max_length=1000), AfterValidator(_not_blank)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Evidence(StrictModel):
    photo_position: int = Field(ge=1, le=5)
    observation: Text


class Criterion(StrictModel):
    guideline_id: Identifier
    version_id: Identifier
    version: int = Field(ge=1)
    rule_key: RuleKey
    verdict: Literal["pass", "fail", "unknown"]
    reason: Text
    evidence: list[Evidence] = Field(max_length=20)
    actions: list[Text] = Field(max_length=10)


class ReferenceComparison(StrictModel):
    reference_id: Identifier
    verdict: Literal["similar", "different", "unknown"]
    photo_positions: list[int] = Field(max_length=5)
    observation: Text


class ReviewResultPayload(StrictModel):
    schema_version: Literal["1.0"]
    question_answer: Text
    summary: Text
    overall_confidence: Literal["high", "medium", "low"]
    criteria: list[Criterion] = Field(max_length=100)
    reference_comparisons: list[ReferenceComparison] = Field(max_length=3)
    limitations: list[Limitation] = Field(max_length=20)
    ofc_review_required: bool
    follow_up_comparison: Text | None


class GuidelineInput(StrictModel):
    guideline_id: Identifier
    version_id: Identifier
    version: int = Field(ge=1)
    level: Literal["HQ", "REGION", "STORE", "CATEGORY"]
    rule_key: RuleKey
    text: Annotated[str, StringConstraints(min_length=1, max_length=10000), AfterValidator(_not_blank)]


class PhotoInput(StrictModel):
    photo_id: Identifier
    position: int = Field(ge=1, le=5)
    mime_type: Literal["image/jpeg", "image/png"]
    sha256: Digest


class ReferenceInput(PhotoInput):
    reference_id: Identifier
    caption: str = Field(max_length=2000)
    position: int = Field(ge=1, le=3)


class PreviousReview(StrictModel):
    submission_id: Identifier
    review_id: Identifier
    criteria: list[Criterion] = Field(max_length=100)


class AnalysisInput(StrictModel):
    schema_version: Literal["1.0"]
    job_id: Identifier
    attempt_id: Identifier
    submission_id: Identifier
    question: str = Field(max_length=2000)
    guidelines: list[GuidelineInput] = Field(max_length=100)
    photos: list[PhotoInput] = Field(min_length=1, max_length=5)
    references: list[ReferenceInput] = Field(max_length=3)
    previous_review: PreviousReview | None

    @model_validator(mode="after")
    def validate_relationships(self):
        if sum(len(item.text) for item in self.guidelines) > 30000:
            raise ValueError("기준 본문 합계 제한을 초과했습니다.")
        for name in ("guideline_id", "version_id", "rule_key"):
            values = [getattr(item, name) for item in self.guidelines]
            if len(set(values)) != len(values):
                raise ValueError("기준 식별자가 중복되었습니다.")
        for group in (self.photos, self.references):
            if [item.position for item in group] != list(range(1, len(group) + 1)):
                raise ValueError("사진 순서는 1부터 연속이어야 합니다.")
            if len({item.photo_id for item in group}) != len(group):
                raise ValueError("사진 식별자가 중복되었습니다.")
        if len({item.reference_id for item in self.references}) != len(self.references):
            raise ValueError("Reference 식별자가 중복되었습니다.")
        return self
