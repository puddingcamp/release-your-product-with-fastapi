from fastapi import status
from fastapi.testclient import TestClient


async def test_회원가입_성공(client: TestClient):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test테스트1234",
        "password_again": "test테스트1234",
    }

    response = client.post("/account/signup", json=payload)

    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert data["username"] == payload["username"]
    assert isinstance(data["display_name"], str)
    assert len(data["display_name"]) == 8


async def test_응답_결과에는_username_display_name_is_host_만_출력한다(client: TestClient):
    payload = {
        "username": "puddingcamp",
        "display_name": "푸딩캠프",
        "email": "test@example.com",
        "password": "test테스트1234",
        "password_again": "test테스트1234",
    }

    response = client.post("/account/signup", json=payload)

    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    response_keys = frozenset(data.keys())
    expected_keys = frozenset(["username", "display_name", "is_host"])
    assert response_keys == expected_keys

