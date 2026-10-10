"""Runtime configuration, read from Lambda environment variables set in template.yaml."""

import os

WARDS_TABLE = os.environ.get("WARDS_TABLE", "heatshield-wards")
FORECASTS_TABLE = os.environ.get("FORECASTS_TABLE", "heatshield-risk-forecasts")
SUBSCRIBERS_TABLE = os.environ.get("SUBSCRIBERS_TABLE", "heatshield-subscribers")
DATA_BUCKET = os.environ.get("DATA_BUCKET", "")
EVENT_BUS_NAME = os.environ.get("EVENT_BUS_NAME", "default")
CITY = os.environ.get("CITY", "delhi")

# How many days of forecast (today + N) the risk engine produces and the API serves.
FORECAST_DAYS = 4
# Forecast rows expire this long after generation so the table never grows unbounded.
FORECAST_TTL_SECONDS = 5 * 24 * 3600

EVENT_SOURCE = "heatshield.risk"
EVENT_DETAIL_TYPE = "RiskScoresUpdated"
