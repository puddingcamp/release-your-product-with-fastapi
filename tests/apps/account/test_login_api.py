from fastapi import status
from fastapi.testclient import TestClient


from appserver.apps.account.schemas import LoginPayload, SignupPayload
from appserver.apps.account.models import User
from appserver.apps.account.constants import AUTH_TOKEN_COOKIE_NAME


async def test_로그인_성공(host_user: User, client: TestClient):
    payload = LoginPayload.model_validate({
        "username": host_user.username,
        "password": "testtest",
    })
    
    response = client.post("/account/login", json=payload.model_dump())

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == host_user.username
    assert data["user"]["display_name"] == host_user.display_name
    assert data["user"]["is_host"] == host_user.is_host

    cookie = response.cookies.get(AUTH_TOKEN_COOKIE_NAME)
    assert cookie is not None
    assert cookie == data["access_token"]


async def test_회원가입_직후_로그인하기(client: TestClient):
    payload = SignupPayload.model_validate({
        "username": "puddingcamp",
        "display_name": "푸딩캠프",
        "email": "test@example.com",
        "password": "test테스트1234",
        "password_again": "test테스트1234",
    })

    # 회원가입
    response = client.post("/account/signup", json=payload.model_dump())
    assert response.status_code == status.HTTP_201_CREATED

    payload = LoginPayload.model_validate({
        "username": "puddingcamp",
        "password": "test테스트1234",
    })
    # 로그인
    response = client.post("/account/login", json=payload.model_dump())
    assert response.status_code == status.HTTP_200_OK
