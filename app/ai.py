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

JSON_INSTRUCTIONS = (
    "你是日历事件解析器。只抽取用户明确表达或强烈暗示的单个日程。"
    "必须返回 JSON，且只能返回 JSON 对象，不要返回 Markdown。"
    "JSON 字段必须是：title, start, end, timezone, location, description。"
    "start 和 end 必须是带时区偏移的 ISO 8601 date-time 字符串。"
    "location 和 description 不存在时返回 null。"
    "如果用户没有说结束时间，根据事件类型选择合理默认时长：会议 1 小时，吃饭 1.5 小时，"
    "提醒/待办 30 分钟。不要编造地点。"
)


class MissingAIConfiguration(RuntimeError):
    pass


def parse_event_text(text: str, settings: Settings) -> ParsedEvent:
    provider = get_ai_provider(settings)
    if provider is None:
        raise MissingAIConfiguration("QWEN_API_KEY or OPENAI_API_KEY is not configured")

    now = datetime.now(settings.timezone)
    client = OpenAI(api_key=provider.api_key, base_url=provider.base_url)
    response = client.chat.completions.create(
        model=provider.model,
        response_format=provider.response_format,
        messages=[
            {
                "role": "system",
                "content": JSON_INSTRUCTIONS,
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
    if settings.qwen_api_key:
        return AIProvider(
            api_key=settings.qwen_api_key,
            model=settings.qwen_model,
            base_url=settings.qwen_base_url,
            response_format={"type": "json_object"},
        )
    if settings.openai_api_key:
        return AIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=None,
            response_format={"type": "json_schema", "json_schema": EVENT_SCHEMA},
        )
    return None
