"""Run with `make test-data` (needs rasterio, shapely, pyproj; no network)."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_ward_layer  # noqa: E402
from vulnerability import vulnerability_score  # noqa: E402

PIXEL = 0.001  # degrees (~100 m)


def write_raster(path: Path, values: np.ndarray) -> Path:
    with rasterio.open(
        path, "w", driver="GTiff", height=values.shape[0], width=values.shape[1], count=1, dtype="float32",
        crs="EPSG:4326", transform=from_origin(77.0, 28.6, PIXEL, PIXEL), nodata=-9999,
    ) as dst:  # fmt: skip
        dst.write(values.astype("float32"), 1)
    return path


def square(x0: float, y0: float, size: float) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [[[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]],
    }


@pytest.fixture
def inputs(tmp_path):
    # 100 x 100 pixels covering lon 77.0-77.1, lat 28.5-28.6. West half hot, bare and dense.
    lst = np.full((100, 100), 40.0)
    lst[:, :50] = 44.0
    ndvi = np.full((100, 100), 0.45)
    ndvi[:, :50] = 0.08
    pop = np.full((100, 100), 20.0)
    pop[:, :50] = 300.0
    wards = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": square(77.0, 28.5, 0.05),
                "properties": {"Ward_No": 1, "Ward_Name": "West"},
            },
            {
                "type": "Feature",
                "geometry": square(77.05, 28.5, 0.05),
                "properties": {"Ward_No": 2, "Ward_Name": "East"},
            },
        ],
    }
    (tmp_path / "wards.geojson").write_text(json.dumps(wards))
    return [
        "--wards", str(tmp_path / "wards.geojson"), "--id-field", "Ward_No", "--name-field", "Ward_Name",
        "--lst", str(write_raster(tmp_path / "lst.tif", lst)),
        "--ndvi", str(write_raster(tmp_path / "ndvi.tif", ndvi)),
        "--pop", str(write_raster(tmp_path / "pop.tif", pop)),
        "--out", str(tmp_path / "out.geojson"),
    ]  # fmt: skip


def test_builds_attributes_per_ward(inputs, tmp_path):
    build_ward_layer.main(inputs)
    out = json.loads((tmp_path / "out.geojson").read_text())
    west, east = (f["properties"] for f in out["features"])
    assert (west["wardId"], west["name"]) == ("DL-1", "West")
    assert west["lstOffset"] == pytest.approx(2.0, abs=0.15)  # 44 vs city mean 42
    assert east["lstOffset"] == pytest.approx(-2.0, abs=0.15)
    assert west["ndvi"] == pytest.approx(0.08, abs=0.02)
    # 300 people per 0.001 deg pixel (111 m x 98 m at 28.5 N) ~ 27,650 / km^2
    assert west["popDensity"] == pytest.approx(27650, rel=0.03)
    assert west["vulnerabilityScore"] > east["vulnerabilityScore"]
    assert west["centroid"] == pytest.approx([77.025, 28.525], abs=1e-4)


def test_vulnerable_groups_raise_the_score():
    assert vulnerability_score(20000, 0.2, 0.25) > vulnerability_score(20000, 0.2, 0.05)
    assert vulnerability_score(0, 0.9) == 0.05  # floor


def test_rejects_rasters_not_in_wgs84(inputs, tmp_path):
    with rasterio.open(
        tmp_path / "utm.tif", "w", driver="GTiff", height=2, width=2, count=1, dtype="float32",
        crs="EPSG:32643", transform=from_origin(700000, 3160000, 30, 30),
    ) as dst:  # fmt: skip
        dst.write(np.zeros((2, 2), dtype="float32"), 1)
    args = list(inputs)
    args[args.index("--lst") + 1] = str(tmp_path / "utm.tif")
    with pytest.raises(SystemExit):
        build_ward_layer.main(args)
