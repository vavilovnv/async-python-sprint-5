
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from models.users import User
from schemas.files import UploadResponse
from services.files import files_crud

from .utils import current_user

router = APIRouter()


@router.post(
    '/upload',
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse,
    response_model_exclude_unset=True,
    description='Uploading user file.'
)
async def upload_file(
    path: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
    file: UploadFile = File(),
) -> UploadResponse:
    file_upload = await files_crud.create(
        db=db,
        file=file,
        user=user,
        path=path)
    return UploadResponse(**file_upload)
