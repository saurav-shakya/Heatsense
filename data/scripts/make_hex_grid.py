"""Build the placeholder Delhi ward layer: a ~1.5 km hex grid clipped to a rough NCT outline.

This is the PRD's fallback layout for when ward boundaries are missing. Ward attributes
(LST offset, NDVI, density) are SYNTHETIC smooth fields; Phase 1 replaces them with
values from Landsat/MODIS, Sentinel-2 and WorldPop. Every feature carries "fixture": true.

    python data/scripts/make_hex_grid.py   ->  data/fixtures/delhi_wards.geojson
"""

import json
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "fixtures" / "delhi_wards.geojson"
HEX_RADIUS_KM = 1.5
KM_PER_DEG_LAT = 110.57
KM_PER_DEG_LON = 111.32 * math.cos(math.radians(28.6))

# Very rough NCT of Delhi outline (lon, lat), clockwise from the north.
DELHI_OUTLINE = [
    (77.10, 28.88), (77.22, 28.86), (77.33, 28.73), (77.35, 28.63), (77.31, 28.55),
    (77.26, 28.50), (77.20, 28.42), (77.10, 28.41), (77.02, 28.48), (76.95, 28.52),
    (76.84, 28.57), (76.86, 28.66), (76.94, 28.76), (77.02, 28.84),
]  # fmt: skip
OLD_DELHI = (77.23, 28.66)  # dense, hot core
RIDGE = (77.17, 28.55)  # greener, cooler band


def inside(lon: float, lat: float, poly: list[tuple[float, float]]) -> bool:
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1], strict=True):
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def km_between(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot((a[0] - b[0]) * KM_PER_DEG_LON, (a[1] - b[1]) * KM_PER_DEG_LAT)


def hexagon(lon: float, lat: float) -> list[list[float]]:
    ring = []
    for i in range(7):  # 7th point closes the ring
        angle = math.radians(60 * (i % 6) + 30)  # pointy-top
        ring.append(
            [
                round(lon + HEX_RADIUS_KM * math.cos(angle) / KM_PER_DEG_LON, 5),
                round(lat + HEX_RADIUS_KM * math.sin(angle) / KM_PER_DEG_LAT, 5),
            ]
        )
    return ring


def synthetic_attributes(lon: float, lat: float, rng: random.Random) -> dict:
    core = math.exp(-((km_between((lon, lat), OLD_DELHI) / 9) ** 2))
    green = math.exp(-((km_between((lon, lat), RIDGE) / 5) ** 2))
    pop_density = round(4000 + 40000 * core + rng.uniform(-2500, 2500))
    ndvi = round(min(max(0.12 + 0.45 * green - 0.08 * core + rng.uniform(-0.04, 0.04), 0.02), 0.7), 3)
    lst_offset = round(4.5 * core - 4.0 * green + rng.uniform(-0.8, 0.8), 2)
    # V: denser is worse, greener is better (weights placeholder until Phase 2).
    density_n = min(pop_density / 45000, 1.0)
    green_n = 1 - min(ndvi / 0.6, 1.0)
    vulnerability = round(min(max(0.55 * density_n + 0.45 * green_n, 0.05), 1.0), 3)
    return {"lstOffset": lst_offset, "ndvi": ndvi, "popDensity": pop_density, "vulnerabilityScore": vulnerability}


def main() -> None:
    rng = random.Random(42)
    lons = [p[0] for p in DELHI_OUTLINE]
    lats = [p[1] for p in DELHI_OUTLINE]
    dx = math.sqrt(3) * HEX_RADIUS_KM / KM_PER_DEG_LON
    dy = 1.5 * HEX_RADIUS_KM / KM_PER_DEG_LAT

    features = []
    row, lat = 0, min(lats)
    while lat <= max(lats):
        lon = min(lons) + (dx / 2 if row % 2 else 0)
        while lon <= max(lons):
            if inside(lon, lat, DELHI_OUTLINE):
                ward_id = f"DL-{len(features) + 1:03d}"
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": [hexagon(lon, lat)]},
                        "properties": {
                            "wardId": ward_id,
                            "name": f"Grid cell {len(features) + 1:03d}",
                            "fixture": True,
                            "centroid": [round(lon, 5), round(lat, 5)],
                            **synthetic_attributes(lon, lat, rng),
                        },
                    }
                )
            lon += dx
        lat += dy
        row += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")))
    print(f"wrote {len(features)} cells -> {OUT}")


if __name__ == "__main__":
    main()
