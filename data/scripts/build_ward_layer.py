# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy>=2", "rasterio>=1.4", "shapely>=2", "pyproj>=3.6"]
# ///
"""Phase 1: build the real ward layer from ward boundaries and three rasters.

    uv run data/scripts/build_ward_layer.py \\
        --wards data/raw/delhi_wards.geojson --id-field Ward_No --name-field Ward_Name \\
        --lst data/raw/delhi_lst_summer_c.tif --ndvi data/raw/delhi_ndvi_summer.tif \\
        --pop data/raw/ind_ppp_2020_delhi.tif [--groups data/raw/ward_groups.csv] \\
        --out data/processed/delhi_wards.geojson

Rasters must be single-band GeoTIFFs in EPSG:4326 (export them that way from Earth Engine,
see data/README.md):
  --lst   mean summer land surface temperature in degC (Landsat 8/9 C2 L2 ST_B10)
  --ndvi  mean summer NDVI (Sentinel-2 L2A)
  --pop   WorldPop people per pixel (100 m)
  --groups optional CSV "wardId,vulnerableShare" (children under 6 + people over 60, 0..1)

Per ward it writes lstOffset (ward mean LST - city mean), ndvi, popDensity (people/km^2),
vulnerabilityScore (data/scripts/vulnerability.py) and centroid, with the geometry
simplified so GET /wards stays small. Load the result with `make seed FILE=...`.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import rasterio
import rasterio.mask
from pyproj import Geod
from shapely.geometry import mapping, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vulnerability import vulnerability_score  # noqa: E402

GEOD = Geod(ellps="WGS84")


def area_km2(geom) -> float:
    return abs(GEOD.geometry_area_perimeter(geom)[0]) / 1e6


def zonal(src, geom, stat: str) -> tuple[float, int]:
    """(mean or sum, valid pixel count) of a raster inside one polygon."""
    data, _ = rasterio.mask.mask(src, [mapping(geom)], crop=True, all_touched=True, filled=False)
    band = data[0]
    valid = band.compressed() if np.ma.isMaskedArray(band) else band.ravel()
    valid = valid[np.isfinite(valid)]
    if src.nodata is not None:
        valid = valid[valid != src.nodata]
    if valid.size == 0:
        return math.nan, 0
    return (float(valid.sum()) if stat == "sum" else float(valid.mean())), int(valid.size)


def check_crs(src, name: str) -> None:
    if src.crs is None or src.crs.to_epsg() != 4326:
        sys.exit(f"{name}: expected EPSG:4326, got {src.crs}. Reproject it (gdalwarp -t_srs EPSG:4326) first.")


def load_groups(path: Path | None) -> dict[str, float]:
    if not path:
        return {}
    with path.open() as fh:
        return {row["wardId"]: float(row["vulnerableShare"]) for row in csv.DictReader(fh)}


def build(args) -> dict:
    features = json.loads(Path(args.wards).read_text())["features"]
    groups = load_groups(args.groups)
    rows = []
    with rasterio.open(args.lst) as lst, rasterio.open(args.ndvi) as ndvi, rasterio.open(args.pop) as pop:
        for src, name in ((lst, "--lst"), (ndvi, "--ndvi"), (pop, "--pop")):
            check_crs(src, name)
        for f in features:
            geom = shape(f["geometry"])
            if not geom.is_valid:
                geom = geom.buffer(0)
            ward_id = str(f["properties"][args.id_field])
            lst_mean, lst_n = zonal(lst, geom, "mean")
            ndvi_mean, _ = zonal(ndvi, geom, "mean")
            people, _ = zonal(pop, geom, "sum")
            rows.append(
                {
                    "wardId": f"{args.prefix}{ward_id}",
                    "rawId": ward_id,
                    "name": str(f["properties"].get(args.name_field) or f"Ward {ward_id}"),
                    "geom": geom,
                    "lst": lst_mean,
                    "lstPixels": lst_n,
                    "ndvi": ndvi_mean,
                    "popDensity": (people if not math.isnan(people) else 0.0) / max(area_km2(geom), 1e-6),
                }
            )

    # City mean LST, weighted by pixel count so big wards count for their size.
    weighted = [(r["lst"], r["lstPixels"]) for r in rows if r["lstPixels"]]
    city_lst = sum(v * n for v, n in weighted) / sum(n for _, n in weighted)

    out = []
    for r in rows:
        missing = [k for k in ("lst", "ndvi") if math.isnan(r[k])]
        if missing:
            print(f"warning: {r['wardId']} has no {', '.join(missing)} pixels; using city values", file=sys.stderr)
        lst_offset = 0.0 if math.isnan(r["lst"]) else r["lst"] - city_lst
        ndvi_value = 0.2 if math.isnan(r["ndvi"]) else r["ndvi"]
        simplified = r["geom"].simplify(args.simplify, preserve_topology=True)
        centre = r["geom"].representative_point() if not r["geom"].centroid.within(r["geom"]) else r["geom"].centroid
        out.append(
            {
                "type": "Feature",
                "geometry": json.loads(json.dumps(mapping(simplified), default=float)),
                "properties": {
                    "wardId": r["wardId"],
                    "name": r["name"],
                    "centroid": [round(centre.x, 5), round(centre.y, 5)],
                    "lstOffset": round(lst_offset, 2),
                    "ndvi": round(ndvi_value, 3),
                    "popDensity": round(r["popDensity"]),
                    "vulnerabilityScore": vulnerability_score(r["popDensity"], ndvi_value, groups.get(r["rawId"])),
                },
            }
        )
    return {"type": "FeatureCollection", "features": out}


def round_coords(obj, digits: int = 5):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, list | tuple):
        return [round_coords(x, digits) for x in obj]
    if isinstance(obj, dict):
        return {k: round_coords(v, digits) for k, v in obj.items()}
    return obj


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wards", required=True)
    p.add_argument("--id-field", default="wardId")
    p.add_argument("--name-field", default="name")
    p.add_argument("--prefix", default="DL-", help="prepended to the ward number to form wardId")
    p.add_argument("--lst", required=True)
    p.add_argument("--ndvi", required=True)
    p.add_argument("--pop", required=True)
    p.add_argument("--groups", type=Path)
    p.add_argument("--simplify", type=float, default=0.0002, help="tolerance in degrees (~20 m)")
    p.add_argument("--out", type=Path, default=Path("data/processed/delhi_wards.geojson"))
    args = p.parse_args(argv)

    collection = build(args)
    for f in collection["features"]:
        f["geometry"]["coordinates"] = round_coords(f["geometry"]["coordinates"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(collection, separators=(",", ":"), ensure_ascii=False))
    size_kb = args.out.stat().st_size / 1024
    print(f"wrote {len(collection['features'])} wards ({size_kb:.0f} KB) -> {args.out}")


if __name__ == "__main__":
    main()
