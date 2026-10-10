import json
from datetime import UTC, datetime, timedelta

import boto3
import pytest
from conftest import fake_open_meteo, load_function

from heatshield import weather
from heatshield.timeutil import IST, ist_day_start


@pytest.fixture
def engine(aws):
    return load_function("risk_engine")


def test_engine_scores_every_ward_and_flags_vulnerable_one(engine, ctx, monkeypatch):
    # Hot day, nights cooling to 26 degC: only the hot, vulnerable ward reaches High.
    monkeypatch.setattr(weather, "_get_json", fake_open_meteo(peak_c=44.0, rh=20.0, night_c=26.0))
    result = engine.handler({}, ctx)
    assert result["wards"] == 2 and result["alertable"] == 1  # DL-001 is hot + vulnerable, DL-002 is not


def test_hot_night_flags_every_ward_for_people_at_home(engine, ctx):
    from heatshield import repo

    # Default weather: 44 degC afternoons, nights that only fall to 32 degC.
    assert engine.handler({}, ctx)["alertable"] == 2
    day = repo.get_ward("DL-002")["daily"][0]
    assert day["hotNight"] is True and day["nightMin"] >= 30
    assert "night_shelter" in day["actions"]


def test_engine_forecast_starts_at_ist_midnight(engine):
    now = datetime(2026, 10, 10, 12, tzinfo=UTC)
    pack = weather.fetch_forecast([(28.7, 77.2)], ist_day_start(now), 4)
    rows = engine.build_forecasts({"wardId": "X", "vulnerabilityScore": 0.5}, now, weather.WeatherIndex(pack))
    assert rows[0].forecastTime == "2026-10-09T18:30:00Z"  # 00:00 IST on 10 Oct
    assert len(rows) == 96
    assert len(engine.daily_summary(rows)) == 4


def test_engine_stores_the_raw_pull(engine, ctx):
    engine.handler({}, ctx)
    keys = [o["Key"] for o in boto3.client("s3").list_objects_v2(Bucket="data", Prefix="raw/forecasts/")["Contents"]]
    assert len(keys) == 1 and keys[0].endswith(".json")


def test_weather_failure_keeps_last_scores_and_sends_no_event(engine, ctx, monkeypatch):
    from heatshield import repo

    engine.handler({}, ctx)
    before = repo.get_ward("DL-001")["daily"]

    def down(url, params):
        raise weather.WeatherError("503")

    monkeypatch.setattr(weather, "_get_json", down)
    put_events = []
    real_client = boto3.client
    monkeypatch.setattr(boto3, "client", lambda name: _Recorder(put_events) if name == "events" else real_client(name))
    assert engine.handler({}, ctx)["error"] == "weather-unavailable"
    assert repo.get_ward("DL-001")["daily"] == before
    assert put_events == []


class _Recorder:
    def __init__(self, sink):
        self.sink = sink

    def put_events(self, **kwargs):
        self.sink.append(kwargs)


def test_replay_scores_a_past_heatwave_onto_today(engine, ctx, monkeypatch):
    from heatshield import repo

    # A severe heatwave pack for 27 May - 31 May 2024, as fetch_replay.py would store it.
    monkeypatch.setattr(weather, "_get_json", fake_open_meteo(peak_c=47.5, rh=10))
    pack = weather.fetch_archive([(28.7, 77.2), (28.5, 77.1)], "2024-05-27", "2024-05-31")
    boto3.client("s3").put_object(Bucket="data", Key="replay/delhi/2024-05-28.json", Body=json.dumps(pack))
    # Live weather is mild; replay must not use it.
    monkeypatch.setattr(weather, "_get_json", fake_open_meteo(peak_c=30, rh=40))

    result = engine.handler({"replay": "2024-05-28"}, ctx)
    assert result["replayOf"] == "2024-05-28"
    ward = repo.get_ward("DL-002")  # even the cool, low-vulnerability ward gets flagged
    assert ward["replayOf"] == "2024-05-28"
    today = datetime.now(UTC).astimezone(IST).strftime("%Y-%m-%d")
    assert ward["daily"][0]["date"] == today
    assert ward["daily"][0]["level"] in ("moderate", "high")
    assert repo.get_ward("DL-001")["daily"][0]["level"] == "extreme"

    # Back to live clears the replay flag.
    engine.handler({"replay": ""}, ctx)
    assert "replayOf" not in repo.get_ward("DL-001")


# --------------------------------------------------------------------------- dispatcher


@pytest.fixture
def dispatcher(aws):
    return load_function("alert_dispatcher")


@pytest.fixture
def outbox(dispatcher, monkeypatch):
    from heatshield.messaging import SendResult

    sent = []
    monkeypatch.setattr(
        dispatcher.messaging,
        "send_whatsapp",
        lambda phone, body: sent.append(("wa", phone, body)) or SendResult(True, "queued"),
    )
    monkeypatch.setattr(
        dispatcher.messaging,
        "send_sms",
        lambda phone, body: sent.append(("sms", phone, body)) or SendResult(True, "sent"),
    )
    return sent


def subscribe(phone: str, ward: str = "DL-001", channel: str = "whatsapp", language: str = "hi", group: str = "worker"):
    from heatshield import repo
    from heatshield.models import Channel, Group, Language, Subscriber

    repo.put_subscriber(
        Subscriber(phone=phone, wardId=ward, group=Group(group), language=Language(language), channel=Channel(channel))
    )


def ist_time_today(hour: float) -> datetime:
    return ist_day_start(datetime.now(UTC)) + timedelta(hours=hour)


@pytest.mark.parametrize(
    ("utc_hour", "quiet"),
    [(16, False), (17, True), (0, True), (1, False)],  # 21:30, 22:30, 05:30, 06:30 IST
)
def test_quiet_hours(dispatcher, utc_hour, quiet):
    assert dispatcher.in_quiet_hours(datetime(2026, 10, 10, utc_hour, tzinfo=UTC)) is quiet


def test_evening_run_targets_tomorrow(dispatcher):
    assert dispatcher.target_day(datetime(2026, 10, 10, 13, 30, tzinfo=UTC)) == 1  # 19:00 IST
    assert dispatcher.target_day(datetime(2026, 10, 10, 1, 30, tzinfo=UTC)) == 0  # 07:00 IST


def test_sends_to_subscribers_of_risky_wards_only(engine, dispatcher, outbox, ctx):
    from heatshield.advisory import Advisor

    engine.handler({}, ctx)
    subscribe("+919800000001", channel="whatsapp", language="hi")
    subscribe("+919800000002", channel="sms", language="en")
    subscribe("+919800000003", ward="DL-002")  # cool ward: no alert
    counts = dispatcher.dispatch(ist_time_today(7), Advisor(mode="template"))
    assert counts == {"sent": 2, "skipped": 0, "failed": 0}
    channels = {phone: (kind, body) for kind, phone, body in outbox}
    assert set(channels) == {"+919800000001", "+919800000002"}
    wa = channels["+919800000001"][1]
    assert "Sample A" in wa and wa.endswith("STOP भेजें।") and len(wa) <= 900
    assert "WBGT" in wa and "मिनट काम" in wa  # outdoor worker gets the stop-work hours and work-rest ratio
    assert channels["+919800000002"][0] == "sms" and "STOP" in channels["+919800000002"][1]


def test_same_level_is_not_resent_on_refresh_but_evening_alert_goes(engine, dispatcher, outbox, ctx):
    from heatshield.advisory import Advisor

    engine.handler({}, ctx)
    subscribe("+919800000001")
    advisor = Advisor(mode="template")
    assert dispatcher.dispatch(ist_time_today(7), advisor)["sent"] == 1
    assert dispatcher.dispatch(ist_time_today(10), advisor) == {"sent": 0, "skipped": 1, "failed": 0}
    assert dispatcher.dispatch(ist_time_today(19), advisor)["sent"] == 1  # warns about tomorrow


def test_at_most_two_alerts_a_day(engine, dispatcher, outbox, ctx, monkeypatch):
    from heatshield import repo
    from heatshield.advisory import Advisor

    engine.handler({}, ctx)
    subscribe("+919800000001")
    advisor = Advisor(mode="template")
    sent = 0
    # Level changes on every refresh, so only the daily cap can stop these.
    for i, level in enumerate(["high", "extreme", "high", "extreme"]):
        ward = repo.get_ward("DL-001")
        ward["daily"][0]["level"] = level
        repo.set_ward_daily("DL-001", ward["daily"])
        sent += dispatcher.dispatch(ist_time_today(7 + i), advisor)["sent"]
    assert sent == 2
    assert repo.get_subscriber("+919800000001")["alertsToday"] == 2


def test_opted_out_subscribers_get_nothing(engine, dispatcher, outbox, ctx):
    from heatshield import repo
    from heatshield.advisory import Advisor

    engine.handler({}, ctx)
    subscribe("+919800000001")
    repo.opt_out("+919800000001")
    assert dispatcher.dispatch(ist_time_today(7), Advisor(mode="template"))["sent"] == 0
    assert outbox == []


def test_handler_skips_quiet_hours_and_reports_counts(dispatcher, ctx, monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 10, 18, tzinfo=UTC)  # 23:30 IST

    monkeypatch.setattr(dispatcher, "datetime", Clock)
    assert dispatcher.handler({}, ctx) == {"sent": 0, "skipped": "quiet-hours"}


# --------------------------------------------------------------------------- personal alerts


def test_tin_roof_subscriber_is_alerted_in_a_moderate_ward(engine, dispatcher, outbox, ctx, monkeypatch):
    from heatshield import repo
    from heatshield.advisory import Advisor
    from heatshield.models import Channel, Group, Home, Language, Subscriber

    monkeypatch.setattr(weather, "_get_json", fake_open_meteo(peak_c=44.0, rh=20.0, night_c=26.0))
    engine.handler({}, ctx)
    ward = repo.get_ward("DL-002")
    ward["daily"][0]["level"] = "moderate"
    repo.set_ward_daily("DL-002", ward["daily"])
    subscribe("+919800000004", ward="DL-002", group="worker")

    repo.put_subscriber(
        Subscriber(
            phone="+919800000005",
            wardId="DL-002",
            group=Group.WORKER,
            language=Language.EN,
            channel=Channel.WHATSAPP,
            home=Home.TIN,
        )
    )
    counts = dispatcher.dispatch(ist_time_today(7), Advisor(mode="template"))
    assert counts["sent"] == 1
    (kind, phone, body), *_ = outbox
    assert phone == "+919800000005"
    assert body.startswith("HeatShield: HIGH heat risk in Sample B")
    assert "tin or sheet roofs" in body


def test_elderly_alert_has_place_night_and_check_in(engine, dispatcher, outbox, ctx):
    from conftest import put_resources

    from heatshield import repo
    from heatshield.advisory import Advisor

    put_resources()
    engine.handler({}, ctx)  # default weather: 44 degC days, nights at 32 degC
    subscribe("+919800000006", group="elderly", language="en")
    dispatcher.dispatch(ist_time_today(7), Advisor(mode="template"))
    (_, _, body), *_ = outbox
    assert "Nearest cool place: Community Hall Cool Room" in body
    assert "Sample point" not in body  # unverified places never reach alerts
    assert "Tonight stays above" in body
    assert "Reply OK if you are fine, or SOS" in body
    sub = repo.get_subscriber("+919800000006")
    assert sub["checkInStatus"] == "asked"


def test_worker_gets_water_point_not_check_in(engine, dispatcher, outbox, ctx):
    from conftest import put_resources

    from heatshield.advisory import Advisor

    put_resources()
    engine.handler({}, ctx)
    subscribe("+919800000007", group="worker", language="en")
    dispatcher.dispatch(ist_time_today(7), Advisor(mode="template"))
    (_, _, body), *_ = outbox
    assert "Nearest drinking water: Water ATM" in body
    assert "Stop heavy outdoor work" in body
    assert "SOS" not in body and "Tonight" not in body


def test_engine_summary_has_work_plan_and_actions(engine, ctx):
    from heatshield import repo

    engine.handler({}, ctx)
    today = repo.get_ward("DL-001")["daily"][0]
    assert today["wbgtMax"] > 31.5
    assert any(seg["work"] == 0 for seg in today["workPlan"])
    assert all(6 <= seg["from"] < seg["to"] <= 20 for seg in today["workPlan"])
    assert {"open_cooling", "shift_work", "night_shelter"} <= set(today["actions"])
    hourly = repo.get_forecast("DL-001", "0", "9")
    assert {"airTemp", "wbgt"} <= hourly[0].keys()
