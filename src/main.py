import multiprocessing
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend

from api import files, services, users
from core.config import ServerApplication, app_settings

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    redoc_url=None
)


@app.on_event('startup')
async def on_startup() -> None:
    rc = RedisCacheBackend(
        f'redis://{app_settings.redis_host}:{app_settings.redis_port}'
    )
    caches.set(CACHE_KEY, rc)


@app.on_event('shutdown')
async def on_shutdown() -> None:
    await close_caches()


app.include_router(services.router, prefix="/api/v1", tags=["Services"])
app.include_router(users.router, prefix='/api/v1', tags=["Users"])
app.include_router(files.router, prefix='/api/v1/files', tags=['Files'])


if __name__ == '__main__':
    options = {
        "bind": f'{app_settings.project_host}:{app_settings.project_port}',
        "workers": multiprocessing.cpu_count(),
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    ServerApplication('main:app', options).run()
