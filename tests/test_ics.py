from datetime import datetime, timezone

from app.ics import build_calendar
from app.models import EventRecord, EventStatus


def test_build_calendar_escapes_text() -> None:
    event = EventRecord(
        id=1,
        calendar_id=1,
        uid="abc@calendar-maker",
        source_text="明天吃饭",
        title="吃饭,聊天",
        start=datetime(2026, 6, 5, 11, 0, tzinfo=timezone.utc),
        end=datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc),
        timezone="Asia/Shanghai",
        location="上海;餐厅",
        description="A\\B\nC",
        status=EventStatus.confirmed,
        created_at=datetime(2026, 6, 4, 1, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 4, 1, 0, tzinfo=timezone.utc),
    )

    content = build_calendar([event], "测试日历")

    assert "BEGIN:VCALENDAR" in content
    assert "SUMMARY:吃饭\\,聊天" in content
    assert "LOCATION:上海\\;餐厅" in content
    assert "DESCRIPTION:A\\\\B\\nC" in content
    assert "DTSTART:20260605T110000Z" in content
