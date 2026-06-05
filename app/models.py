from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator


class EventStatus(StrEnum):
    pending = "pending"
    confirmed = "confirmed"


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


class EventRecord(ParsedEvent):
    id: int
    calendar_id: int
    uid: str
    source_text: str
    status: EventStatus
    created_at: datetime
    updated_at: datetime


class ParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    calendar_id: int = Field(default=1, ge=1)


class UpdateEventRequest(ParsedEvent):
    pass


class ParseResponse(BaseModel):
    event: EventRecord


class CalendarRecord(BaseModel):
    id: int
    name: str
    token: str
    created_at: datetime
    updated_at: datetime


class CalendarListResponse(BaseModel):
    calendars: list[CalendarRecord]


class CreateCalendarRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name cannot be blank")
        return stripped


class CalendarResponse(BaseModel):
    calendar: CalendarRecord
