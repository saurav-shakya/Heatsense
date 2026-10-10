import importlib.util
import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

# Must be set before heatshield.config is imported anywhere.
os.environ.update(
    AWS_DEFAULT_REGION="us-east-1",
    AWS_ACCESS_KEY_ID="testing",
    AWS_SECRET_ACCESS_KEY="testing",
    WARDS_TABLE="wards",
    FORECASTS_TABLE="forecasts",
    SUBSCRIBERS_TABLE="subscribers",
    DATA_BUCKET="data",
    EVENT_BUS_NAME="heatshield-test",
    CITY="delhi",
    POWERTOOLS_SERVICE_NAME="heatshield",
)

FUNCTIONS = Path(__file__).parent.parent / "functions"


def load_function(name: str):
    """Import functions/<name>/app.py under a unique module name (they're all called app.py)."""
    spec = importlib.util.spec_from_file_location(f"fn_{name}", FUNCTIONS / name / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeContext:
    function_name = "test"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
    aws_request_id = "req-1"


@pytest.fixture
def ctx():
    return FakeContext()


SAMPLE_WARDS = [
    {"wardId": "DL-001", "name": "Sample A", "lstOffset": 3.0, "vulnerabilityScore": 0.9, "centroid": [77.23, 28.66]},
    {"wardId": "DL-002", "name": "Sample B", "lstOffset": -2.0, "vulnerabilityScore": 0.3, "centroid": [77.1, 28.5]},
]


def fake_open_meteo(peak_c: float = 44.0, rh: float = 20.0):
    """Stand-in for weather._get_json: an Open-Meteo-shaped multi-location response for the asked dates.

    Air temperature follows a diurnal curve peaking at peak_c around 14:00 IST (08:30 UTC).
    """

    def get_json(url: str, params: dict) -> object:
        start = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end = datetime.strptime(params["end_date"], "%Y-%m-%d") + timedelta(days=1)
        hours = [start + timedelta(hours=h) for h in range(int((end - start).total_seconds() // 3600))]
        temps = [
            round(peak_c - 12 + 12 * max(0.0, math.sin(math.pi * ((t.hour + 5.5) % 24 - 6) / 16)), 1) for t in hours
        ]
        location = {
            "latitude": 28.625,
            "longitude": 77.25,
            "generationtime_ms": 0.1,
            "utc_offset_seconds": 0,
            "timezone": "GMT",
            "hourly_units": {"time": "iso8601", "temperature_2m": "°C", "relative_humidity_2m": "%"},
            "hourly": {
                "time": [t.strftime("%Y-%m-%dT%H:%M") for t in hours],
                "temperature_2m": temps,
                "relative_humidity_2m": [rh] * len(hours),
            },
        }
        n = len(params["latitude"].split(","))
        return [location] * n if n > 1 else location

    return get_json


@pytest.fixture(autouse=True)
def hot_weather(monkeypatch):
    """No test reaches the real Open-Meteo or Bedrock."""
    from heatshield import advisory, weather

    monkeypatch.setattr(weather, "_get_json", fake_open_meteo())
    monkeypatch.setattr(advisory, "_client", _RefusingClient)


class _RefusingClient:
    """Bedrock stand-in that declines everything, so callers take their fallback path."""

    def __init__(self):
        self.messages = self

    def create(self, **kwargs):
        from types import SimpleNamespace

        return SimpleNamespace(stop_reason="refusal", content=[])


@pytest.fixture
def aws():
    with mock_aws():
        ddb = boto3.client("dynamodb")
        ddb.create_table(
            TableName="wards",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[{"AttributeName": "wardId", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "wardId", "KeyType": "HASH"}],
        )
        ddb.create_table(
            TableName="forecasts",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "wardId", "AttributeType": "S"},
                {"AttributeName": "forecastTime", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "wardId", "KeyType": "HASH"},
                {"AttributeName": "forecastTime", "KeyType": "RANGE"},
            ],
        )
        ddb.create_table(
            TableName="subscribers",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "phone", "AttributeType": "S"},
                {"AttributeName": "wardId", "AttributeType": "S"},
            ],
            KeySchema=[{"AttributeName": "phone", "KeyType": "HASH"}],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "byWard",
                    "KeySchema": [{"AttributeName": "wardId", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )
        boto3.client("events").create_event_bus(Name="heatshield-test")

        from heatshield import messaging, repo
        from heatshield.models import Ward

        repo._ddb.cache_clear()
        messaging.twilio_credentials.cache_clear()
        repo.put_wards(
            [
                Ward(city="delhi", geometryS3Key="wards/delhi.geojson", ndvi=0.2, popDensity=20000.0, **w)
                for w in SAMPLE_WARDS
            ]
        )

        s3 = boto3.client("s3")
        s3.create_bucket(Bucket="data")
        square = {"type": "Polygon", "coordinates": [[[77.2, 28.6], [77.21, 28.6], [77.21, 28.61], [77.2, 28.6]]]}
        geo = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": square, "properties": {"wardId": w["wardId"]}} for w in SAMPLE_WARDS
            ],
        }
        s3.put_object(Bucket="data", Key="wards/delhi.geojson", Body=json.dumps(geo))
        yield
        repo._ddb.cache_clear()
