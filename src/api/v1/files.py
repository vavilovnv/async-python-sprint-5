from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from models.users import User
from schemas.files import FileInDB, FilesList, FileSearchMatches
from services.files import files_crud

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
        example=f'my_path',
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
    description='Download file or archived folder.'
)
async def download_file_or_folder(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user),
        path_or_id: str = Query(
            default='',
            alias='path_to_file',
            description='Path to file or file id'
        ),
        path_to_folder: str = Query(
            default='',
            description='Path to folder'
        ),
        compression_type: str = Query(
            default='',
            description='Archive type: zip | tar | 7z'
        )
) -> FileResponse:
    if compression_type and compression_type not in ('zip', 'tar', '7z'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Wrong compression type.'
        )
    if path_to_folder:
        return await files_crud.get_folder_archive(
            user=user,
            path=path_to_folder,
            compression_type=compression_type
        )
    return await files_crud.download_file(
        db=db,
        user=user,
        path_or_id=path_or_id,
        compression_type=compression_type
    )


@router.get(
    '/search',
    response_model=FileSearchMatches,
    description='Searching for an uploaded file.'
)
async def files_search(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_user),
        path: str = Query(
            default='',
            max_length=500,
            description='Folder id to search'
        ),
        extension: str = Query(
            default='',
            max_length=10,
            description='File extension'
        ),
        order_by: str = Query(
            default='',
            max_length=50,
            description=f"Field to order search result: "
                        f"{', '.join(list(FileInDB.__fields__.keys()))}"),
        limit: int = Query(
            default=100,
            ge=1,
            description='Max number of result.'
        ),
) -> FileSearchMatches:
    if order_by not in FileInDB.__fields__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order_by field should be in {FileInDB.__fields__}"
        )
    result = await files_crud.search(db=db, user=user, path=path,
                                     ext=extension, order=order_by,
                                     limit=limit)
    return FileSearchMatches(matches=result)
