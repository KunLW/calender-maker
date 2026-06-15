import json
from datetime import datetime, timezone
from types import SimpleNamespace

from app.ai import get_ai_provider, parse_event_text
from app.config import Settings
from app.models import CalendarRecord


def test_qwen_provider_prefers_system_environment(monkeypatch) -> None:
    monkeypatch.setenv("QWEN_API_KEY", "system-qwen-key")
    settings = Settings(QWEN_API_KEY="$QWEN_API_KEY")

    provider = get_ai_provider(settings)

    assert provider is not None
    assert provider.api_key == "system-qwen-key"


def test_qwen_provider_uses_openai_compatible_settings(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings(QWEN_API_KEY="qwen-key")

    provider = get_ai_provider(settings)

    assert provider is not None
    assert provider.api_key == "qwen-key"
    assert provider.model == "qwen-plus"
    assert provider.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert provider.response_format == {"type": "json_object"}


def test_openai_provider_is_fallback(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings(QWEN_API_KEY="", OPENAI_API_KEY="openai-key")

    provider = get_ai_provider(settings)

    assert provider is not None
    assert provider.api_key == "openai-key"
    assert provider.model == "gpt-4.1-mini"
    assert provider.base_url is None
    assert provider.response_format["type"] == "json_schema"


def test_placeholder_api_key_is_ignored(monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings(QWEN_API_KEY="$QWEN_API_KEY", OPENAI_API_KEY="")

    provider = get_ai_provider(settings)

    assert provider is None


def test_ai_recommendation_is_limited_to_user_calendars(monkeypatch) -> None:
    settings = Settings(QWEN_API_KEY="qwen-key")
    calendar = CalendarRecord(
        id=4,
        user_id=2,
        name="Work",
        color="#2563eb",
        description="Meetings and deadlines",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    payload = {
        "title": "Team sync",
        "start": "2026-06-16T10:00:00+08:00",
        "end": "2026-06-16T11:00:00+08:00",
        "timezone": "Asia/Shanghai",
        "location": None,
        "description": "Weekly team sync",
        "recommended_calendar_id": 999,
        "recommendation_reason": "Work meeting",
        "recommendation_confidence": 0.9,
        "proposed_calendar": None,
    }

    class FakeCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
            )

    monkeypatch.setattr(
        "app.ai.OpenAI",
        lambda **kwargs: SimpleNamespace(
            chat=SimpleNamespace(completions=FakeCompletions())
        ),
    )

    parsed = parse_event_text("team sync", settings, [calendar])

    assert parsed.recommended_calendar_id is None
