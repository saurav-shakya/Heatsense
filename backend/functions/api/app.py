"""Public REST API for the map and the subscribe flow.

Routes (HTTP API -> this function):
  GET  /wards                  GeoJSON FeatureCollection, ward properties + daily risk summary
  GET  /wards/{wardId}/forecast  hourly risk timeline (today + 3 days) for one ward
  POST /subscribe              register phone, ward, group, language, channel
  POST /unsubscribe            opt out
"""

import json
import re
from datetime import UTC, datetime, timedelta
from functools import cache

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.event_handler.exceptions import BadRequestError, NotFoundError

from heatshield import config, repo
from heatshield.models import Channel, Group, Language, Subscriber
from heatshield.timeutil import iso, ist_day_start

logger = Logger()
app = APIGatewayHttpResolver()

# Indian mobile numbers in E.164 form. Widen when more countries are supported.
PHONE_RE = re.compile(r"^\+91[6-9]\d{9}$")
WARD_PROPS = ("wardId", "name", "lstOffset", "ndvi", "popDensity", "vulnerabilityScore", "daily")


@cache
def _ward_geometries() -> dict[str, dict]:
    """wardId -> GeoJSON geometry, loaded once per container from S3."""
    obj = boto3.client("s3").get_object(Bucket=config.DATA_BUCKET, Key=f"wards/{config.CITY}.geojson")
    collection = json.loads(obj["Body"].read())
    return {f["properties"]["wardId"]: f["geometry"] for f in collection["features"]}


@app.get("/wards", compress=True)
def list_wards():
    geometries = _ward_geometries()
    features = [
        {
            "type": "Feature",
            "id": ward["wardId"],
            "geometry": geometries.get(ward["wardId"]),
            "properties": {k: ward.get(k) for k in WARD_PROPS},
        }
        for ward in repo.list_wards()
        if ward["wardId"] in geometries
    ]
    return {"type": "FeatureCollection", "city": config.CITY, "features": features}


@app.get("/wards/<ward_id>/forecast")
def ward_forecast(ward_id: str):
    ward = repo.get_ward(ward_id)
    if not ward:
        raise NotFoundError(f"Unknown ward {ward_id}")
    today = ist_day_start(datetime.now(UTC))
    end = today + timedelta(days=config.FORECAST_DAYS)
    hourly = repo.get_forecast(ward_id, iso(today), iso(end))
    return {"ward": ward, "hourly": hourly}


@app.post("/subscribe")
def subscribe():
    body = app.current_event.json_body or {}
    phone = str(body.get("phone", "")).replace(" ", "")
    if not PHONE_RE.match(phone):
        raise BadRequestError("phone must be an Indian mobile number like +919876543210")
    ward_id = body.get("wardId", "")
    if not repo.get_ward(ward_id):
        raise BadRequestError(f"Unknown ward {ward_id}")
    try:
        sub = Subscriber(
            phone=phone,
            wardId=ward_id,
            group=Group(body.get("group")),
            language=Language(body.get("language", "hi")),
            channel=Channel(body.get("channel", "whatsapp")),
            createdAt=iso(datetime.now(UTC)),
        )
    except ValueError as exc:
        raise BadRequestError(str(exc)) from exc
    repo.put_subscriber(sub)
    logger.info("subscribed", extra={"wardId": ward_id, "group": sub.group.value})
    return Response(status_code=201, content_type="application/json", body=json.dumps({"ok": True}))


@app.post("/unsubscribe")
def unsubscribe():
    body = app.current_event.json_body or {}
    phone = str(body.get("phone", "")).replace(" ", "")
    if not PHONE_RE.match(phone):
        raise BadRequestError("phone must be an Indian mobile number like +919876543210")
    # Same response whether or not the number exists, so the endpoint can't be used to probe subscribers.
    repo.opt_out(phone)
    return {"ok": True}


@logger.inject_lambda_context
def handler(event, context):
    return app.resolve(event, context)
