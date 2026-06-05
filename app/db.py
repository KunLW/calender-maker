from __future__ import annotations

import sqlite3
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.models import CalendarRecord, EventRecord, EventStatus, ParsedEvent


SCHEMA = """
CREATE TABLE IF NOT EXISTS calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calendar_id INTEGER NOT NULL DEFAULT 1,
    uid TEXT NOT NULL UNIQUE,
    source_text TEXT NOT NULL,
    title TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    timezone TEXT NOT NULL,
    location TEXT,
    description TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (calendar_id) REFERENCES calendars(id)
);
"""


class EventStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)

    def connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            ensure_calendar_schema(conn)
            ensure_default_calendar(conn)

    def sync_default_calendar(self, name: str, token: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE calendars
                SET name = ?, token = ?, updated_at = ?
                WHERE id = 1
                """,
                (name, token, now),
            )

    def create_calendar(self, name: str) -> CalendarRecord:
        now = datetime.now(timezone.utc).isoformat()
        token = secrets.token_urlsafe(24)
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO calendars (name, token, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, token, now, now),
            )
            calendar_id = int(cursor.lastrowid)
        record = self.get_calendar(calendar_id)
        if record is None:
            raise RuntimeError("created calendar could not be loaded")
        return record

    def list_calendars(self) -> list[CalendarRecord]:
        with self.connect() as conn:
            rows: Iterable[sqlite3.Row] = conn.execute(
                "SELECT * FROM calendars ORDER BY id ASC",
            ).fetchall()
        return [row_to_calendar(row) for row in rows]

    def get_calendar(self, calendar_id: int) -> CalendarRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM calendars WHERE id = ?", (calendar_id,)).fetchone()
        return row_to_calendar(row) if row else None

    def find_calendar_by_token(self, calendar_id: int, token: str) -> CalendarRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM calendars WHERE id = ? AND token = ?",
                (calendar_id, token),
            ).fetchone()
        return row_to_calendar(row) if row else None

    def create_pending(self, source_text: str, event: ParsedEvent, calendar_id: int) -> EventRecord:
        now = datetime.now(timezone.utc).isoformat()
        uid = f"{uuid.uuid4()}@calendar-maker"
        with self.connect() as conn:
            calendar = conn.execute("SELECT id FROM calendars WHERE id = ?", (calendar_id,)).fetchone()
            if calendar is None:
                raise ValueError("calendar not found")
            cursor = conn.execute(
                """
                INSERT INTO events (
                    calendar_id, uid, source_text, title, start, end, timezone,
                    location, description, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    calendar_id,
                    uid,
                    source_text,
                    event.title,
                    event.start.isoformat(),
                    event.end.isoformat(),
                    event.timezone,
                    event.location,
                    event.description,
                    EventStatus.pending.value,
                    now,
                    now,
                ),
            )
            event_id = int(cursor.lastrowid)
        record = self.get(event_id)
        if record is None:
            raise RuntimeError("created event could not be loaded")
        return record

    def get(self, event_id: int) -> EventRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        return row_to_event(row) if row else None

    def confirm(self, event_id: int) -> EventRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                "UPDATE events SET status = ?, updated_at = ? WHERE id = ?",
                (EventStatus.confirmed.value, now, event_id),
            )
        return self.get(event_id)

    def update_and_confirm(self, event_id: int, event: ParsedEvent) -> EventRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE events
                SET title = ?, start = ?, end = ?, timezone = ?, location = ?,
                    description = ?, status = ?, updated_at = ?
                WHERE id = ? AND status = ?
                """,
                (
                    event.title,
                    event.start.isoformat(),
                    event.end.isoformat(),
                    event.timezone,
                    event.location,
                    event.description,
                    EventStatus.confirmed.value,
                    now,
                    event_id,
                    EventStatus.pending.value,
                ),
            )
            if cursor.rowcount == 0:
                return None
        return self.get(event_id)

    def confirmed_events(self, calendar_id: int | None = None) -> list[EventRecord]:
        with self.connect() as conn:
            if calendar_id is None:
                rows: Iterable[sqlite3.Row] = conn.execute(
                    "SELECT * FROM events WHERE status = ? ORDER BY start ASC, id ASC",
                    (EventStatus.confirmed.value,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM events
                    WHERE status = ? AND calendar_id = ?
                    ORDER BY start ASC, id ASC
                    """,
                    (EventStatus.confirmed.value, calendar_id),
                ).fetchall()
        return [row_to_event(row) for row in rows]


def ensure_calendar_schema(conn: sqlite3.Connection) -> None:
    event_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(events)").fetchall()
    }
    if "calendar_id" not in event_columns:
        conn.execute("ALTER TABLE events ADD COLUMN calendar_id INTEGER NOT NULL DEFAULT 1")


def ensure_default_calendar(conn: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    row = conn.execute("SELECT id FROM calendars WHERE id = 1").fetchone()
    if row is None:
        conn.execute(
            """
            INSERT INTO calendars (id, name, token, created_at, updated_at)
            VALUES (1, ?, ?, ?, ?)
            """,
            ("AI Calendar", "change-me", now, now),
        )


def row_to_calendar(row: sqlite3.Row) -> CalendarRecord:
    return CalendarRecord(
        id=row["id"],
        name=row["name"],
        token=row["token"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def row_to_event(row: sqlite3.Row) -> EventRecord:
    return EventRecord(
        id=row["id"],
        calendar_id=row["calendar_id"],
        uid=row["uid"],
        source_text=row["source_text"],
        title=row["title"],
        start=datetime.fromisoformat(row["start"]),
        end=datetime.fromisoformat(row["end"]),
        timezone=row["timezone"],
        location=row["location"],
        description=row["description"],
        status=EventStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
