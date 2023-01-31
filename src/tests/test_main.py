import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from main import app

from .utils import TEST_USER1, TEST_PASSWORD


@pytest.mark.asyncio()
async def test_ping(
        client: AsyncClient,
        async_session: AsyncSession
) -> None:
    response = await client.get(app.url_path_for('check_db'))
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    assert 'db' in res
    assert 'cache' in res
    assert res['db'] > 0
    assert res['cache'] > 0


@pytest.mark.asyncio()
async def test_register_user(
        client: AsyncClient,
        async_session: AsyncSession
) -> None:
    response = await client.post(
        app.url_path_for('register_user'),
        json={
            'login': TEST_USER1,
            'password': TEST_PASSWORD
        }
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio()
async def test_get_files_list_401(
        client: AsyncClient,
        async_session: AsyncSession
) -> None:
    response = await client.get(app.url_path_for('get_files_list'))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio()
async def test_auth_user(
        client: AsyncClient,
        async_session: AsyncSession
) -> None:
    response = await client.post(
        app.url_path_for('auth_user'),
        data={
            'username': TEST_USER1,
            'password': TEST_PASSWORD,
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access_token' in response.json()


@pytest.mark.asyncio()
async def test_get_empty_file_list(
        client_authorized: AsyncClient,
        async_session: AsyncSession
) -> None:
    response = await client_authorized.get(app.url_path_for("get_files_list"))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'files' in data
    assert isinstance(data['files'], list)
    assert len(data['files']) == 0
    assert 'account_id' in data
