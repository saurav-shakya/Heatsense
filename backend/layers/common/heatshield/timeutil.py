"""Time helpers. Storage is UTC ISO-8601; "days" are Delhi (IST) calendar days."""

from datetime import UTC, datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30), "IST")


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def ist_day_start(now: datetime) -> datetime:
    """Midnight IST of the day containing `now`, as an aware datetime."""
    return now.astimezone(IST).replace(hour=0, minute=0, second=0, microsecond=0)


def ist_date(value: str) -> str:
    """'2026-10-10T20:30:00Z' -> '2026-10-11' (the IST calendar date)."""
    return parse_iso(value).astimezone(IST).strftime("%Y-%m-%d")


def ist_hour(value: str) -> int:
    return parse_iso(value).astimezone(IST).hour
