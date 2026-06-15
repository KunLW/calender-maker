from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


CALENDAR_COLORS = (
    "#2563eb",
    "#0f766e",
    "#7c3aed",
    "#be123c",
    "#b45309",
    "#4d7c0f",
    "#0369a1",
    "#6b7280",
)


class EventStatus(StrEnum):
    pending = "pending"
    confirmed = "confirmed"


class UserRecord(BaseModel):
    id: int
    email: str
    all_feed_token: str
    created_at: datetime
    updated_at: datetime


class UserPublic(BaseModel):
    id: int
    email: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)
    invite_code: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class AuthResponse(BaseModel):
    user: UserPublic


class ParsedEvent(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    start: datetime
    end: datetime
    timezone: str = Field(default="Asia/Shanghai", min_length=1)
    location: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        return stripped

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "ParsedEvent":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class ProposedCalendar(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str
    description: str = Field(default="", max_length=500)

    @field_validator("color")
    @classmethod
    def color_must_be_supported(cls, value: str) -> str:
        if value not in CALENDAR_COLORS:
            raise ValueError("unsupported calendar color")
        return value


class AIParsedEvent(ParsedEvent):
    recommended_calendar_id: int | None = None
    recommendation_reason: str = Field(default="", max_length=500)
    recommendation_confidence: float = Field(default=0, ge=0, le=1)
    proposed_calendar: ProposedCalendar | None = None


class EventRecord(ParsedEvent):
    id: int
    user_id: int
    calendar_id: int
    uid: str
    source_text: str
    status: EventStatus
    created_at: datetime
    updated_at: datetime


class ParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    preferred_calendar_id: int | None = Field(default=None, ge=1)


class UpdateEventRequest(ParsedEvent):
    calendar_id: int = Field(ge=1)


class ParseResponse(BaseModel):
    event: EventRecord
    recommended_calendar_id: int | None
    recommendation_reason: str
    recommendation_confidence: float
    proposed_calendar: ProposedCalendar | None


class CalendarRecord(BaseModel):
    id: int
    user_id: int
    name: str
    color: str
    description: str
    token: str | None = None
    created_at: datetime
    updated_at: datetime


class CalendarListResponse(BaseModel):
    calendars: list[CalendarRecord]


class CreateCalendarRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str = CALENDAR_COLORS[0]
    description: str = Field(default="", max_length=500)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name cannot be blank")
        return stripped

    @field_validator("color")
    @classmethod
    def color_must_be_supported(cls, value: str) -> str:
        if value not in CALENDAR_COLORS:
            raise ValueError("unsupported calendar color")
        return value


class UpdateCalendarRequest(CreateCalendarRequest):
    pass


class CalendarResponse(BaseModel):
    calendar: CalendarRecord


class AgendaResponse(BaseModel):
    events: list[EventRecord]


class SubscriptionResponse(BaseModel):
    https_url: str
    webcal_url: str

