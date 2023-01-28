from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from db import get_session
from services.users import user_crud

from services.utils import hash_password


def validate_password(hashed_password: str, password: str):
    hash_salt = hashed_password.split("$")[0]
    return hashed_password == hash_password(password, hash_salt)


async def current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="v1/auth")),
    db=Depends(get_session)
):
    user = await user_crud.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not active."
        )
    return user
