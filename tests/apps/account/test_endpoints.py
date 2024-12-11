import pytest

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from appserver.app import app
from appserver.apps.account.endpoints import user_detail


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


def test_user_detail_by_http():
    client = TestClient(app)

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


def test_user_detail_by_http_not_found():
    client = TestClient(app)

    response = client.get("/account/users/not_found")

    assert response.status_code == status.HTTP_404_NOT_FOUND
