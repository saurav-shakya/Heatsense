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

# Sticky replay date (YYYY-MM-DD) for an off-season demo; empty = live forecasts.
REPLAY_DATE = os.environ.get("REPLAY_DATE", "")
STAGE = os.environ.get("STAGE", "dev")
# Public web map, linked from alerts and bot replies.
SITE_URL = os.environ.get("SITE_URL", "https://heatshield.pages.dev")

# Alerts
MAX_ALERTS_PER_DAY = 2
# "bedrock" writes advisories with Claude on Amazon Bedrock; "template" uses the fixed texts only.
ADVISORY_MODE = os.environ.get("ADVISORY_MODE", "template")
ADVISORY_MODEL_ID = os.environ.get("ADVISORY_MODEL_ID", "anthropic.claude-opus-5-5")
AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
# SSM prefix holding the Twilio SecureStrings: account-sid, auth-token, whatsapp-from.
TWILIO_SSM_PREFIX = os.environ.get("TWILIO_SSM_PREFIX", f"/heatshield/{STAGE}/twilio")
