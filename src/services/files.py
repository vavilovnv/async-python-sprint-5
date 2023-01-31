from models.files import File
from schemas.files import FileCreate, FileInDB

from .base import RepositoryDBFile


class RepositoryFiles(RepositoryDBFile[File, FileCreate]):
    pass


files_crud = RepositoryFiles(File, FileInDB)
