import logging.config

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import LOGGING
from services.files import files_crud
from schemas.services import Ping
from db import get_session

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('fastapi_filestorage_logger')

router = APIRouter()


@router.get(
    '/ping',
    response_model=Ping,
    description='Execute a database ping.'
)
async def check_db(db: AsyncSession = Depends(get_session)) -> Any:
    logger.info('A ping to the DB is requested')
    return await files_crud.get_ping_db(db=db)
