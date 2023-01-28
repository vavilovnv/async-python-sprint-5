from models.users import Token, User
from schemas.users import UserCreate

from .base import RepositoryDBToken, RepositoryDBUser


class RepositoryUser(RepositoryDBUser[User, UserCreate]):
    pass


user_crud = RepositoryUser(User)
token_crud = RepositoryDBToken(Token)
