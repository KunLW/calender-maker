from __future__ import annotations

import json
from datetime import datetime

from openai import OpenAI

from app.config import Settings
from app.models import AIParsedEvent, CALENDAR_COLORS, CalendarRecord


EVENT_SCHEMA = {
    "name": "calendar_event",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "start": {"type": "string", "format": "date-time"},
            "end": {"type": "string", "format": "date-time"},
            "timezone": {"type": "string"},
            "location": {"type": ["string", "null"]},
            "description": {"type": ["string", "null"]},
            "recommended_calendar_id": {"type": ["integer", "null"]},
            "recommendation_reason": {"type": "string"},
            "recommendation_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "proposed_calendar": {
                "anyOf": [
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "color": {"type": "string", "enum": list(CALENDAR_COLORS)},
                            "description": {"type": "string"},
                        },
                        "required": ["name", "color", "description"],
                    },
                    {"type": "null"},
                ]
            },
        },
        "required": [
            "title",
            "start",
            "end",
            "timezone",
            "location",
            "description",
            "recommended_calendar_id",
            "recommendation_reason",
            "recommendation_confidence",
            "proposed_calendar",
        ],
    },
}

JSON_INSTRUCTIONS = (
    "You convert one natural-language request into one calendar event. "
    "Return only a JSON object with title, start, end, timezone, location, description, "
    "recommended_calendar_id, recommendation_reason, recommendation_confidence, and "
    "proposed_calendar. Times must be ISO 8601 with timezone offsets. Preserve useful context, "
    "participants, links, constraints, reminders, and any inferred duration in description. "
    "If no end time is given, use a sensible duration: meeting 1 hour, meal 1.5 hours, reminder "
    "or task 30 minutes. Do not invent a location. Recommend only an ID from AVAILABLE_CALENDARS. "
    "If none fits with confidence of at least 0.55, set recommended_calendar_id to null and propose "
    "a new calendar with a concise name, one allowed color, and a useful description."
)


class MissingAIConfiguration(RuntimeError):
    pass


def parse_event_text(
    text: str,
    settings: Settings,
    calendars: list[CalendarRecord],
) -> AIParsedEvent:
    provider = get_ai_provider(settings)
    if provider is None:
        raise MissingAIConfiguration(
            "QWEN_API_KEY is not visible to this running service. "
            "Set it before starting uvicorn, or put it in .env."
        )

    now = datetime.now(settings.timezone)
    available = [
        {
            "id": calendar.id,
            "name": calendar.name,
            "color": calendar.color,
            "description": calendar.description,
        }
        for calendar in calendars
    ]
    client = OpenAI(api_key=provider.api_key, base_url=provider.base_url)
    response = client.chat.completions.create(
        model=provider.model,
        response_format=provider.response_format,
        messages=[
            {"role": "system", "content": JSON_INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    f"CURRENT_TIME: {now.isoformat()}\n"
                    f"DEFAULT_TIMEZONE: {settings.app_timezone}\n"
                    f"AVAILABLE_CALENDARS: {json.dumps(available, ensure_ascii=False)}\n"
                    f"USER_INPUT: {text}"
                ),
            },
        ],
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("AI response was empty")
    parsed = AIParsedEvent.model_validate(json.loads(content))
    calendar_ids = {calendar.id for calendar in calendars}
    if parsed.recommended_calendar_id not in calendar_ids:
        parsed.recommended_calendar_id = None
    if parsed.recommended_calendar_id is not None:
        parsed.proposed_calendar = None
    return parsed


class AIProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None,
        response_format: dict,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.response_format = response_format


def get_ai_provider(settings: Settings) -> AIProvider | None:
    qwen_api_key = settings.effective_qwen_api_key
    openai_api_key = settings.effective_openai_api_key
    if qwen_api_key:
        return AIProvider(
            api_key=qwen_api_key,
            model=settings.qwen_model,
            base_url=settings.qwen_base_url,
            response_format={"type": "json_object"},
        )
    if openai_api_key:
        return AIProvider(
            api_key=openai_api_key,
            model=settings.openai_model,
            base_url=None,
            response_format={"type": "json_schema", "json_schema": EVENT_SCHEMA},
        )
    return None
