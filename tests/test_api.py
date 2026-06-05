from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import app.main as main
from app.config import Settings
from app.db import EventStore
from app.models import ParsedEvent


def test_parse_confirm_and_calendar_feed(tmp_path, monkeypatch) -> None:
    settings = Settings(
        DATABASE_PATH=str(tmp_path / "calendar.db"),
        CALENDAR_TOKEN="calendar-secret",
        APP_TOKEN="app-secret",
        OPENAI_API_KEY="test-key",
    )
    store = EventStore(settings.database_path)
    store.init()

    def fake_parse_event_text(text: str, settings: Settings) -> ParsedEvent:
        start = datetime(2026, 6, 5, 15, 0, tzinfo=settings.timezone)
        return ParsedEvent(
            title="测试会议",
            start=start,
            end=start + timedelta(hours=1),
            timezone=settings.app_timezone,
            location="线上",
            description=text,
        )

    monkeypatch.setattr(main, "parse_event_text", fake_parse_event_text)
    main.app.dependency_overrides[main.get_settings] = lambda: settings
    main.app.dependency_overrides[main.get_store] = lambda: store

    try:
        with TestClient(main.app) as client:
            unauthorized = client.post("/api/parse", json={"text": "明天下午三点开会"})
            assert unauthorized.status_code == 401

            parsed = client.post(
                "/api/parse",
                headers={"X-App-Token": "app-secret"},
                json={"text": "明天下午三点开会"},
            )
            assert parsed.status_code == 200
            event_id = parsed.json()["event"]["id"]

            confirmed = client.post(
                f"/api/events/{event_id}/confirm",
                headers={"X-App-Token": "app-secret"},
            )
            assert confirmed.status_code == 200
            assert confirmed.json()["event"]["status"] == "confirmed"

            feed = client.get("/calendar.ics?token=calendar-secret")
            assert feed.status_code == 200
            assert "SUMMARY:测试会议" in feed.text
    finally:
        main.app.dependency_overrides.clear()

