from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import UUID1
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from models.users import User
from schemas.files import FileInDB, FilesList
from services.files import files_crud
from services.utils import DEFAULT_FOLDER

from .utils import current_user

router = APIRouter()


@router.post(
    '/upload',
    status_code=status.HTTP_201_CREATED,
    response_model=FileInDB,
    response_model_exclude_unset=True,
    description='Uploading user file.'
)
async def upload_file(
    path: str = Query(
        example=f'/src/{DEFAULT_FOLDER}/',
        max_length=450,
        min_length=1
    ),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
    file: UploadFile = File(),
) -> FileInDB:
    file_upload = await files_crud.upload_file(
        db=db,
        file=file,
        user=user,
        path=path)
    return FileInDB(**file_upload)


@router.get(
    '/list',
    response_model=FilesList,
    description='Getting the file list.'
)
async def get_files_list(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user),
) -> FilesList:
    files = await files_crud.get_files_list(db=db, user=user)
    files_list = [FileInDB.from_orm(file).dict() for file in files]
    return FilesList(account_id=user.id, files=files_list)


@router.get(
    '/download',
    response_class=FileResponse,
    description='Download user file.'
)
async def download_file(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user),
        path_or_id: str = ''
) -> FileResponse:
    return await files_crud.download_file(
        db=db,
        user=user,
        path_or_id=path_or_id
    )
