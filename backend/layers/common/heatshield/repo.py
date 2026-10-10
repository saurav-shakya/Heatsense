"""Thin DynamoDB access layer. Handlers call these instead of boto3 directly."""

from functools import cache

import boto3
from boto3.dynamodb.conditions import Key

from heatshield import config
from heatshield.models import RiskForecast, Subscriber, Ward, from_ddb, to_ddb


@cache
def _ddb():
    return boto3.resource("dynamodb")


def _table(name: str):
    return _ddb().Table(name)


def _scan_all(table) -> list[dict]:
    items, kwargs = [], {}
    while True:
        page = table.scan(**kwargs)
        items.extend(page.get("Items", []))
        if "LastEvaluatedKey" not in page:
            return items
        kwargs["ExclusiveStartKey"] = page["LastEvaluatedKey"]


# --- Wards -----------------------------------------------------------------


def list_wards() -> list[dict]:
    return from_ddb(_scan_all(_table(config.WARDS_TABLE)))


def get_ward(ward_id: str) -> dict | None:
    item = _table(config.WARDS_TABLE).get_item(Key={"wardId": ward_id}).get("Item")
    return from_ddb(item) if item else None


def put_wards(wards: list[Ward]) -> None:
    with _table(config.WARDS_TABLE).batch_writer() as batch:
        for ward in wards:
            batch.put_item(Item=ward.to_item())


def set_ward_daily(ward_id: str, daily: list[dict]) -> None:
    """Store the per-day peak risk summary on the ward row (read by GET /wards)."""
    _table(config.WARDS_TABLE).update_item(
        Key={"wardId": ward_id},
        UpdateExpression="SET daily = :d",
        ExpressionAttributeValues={":d": to_ddb(daily)},
    )


# --- Risk forecasts --------------------------------------------------------


def put_forecasts(forecasts: list[RiskForecast]) -> None:
    with _table(config.FORECASTS_TABLE).batch_writer() as batch:
        for f in forecasts:
            batch.put_item(Item=f.to_item())


def get_forecast(ward_id: str, start: str, end: str) -> list[dict]:
    """Forecast rows for one ward with start <= forecastTime < end (ISO strings sort lexically)."""
    resp = _table(config.FORECASTS_TABLE).query(
        KeyConditionExpression=Key("wardId").eq(ward_id) & Key("forecastTime").between(start, end),
    )
    return [r for r in from_ddb(resp.get("Items", [])) if r["forecastTime"] < end]


# --- Subscribers -----------------------------------------------------------


def put_subscriber(sub: Subscriber) -> None:
    _table(config.SUBSCRIBERS_TABLE).put_item(Item=sub.to_item())


def opt_out(phone: str) -> bool:
    """Mark a subscriber opted out. Returns False if the phone isn't subscribed."""
    table = _table(config.SUBSCRIBERS_TABLE)
    try:
        table.update_item(
            Key={"phone": phone},
            UpdateExpression="SET optedIn = :f",
            ConditionExpression="attribute_exists(phone)",
            ExpressionAttributeValues={":f": False},
        )
        return True
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return False


def subscribers_for_ward(ward_id: str) -> list[dict]:
    resp = _table(config.SUBSCRIBERS_TABLE).query(
        IndexName="byWard",
        KeyConditionExpression=Key("wardId").eq(ward_id),
    )
    return [s for s in from_ddb(resp.get("Items", [])) if s.get("optedIn")]
