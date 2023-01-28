import uuid
from sqlalchemy import (Column, String)
from sqlalchemy.dialects.postgresql import UUID

from db import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(75), unique=True, index=True)
    hashed_password = Column(String())
