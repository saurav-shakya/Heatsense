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


def stack_outputs(cfn, stack: str) -> dict[str, str]:
    outputs = cfn.describe_stacks(StackName=stack)["Stacks"][0]["Outputs"]
    return {o["OutputKey"]: o["OutputValue"] for o in outputs}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stack", default="heatshield-dev")
    parser.add_argument("--city", default="delhi")
    parser.add_argument("--file", type=Path, default=ROOT / "fixtures" / "delhi_wards.geojson")
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
            }
            batch.put_item(Item=item)

    print(f"seeded {len(collection['features'])} wards -> s3://{bucket}/{geometry_key} + {table_name}")


if __name__ == "__main__":
    main()
