from __future__ import annotations

import hashlib
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from app.models import (
    CALENDAR_COLORS,
    CalendarRecord,
    EventRecord,
    EventStatus,
    ParsedEvent,
    UserRecord,
)


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    all_feed_token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invite_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL UNIQUE,
    used_by_user_id INTEGER,
    used_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (used_by_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS calendars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#2563eb',
    description TEXT NOT NULL DEFAULT '',
    token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_calendars_user ON calendars(user_id);
CREATE INDEX IF NOT EXISTS idx_events_user_start ON events(user_id, start);
CREATE INDEX IF NOT EXISTS idx_events_calendar_status ON events(calendar_id, status);
"""


class EventStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)

    def connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            migrate_legacy_schema(conn)
            conn.executescript(SCHEMA)
            ensure_default_legacy_calendar(conn)
            conn.execute(
                "DELETE FROM sessions WHERE expires_at <= ?",
                (datetime.now(timezone.utc).isoformat(),),
            )

    def create_invite(self) -> str:
        code = secrets.token_urlsafe(18)
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO invite_codes (code_hash, created_at) VALUES (?, ?)",
                (sha256(code), now),
            )
        return code

    def register_user(self, email: str, password_hash: str, invite_code: str) -> UserRecord:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            invite = conn.execute(
                "SELECT * FROM invite_codes WHERE code_hash = ? AND used_at IS NULL",
                (sha256(invite_code),),
            ).fetchone()
            if invite is None:
                raise ValueError("invalid or used invite code")
            if conn.execute(
                "SELECT 1 FROM users WHERE email = ? COLLATE NOCASE",
                (email,),
            ).fetchone():
                raise ValueError("email already registered")
            cursor = conn.execute(
                """
                INSERT INTO users (
                    email, password_hash, all_feed_token, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (email.lower(), password_hash, secrets.token_urlsafe(24), now, now),
            )
            user_id = int(cursor.lastrowid)
            conn.execute(
                "UPDATE invite_codes SET used_by_user_id = ?, used_at = ? WHERE id = ?",
                (user_id, now, invite["id"]),
            )
            claimed = conn.execute(
                "UPDATE calendars SET user_id = ? WHERE user_id IS NULL",
                (user_id,),
            ).rowcount
            conn.execute(
                "UPDATE events SET user_id = ? WHERE user_id IS NULL",
                (user_id,),
            )
            if claimed == 0:
                self._create_calendar_conn(
                    conn,
                    user_id,
                    "My Calendar",
                    CALENDAR_COLORS[0],
                    "Default personal calendar",
                )
        user = self.get_user(user_id)
        if user is None:
            raise RuntimeError("created user could not be loaded")
        return user

    def get_user(self, user_id: int) -> UserRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return row_to_user(row) if row else None

    def get_user_credentials(self, email: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
                (email,),
            ).fetchone()

    def create_session(self, user_id: int, token_hash: str, expires_at: datetime) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (user_id, token_hash, expires_at, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, token_hash, expires_at.isoformat(), now),
            )

    def delete_session(self, token_hash: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))

    def get_user_by_session(self, token_hash: str) -> UserRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT users.*
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ? AND sessions.expires_at > ?
                """,
                (token_hash, now),
            ).fetchone()
        return row_to_user(row) if row else None

    def create_calendar(
        self,
        user_id: int,
        name: str,
        color: str,
        description: str,
    ) -> CalendarRecord:
        with self.connect() as conn:
            calendar_id = self._create_calendar_conn(conn, user_id, name, color, description)
        record = self.get_calendar(user_id, calendar_id, include_token=True)
        if record is None:
            raise RuntimeError("created calendar could not be loaded")
        return record

    def _create_calendar_conn(
        self,
        conn: sqlite3.Connection,
        user_id: int,
        name: str,
        color: str,
        description: str,
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            """
            INSERT INTO calendars (
                user_id, name, color, description, token, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, color, description, secrets.token_urlsafe(24), now, now),
        )
        return int(cursor.lastrowid)

    def list_calendars(self, user_id: int, include_tokens: bool = False) -> list[CalendarRecord]:
        with self.connect() as conn:
            rows: Iterable[sqlite3.Row] = conn.execute(
                "SELECT * FROM calendars WHERE user_id = ? ORDER BY id ASC",
                (user_id,),
            ).fetchall()
        return [row_to_calendar(row, include_tokens) for row in rows]

    def get_calendar(
        self,
        user_id: int,
        calendar_id: int,
        include_token: bool = False,
    ) -> CalendarRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM calendars WHERE id = ? AND user_id = ?",
                (calendar_id, user_id),
            ).fetchone()
        return row_to_calendar(row, include_token) if row else None

    def update_calendar(
        self,
        user_id: int,
        calendar_id: int,
        name: str,
        color: str,
        description: str,
    ) -> CalendarRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE calendars
                SET name = ?, color = ?, description = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (name, color, description, now, calendar_id, user_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get_calendar(user_id, calendar_id, include_token=True)

    def regenerate_calendar_token(self, user_id: int, calendar_id: int) -> CalendarRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE calendars SET token = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (secrets.token_urlsafe(24), now, calendar_id, user_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get_calendar(user_id, calendar_id, include_token=True)

    def find_calendar_by_token(self, calendar_id: int, token: str) -> CalendarRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM calendars WHERE id = ? AND token = ?",
                (calendar_id, token),
            ).fetchone()
        return row_to_calendar(row, include_token=False) if row else None

    def create_pending(
        self,
        user_id: int,
        source_text: str,
        event: ParsedEvent,
        calendar_id: int,
    ) -> EventRecord:
        now = datetime.now(timezone.utc).isoformat()
        uid = f"{uuid.uuid4()}@calendar-maker"
        with self.connect() as conn:
            calendar = conn.execute(
                "SELECT id FROM calendars WHERE id = ? AND user_id = ?",
                (calendar_id, user_id),
            ).fetchone()
            if calendar is None:
                raise ValueError("calendar not found")
            cursor = conn.execute(
                """
                INSERT INTO events (
                    user_id, calendar_id, uid, source_text, title, start, end,
                    timezone, location, description, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
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
        record = self.get_event(user_id, event_id)
        if record is None:
            raise RuntimeError("created event could not be loaded")
        return record

    def get_event(self, user_id: int, event_id: int) -> EventRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM events WHERE id = ? AND user_id = ?",
                (event_id, user_id),
            ).fetchone()
        return row_to_event(row) if row else None

    def update_event(
        self,
        user_id: int,
        event_id: int,
        event: ParsedEvent,
        calendar_id: int,
        confirm: bool | None = None,
    ) -> EventRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            if not conn.execute(
                "SELECT 1 FROM calendars WHERE id = ? AND user_id = ?",
                (calendar_id, user_id),
            ).fetchone():
                raise ValueError("calendar not found")
            existing = conn.execute(
                "SELECT status FROM events WHERE id = ? AND user_id = ?",
                (event_id, user_id),
            ).fetchone()
            if existing is None:
                return None
            if confirm is True and existing["status"] != EventStatus.pending.value:
                raise RuntimeError("event already confirmed")
            status = EventStatus.confirmed.value if confirm else existing["status"]
            conn.execute(
                """
                UPDATE events
                SET calendar_id = ?, title = ?, start = ?, end = ?, timezone = ?,
                    location = ?, description = ?, status = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    calendar_id,
                    event.title,
                    event.start.isoformat(),
                    event.end.isoformat(),
                    event.timezone,
                    event.location,
                    event.description,
                    status,
                    now,
                    event_id,
                    user_id,
                ),
            )
        return self.get_event(user_id, event_id)

    def delete_event(self, user_id: int, event_id: int) -> bool:
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM events WHERE id = ? AND user_id = ?",
                (event_id, user_id),
            )
        return cursor.rowcount > 0

    def agenda_events(
        self,
        user_id: int,
        start: datetime | None = None,
        end: datetime | None = None,
        calendar_id: int | None = None,
    ) -> list[EventRecord]:
        clauses = ["user_id = ?", "status = ?"]
        params: list[object] = [user_id, EventStatus.confirmed.value]
        if start:
            clauses.append("end >= ?")
            params.append(start.isoformat())
        if end:
            clauses.append("start <= ?")
            params.append(end.isoformat())
        if calendar_id:
            clauses.append("calendar_id = ?")
            params.append(calendar_id)
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM events WHERE {' AND '.join(clauses)} ORDER BY start ASC, id ASC",
                params,
            ).fetchall()
        return [row_to_event(row) for row in rows]

    def confirmed_events(
        self,
        user_id: int,
        calendar_id: int | None = None,
    ) -> list[EventRecord]:
        return self.agenda_events(user_id, calendar_id=calendar_id)

    def user_by_feed_token(self, token: str) -> UserRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE all_feed_token = ?",
                (token,),
            ).fetchone()
        return row_to_user(row) if row else None

    def regenerate_all_feed_token(self, user_id: int) -> UserRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET all_feed_token = ?, updated_at = ? WHERE id = ?",
                (secrets.token_urlsafe(24), now, user_id),
            )
        return self.get_user(user_id)


def migrate_legacy_schema(conn: sqlite3.Connection) -> None:
    for table, columns in {
        "calendars": {
            "user_id": "INTEGER",
            "color": "TEXT NOT NULL DEFAULT '#2563eb'",
            "description": "TEXT NOT NULL DEFAULT ''",
        },
        "events": {"user_id": "INTEGER"},
    }.items():
        if not table_exists(conn, table):
            continue
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def ensure_default_legacy_calendar(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT 1 FROM calendars LIMIT 1").fetchone():
        return
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO calendars (
            name, color, description, token, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("AI Calendar", CALENDAR_COLORS[0], "Legacy default calendar", "change-me", now, now),
    )


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone() is not None


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def row_to_user(row: sqlite3.Row) -> UserRecord:
    return UserRecord(
        id=row["id"],
        email=row["email"],
        all_feed_token=row["all_feed_token"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def row_to_calendar(row: sqlite3.Row, include_token: bool = False) -> CalendarRecord:
    return CalendarRecord(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        color=row["color"],
        description=row["description"],
        token=row["token"] if include_token else None,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def row_to_event(row: sqlite3.Row) -> EventRecord:
    return EventRecord(
        id=row["id"],
        user_id=row["user_id"],
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
