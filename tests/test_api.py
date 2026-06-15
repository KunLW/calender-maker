from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import app.main as main
from app.config import Settings
from app.db import EventStore
from app.models import AIParsedEvent


def make_app(tmp_path, monkeypatch):
    settings = Settings(
        DATABASE_PATH=str(tmp_path / "calendar.db"),
        CANONICAL_ORIGIN="https://quantumman.tech",
        SESSION_COOKIE_SECURE=False,
        QWEN_API_KEY="test-key",
    )
    store = EventStore(settings.database_path)
    store.init()

    def fake_parse(text, settings, calendars):
        start = datetime(2026, 6, 16, 10, 0, tzinfo=settings.timezone)
        return AIParsedEvent(
            title="Team sync",
            start=start,
            end=start + timedelta(hours=1),
            timezone=settings.app_timezone,
            location="Meeting room",
            description=text,
            recommended_calendar_id=calendars[0].id,
            recommendation_reason="This is a work meeting",
            recommendation_confidence=0.92,
            proposed_calendar=None,
        )

    monkeypatch.setattr(main, "parse_event_text", fake_parse)
    main.app.dependency_overrides[main.get_settings] = lambda: settings
    main.app.dependency_overrides[main.get_store] = lambda: store
    return settings, store


def register(client: TestClient, store: EventStore, email: str) -> dict:
    invite = store.create_invite()
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "strong-password",
            "invite_code": invite,
        },
    )
    assert response.status_code == 200
    return response.json()["user"]


def teardown_app() -> None:
    main.app.dependency_overrides.clear()


def test_registration_parse_confirm_agenda_and_feeds(tmp_path, monkeypatch) -> None:
    _, store = make_app(tmp_path, monkeypatch)
    try:
        with TestClient(main.app) as client:
            user = register(client, store, "owner@example.com")
            calendars = client.get("/api/calendars").json()["calendars"]
            calendar = calendars[0]
            assert calendar["token"] is None

            parsed = client.post(
                "/api/parse",
                json={"text": "team sync tomorrow", "preferred_calendar_id": None},
            )
            assert parsed.status_code == 200
            payload = parsed.json()
            assert payload["recommended_calendar_id"] == calendar["id"]
            event = payload["event"]

            confirmed = client.post(
                f"/api/events/{event['id']}/confirm",
                json={
                    "calendar_id": calendar["id"],
                    "title": "Edited team sync",
                    "start": event["start"],
                    "end": event["end"],
                    "timezone": event["timezone"],
                    "location": event["location"],
                    "description": "Detailed notes",
                },
            )
            assert confirmed.status_code == 200
            assert confirmed.json()["event"]["status"] == "confirmed"

            duplicate = client.post(
                f"/api/events/{event['id']}/confirm",
                json={
                    "calendar_id": calendar["id"],
                    "title": "Duplicate",
                    "start": event["start"],
                    "end": event["end"],
                    "timezone": event["timezone"],
                    "location": None,
                    "description": None,
                },
            )
            assert duplicate.status_code == 409

            agenda = client.get("/api/agenda?include_past=true")
            assert agenda.status_code == 200
            assert agenda.json()["events"][0]["title"] == "Edited team sync"

            subscription = client.get(
                f"/api/calendars/{calendar['id']}/subscription"
            ).json()
            assert subscription["https_url"].startswith(
                f"https://quantumman.tech/calendars/{calendar['id']}.ics?token="
            )
            assert subscription["webcal_url"].startswith(
                f"webcal://quantumman.tech/calendars/{calendar['id']}.ics?token="
            )
            token = subscription["https_url"].split("token=", 1)[1]
            feed = client.get(f"/calendars/{calendar['id']}.ics?token={token}")
            assert "SUMMARY:Edited team sync" in feed.text

            combined = client.get("/api/feeds/all/subscription").json()
            all_token = combined["https_url"].split("token=", 1)[1]
            all_feed = client.get(f"/feeds/all.ics?token={all_token}")
            assert "SUMMARY:Edited team sync" in all_feed.text
            assert user["email"] == "owner@example.com"
    finally:
        teardown_app()


def test_users_are_isolated_and_can_edit_delete_own_events(tmp_path, monkeypatch) -> None:
    _, store = make_app(tmp_path, monkeypatch)
    try:
        with TestClient(main.app) as first, TestClient(main.app) as second:
            register(first, store, "first@example.com")
            first_calendar = first.get("/api/calendars").json()["calendars"][0]
            parsed = first.post(
                "/api/parse",
                json={"text": "private event"},
            ).json()["event"]

            register(second, store, "second@example.com")
            assert second.patch(
                f"/api/events/{parsed['id']}",
                json={
                    "calendar_id": first_calendar["id"],
                    "title": "Stolen",
                    "start": parsed["start"],
                    "end": parsed["end"],
                    "timezone": parsed["timezone"],
                    "location": None,
                    "description": None,
                },
            ).status_code == 404
            assert second.delete(f"/api/events/{parsed['id']}").status_code == 404

            confirmed = first.post(
                f"/api/events/{parsed['id']}/confirm",
                json={
                    "calendar_id": first_calendar["id"],
                    "title": parsed["title"],
                    "start": parsed["start"],
                    "end": parsed["end"],
                    "timezone": parsed["timezone"],
                    "location": parsed["location"],
                    "description": parsed["description"],
                },
            )
            assert confirmed.status_code == 200
            edited = first.patch(
                f"/api/events/{parsed['id']}",
                json={
                    "calendar_id": first_calendar["id"],
                    "title": "Updated title",
                    "start": parsed["start"],
                    "end": parsed["end"],
                    "timezone": parsed["timezone"],
                    "location": None,
                    "description": None,
                },
            )
            assert edited.status_code == 200
            assert first.delete(f"/api/events/{parsed['id']}").status_code == 204
    finally:
        teardown_app()


def test_token_regeneration_invalidates_old_feed(tmp_path, monkeypatch) -> None:
    _, store = make_app(tmp_path, monkeypatch)
    try:
        with TestClient(main.app) as client:
            register(client, store, "owner@example.com")
            calendar = client.get("/api/calendars").json()["calendars"][0]
            old_url = client.get(
                f"/api/calendars/{calendar['id']}/subscription"
            ).json()["https_url"]
            old_token = old_url.split("token=", 1)[1]

            regenerated = client.post(
                f"/api/calendars/{calendar['id']}/regenerate-token"
            )
            assert regenerated.status_code == 200
            assert client.get(
                f"/calendars/{calendar['id']}.ics?token={old_token}"
            ).status_code == 401
    finally:
        teardown_app()

