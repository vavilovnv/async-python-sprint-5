from models.files import File
from schemas.files import FileInDB, FileCreate

from .base import RepositoryDBFile


class RepositoryFiles(RepositoryDBFile[File, FileCreate]):
    pass


files_crud = RepositoryFiles(File, FileInDB)
