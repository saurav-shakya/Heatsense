import json

import pytest
from conftest import load_function


def http_event(method: str, path: str, body: dict | None = None, path_params: dict | None = None) -> dict:
    return {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {"content-type": "application/json"},
        "requestContext": {"http": {"method": method, "path": path}, "stage": "$default"},
        "pathParameters": path_params or {},
        "body": json.dumps(body) if body is not None else None,
        "isBase64Encoded": False,
    }


@pytest.fixture
def api(aws):
    return load_function("api")


@pytest.fixture
def engine(aws):
    return load_function("risk_engine")


def test_list_wards_returns_geojson_with_daily_summary(api, engine, ctx):
    engine.handler({}, ctx)
    resp = api.handler(http_event("GET", "/wards"), ctx)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["type"] == "FeatureCollection"
    assert body["replayOf"] is None
    assert {f["id"] for f in body["features"]} == {"DL-001", "DL-002"}
    daily = body["features"][0]["properties"]["daily"]
    assert len(daily) == 4
    assert {"date", "risk", "level"} <= daily[0].keys()


def test_forecast_returns_96_hourly_rows(api, engine, ctx):
    engine.handler({}, ctx)
    resp = api.handler(http_event("GET", "/wards/DL-001/forecast", path_params={"wardId": "DL-001"}), ctx)
    assert resp["statusCode"] == 200
    assert len(json.loads(resp["body"])["hourly"]) == 96


def test_forecast_unknown_ward_is_404(api, ctx):
    resp = api.handler(http_event("GET", "/wards/NOPE/forecast", path_params={"wardId": "NOPE"}), ctx)
    assert resp["statusCode"] == 404


def test_subscribe_then_unsubscribe(api, ctx):
    from heatshield import repo

    sub = {"phone": "+919876543210", "wardId": "DL-001", "group": "worker", "language": "hi", "channel": "whatsapp"}
    assert api.handler(http_event("POST", "/subscribe", sub), ctx)["statusCode"] == 201
    assert [s["phone"] for s in repo.subscribers_for_ward("DL-001")] == ["+919876543210"]

    assert api.handler(http_event("POST", "/unsubscribe", {"phone": "+919876543210"}), ctx)["statusCode"] == 200
    assert repo.subscribers_for_ward("DL-001") == []


@pytest.mark.parametrize(
    "patch",
    [{"phone": "12345"}, {"wardId": "NOPE"}, {"group": "astronaut"}, {"language": "fr"}],
)
def test_subscribe_rejects_bad_input(api, ctx, patch):
    sub = {"phone": "+919876543210", "wardId": "DL-001", "group": "worker", "language": "hi", "channel": "whatsapp"}
    resp = api.handler(http_event("POST", "/subscribe", {**sub, **patch}), ctx)
    assert resp["statusCode"] == 400


def test_subscribe_with_thin_roof_and_caregiver(api, ctx):
    from heatshield import repo

    sub = {
        "phone": "+919876543210",
        "wardId": "DL-001",
        "group": "elderly",
        "language": "hi",
        "channel": "whatsapp",
        "home": "tin",
        "caregiverPhone": "+91 98111 11111",
    }
    assert api.handler(http_event("POST", "/subscribe", sub), ctx)["statusCode"] == 201
    stored = repo.get_subscriber("+919876543210")
    assert stored["home"] == "tin" and stored["caregiverPhone"] == "+919811111111"


@pytest.mark.parametrize("patch", [{"home": "castle"}, {"caregiverPhone": "123"}, {"caregiverPhone": "+919876543210"}])
def test_subscribe_rejects_bad_profile(api, ctx, patch):
    sub = {"phone": "+919876543210", "wardId": "DL-001", "group": "elderly", "language": "hi", "channel": "whatsapp"}
    assert api.handler(http_event("POST", "/subscribe", {**sub, **patch}), ctx)["statusCode"] == 400


def test_resources_lists_points_including_samples(api, ctx):
    from conftest import put_resources

    put_resources()
    body = json.loads(api.handler(http_event("GET", "/resources"), ctx)["body"])
    assert {f["id"] for f in body["features"]} == {"CC-1", "W-1", "S-1"}
    sample = next(f for f in body["features"] if f["id"] == "S-1")
    assert sample["properties"]["verified"] is False and sample["geometry"]["type"] == "Point"


def test_officer_checkins_are_counts_without_phone_numbers(api, ctx):
    from heatshield import repo
    from heatshield.models import Channel, Group, Language, Subscriber

    for i, status in enumerate(["asked", "ok", "help", "asked"]):
        phone = f"+91980000001{i}"
        repo.put_subscriber(Subscriber(phone, "DL-001", Group.ELDERLY, Language.HI, Channel.WHATSAPP))
        repo.set_check_in(phone, "2026-05-28", status)
    event = http_event("GET", "/officer/checkins")
    event["rawQueryString"] = "date=2026-05-28"
    event["queryStringParameters"] = {"date": "2026-05-28"}
    resp = api.handler(event, ctx)
    body = json.loads(resp["body"])
    assert body["wards"] == [{"wardId": "DL-001", "asked": 4, "ok": 1, "help": 1, "noReply": 2}]
    assert "+91" not in resp["body"]
