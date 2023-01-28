from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID1


class FileBase(BaseModel):
    name: str


class FileCreate(FileBase):
    pass


class FileUpload(BaseModel):
    path: str


class FileInDBBase(FileBase):
    id: UUID1
    created_at: datetime
    path: Optional[str]
    size: int
    is_downloadable: bool

    class Config:
        orm_mode = True


class File(FileInDBBase):
    pass


class FileInDB(FileInDBBase):
    pass


class UploadResponse(BaseModel):
    Info: Optional[str] = None
    Filesize: Optional[str] = None
    Error: Optional[str] = None
