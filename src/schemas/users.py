from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class UserBase(BaseModel):
    name: str

    class Config:
        orm_model = True


class UserCreate(UserBase):
    password: str


class DBUser(UserBase):
    hashed_password: str


class UserID(UserBase):
    id: UUID
