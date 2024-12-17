from fastapi import status
from fastapi.testclient import TestClient
import pytest

from appserver.apps.account.models import User
from appserver.apps.calendar.models import Calendar
from appserver.apps.calendar.schemas import CalendarDetailOut, CalendarOut
from appserver.libs.collections.sort import deduplicate_and_sort


@pytest.mark.parametrize("user_key, expected_type", [
    ("host_user", CalendarDetailOut),
    ("guest_user", CalendarOut),
    (None, CalendarOut),
])
async def test_호스트인_사용자의_username_으로_캘린더_정보를_가져온다(
    user_key: str | None,
    expected_type: type[CalendarOut | CalendarDetailOut],
    host_user: User,
    host_user_calendar: Calendar,
    client: TestClient,
    client_with_auth: TestClient,
) -> CalendarOut | CalendarDetailOut:
    clients = {
        "host_user": client_with_auth,
        "guest_user": client,
        None: client,
    }
    user_client = clients[user_key]

    response = user_client.get(f"/calendar/{host_user.username}")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK

    expected_obj = expected_type.model_validate(result)

    assert expected_obj.topics == host_user_calendar.topics
    assert expected_obj.description == host_user_calendar.description
    if isinstance(expected_obj, CalendarDetailOut):
        assert expected_obj.google_calendar_id == host_user_calendar.google_calendar_id


async def test_존재하지_않는_사용자의_username_으로_캘린더_정보를_가져오려_하면_404_응답을_반환한다(
    client: TestClient,
) -> None:
    response = client.get("/calendar/not_exist_user")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_호스트가_아닌_사용자의_username_으로_캘린더_정보를_가져오려_하면_404_응답을_반환한다(
    guest_user: User,
    client: TestClient,
) -> None:
    response = client.get(f"/calendar/{guest_user.username}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_호스트_사용자는_유효한_캘린더_정보를_제출하여_캘린더를_생성할_수_있다(
    host_user: User,
    client_with_auth: TestClient,
) -> None:
    google_calendar_id = "valid_google_calendar_id@group.calendar.google.com"

    payload = {
        "topics": ["topic2", "topic1", "topic2"],
        "description": "description",
        "google_calendar_id": google_calendar_id,
    }

    response = client_with_auth.post("/calendar", json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["host_id"] == host_user.id
    assert result["topics"] == ["topic2", "topic1"]
    assert result["description"] == payload["description"]
    assert result["google_calendar_id"] == payload["google_calendar_id"]


async def test_캘린더가_있는_상황에서_추가_생성하려_하면_422_응답을_반환한다(
    client_with_auth: TestClient,
) -> None:
    google_calendar_id = "valid_google_calendar_id@group.calendar.google.com"

    payload = {
        "topics": ["topic2", "topic1", "topic2"],
        "description": "description",
        "google_calendar_id": google_calendar_id,
    }
    response = client_with_auth.post("/calendar", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    response = client_with_auth.post("/calendar", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_게스트_사용자가_캘린더를_생성하려_하면_422_응답을_반환한다(
    client_with_guest_auth: TestClient,
) -> None:
    google_calendar_id = "valid_google_calendar_id@group.calendar.google.com"

    payload = {
        "topics": ["topic2", "topic1", "topic2"],
        "description": "description",
        "google_calendar_id": google_calendar_id,
    }
    response = client_with_guest_auth.post("/calendar", json=payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN



UPDATABLE_FIELDS = frozenset(["topics", "description", "google_calendar_id"])

@pytest.mark.parametrize("payload", [
    {"topics": ["topic2", "topic1", "topic2"]},
    {"description": "문자열 길이가 10자 이상인 설명입니다."},
    {"google_calendar_id": "invalid_google_calendar_id@group.calendar.google.com"},
    {"topics": ["topic2", "topic1", "topic2"], "description": "문자열 길이가 10자 이상인 설명입니다.", "google_calendar_id": "invalid_google_calendar_id@group.calendar.google.com"},
])
async def test_사용자가_변경하는_항목만_변경되고_나머지는_기존_값을_유지한다(
    client_with_auth: TestClient,
    host_user_calendar: Calendar,
    payload: dict,
) -> None:
    before_data = host_user_calendar.model_dump()

    response = client_with_auth.patch("/calendar", json=payload)
    assert response.status_code == status.HTTP_200_OK

    response = client_with_auth.get(f"/calendar/{host_user_calendar.host.username}")
    data = response.json()

    # 변경된 항목은 변경된 값으로 변경되어야 한다.
    for key, value in payload.items():
        if key == "topics":
            assert data[key] == deduplicate_and_sort(value)
        else:
            assert data[key] == value

    # 변경되지 않은 항목은 기존 값을 유지한다.
    for key in UPDATABLE_FIELDS - frozenset(payload.keys()):
        assert data[key] == before_data[key]
