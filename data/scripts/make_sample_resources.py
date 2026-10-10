"""Build the placeholder layer of cooling centres, water and rest points for the Delhi map.

    python data/scripts/make_sample_resources.py  ->  data/fixtures/delhi_resources.geojson

Points sit on wards of the placeholder grid, denser where vulnerability is high, so the map
and the ward action list have something to show before real data exists. Every point is
"verified": false and named "Sample ...": the alert dispatcher and the bot never send people
to an unverified place. Replace with the DDMA / MCD list of cooling centres, Jal Board water
points and platform rest points (see data/README.md), set "verified": true per point once a
ward officer has checked it, and run make seed.
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WARDS = ROOT / "fixtures" / "delhi_wards.geojson"
OUT = ROOT / "fixtures" / "delhi_resources.geojson"

KINDS = {
    "cooling": ("Sample cooling centre", "नमूना ठंडी जगह", [11, 18]),
    "water": ("Sample water point", "नमूना पानी केंद्र", None),
    "rest": ("Sample shaded rest point", "नमूना छांव विश्राम स्थल", [10, 19]),
}
COUNTS = {"cooling": 30, "water": 45, "rest": 20}


def main() -> None:
    rng = random.Random(7)
    wards = [f["properties"] for f in json.loads(WARDS.read_text())["features"]]
    weights = [w["vulnerabilityScore"] ** 2 for w in wards]
    features = []
    for kind, count in COUNTS.items():
        name, name_hi, hours = KINDS[kind]
        for i, ward in enumerate(rng.choices(wards, weights=weights, k=count), start=1):
            lon, lat = ward["centroid"]
            props = {
                "id": f"{kind[:1].upper()}-{i:03d}",
                "name": f"{name} {i}",
                "nameHi": f"{name_hi} {i}",
                "kind": kind,
                "verified": False,
                "sample": True,
            }
            if hours:
                props["hours"] = hours
            jitter = (rng.uniform(-0.004, 0.004), rng.uniform(-0.004, 0.004))
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [round(lon + jitter[0], 5), round(lat + jitter[1], 5)],
                    },
                    "properties": props,
                }
            )
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=0))
    print(f"wrote {len(features)} sample points -> {OUT}")


if __name__ == "__main__":
    main()
