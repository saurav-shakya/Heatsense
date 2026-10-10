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
