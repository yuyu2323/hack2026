from pydantic import BaseModel,ConfigDict,Field,field_validator

class StrictInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    @field_validator('*',mode='before',check_fields=False)
    @classmethod
    def clean_strings(cls,value,info):
        return value.strip() if isinstance(value,str) and info.field_name!='password' else value

class LoginInput(StrictInput):
    login_id:str=Field(min_length=3,max_length=80,pattern=r'^[A-Za-z0-9._-]+$')
    password:str=Field(min_length=12,max_length=128)
    @field_validator('login_id')
    @classmethod
    def normalize_login(cls,value): return value.strip().lower()

class EmptyInput(StrictInput):
    pass
