import time
from datetime import datetime, timedelta
from typing import Generic, Optional, Type, TypeVar

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import app_settings
from db import Base
from .utils import hash_password


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class RepositoryDBUser(Generic[ModelType, CreateSchemaType]):
    def __init__(self, user_model: Type[ModelType]):
        self._user_model = user_model

    async def get_ping_db(self, db: AsyncSession) -> dict[str, str]:
        start = time.time()
        statement = select(self._user_model)
        await db.execute(statement=statement)
        return {'ping_db': '{:.5f}'.format(time.time() - start)}

    async def add(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        hashed_password = hash_password(obj_in_data.pop('password'))
        obj_in_data['hashed_password'] = hashed_password
        db_obj = self._user_model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
        except exc.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Input another name.'
            )
        except exc.SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error
            )
        return db_obj

    async def get_user_by_name(
        self,
        db: AsyncSession,
        login: str
    ) -> Optional[ModelType]:
        statement = select(self._user_model).where(
            self._user_model.login == login
        )
        user = await db.execute(statement=statement)
        return user.scalar_one_or_none()


class RepositoryDBToken(Generic[ModelType, CreateSchemaType]):
    def __init__(self, token_model: Type[ModelType]):
        self._token_model = token_model

    async def create_token(
        self,
        db: AsyncSession,
        id: int
    ) -> ModelType:
        expires_time = datetime.now() + timedelta(
            minutes=app_settings.token_expires_min
        )
        db_obj = self._token_model(
            user_id=id,
            expires=expires_time)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
        except exc.SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error
            )
        return db_obj
