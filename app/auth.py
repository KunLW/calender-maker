from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, Request

from app.config import Settings, get_settings
from app.db import EventStore
from app.models import UserRecord


SESSION_COOKIE = "calendar_session"
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry(settings: Settings) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.session_days)


def get_store(settings: Settings = Depends(get_settings)) -> EventStore:
    return EventStore(settings.database_path)


def require_user(
    request: Request,
    store: EventStore = Depends(get_store),
) -> UserRecord:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="authentication required")
    user = store.get_user_by_session(hash_token(token))
    if user is None:
        raise HTTPException(status_code=401, detail="session expired")
    return user
