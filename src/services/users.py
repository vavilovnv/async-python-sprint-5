from fastapi.security import OAuth2PasswordBearer

from models.users import Tokens, Users
from schemas.users import UserCreate

from .base import RepositoryDBToken, RepositoryDBUser


class RepositoryUser(RepositoryDBUser[Users, UserCreate]):
    pass


user_crud = RepositoryUser(Users)
token_crud = RepositoryDBToken(Tokens)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth")
