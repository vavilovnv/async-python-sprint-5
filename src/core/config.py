from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

if not load_dotenv(dotenv_path=Path('../.env')):
    load_dotenv(dotenv_path=Path('./.env'))


class AppSettings(BaseSettings):
    app_title: str = "Fastapi file server"
    database_dsn: PostgresDsn = ('postgresql+asyncpg://postgres:'
                                 'postgres@postgres-fastapi:5432/postgres')
    project_host: str = '0.0.0.0'
    project_port: int = 8000
    token_expires_min: int = 120
    redis_host: str = 'cache'
    redis_port: int = 6379

    class Config:
        env_file = '.env'


app_settings = AppSettings()
