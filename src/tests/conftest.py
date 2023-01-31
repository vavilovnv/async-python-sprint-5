import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import asyncpg
import pytest
import pytest_asyncio
from fastapi import status
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import RedisCacheBackend
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from cache.utils import redis_cache
from db import Base, get_session
from main import app

from .utils import (BASE_URL, REDIS_KEY, REDIS_URL, TEST_DB_NAME,
                    TEST_PASSWORD, TEST_USER2, database_dsn)


@pytest_asyncio.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, follow_redirects=False,
                           base_url=BASE_URL) as async_client:
        yield async_client


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def create_test_db() -> None:
    user, password, database = 'postgres', 'postgres', TEST_DB_NAME
    try:
        await asyncpg.connect(database=database, user=user, password=password)
    except asyncpg.InvalidCatalogNameError:
        conn = await asyncpg.connect(
            database='postgres',
            user=user,
            password=password
        )
        sql_command = text(f'CREATE DATABASE "{database}" OWNER "{user}"')
        await conn.execute(sql_command)
        await conn.close()
        await asyncpg.connect(database=database, user=user, password=password)


@pytest_asyncio.fixture(scope="module")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    await create_test_db()
    engine = create_async_engine(database_dsn, echo=False, future=True)
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    cache_redis = RedisCacheBackend(REDIS_URL)
    caches.set(REDIS_KEY, cache_redis)

    def get_cache_override():
        return caches.get(REDIS_KEY)
    app.dependency_overrides[redis_cache] = get_cache_override
    async with session() as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        yield session
    await engine.dispose()
    await close_caches()


@pytest_asyncio.fixture(scope='module')
async def client_authorized() -> AsyncGenerator:
    async with AsyncClient(app=app, follow_redirects=False,
                           base_url=BASE_URL) as async_client:
        response = await async_client.post(
            app.url_path_for("register_user"),
            json={
                'login': TEST_USER2,
                'password': TEST_PASSWORD
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        response = await async_client.post(
            app.url_path_for("auth_user"),
            data={
                'username': TEST_USER2,
                'password': TEST_PASSWORD,
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access_token' in response.json()
        token = response.json().get('access_token')
        async_client.headers.update({'Authorization': f'Bearer {token}'})
        yield async_client
