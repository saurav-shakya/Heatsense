"""Alert dispatcher: sends High/Extreme heat alerts to the subscribers of affected wards.

Triggered by the risk engine's RiskScoresUpdated event and by 07:00 / 19:00 IST schedules.
Evening runs warn about tomorrow, earlier runs about today.

Each subscriber's level is personal (heatshield.personal): one step above the ward's under a
tin or sheet roof, and at least High on a hot night for people who are at home at night. So a
Moderate ward can still alert its tin-roof subscribers. WhatsApp alerts then add the lines that
make them actionable: the stop-work hours and work-rest ratio for outdoor workers, tonight's
low, the nearest verified cooling or water point, and for elderly people on the worst days a
wellbeing check-in (reply OK or HELP; see the WhatsApp webhook).

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

from heatshield import config, messaging, repo, resources
from heatshield.advisory import (
    CHECK_IN,
    Advisor,
    format_window,
    night_line,
    place_line,
    roof_line,
    sms_message,
    whatsapp_message,
    work_plan_line,
)
from heatshield.personal import may_concern, night_sensitive, personal_level, thin_roof
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


def concerned_wards(wards: list[dict], day: int) -> list[dict]:
    """Wards where some subscriber could be at High or above on the target day."""
    out = []
    for ward in wards:
        daily = ward.get("daily") or []
        if len(daily) > day and may_concern(daily[day]):
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


PLACE_KINDS = {"worker": ("water", "rest", "cooling")}  # everyone else: somewhere cool to sit


def asks_check_in(sub: dict, level: RiskLevel, day_summary: dict) -> bool:
    """Ask elderly subscribers (or anyone with a caregiver on file) to confirm they're OK on the worst days."""
    if sub.get("channel") == "sms":  # SMS replies don't reach us
        return False
    if sub.get("group") != "elderly" and not sub.get("caregiverPhone"):
        return False
    return level == RiskLevel.EXTREME or bool(day_summary.get("hotNight"))


def personal_lines(
    sub: dict, ward: dict, summary: dict, level: RiskLevel, window: str, places: list[dict], lang: str
) -> list[str]:
    """The numbers and places that make an alert actionable for this subscriber.

    The place named must be open at the day's peak hour, when people most need it.
    """
    group = sub.get("group", "elderly")
    lines = []
    if group == "worker":
        line = work_plan_line(summary.get("workPlan") or [], summary.get("wbgtMax"), lang)
        if line:
            lines.append(line)
    if thin_roof(sub):
        lines.append(roof_line(window, lang))
    if summary.get("hotNight") and night_sensitive(sub):
        lines.append(night_line(summary["nightMin"], lang))
    centroid = ward.get("centroid")
    if centroid:
        kinds = PLACE_KINDS.get(group, ("cooling",))
        near = resources.nearest(
            float(centroid[0]), float(centroid[1]), places, kinds=kinds, open_at=ist_hour(summary["peakAt"])
        )
        if near:
            lines.append(place_line(near[0]["kind"], resources.label(near[0], lang), lang))
    if asks_check_in(sub, level, summary):
        lines.append(CHECK_IN[lang])
    return lines


def dispatch(now: datetime, advisor: Advisor) -> dict:
    day = target_day(now)
    today = now.astimezone(IST).strftime("%Y-%m-%d")
    places = resources.load()
    counts = {"sent": 0, "skipped": 0, "failed": 0}
    for ward in concerned_wards(repo.list_wards(), day):
        summary = ward["daily"][day]
        subscribers = repo.subscribers_for_ward(ward["wardId"])
        if not subscribers:
            continue
        start, end = risky_window(ward["wardId"], summary)
        for sub in subscribers:
            level = personal_level(summary, sub)
            if not level.alertable:
                continue
            key = f"{summary['date']}:{level.value}:{slot(now)}"
            if not repo.claim_alert(sub["phone"], today, key, iso(now), config.MAX_ALERTS_PER_DAY):
                counts["skipped"] += 1
                continue
            lang = sub.get("language", "hi")
            window = format_window(start, end, lang)
            check_in = asks_check_in(sub, level, summary)
            if sub.get("channel") == "sms":
                result = messaging.send_sms(sub["phone"], sms_message(ward["name"], day, level.value, window, lang))
            else:
                advice = advisor.advice(level.value, window, sub.get("group", "elderly"), lang)
                extras = personal_lines(sub, ward, summary, level, window, places, lang)
                body = whatsapp_message(ward["name"], day, level.value, summary["heatIndex"], advice, lang, extras)
                result = messaging.send_whatsapp(sub["phone"], body)
            if result.ok and check_in:
                repo.set_check_in(sub["phone"], summary["date"], "asked")
            counts["sent" if result.ok else "failed"] += 1
            logger.info(
                "alert",
                extra={
                    "wardId": ward["wardId"],
                    "level": level.value,
                    "wardLevel": summary["level"],
                    "channel": sub.get("channel"),
                    "checkIn": check_in,
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
