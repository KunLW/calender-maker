from __future__ import annotations

import json
from datetime import datetime

from openai import OpenAI

from app.config import Settings
from app.models import ParsedEvent


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
        },
        "required": ["title", "start", "end", "timezone", "location", "description"],
    },
}


class MissingAIConfiguration(RuntimeError):
    pass


def parse_event_text(text: str, settings: Settings) -> ParsedEvent:
    if not settings.openai_api_key:
        raise MissingAIConfiguration("OPENAI_API_KEY is not configured")

    now = datetime.now(settings.timezone)
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_schema", "json_schema": EVENT_SCHEMA},
        messages=[
            {
                "role": "system",
                "content": (
                    "你是日历事件解析器。只抽取用户明确表达或强烈暗示的单个日程。"
                    "返回 JSON 必须符合 schema。时间必须带时区偏移。"
                    "如果用户没有说结束时间，根据事件类型选择合理默认时长：会议 1 小时，吃饭 1.5 小时，"
                    "提醒/待办 30 分钟。不要编造地点。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"当前时间：{now.isoformat()}\n"
                    f"默认时区：{settings.app_timezone}\n"
                    f"用户输入：{text}"
                ),
            },
        ],
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("AI response was empty")
    return ParsedEvent.model_validate(json.loads(content))

