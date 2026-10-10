"""Alert dispatcher: finds High/Extreme wards and the subscribers who should hear about it.

Triggered by the risk engine's RiskScoresUpdated event and by 07:00 / 19:00 IST schedules.

SKELETON: logs the alerts it *would* send. Phase 3 adds Bedrock-written advisories,
Twilio WhatsApp / SNS SMS delivery, and the 2-per-day cap via lastAlertAt.
"""

from datetime import UTC, datetime

from aws_lambda_powertools import Logger

from heatshield import repo
from heatshield.risk import RiskLevel
from heatshield.timeutil import IST

logger = Logger()

QUIET_START_HOUR = 22  # never alert 22:00-06:00 IST
QUIET_END_HOUR = 6


def in_quiet_hours(now: datetime) -> bool:
    hour = now.astimezone(IST).hour
    return hour >= QUIET_START_HOUR or hour < QUIET_END_HOUR


def target_day(now: datetime) -> int:
    """Index into ward.daily: evening runs warn about tomorrow, earlier runs about today."""
    return 1 if now.astimezone(IST).hour >= 17 else 0


def alertable_wards(wards: list[dict], day: int) -> list[dict]:
    out = []
    for ward in wards:
        daily = ward.get("daily") or []
        if len(daily) > day and RiskLevel(daily[day]["level"]).alertable:
            out.append(ward)
    return out


@logger.inject_lambda_context
def handler(event, context):
    now = datetime.now(UTC)
    if in_quiet_hours(now):
        logger.info("quiet hours, skipping")
        return {"sent": 0, "skipped": "quiet-hours"}

    day = target_day(now)
    planned = 0
    for ward in alertable_wards(repo.list_wards(), day):
        level = ward["daily"][day]["level"]
        for sub in repo.subscribers_for_ward(ward["wardId"]):
            planned += 1
            logger.info(
                "would alert",
                extra={"wardId": ward["wardId"], "level": level, "group": sub["group"], "channel": sub["channel"]},
            )
    logger.info("dispatch done", extra={"trigger": event.get("detail-type", "schedule"), "planned": planned})
    return {"sent": 0, "planned": planned}
