import pytest

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from appserver.apps.account.endpoints import user_detail
from appserver.apps.account.models import User


async def test_user_detail_successfully(db_session: AsyncSession, host_user: User):
    result = await user_detail(host_user.username, db_session)
    assert result.id == host_user.id
    assert result.username == host_user.username
    assert result.email == host_user.email
    assert result.display_name == host_user.display_name
    assert result.is_host is True
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_user_detail_not_found(db_session: AsyncSession):
    with pytest.raises(HTTPException) as exc_info:
        await user_detail("not_found", db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_user_detail_by_http(client: TestClient, host_user: User):
    response = client.get(f"/account/users/{host_user.username}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "test"
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "test"
    assert data["is_host"] is True
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_user_detail_by_http_not_found(client: TestClient):
    response = client.get("/account/users/not_found")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_user_detail_for_real_user(client: TestClient, host_user: User):
    response = client.get(f"/account/users/{host_user.username}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == host_user.username
    assert data["email"] == host_user.email
    assert data["display_name"] == host_user.display_name

    response = client.get("/account/users/not_found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
