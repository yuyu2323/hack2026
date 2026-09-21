from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import Field,AwareDatetime,field_validator
from server.stores.schemas import ReasonInput

GeneralRole=Literal['store_owner','ofc','regional','hq']

class VersionInput(ReasonInput):
    version:int=Field(ge=1)

class AccountCreate(ReasonInput):
    login_id:str=Field(min_length=3,max_length=80,pattern=r'^[a-zA-Z0-9._-]+$')
    display_name:str=Field(min_length=1,max_length=120)
    role:GeneralRole
    region_id:UUID|None=None
    password:str=Field(min_length=12,max_length=128)
    @field_validator('login_id')
    @classmethod
    def lowercase(cls,value):return value.lower()

class AccountUpdate(VersionInput):
    display_name:str|None=Field(default=None,min_length=1,max_length=120)
    role:GeneralRole|None=None
    region_id:UUID|None=None
    is_active:bool|None=None
    password:str|None=Field(default=None,min_length=12,max_length=128)

class MappingUpdate(VersionInput):
    store_ids:list[UUID]=Field(max_length=100)
    @field_validator('store_ids')
    @classmethod
    def unique_ids(cls,value):
        if len(value)!=len(set(value)):raise ValueError('중복 매장입니다.')
        return value

class RegionCreate(ReasonInput):
    code:str=Field(min_length=1,max_length=32,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=1,max_length=120)

class RegionUpdate(VersionInput):
    name:str|None=Field(default=None,min_length=1,max_length=120)
    is_active:bool|None=None

class CategoryCreate(RegionCreate):
    description:str=Field(default='',max_length=4000)

class CategoryUpdate(RegionUpdate):
    description:str|None=Field(default=None,max_length=4000)

class StoreCreate(RegionCreate):
    region_id:UUID
    store_type:str=Field(min_length=1,max_length=80)
    address:str=Field(default='',max_length=4000)

class StoreUpdate(RegionUpdate):
    region_id:UUID|None=None
    store_type:str|None=Field(default=None,min_length=1,max_length=80)
    address:str|None=Field(default=None,max_length=4000)

class AnnouncementCreate(ReasonInput):
    title:str=Field(min_length=1,max_length=160)
    body:str=Field(min_length=1,max_length=4000)
    severity:Literal['info','maintenance']
    starts_at:AwareDatetime
    ends_at:AwareDatetime|None=None

class AnnouncementUpdate(VersionInput):
    title:str|None=Field(default=None,min_length=1,max_length=160)
    body:str|None=Field(default=None,min_length=1,max_length=4000)
    severity:Literal['info','maintenance']|None=None
    starts_at:AwareDatetime|None=None
    ends_at:AwareDatetime|None=None
    is_active:bool|None=None
