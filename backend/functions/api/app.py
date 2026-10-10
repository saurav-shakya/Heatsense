"""Public REST API for the map and the subscribe flow.

Routes (HTTP API -> this function):
  GET  /wards                  GeoJSON FeatureCollection, ward properties + daily risk summary;
                               top-level replayOf is set while scores come from a past heatwave
  GET  /wards/{wardId}/forecast  hourly risk timeline (today + 3 days) for one ward
  POST /subscribe              register phone, ward, group, language, channel, and optionally
                               home (pucca | tin) and caregiverPhone
  POST /unsubscribe            opt out
  GET  /resources              cooling centres, water and rest points (GeoJSON points)
  GET  /officer/checkins       wellbeing check-ins per ward for an IST date (?date=YYYY-MM-DD):
                               counts only, never phone numbers
"""

import json
import re
from datetime import UTC, datetime, timedelta
from functools import cache

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.event_handler.exceptions import BadRequestError, NotFoundError

from heatshield import config, repo, resources
from heatshield.models import Channel, Group, Home, Language, Subscriber
from heatshield.timeutil import IST, iso, ist_day_start

logger = Logger()
app = APIGatewayHttpResolver()

# Indian mobile numbers in E.164 form. Widen when more countries are supported.
PHONE_RE = re.compile(r"^\+91[6-9]\d{9}$")
WARD_PROPS = ("wardId", "name", "lstOffset", "ndvi", "popDensity", "vulnerabilityScore", "daily", "fixture")


@cache
def _ward_geometries() -> dict[str, dict]:
    """wardId -> GeoJSON geometry, loaded once per container from S3."""
    obj = boto3.client("s3").get_object(Bucket=config.DATA_BUCKET, Key=f"wards/{config.CITY}.geojson")
    collection = json.loads(obj["Body"].read())
    return {f["properties"]["wardId"]: f["geometry"] for f in collection["features"]}


@app.get("/wards", compress=True)
def list_wards():
    geometries = _ward_geometries()
    wards = repo.list_wards()
    features = [
        {
            "type": "Feature",
            "id": ward["wardId"],
            "geometry": geometries.get(ward["wardId"]),
            "properties": {k: ward.get(k) for k in WARD_PROPS},
        }
        for ward in wards
        if ward["wardId"] in geometries
    ]
    replay_of = next((w["replayOf"] for w in wards if w.get("replayOf")), None)
    return {"type": "FeatureCollection", "city": config.CITY, "replayOf": replay_of, "features": features}


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
    caregiver = str(body.get("caregiverPhone") or "").replace(" ", "") or None
    if caregiver and (not PHONE_RE.match(caregiver) or caregiver == phone):
        raise BadRequestError("caregiverPhone must be a different Indian mobile number like +919876543210")
    try:
        sub = Subscriber(
            phone=phone,
            wardId=ward_id,
            group=Group(body.get("group")),
            language=Language(body.get("language", "hi")),
            channel=Channel(body.get("channel", "whatsapp")),
            home=Home(body["home"]) if body.get("home") else None,
            caregiverPhone=caregiver,
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


@app.get("/resources", compress=True)
def list_resources():
    features = [
        {
            "type": "Feature",
            "id": r.get("id"),
            "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
            "properties": {k: v for k, v in r.items() if k not in ("lon", "lat")},
        }
        for r in resources.load()
    ]
    return {"type": "FeatureCollection", "city": config.CITY, "features": features}


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@app.get("/officer/checkins")
def check_ins():
    """Per ward: how many people were asked to check in on `date`, and how many said OK, SOS or nothing."""
    date = app.current_event.get_query_string_value("date") or datetime.now(UTC).astimezone(IST).strftime("%Y-%m-%d")
    if not DATE_RE.match(date):
        raise BadRequestError("date must be YYYY-MM-DD")
    wards: dict[str, dict[str, int]] = {}
    for sub in repo.all_subscribers():
        if sub.get("checkInDate") != date or not sub.get("checkInStatus"):
            continue
        counts = wards.setdefault(sub["wardId"], {"asked": 0, "ok": 0, "help": 0, "noReply": 0})
        status = sub["checkInStatus"]
        counts["asked"] += 1
        counts["noReply" if status == "asked" else status] += 1
    ranked = sorted(wards.items(), key=lambda kv: (-kv[1]["help"], -kv[1]["noReply"]))
    return {"date": date, "wards": [{"wardId": w, **c} for w, c in ranked]}


@logger.inject_lambda_context
def handler(event, context):
    return app.resolve(event, context)
