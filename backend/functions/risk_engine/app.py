"""Risk engine: runs every 3 hours, scores every ward, then announces new scores.

SKELETON: hazard comes from a deterministic placeholder curve, not Open-Meteo. Phase 2
replaces `placeholder_hazard` with real forecast pulls; the write/summary/event plumbing stays.
"""

import json
import math
from datetime import UTC, datetime, timedelta

import boto3
from aws_lambda_powertools import Logger

from heatshield import config, repo
from heatshield.models import RiskForecast
from heatshield.risk import RiskLevel, bucket, score
from heatshield.timeutil import IST, iso, ist_date, ist_day_start

logger = Logger()


def placeholder_hazard(ward: dict, t: datetime, day_index: int) -> tuple[float, float]:
    """Fake (heatIndex degC, hazard 0..1): afternoon peak, warming over the 4 days, hotter wards hotter."""
    hour = t.astimezone(IST).hour
    diurnal = max(0.0, math.sin(math.pi * (hour - 6) / 16))  # 0 at 06:00, peak ~14:00 IST
    heat_index = 30 + 4 * day_index + 12 * diurnal + float(ward.get("lstOffset", 0))
    hazard = min(max((heat_index - 27) / 25, 0.0), 1.0)  # 27C -> 0, 52C -> 1
    return round(heat_index, 1), round(hazard, 3)


def build_forecasts(ward: dict, now: datetime) -> list[RiskForecast]:
    """Hourly rows from midnight IST today through the end of day +3."""
    start = ist_day_start(now)
    generated = iso(now)
    expires = int(now.timestamp()) + config.FORECAST_TTL_SECONDS
    rows = []
    for h in range(24 * config.FORECAST_DAYS):
        t = start + timedelta(hours=h)
        heat_index, hazard = placeholder_hazard(ward, t, h // 24)
        risk = score(hazard, float(ward["vulnerabilityScore"]))
        rows.append(
            RiskForecast(
                wardId=ward["wardId"],
                forecastTime=iso(t),
                heatIndex=heat_index,
                hazard=hazard,
                risk=risk,
                level=bucket(risk).value,
                generatedAt=generated,
                expiresAt=expires,
            )
        )
    return rows


def daily_summary(rows: list[RiskForecast]) -> list[dict]:
    """Peak risk per IST day, stored on the ward row so GET /wards is a single scan."""
    days: dict[str, RiskForecast] = {}
    for r in rows:
        day = ist_date(r.forecastTime)
        if day not in days or r.risk > days[day].risk:
            days[day] = r
    return [
        {"date": d, "risk": r.risk, "level": r.level, "heatIndex": r.heatIndex, "peakAt": r.forecastTime}
        for d, r in sorted(days.items())
    ]


@logger.inject_lambda_context
def handler(event, context):
    now = datetime.now(UTC)
    wards = repo.list_wards()
    alertable = []
    for ward in wards:
        rows = build_forecasts(ward, now)
        repo.put_forecasts(rows)
        summary = daily_summary(rows)
        repo.set_ward_daily(ward["wardId"], summary)
        # Today or tomorrow reaching High/Extreme is what the dispatcher cares about.
        if any(RiskLevel(d["level"]).alertable for d in summary[:2]):
            alertable.append(ward["wardId"])

    boto3.client("events").put_events(
        Entries=[
            {
                "Source": config.EVENT_SOURCE,
                "DetailType": config.EVENT_DETAIL_TYPE,
                "EventBusName": config.EVENT_BUS_NAME,
                "Detail": json.dumps(
                    {"city": config.CITY, "generatedAt": iso(now), "wardCount": len(wards), "alertableWards": alertable}
                ),
            }
        ]
    )
    logger.info("scored wards", extra={"wards": len(wards), "alertable": len(alertable)})
    return {"wards": len(wards), "alertable": len(alertable)}
