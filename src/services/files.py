from models.files import File
from schemas.files import FileCreate

from .base import RepositoryDBFile


class RepositoryFile(RepositoryDBFile[File, FileCreate]):
    pass


files_crud = RepositoryFile(File)
