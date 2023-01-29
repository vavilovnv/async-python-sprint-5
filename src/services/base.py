import os
import time

import aiofiles

from datetime import datetime, timedelta
from pathlib import Path
from typing import Generic, Type, TypeVar

from fastapi import File, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import and_, exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import app_settings
from db import Base
from models.users import User, Token

from .utils import DEFAULT_FOLDER, hash_password, validate_path, validate_uuid


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
    ) -> ModelType | None:
        statement = select(self._user_model).where(
            self._user_model.login == login
        )
        user = await db.execute(statement=statement)
        return user.scalar_one_or_none()

    async def get_user_by_token(
            self,
            db: AsyncSession,
            token: str
    ) -> ModelType | None:
        query = select(self._user_model).join(Token).where(
            and_(Token.token == token, Token.expires > datetime.now())
        )
        user = await db.execute(query)
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


class RepositoryDBFile(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    @staticmethod
    async def save_file(
            user: User,
            path: str = '',
            file: UploadFile = File(),
    ) -> None:
        file.file.seek(0)
        content = file.file.read()
        user_folder = DEFAULT_FOLDER + f'/{user.login}'
        if path:
            user_folder = f'{user_folder}/{path}'
        folder = Path(user_folder)
        try:
            if not Path.exists(folder):
                Path(folder).mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(Path(folder, file.filename), 'wb') as f:
                await f.write(content)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'File not saved: {error}'
            )

    async def create_in_db(
            self,
            size: int,
            db: AsyncSession,
            user: User,
            path: str,
            file: UploadFile = File(),
    ) -> ModelType:
        db_obj = self._model(
            name=file.filename,
            path=path,
            size=size,
            is_downloadable=True,
            author=user.id
        )
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

    async def upload_file(
            self,
            db: AsyncSession,
            user: User,
            path: str,
            file: UploadFile = File(),
    ) -> dict:
        file_size = len(await file.read())
        await self.save_file(
            user=user,
            path=path,
            file=file,
        )
        db_obj = await self.create_in_db(
            db=db,
            user=user,
            path=path,
            file=file,
            size=file_size
        )
        return jsonable_encoder(db_obj)

    async def get_files_list(
            self,
            db: AsyncSession,
            user: User,
            skip=0,
            limit=100
    ) -> list[ModelType]:
        statement = select(self._model).where(
            self._model.author == user.id
            ).offset(skip).limit(limit)
        result = await db.execute(statement=statement)
        return result.scalars().all()

    async def get_file_by_path(
            self,
            db: AsyncSession,
            user: User,
            path: Path
    ) -> File:
        file_path = Path(path)
        statement = select(self._model).where(
            and_(
                self._model.path == str(file_path.parent),
                self._model.name == file_path.name,
                self._model.author == user.id
            )
        )
        result = await db.scalar(statement=statement)
        if result:
            path = f'{DEFAULT_FOLDER}/{user.login}/{result.path}/{result.name}'
            if os.path.exists(path) and os.path.isfile(path):
                return FileResponse(path=path)

    async def get_file_by_id(
            self,
            db: AsyncSession,
            user: User,
            id: str
    ) -> File:
        statement = select(self._model).where(self._model.id == id)
        result = await db.scalar(statement=statement)
        if result:
            path = f'{DEFAULT_FOLDER}/{user.login}/{result.path}/{result.name}'
            if os.path.exists(path) and os.path.isfile(path):
                return FileResponse(path=path)

    async def download_file(
            self,
            db: AsyncSession,
            user: User,
            path_or_id: str
    ) -> File:
        if validate_uuid(path_or_id):
            return await self.get_file_by_id(
                db=db,
                user=user,
                id=path_or_id
            )
        if validate_path(path_or_id):
            return await self.get_file_by_path(
                db=db,
                user=user,
                path=Path(path_or_id)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found."
        )
