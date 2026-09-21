from uuid import UUID
from pydantic import Field
from server.business_common import InputModel

class SubmissionCreate(InputModel):
    store_id: UUID
    category_id: UUID
    question: str = Field(default='', max_length=2000)
    parent_submission_id: UUID | None = None
