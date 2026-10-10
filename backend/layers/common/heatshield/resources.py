"""Places people can go when it's hot: cooling centres, drinking-water points, shaded rest points.

An alert that only says "stay cool" leaves the person to work out where. Alerts, the bot and
the map name the nearest open place instead. The layer is a GeoJSON FeatureCollection of
points at s3://<bucket>/resources/<city>.geojson, each with properties:

    {"id": "CC-001", "name": "...", "nameHi": "...", "kind": "cooling" | "water" | "rest",
     "hours": [11, 18],          # IST opening hours [open, close), omitted = always open
     "verified": true}           # false for sample points: shown on the map, never in alerts

Delhi's Heat Action Plan lists cooling centres and water points by district; ward officers
load and verify them (see data/README.md).
"""

import json
import math
from functools import cache

import boto3

from heatshield import config

KINDS = ("cooling", "water", "rest")
NEAREST_MAX_KM = 2.0  # walking distance; anything further isn't worth naming in an alert


def key(city: str | None = None) -> str:
    return f"resources/{city or config.CITY}.geojson"


@cache
def load() -> list[dict]:
    """All resource points as flat dicts with lon/lat, loaded once per container. [] if none are stored."""
    try:
        obj = boto3.client("s3").get_object(Bucket=config.DATA_BUCKET, Key=key())
    except Exception:
        return []
    return from_geojson(json.loads(obj["Body"].read()))


def from_geojson(collection: dict) -> list[dict]:
    out = []
    for f in collection.get("features", []):
        props = f.get("properties") or {}
        if (f.get("geometry") or {}).get("type") != "Point" or props.get("kind") not in KINDS:
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        out.append({**props, "lon": float(lon), "lat": float(lat), "verified": bool(props.get("verified"))})
    return out


def km_between(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance in km (haversine)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def is_open(resource: dict, ist_hour: int) -> bool:
    hours = resource.get("hours")
    if not hours:
        return True
    start, end = int(hours[0]), int(hours[1])
    return start <= ist_hour < end if start < end else ist_hour >= start or ist_hour < end


def nearest(
    lon: float,
    lat: float,
    resources: list[dict],
    *,
    kinds: tuple[str, ...] = KINDS,
    max_km: float = NEAREST_MAX_KM,
    verified_only: bool = True,
    open_at: int | None = None,
    limit: int = 1,
) -> list[dict]:
    """The closest resources within max_km, nearest first, each with a "km" field."""
    found = []
    for r in resources:
        if r["kind"] not in kinds or (verified_only and not r["verified"]):
            continue
        if open_at is not None and not is_open(r, open_at):
            continue
        km = km_between(lon, lat, r["lon"], r["lat"])
        if km <= max_km:
            found.append({**r, "km": round(km, 1)})
    return sorted(found, key=lambda r: r["km"])[:limit]


def label(resource: dict, lang: str) -> str:
    """'Name (1.2 km)' in the subscriber's language."""
    name = resource.get("nameHi") if lang == "hi" and resource.get("nameHi") else resource["name"]
    dist = f"{resource['km']:.1f} किमी" if lang == "hi" else f"{resource['km']:.1f} km"
    return f"{name} ({dist})"
