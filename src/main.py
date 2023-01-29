import multiprocessing

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import files, users
from core.config import StandaloneApplication, app_settings

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    redoc_url=None
)

app.include_router(users.router, prefix='/api/v1')
app.include_router(files.router, prefix='/api/v1/files', tags=['Files'])


if __name__ == '__main__':
    options = {
        "bind": f'{app_settings.project_host}:{app_settings.project_port}',
        "workers": multiprocessing.cpu_count(),
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    StandaloneApplication('main:app', options).run()
