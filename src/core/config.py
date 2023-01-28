from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from gunicorn.app.wsgiapp import WSGIApplication
from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

if not load_dotenv(dotenv_path=Path('../.env')):
    load_dotenv(dotenv_path=Path('./.env'))


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


class AppSettings(BaseSettings):
    app_title: str = "Fastapi file server"
    database_dsn: PostgresDsn = ('postgresql+asyncpg://postgres:'
                                 'postgres@localhost:5432/postgres')
    project_host: str = '0.0.0.0'
    project_port: int = 8000

    class Config:
        env_file = '.env'


app_settings = AppSettings()
