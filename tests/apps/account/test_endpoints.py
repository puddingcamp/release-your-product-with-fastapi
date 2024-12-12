import pytest

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from appserver.apps.account.endpoints import user_detail
from appserver.apps.account.models import User


async def test_user_detail_successfully():
    result = await user_detail("test")
    assert result["id"] == 1
    assert result["username"] == "test"
    assert result["email"] == "test@example.com"
    assert result["display_name"] == "test"
    assert result["is_host"] is True
    assert result["created_at"] is not None
    assert result["updated_at"] is not None


async def test_user_detail_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await user_detail("not_found")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_user_detail_by_http(client: TestClient):
    response = client.get("/account/users/test")

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


async def test_user_detail_for_real_user(client: TestClient, db_session: AsyncSession):
    user = User(
        username="test",
        password="test",
        email="test@example.com",
        display_name="test",
        is_host=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()

    response = client.get(f"/account/users/{user.username}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["display_name"] == user.display_name

    response = client.get("/account/users/not_found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
