"""Load a city's ward layer into the deployed stack: GeoJSON -> S3, attributes -> Wards table.

    AWS_PROFILE=saurav-cli python data/scripts/seed.py [--stack heatshield-dev] [--city delhi] [--file ...]

Resource names come from the CloudFormation stack outputs, so nothing is hard-coded.
"""

import argparse
import json
from decimal import Decimal
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parent.parent
WARD_FIELDS = ("lstOffset", "ndvi", "popDensity", "vulnerabilityScore")


def ring_centroid(ring: list[list[float]]) -> tuple[float, float, float]:
    """(signed area, cx, cy) of a closed lon/lat ring (shoelace formula; fine at ward scale)."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:], strict=False):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a /= 2
    if a == 0:
        return 0.0, ring[0][0], ring[0][1]
    return a, cx / (6 * a), cy / (6 * a)


def centroid(geometry: dict) -> list[float]:
    """Area-weighted centroid [lon, lat] of a Polygon or MultiPolygon (outer rings)."""
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    parts = [ring_centroid(poly[0]) for poly in polygons]
    total = sum(abs(a) for a, _, _ in parts) or 1.0
    lon = sum(abs(a) * x for a, x, _ in parts) / total
    lat = sum(abs(a) * y for a, _, y in parts) / total
    return [round(lon, 5), round(lat, 5)]


def stack_outputs(cfn, stack: str) -> dict[str, str]:
    outputs = cfn.describe_stacks(StackName=stack)["Stacks"][0]["Outputs"]
    return {o["OutputKey"]: o["OutputValue"] for o in outputs}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stack", default="heatshield-dev")
    parser.add_argument("--city", default="delhi")
    parser.add_argument("--file", type=Path, default=ROOT / "fixtures" / "delhi_wards.geojson")
    parser.add_argument(
        "--resources",
        type=Path,
        default=ROOT / "fixtures" / "delhi_resources.geojson",
        help="cooling centres, water and rest points (GeoJSON points); skipped if the file is missing",
    )
    args = parser.parse_args()

    session = boto3.Session()
    out = stack_outputs(session.client("cloudformation"), args.stack)
    bucket, table_name = out["DataBucketName"], out["WardsTableName"]

    collection = json.loads(args.file.read_text())
    geometry_key = f"wards/{args.city}.geojson"

    # The map only needs geometry + id + name; attributes are served from DynamoDB.
    slim = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": f["geometry"],
                "properties": {"wardId": f["properties"]["wardId"], "name": f["properties"]["name"]},
            }
            for f in collection["features"]
        ],
    }
    session.client("s3").put_object(
        Bucket=bucket,
        Key=geometry_key,
        Body=json.dumps(slim, separators=(",", ":")).encode(),
        ContentType="application/geo+json",
    )

    table = session.resource("dynamodb").Table(table_name)
    with table.batch_writer(overwrite_by_pkeys=["wardId"]) as batch:
        for f in collection["features"]:
            p = f["properties"]
            item = {
                "wardId": p["wardId"],
                "name": p["name"],
                "city": args.city,
                "geometryS3Key": geometry_key,
                **{k: Decimal(str(p[k])) for k in WARD_FIELDS},
                "centroid": [Decimal(str(c)) for c in (p.get("centroid") or centroid(f["geometry"]))],
                "fixture": bool(p.get("fixture", False)),
            }
            batch.put_item(Item=item)

    print(f"seeded {len(collection['features'])} wards -> s3://{bucket}/{geometry_key} + {table_name}")

    if args.resources.exists():
        key = f"resources/{args.city}.geojson"
        body = args.resources.read_bytes()
        session.client("s3").put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/geo+json")
        print(f"seeded {len(json.loads(body)['features'])} places -> s3://{bucket}/{key}")


if __name__ == "__main__":
    main()
