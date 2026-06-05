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
                json={"text": "明天下午三点开会", "calendar_id": 1},
            )
            assert parsed.status_code == 200
            parsed_event = parsed.json()["event"]
            event_id = parsed_event["id"]

            confirmed = client.post(
                f"/api/events/{event_id}/confirm",
                headers={"X-App-Token": "app-secret"},
                json={
                    "title": "修改后的会议",
                    "start": parsed_event["start"],
                    "end": parsed_event["end"],
                    "timezone": parsed_event["timezone"],
                    "location": "会议室 A",
                    "description": "保留更完整的备注",
                },
            )
            assert confirmed.status_code == 200
            assert confirmed.json()["event"]["status"] == "confirmed"
            assert confirmed.json()["event"]["title"] == "修改后的会议"

            duplicate = client.post(
                f"/api/events/{event_id}/confirm",
                headers={"X-App-Token": "app-secret"},
                json={
                    "title": "不应再次添加",
                    "start": parsed_event["start"],
                    "end": parsed_event["end"],
                    "timezone": parsed_event["timezone"],
                    "location": "会议室 B",
                    "description": "重复提交",
                },
            )
            assert duplicate.status_code == 409
            assert duplicate.json()["detail"] == "event already confirmed"

            feed = client.get("/calendar.ics?token=calendar-secret")
            assert feed.status_code == 200
            assert "SUMMARY:修改后的会议" in feed.text
            assert "SUMMARY:不应再次添加" not in feed.text
            assert "DESCRIPTION:保留更完整的备注" in feed.text
    finally:
        main.app.dependency_overrides.clear()


def test_can_create_calendar_and_subscribe_to_its_feed(tmp_path, monkeypatch) -> None:
    settings = Settings(
        DATABASE_PATH=str(tmp_path / "calendar.db"),
        CALENDAR_TOKEN="calendar-secret",
        APP_TOKEN="app-secret",
        OPENAI_API_KEY="test-key",
    )
    store = EventStore(settings.database_path)
    store.init()

    def fake_parse_event_text(text: str, settings: Settings) -> ParsedEvent:
        start = datetime(2026, 6, 6, 9, 0, tzinfo=settings.timezone)
        return ParsedEvent(
            title="家庭早餐",
            start=start,
            end=start + timedelta(hours=1),
            timezone=settings.app_timezone,
            location="家",
            description=text,
        )

    monkeypatch.setattr(main, "parse_event_text", fake_parse_event_text)
    main.app.dependency_overrides[main.get_settings] = lambda: settings
    main.app.dependency_overrides[main.get_store] = lambda: store

    try:
        with TestClient(main.app) as client:
            created = client.post(
                "/api/calendars",
                headers={"X-App-Token": "app-secret"},
                json={"name": "家庭"},
            )
            assert created.status_code == 200
            calendar = created.json()["calendar"]

            listed = client.get("/api/calendars", headers={"X-App-Token": "app-secret"})
            assert listed.status_code == 200
            assert [item["name"] for item in listed.json()["calendars"]] == ["AI Calendar", "家庭"]

            parsed = client.post(
                "/api/parse",
                headers={"X-App-Token": "app-secret"},
                json={"text": "周六早上家庭早餐", "calendar_id": calendar["id"]},
            )
            assert parsed.status_code == 200
            event = parsed.json()["event"]
            assert event["calendar_id"] == calendar["id"]

            confirmed = client.post(
                f"/api/events/{event['id']}/confirm",
                headers={"X-App-Token": "app-secret"},
                json={
                    "title": event["title"],
                    "start": event["start"],
                    "end": event["end"],
                    "timezone": event["timezone"],
                    "location": event["location"],
                    "description": event["description"],
                },
            )
            assert confirmed.status_code == 200

            default_feed = client.get("/calendar.ics?token=calendar-secret")
            assert default_feed.status_code == 200
            assert "SUMMARY:家庭早餐" not in default_feed.text

            custom_feed = client.get(
                f"/calendars/{calendar['id']}.ics?token={calendar['token']}"
            )
            assert custom_feed.status_code == 200
            assert "X-WR-CALNAME:家庭" in custom_feed.text
            assert "SUMMARY:家庭早餐" in custom_feed.text
    finally:
        main.app.dependency_overrides.clear()


def test_config_status_reports_qwen_environment(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("QWEN_API_KEY", "system-qwen-key")
    settings = Settings(
        DATABASE_PATH=str(tmp_path / "calendar.db"),
        CALENDAR_TOKEN="calendar-secret",
        QWEN_API_KEY="$QWEN_API_KEY",
    )
    store = EventStore(settings.database_path)
    store.init()
    main.app.dependency_overrides[main.get_settings] = lambda: settings
    main.app.dependency_overrides[main.get_store] = lambda: store

    try:
        with TestClient(main.app) as client:
            response = client.get("/api/config/status")
            assert response.status_code == 200
            assert response.json() == {
                "ai_provider": "qwen",
                "api_key_configured": True,
                "model": "qwen-plus",
            }
    finally:
        main.app.dependency_overrides.clear()


def test_config_status_reports_missing_key(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings(
        DATABASE_PATH=str(tmp_path / "calendar.db"),
        CALENDAR_TOKEN="calendar-secret",
        QWEN_API_KEY="$QWEN_API_KEY",
        OPENAI_API_KEY="",
    )
    store = EventStore(settings.database_path)
    store.init()
    main.app.dependency_overrides[main.get_settings] = lambda: settings
    main.app.dependency_overrides[main.get_store] = lambda: store

    try:
        with TestClient(main.app) as client:
            response = client.get("/api/config/status")
            assert response.status_code == 200
            assert response.json() == {
                "ai_provider": None,
                "api_key_configured": False,
                "model": None,
            }
    finally:
        main.app.dependency_overrides.clear()
