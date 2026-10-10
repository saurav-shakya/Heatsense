"""Score every ward once, locally, and save the result as static JSON for the web map.

    cd backend && uv run python ../data/scripts/build_snapshot.py [--replay 2024-05-28]

The frontend reads these files when it is built without VITE_API_URL (or when the live API
is unreachable), so the map can be hosted on its own, e.g. on Vercel. It uses the same code
as the risk engine Lambda, but needs no AWS account: weather comes straight from Open-Meteo.
--replay scores from a past heatwave shifted onto today instead of the live forecast.

Writes frontend/public/snapshot/wards.json (the GET /wards shape) and
frontend/public/snapshot/forecast/<wardId>.json (the GET /wards/{id}/forecast shape).
"""

import argparse
import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "backend" / "layers" / "common"))
sys.path.insert(0, str(REPO / "backend" / "functions" / "risk_engine"))

from app import build_forecasts, daily_summary, forecast_hours  # noqa: E402
from seed import centroid  # noqa: E402

from heatshield import config, weather  # noqa: E402
from heatshield.timeutil import IST, iso, ist_day_start  # noqa: E402

WARD_PROPS = ("wardId", "name", "lstOffset", "ndvi", "popDensity", "vulnerabilityScore", "fixture")


def get_weather(wards: list[dict], now: datetime, replay: str) -> dict:
    points = weather.grid_points(wards, config.CITY)
    if not replay:
        return weather.fetch_forecast(points, ist_day_start(now), config.FORECAST_DAYS)
    day = date.fromisoformat(replay)
    pack = weather.fetch_archive(points, str(day - timedelta(days=1)), str(day + timedelta(days=3)))
    return weather.shift_days(pack, (now.astimezone(IST).date() - day).days)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=ROOT / "fixtures" / "delhi_wards.geojson")
    parser.add_argument("--out", type=Path, default=REPO / "frontend" / "public" / "snapshot")
    parser.add_argument("--replay", default="", help="score from this past heatwave (YYYY-MM-DD) instead")
    args = parser.parse_args()

    now = datetime.now(UTC)
    features = json.loads(args.file.read_text())["features"]
    wards = [
        {**f["properties"], "centroid": f["properties"].get("centroid") or centroid(f["geometry"])} for f in features
    ]
    index = weather.WeatherIndex(get_weather(wards, now, args.replay))
    if not index.covers(forecast_hours(now)):
        print("warning: weather does not cover the whole forecast window", file=sys.stderr)

    (args.out / "forecast").mkdir(parents=True, exist_ok=True)
    out_features = []
    for feature, ward in zip(features, wards, strict=True):
        rows = build_forecasts(ward, now, index)
        props = {k: ward[k] for k in WARD_PROPS if k in ward}
        props["daily"] = daily_summary(rows) or None
        hourly = [{k: getattr(r, k) for k in ("forecastTime", "heatIndex", "hazard", "risk", "level")} for r in rows]
        out_features.append(
            {"type": "Feature", "id": ward["wardId"], "geometry": feature["geometry"], "properties": props}
        )
        (args.out / "forecast" / f"{ward['wardId']}.json").write_text(
            json.dumps({"ward": props, "hourly": hourly}, separators=(",", ":"))
        )

    collection = {
        "type": "FeatureCollection",
        "city": config.CITY,
        "replayOf": args.replay or None,
        "snapshotAt": iso(now),
        "features": out_features,
    }
    (args.out / "wards.json").write_text(json.dumps(collection, separators=(",", ":")))
    scored = sum(1 for f in out_features if f["properties"]["daily"])
    print(f"scored {scored}/{len(out_features)} wards -> {args.out}")


if __name__ == "__main__":
    main()
