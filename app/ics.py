from __future__ import annotations

from datetime import datetime, timezone

from app.models import EventRecord


def build_calendar(events: list[EventRecord], calendar_name: str) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Calendar Maker//AI Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_text(calendar_name)}",
    ]

    for event in events:
        lines.extend(build_event(event))

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def build_event(event: EventRecord) -> list[str]:
    lines = [
        "BEGIN:VEVENT",
        f"UID:{escape_text(event.uid)}",
        f"DTSTAMP:{format_utc(event.updated_at)}",
        f"DTSTART:{format_utc(event.start)}",
        f"DTEND:{format_utc(event.end)}",
        f"SUMMARY:{escape_text(event.title)}",
    ]
    if event.location:
        lines.append(f"LOCATION:{escape_text(event.location)}")
    description = event.description or event.source_text
    if description:
        lines.append(f"DESCRIPTION:{escape_text(description)}")
    lines.append("END:VEVENT")
    return lines


def format_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\r", "")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )

