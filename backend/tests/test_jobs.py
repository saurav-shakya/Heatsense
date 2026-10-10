from datetime import UTC, datetime

import pytest
from conftest import load_function


@pytest.fixture
def engine(aws):
    return load_function("risk_engine")


@pytest.fixture
def dispatcher(aws):
    return load_function("alert_dispatcher")


def test_engine_scores_every_ward_and_flags_vulnerable_one(engine, ctx):
    result = engine.handler({}, ctx)
    assert result == {"wards": 2, "alertable": 1}  # DL-001 is hot + vulnerable, DL-002 is not


def test_engine_forecast_starts_at_ist_midnight(engine):
    rows = engine.build_forecasts({"wardId": "X", "vulnerabilityScore": 0.5}, datetime(2026, 10, 10, 12, tzinfo=UTC))
    assert rows[0].forecastTime == "2026-10-09T18:30:00Z"  # 00:00 IST on 10 Oct
    assert len(engine.daily_summary(rows)) == 4


@pytest.mark.parametrize(
    ("utc_hour", "quiet"),
    [(16, False), (17, True), (0, True), (1, False)],  # 21:30, 22:30, 05:30, 06:30 IST
)
def test_quiet_hours(dispatcher, utc_hour, quiet):
    assert dispatcher.in_quiet_hours(datetime(2026, 10, 10, utc_hour, tzinfo=UTC)) is quiet


def test_evening_run_targets_tomorrow(dispatcher):
    assert dispatcher.target_day(datetime(2026, 10, 10, 13, 30, tzinfo=UTC)) == 1  # 19:00 IST
    assert dispatcher.target_day(datetime(2026, 10, 10, 1, 30, tzinfo=UTC)) == 0  # 07:00 IST


def test_webhook_replies_with_twiml(aws, ctx):
    webhook = load_function("whatsapp_webhook")
    resp = webhook.handler({"body": "Body=Can+I+go+out%3F&From=whatsapp%3A%2B919876543210"}, ctx)
    assert resp["headers"]["Content-Type"] == "text/xml"
    assert "<Response><Message>" in resp["body"]
