"""Alert dispatcher: sends High/Extreme heat alerts to the subscribers of affected wards.

Triggered by the risk engine's RiskScoresUpdated event and by 07:00 / 19:00 IST schedules.
Evening runs warn about tomorrow, earlier runs about today.

Rules:
  - never between 22:00 and 06:00 IST,
  - at most config.MAX_ALERTS_PER_DAY per subscriber per IST day,
  - no repeat for the same (target day, level, morning/evening slot), so a 3-hourly refresh
    only re-alerts when the level changes,
  - every message ends with how to stop alerts.
Both caps are enforced with a conditional write on the subscriber row before sending.
"""

from datetime import UTC, datetime, timedelta

from aws_lambda_powertools import Logger

from heatshield import config, messaging, repo
from heatshield.advisory import Advisor, format_window, sms_message, whatsapp_message
from heatshield.risk import RiskLevel
from heatshield.timeutil import IST, iso, ist_hour

logger = Logger()

QUIET_START_HOUR = 22  # never alert 22:00-06:00 IST
QUIET_END_HOUR = 6
EVENING_HOUR = 17


def in_quiet_hours(now: datetime) -> bool:
    hour = now.astimezone(IST).hour
    return hour >= QUIET_START_HOUR or hour < QUIET_END_HOUR


def target_day(now: datetime) -> int:
    """Index into ward.daily: evening runs warn about tomorrow, earlier runs about today."""
    return 1 if now.astimezone(IST).hour >= EVENING_HOUR else 0


def slot(now: datetime) -> str:
    return "eve" if now.astimezone(IST).hour >= EVENING_HOUR else "morn"


def alertable_wards(wards: list[dict], day: int) -> list[dict]:
    out = []
    for ward in wards:
        daily = ward.get("daily") or []
        if len(daily) > day and RiskLevel(daily[day]["level"]).alertable:
            out.append(ward)
    return out


def risky_window(ward_id: str, day_summary: dict) -> tuple[int, int]:
    """IST hours [start, end) of the target day at High or above; around the peak if rows are missing."""
    day_start = datetime.fromisoformat(day_summary["date"]).replace(tzinfo=IST)
    rows = repo.get_forecast(ward_id, iso(day_start), iso(day_start + timedelta(days=1)))
    hours = [ist_hour(r["forecastTime"]) for r in rows if RiskLevel(r["level"]).alertable]
    if hours:
        return min(hours), max(hours) + 1
    peak = ist_hour(day_summary["peakAt"])
    return max(peak - 2, 0), min(peak + 2, 24)


def dispatch(now: datetime, advisor: Advisor) -> dict:
    day = target_day(now)
    today = now.astimezone(IST).strftime("%Y-%m-%d")
    counts = {"sent": 0, "skipped": 0, "failed": 0}
    for ward in alertable_wards(repo.list_wards(), day):
        summary = ward["daily"][day]
        level = summary["level"]
        key = f"{summary['date']}:{level}:{slot(now)}"
        subscribers = repo.subscribers_for_ward(ward["wardId"])
        if not subscribers:
            continue
        start, end = risky_window(ward["wardId"], summary)
        for sub in subscribers:
            if not repo.claim_alert(sub["phone"], today, key, iso(now), config.MAX_ALERTS_PER_DAY):
                counts["skipped"] += 1
                continue
            lang = sub.get("language", "hi")
            window = format_window(start, end, lang)
            if sub.get("channel") == "sms":
                result = messaging.send_sms(sub["phone"], sms_message(ward["name"], day, level, window, lang))
            else:
                advice = advisor.advice(level, window, sub.get("group", "elderly"), lang)
                body = whatsapp_message(ward["name"], day, level, summary["heatIndex"], advice, lang)
                result = messaging.send_whatsapp(sub["phone"], body)
            counts["sent" if result.ok else "failed"] += 1
            logger.info(
                "alert",
                extra={
                    "wardId": ward["wardId"],
                    "level": level,
                    "channel": sub.get("channel"),
                    "status": result.status,
                    "messageId": result.id,
                },
            )
    return counts


@logger.inject_lambda_context
def handler(event, context):
    now = datetime.now(UTC)
    if in_quiet_hours(now):
        logger.info("quiet hours, skipping")
        return {"sent": 0, "skipped": "quiet-hours"}

    advisor = Advisor()
    counts = dispatch(now, advisor)
    trigger = (event or {}).get("detail-type", "schedule")
    logger.info("dispatch done", extra={"trigger": trigger, "aiCalls": advisor.ai_calls, **counts})
    return {**counts, "aiCalls": advisor.ai_calls}
