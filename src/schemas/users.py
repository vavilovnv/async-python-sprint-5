from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, UUID1, UUID4, validator


class UserBase(BaseModel):
    login: str

    class Config:
        orm_model = True


class UserCreate(UserBase):
    password: str


class DBUser(UserBase):
    hashed_password: str


class UserID(UserBase):
    id: UUID1


class UserToken(BaseModel):
    token: UUID4 = Field(..., alias='access_token')
    token_type: Optional[str] = 'Bearer'
    expires: datetime

    class Config:
        orm_model = True
        allow_population_by_field_name = True

        @validator('token')
        def token_to_hex(cls, value):
            return value.hex
