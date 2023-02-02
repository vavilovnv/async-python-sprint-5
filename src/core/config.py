from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from gunicorn.app.wsgiapp import WSGIApplication
from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

load_dotenv(dotenv_path=Path('./.env'))


class ServerApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


class AppSettings(BaseSettings):
    app_title: str = "Fastapi file server"
    database_dsn: PostgresDsn = ('postgresql+asyncpg://postgres:'
                                 'postgres@postgres-fastapi:5432/postgres')
    project_host: str = '0.0.0.0'
    project_port: int = 8000
    token_expires_min: int = 120
    redis_host: str = 'cache'
    redis_port: int = 6379
    echo_queries: bool = False

    class Config:
        env_file = '.env'


app_settings = AppSettings()
