from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt

from appserver.apps.account.utils import SECRET_KEY, create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from appserver.apps.account.models import User


def test_내_정보_조회(client_with_auth: TestClient, host_user: User):
    response = client_with_auth.get("/account/@me")

    data = response.json()
    assert response.status_code == status.HTTP_200_OK

    response_keys = frozenset(data.keys())
    expected_keys = frozenset(["username", "display_name", "is_host", "email", "created_at", "updated_at"])
    assert response_keys == expected_keys


def test_토큰이_없는_경우_의심스런_접근_오류를_일으킨다(client: TestClient):
    response = client.get("/account/@me")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_유효하지_않은_토큰인_경우_인증_오류를_일으킨다(client_with_auth: TestClient):
    client_with_auth.cookies["auth_token"] = "invalid_token"
    response = client_with_auth.get("/account/@me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_만료된_토큰으로_내_정보_조회(client_with_auth: TestClient):
    token = client_with_auth.cookies.get("auth_token", domain="", path="/")
    decoded = decode_token(token)
    jwt = create_access_token(decoded, timedelta(hours=-1))
    client_with_auth.cookies["auth_token"] = jwt

    response = client_with_auth.get("/account/@me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_유저가_존재하지_않는_경우_내_정보_조회(client_with_auth: TestClient):
    # token = client_with_auth.cookies.get("auth_token", domain="", path="/")
    token = client_with_auth.cookies.get("auth_token")
    decoded = decode_token(token)
    decoded["sub"] = "invalid_user_id"
    jwt = create_access_token(decoded)
    client_with_auth.cookies["auth_token"] = jwt

    response = client_with_auth.get("/account/@me")
    assert response.status_code == status.HTTP_404_NOT_FOUND

