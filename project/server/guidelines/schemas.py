from typing import Literal
from uuid import UUID
from pydantic import Field, model_validator
from server.business_common import InputModel

class GuidelineCreate(InputModel):
    rule_key: str = Field(min_length=1, max_length=80, pattern=r'^[a-z][a-z0-9_]{0,79}$')
    title: str = Field(min_length=1, max_length=160)
    level: Literal['HQ', 'REGION', 'STORE', 'CATEGORY']
    region_id: UUID | None = None
    store_id: UUID | None = None
    category_id: UUID | None = None
    text: str = Field(min_length=1, max_length=10000)
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode='after')
    def validate_scope(self):
        valid = ((self.level == 'HQ' and not self.region_id and not self.store_id)
                 or (self.level == 'REGION' and self.region_id and not self.store_id)
                 or (self.level == 'STORE' and self.store_id and not self.region_id)
                 or (self.level == 'CATEGORY' and self.category_id and not self.region_id))
        if not valid:
            raise ValueError('기준 레벨과 적용 범위를 확인해 주세요.')
        return self

class GuidelineVersionCreate(InputModel):
    version: int = Field(ge=1)
    text: str = Field(min_length=1, max_length=10000)
    reason: str = Field(min_length=1, max_length=500)
    title: str | None = Field(default=None, min_length=1, max_length=160)

class GuidelineStatus(InputModel):
    version: int = Field(ge=1)
    is_active: bool
    reason: str = Field(min_length=1, max_length=500)

class ReferenceCreate(InputModel):
    category_id: UUID
    store_id: UUID | None = None
    caption: str = Field(default='', max_length=2000)
    reason: str = Field(min_length=1, max_length=500)

class ReferenceChange(InputModel):
    state_version: int = Field(ge=1)
    caption: str = Field(max_length=2000)
    reason: str = Field(min_length=1, max_length=500)

class ReferenceStatus(InputModel):
    state_version: int = Field(ge=1)
    is_active: bool
    reason: str = Field(min_length=1, max_length=500)
