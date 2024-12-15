from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from fastapi import status
from appserver.apps.account.models import User


async def test_회원탈퇴_시_유저가_삭제되어야_한다(
    client_with_auth: TestClient,
    host_user: User,
    db_session: AsyncSession,
):
    user_id = host_user.id

    assert await db_session.get(User, user_id) is not None

    response = client_with_auth.delete("/account/unregister")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await db_session.get(User, user_id) is None
