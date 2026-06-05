from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.models import ParsedEvent


def test_parsed_event_requires_end_after_start() -> None:
    start = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        ParsedEvent(
            title="开会",
            start=start,
            end=start - timedelta(minutes=1),
            timezone="Asia/Shanghai",
        )

