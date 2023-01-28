from typing import Any

import logging.config
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import LOGGING
from db import get_session
from schemas import users as schema_users
from schemas import services as schema_services
from services.users import token_crud, user_crud

from .utils import validate_password

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('fastapi_filestorage_logger')

router = APIRouter()


@router.get(
    '/ping',
    response_model=schema_services.Ping,
    tags=['Service'],
    description='Execute a database ping.'
)
async def check_db(db: AsyncSession = Depends(get_session)) -> Any:
    logger.info('A ping to the DB is requested')
    return await user_crud.get_ping_db(db=db)


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=schema_users.UserID,
    tags=['Users'],
    description='Registering a new user.'
)
async def register_user(
    user: schema_users.UserCreate,
    db: AsyncSession = Depends(get_session)
) -> schema_users.UserID:
    logger.info('Registering a new user.')
    answer = await user_crud.add(db=db, obj_in=user)
    return schema_users.UserID(id=answer.id, login=answer.login)


@router.post(
    '/auth',
    status_code=status.HTTP_201_CREATED,
    response_model=schema_users.UserToken,
    tags=['Users'],
    description='Authenticating user and getting a token.'
)
async def auth_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
) -> schema_users.UserToken:
    user = await user_crud.get_user_by_name(db=db, login=form_data.username)
    if (not user
            or not validate_password(
                user.hashed_password,
                form_data.password
            )):
        raise HTTPException(
            status_code=400,
            detail="Wrong login or password."
        )
    token = await token_crud.create_token(db=db, id=user.id)
    return schema_users.UserToken(
        access_token=token.token,
        expires=token.expires
    )
