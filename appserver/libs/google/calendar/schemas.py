from sqlmodel import SQLModel

from typing import Literal, Optional, Sequence, TypedDict


class ReminderItem(SQLModel):
    method: Literal["email", "popup"]
    minutes: int


class Reminder(SQLModel):
    useDefault: bool
    overrides: Sequence[ReminderItem]


class NotificationSettingItem(SQLModel):
    type: Literal["eventCreation", "eventChange", "eventCancellation", "eventResponse"]
    method: Literal["email", "popup"]


class NotificationSetting(SQLModel):
    notifications: Sequence[NotificationSettingItem]


class CalendarItem(SQLModel):
    kind: str
    etag: str
    id: str
    summary: str
    timeZone: str
    colorId: str
    backgroundColor: str
    foregroundColor: str
    selected: bool
    accessRole: Literal["owner", "reader"]
    defaultReminders: Sequence[ReminderItem]
    notificationSettings: NotificationSetting
    primary: bool
    conferenceProperties: dict


class CalendarList(SQLModel):
    kind: str
    etag: str
    nextSyncToken: str
    items: Sequence[CalendarItem]


class EventAttendee(SQLModel):
    email: str
    responseStatus: Literal["accepted", "declined", "needsAction", "tentative"]
    displayName: Optional[str]
    organizer: Optional[bool]
    self: Optional[bool]


class EventCreator(SQLModel):
    email: str


class EventStartEnd(SQLModel):
    dateTime: str
    timeZone: str


class EventOrganizer(SQLModel):
    displayName: str
    email: str
    self: bool


class CalendarEvent(SQLModel):
    attendees: list[EventAttendee]
    created: str  # ISO 8601
    creator: EventCreator
    description: str
    end: EventStartEnd
    etag: str
    eventType: str
    htmlLink: str
    iCalUID: str
    id: str
    kind: str
    location: str
    organizer: EventOrganizer
    reminders: Reminder
    sequence: int
    start: EventStartEnd
    status: Literal["confirmed", "tentative", "cancelled"]
    summary: str
    updated: str  # ISO 8601


