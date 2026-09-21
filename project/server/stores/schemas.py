from pydantic import Field,field_validator
from server.accounts.schemas import StrictInput

class ReasonInput(StrictInput):
    reason:str=Field(min_length=1,max_length=500)
    @field_validator('reason')
    @classmethod
    def clean_reason(cls,value):
        value=value.strip()
        if not value: raise ValueError('사유를 입력해 주세요.')
        return value
