from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.models import EventRecord, EventStatus, ParsedEvent


SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    updated_at TEXT NOT NULL
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

    def create_pending(self, source_text: str, event: ParsedEvent) -> EventRecord:
        now = datetime.now(timezone.utc).isoformat()
        uid = f"{uuid.uuid4()}@calendar-maker"
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (
                    uid, source_text, title, start, end, timezone,
                    location, description, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
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

    def confirmed_events(self) -> list[EventRecord]:
        with self.connect() as conn:
            rows: Iterable[sqlite3.Row] = conn.execute(
                "SELECT * FROM events WHERE status = ? ORDER BY start ASC, id ASC",
                (EventStatus.confirmed.value,),
            ).fetchall()
        return [row_to_event(row) for row in rows]


def row_to_event(row: sqlite3.Row) -> EventRecord:
    return EventRecord(
        id=row["id"],
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
