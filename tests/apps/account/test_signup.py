from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from appserver.apps.account.schemas import SignupPayload
from appserver.apps.account.exceptions import DuplicatedUsernameError, DuplicatedEmailError
from appserver.apps.account.endpoints import signup
from appserver.apps.account.models import User


async def test_모든_입력_항목을_유효한_값으로_입력하면_계정이_생성된다(
    client: TestClient,
    db_session: AsyncSession
):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }

    result = await signup(payload, db_session)

    assert isinstance(result, User)
    assert result.username == payload["username"]
    assert result.email == payload["email"]
    assert result.display_name == payload["display_name"]
    assert result.is_host is False

    response = client.get(f"/account/users/{payload['username']}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["display_name"] == payload["display_name"]
    assert data["is_host"] is False


@pytest.mark.parametrize(
    "username",
    [
        "puddingcamppuddingcamppuddingcamppuddingcamppuddingcamp",
        12345678,
        "x",
    ]
)
async def test_사용자명이_유효하지_않으면_사용자명이_유효하지_않다는_메시지를_담은_오류를_일으킨다(
    db_session: AsyncSession,
    username: str
):
    payload = {
        "username": username,
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }

    with pytest.raises(ValidationError):
        await signup(payload, db_session)


async def test_계정_ID가_중복되면_중복_계정_ID_오류를_일으킨다(db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }
    await signup(payload, db_session)

    payload["email"] = "test2@example.com"
    with pytest.raises(DuplicatedUsernameError):
        await signup(payload, db_session)


async def test_e_mail_주소가_중복되면_중복_E_mail_주소_오류를_일으킨다(db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }
    await signup(payload, db_session)

    payload["username"] = "test2"
    with pytest.raises(DuplicatedEmailError):
        await signup(payload, db_session)


async def test_표시명을_입력하지_않으면_무작위_문자열_8글자로_대신한다(db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test테스트1234",
    }

    user = await signup(payload, db_session)
    assert isinstance(user.display_name, str)
    assert len(user.display_name) == 8


async def test_회원가입하면_비밀번호는_해시되어_저장된다(db_session: AsyncSession):
    payload_data = {
        "username": "puddingcamp",
        "display_name": "푸딩캠프",
        "email": "test@example.com",
        "password": "test테스트1234",
        "password_again": "test테스트1234",
    }
    payload = SignupPayload.model_validate(payload_data)

    user = await signup(payload, db_session)

    assert user.hashed_password != payload.password
