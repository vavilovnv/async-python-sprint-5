import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from db import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    login = Column(String(75), unique=True, index=True)
    hashed_password = Column(String())
    tokens = relationship(
        'Tokens',
        back_populates="user",
        passive_deletes=True
    )


class Tokens(Base):
    __tablename__ = 'tokens'
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid1)
    token = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
        index=True,
    )
    user = relationship('Users', back_populates='tokens')
    user_id = Column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    expires = Column(DateTime())
