"""Fetch a past heatwave's hourly weather from the Open-Meteo archive for replay mode.

    cd backend && uv run python ../data/scripts/fetch_replay.py --date 2024-05-28 [--upload]

Writes data/processed/replay/<city>/<date>.json (the risk engine's "weather pack" format)
covering <date> - 1 to <date> + 3, so that after shifting <date> onto today the whole
4-day IST window is covered. --upload copies it to s3://<DataBucket>/replay/<city>/<date>.json.
Then score from it with `make replay DATE=<date>`.
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "backend" / "layers" / "common"))

from seed import centroid, stack_outputs  # noqa: E402

from heatshield import weather  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="first day of the heatwave to replay, YYYY-MM-DD")
    parser.add_argument("--city", default="delhi")
    parser.add_argument("--file", type=Path, default=ROOT / "fixtures" / "delhi_wards.geojson")
    parser.add_argument("--stack", default="heatshield-dev")
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()

    day = date.fromisoformat(args.date)
    features = json.loads(args.file.read_text())["features"]
    wards = [{"centroid": f["properties"].get("centroid") or centroid(f["geometry"])} for f in features]
    points = weather.grid_points(wards, args.city)
    pack = weather.fetch_archive(points, str(day - timedelta(days=1)), str(day + timedelta(days=3)))
    pack["replayOf"] = args.date

    out = ROOT / "processed" / "replay" / args.city / f"{args.date}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, separators=(",", ":")))
    peak = max(max(t for t in p["temperature"] if t is not None) for p in pack["points"])
    print(f"{len(points)} grid points, peak air temperature {peak} degC -> {out}")

    if args.upload:
        session = boto3.Session()
        bucket = stack_outputs(session.client("cloudformation"), args.stack)["DataBucketName"]
        key = f"replay/{args.city}/{args.date}.json"
        session.client("s3").put_object(Bucket=bucket, Key=key, Body=out.read_bytes(), ContentType="application/json")
        print(f"uploaded -> s3://{bucket}/{key}")


if __name__ == "__main__":
    main()
