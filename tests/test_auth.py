from datetime import datetime, timezone

import pytest

from app.auth import hash_password, hash_token, verify_password
from app.db import EventStore


def test_invite_registration_claims_legacy_data_and_creates_session(tmp_path) -> None:
    store = EventStore(str(tmp_path / "calendar.db"))
    store.init()
    invite = store.create_invite()

    user = store.register_user("Owner@example.com", hash_password("strong-password"), invite)

    assert user.email == "owner@example.com"
    assert store.list_calendars(user.id)[0].name == "AI Calendar"
    with pytest.raises(ValueError, match="invalid or used invite code"):
        store.register_user("second@example.com", hash_password("other-password"), invite)

    token = "session-token"
    store.create_session(
        user.id,
        hash_token(token),
        datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    assert store.get_user_by_session(hash_token(token)).id == user.id


def test_password_hashing_uses_argon2() -> None:
    password_hash = hash_password("strong-password")

    assert password_hash.startswith("$argon2")
    assert verify_password(password_hash, "strong-password")
    assert not verify_password(password_hash, "wrong-password")

