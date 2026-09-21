from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import Field, model_validator
from server.business_common import InputModel

class IssueCreate(InputModel):
    submission_id: UUID
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=2000)
    priority: Literal['normal', 'high'] = 'normal'

class IssueChange(InputModel):
    version: int = Field(ge=1)
    status: Literal['open', 'in_progress', 'resolved'] | None = None
    assignee_id: UUID | None = None
    priority: Literal['normal', 'high'] | None = None
    resolution: str | None = Field(default=None, min_length=1, max_length=2000)
    next_check_at: datetime | None = None

    @model_validator(mode='after')
    def check_change(self):
        if not self.model_fields_set - {'version'}:
            raise ValueError('변경할 내용을 입력해 주세요.')
        if any(name in self.model_fields_set and getattr(self, name) is None for name in ['status', 'priority']):
            raise ValueError('상태와 우선순위는 비울 수 없습니다.')
        return self

class ActionCreate(InputModel):
    body: str = Field(min_length=1, max_length=2000)
