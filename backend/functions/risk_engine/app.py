"""Risk engine: runs every 3 hours, scores every ward, then announces new scores.

Hazard comes from Open-Meteo hourly temperature and humidity (heatshield.weather), turned
into a felt temperature and H in [0, 1] by heatshield.heat, then Risk = H x V.

Replay mode scores from a past heatwave's recorded weather stored in S3 at
replay/{city}/{date}.json (see data/scripts/fetch_replay.py), shifted so that day lands on
today. Trigger it with the event {"replay": "2024-05-28"}, or keep it on with the
REPLAY_DATE environment variable (template parameter ReplayDate). {"replay": ""} forces live.

If the weather can't be fetched, nothing is written: the last good scores stay in place
and no RiskScoresUpdated event goes out.
"""

import json
from datetime import UTC, date, datetime, timedelta

import boto3
from aws_lambda_powertools import Logger

from heatshield import config, repo, resources, weather
from heatshield.actions import ward_actions
from heatshield.heat import LST_TO_AIR, hazard, is_hot_night, wbgt_c, work_minutes_per_hour
from heatshield.models import RiskForecast
from heatshield.risk import RiskLevel, bucket, score
from heatshield.timeutil import IST, iso, ist_date, ist_day_start, ist_hour

logger = Logger()


def forecast_hours(now: datetime) -> list[str]:
    """UTC ISO hours from midnight IST today through the end of day +3."""
    start = ist_day_start(now)
    return [iso(start + timedelta(hours=h)) for h in range(24 * config.FORECAST_DAYS)]


def build_forecasts(ward: dict, now: datetime, index: weather.WeatherIndex) -> list[RiskForecast]:
    point = weather.ward_point(ward, config.CITY)
    lst_offset = float(ward.get("lstOffset", 0))
    vulnerability = float(ward["vulnerabilityScore"])
    generated = iso(now)
    expires = int(now.timestamp()) + config.FORECAST_TTL_SECONDS
    rows = []
    for hour in forecast_hours(now):
        obs = index.at(point, hour)
        if obs is None:
            continue
        felt, h = hazard(obs[0], obs[1], lst_offset)
        risk = score(h, vulnerability)
        rows.append(
            RiskForecast(
                wardId=ward["wardId"],
                forecastTime=hour,
                heatIndex=felt,
                hazard=h,
                risk=risk,
                level=bucket(risk).value,
                generatedAt=generated,
                expiresAt=expires,
                airTemp=round(obs[0], 1),
                wbgt=wbgt_c(obs[0], obs[1], sun=True),
            )
        )
    return rows


# "Tonight" for day D runs from 21:00 on D to 06:00 on D+1 (IST).
NIGHT_START_HOUR = 21
NIGHT_END_HOUR = 6
MIN_NIGHT_HOURS = 6  # fewer than this at the end of the forecast: no night figure


def _night_min(rows: list[RiskForecast], day: str, lst_offset: float = 0.0) -> float | None:
    """Tonight's lowest air temperature in the ward. Built-up wards hold heat most at night."""
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    temps = []
    for r in rows:
        if r.airTemp is None:
            continue
        d, h = ist_date(r.forecastTime), ist_hour(r.forecastTime)
        if (d == day and h >= NIGHT_START_HOUR) or (d == next_day and h < NIGHT_END_HOUR):
            temps.append(r.airTemp)
    if len(temps) < MIN_NIGHT_HOURS:
        return None
    return round(min(temps) + LST_TO_AIR * lst_offset, 1)


WORK_DAY = (6, 20)  # IST hours [start, end) a work plan covers


def work_plan(rows: list[RiskForecast]) -> list[dict]:
    """Daytime hours when moderate outdoor work must be cut back, as runs of equal advice.

    [{"from": 9, "to": 11, "work": 30}, {"from": 11, "to": 17, "work": 0}, ...]: minutes of work
    per hour (the rest in shade), 0 = stop heavy work. Hours safe for normal work are left out.
    """
    by_hour = {
        ist_hour(r.forecastTime): work_minutes_per_hour(r.wbgt)
        for r in rows
        if r.wbgt is not None and WORK_DAY[0] <= ist_hour(r.forecastTime) < WORK_DAY[1]
    }
    plan: list[dict] = []
    for hour in sorted(by_hour):
        minutes = by_hour[hour]
        if minutes >= 60:
            continue
        if plan and plan[-1]["to"] == hour and plan[-1]["work"] == minutes:
            plan[-1]["to"] = hour + 1
        else:
            plan.append({"from": hour, "to": hour + 1, "work": minutes})
    return plan


def daily_summary(rows: list[RiskForecast], ward: dict | None = None, places: list[dict] | None = None) -> list[dict]:
    """Per IST day: peak risk, the numbers people act on (work plan, tonight's low) and ward actions.

    Stored on the ward row so GET /wards is a single scan.
    """
    by_day: dict[str, list[RiskForecast]] = {}
    for r in rows:
        by_day.setdefault(ist_date(r.forecastTime), []).append(r)
    out = []
    for d, day_rows in sorted(by_day.items()):
        peak = max(day_rows, key=lambda r: r.risk)
        entry = {
            "date": d,
            "risk": peak.risk,
            "level": peak.level,
            "heatIndex": peak.heatIndex,
            "peakAt": peak.forecastTime,
        }
        wbgts = [r.wbgt for r in day_rows if r.wbgt is not None]
        if wbgts:
            entry["wbgtMax"] = max(wbgts)
            entry["workPlan"] = work_plan(day_rows)
        night = _night_min(rows, d, float((ward or {}).get("lstOffset", 0)))
        if night is not None:
            entry["nightMin"] = night
            entry["hotNight"] = is_hot_night(night)
        entry["actions"] = ward_actions(entry, ward or {}, places or [])
        out.append(entry)
    return out


def _s3():
    return boto3.client("s3")


def load_replay(replay_date: str, now: datetime) -> dict:
    """The stored past-heatwave pack, with its first day moved onto today (IST)."""
    obj = _s3().get_object(Bucket=config.DATA_BUCKET, Key=f"replay/{config.CITY}/{replay_date}.json")
    pack = json.loads(obj["Body"].read())
    offset = (now.astimezone(IST).date() - date.fromisoformat(replay_date)).days
    return weather.shift_days(pack, offset)


def store_raw(pack: dict, now: datetime) -> None:
    """Keep every live pull: raw/forecasts/{date}/{hour}.json (UTC)."""
    key = f"raw/forecasts/{now.astimezone(UTC):%Y-%m-%d}/{now.astimezone(UTC):%H}.json"
    try:
        _s3().put_object(
            Bucket=config.DATA_BUCKET,
            Key=key,
            Body=json.dumps(pack, separators=(",", ":")).encode(),
            ContentType="application/json",
        )
    except Exception:
        logger.exception("could not store raw forecast", extra={"key": key})


def get_weather(wards: list[dict], now: datetime, replay_date: str) -> dict:
    if replay_date:
        return load_replay(replay_date, now)
    # Midnight IST is 18:30 UTC the day before, so this asks from yesterday's UTC date.
    pack = weather.fetch_forecast(weather.grid_points(wards, config.CITY), ist_day_start(now), config.FORECAST_DAYS)
    store_raw(pack, now)
    return pack


@logger.inject_lambda_context
def handler(event, context):
    now = datetime.now(UTC)
    event = event or {}
    replay_date = event["replay"] if "replay" in event else config.REPLAY_DATE
    wards = repo.list_wards()

    try:
        index = weather.WeatherIndex(get_weather(wards, now, replay_date))
    except Exception:
        # Keep the last good scores; the dispatcher's schedules still run on them.
        logger.exception("weather unavailable, keeping previous scores", extra={"replay": replay_date or None})
        return {"wards": 0, "alertable": 0, "error": "weather-unavailable"}

    if not index.covers(forecast_hours(now)):
        logger.warning("weather does not cover the whole forecast window", extra={"replay": replay_date or None})

    places = resources.load()
    alertable = []
    scored = 0
    for ward in wards:
        rows = build_forecasts(ward, now, index)
        if not rows:
            continue
        repo.put_forecasts(rows)
        summary = daily_summary(rows, ward, places)
        repo.set_ward_daily(ward["wardId"], summary, replay_of=replay_date or None)
        scored += 1
        # Today or tomorrow reaching High/Extreme is what the dispatcher cares about.
        if any(RiskLevel(d["level"]).alertable or d.get("hotNight") for d in summary[:2]):
            alertable.append(ward["wardId"])

    boto3.client("events").put_events(
        Entries=[
            {
                "Source": config.EVENT_SOURCE,
                "DetailType": config.EVENT_DETAIL_TYPE,
                "EventBusName": config.EVENT_BUS_NAME,
                "Detail": json.dumps(
                    {
                        "city": config.CITY,
                        "generatedAt": iso(now),
                        "wardCount": scored,
                        "alertableWards": alertable,
                        "replayOf": replay_date or None,
                    }
                ),
            }
        ]
    )
    logger.info("scored wards", extra={"wards": scored, "alertable": len(alertable), "replay": replay_date or None})
    return {"wards": scored, "alertable": len(alertable), "replayOf": replay_date or None}
