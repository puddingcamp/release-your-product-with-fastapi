from fastapi.testclient import TestClient
from fastapi import status

from appserver.apps.account.constants import AUTH_TOKEN_COOKIE_NAME
from appserver.apps.account.models import User


async def test_로그아웃_시_인증_토큰이_삭제되어야_한다(
    client_with_auth: TestClient,
):
    response = client_with_auth.delete("/account/logout")
    assert response.status_code == status.HTTP_200_OK

    assert response.cookies.get(AUTH_TOKEN_COOKIE_NAME) is None
