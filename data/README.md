# Data

## What's here now

`fixtures/delhi_wards.geojson` is a **synthetic placeholder**: a 1.5 km hex grid clipped to a rough outline of NCT Delhi (289 cells). This is the PRD's fallback for missing ward boundaries. Each cell's `lstOffset`, `ndvi`, `popDensity` and `vulnerabilityScore` come from smooth made-up fields (hot, dense core around Old Delhi; greener Ridge), and every feature is marked `"fixture": true`.

```bash
make fixture   # regenerate the grid (only needed if make_hex_grid.py changes)
make seed      # upload the GeoJSON to S3 and write the Wards table
```

## Phase 1: replace the fixture with real inputs

| Input | Source | Per-ward value |
|---|---|---|
| Ward boundaries | MCD ward GeoJSON (Delhi open data / Datameet), else OpenStreetMap `admin_level=10` | polygon, simplified to keep `/wards` small |
| Land surface temperature | Landsat 8/9 Collection 2 L2 (ST_B10), Apr–Jun | mean LST minus city mean, so `lstOffset` in °C |
| Green cover | Sentinel-2 L2A NDVI, same season | mean NDVI |
| Population density | WorldPop 100 m (India, latest year) | people per km² |
| Vulnerable groups (optional) | Census ward tables | share of under-6s and over-60s |

Raw downloads go in `data/raw/` and outputs in `data/processed/`; both are gitignored.

### 1. Export the rasters from Google Earth Engine

Paste into the [Earth Engine code editor](https://code.earthengine.google.com/), run, and start the three export tasks. Each export is a single-band GeoTIFF in EPSG:4326, which is what the build script expects.

```js
var delhi = ee.Geometry.Rectangle([76.83, 28.40, 77.35, 28.89]);
var season = ['2024-04-01', '2024-06-30'];

// Landsat 8/9 C2 L2 surface temperature, cloud-masked, in degC.
function lst(img) {
  var qa = img.select('QA_PIXEL');
  var clear = qa.bitwiseAnd(1 << 3).eq(0).and(qa.bitwiseAnd(1 << 4).eq(0));
  return img.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).updateMask(clear);
}
var lstC = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2'))
  .filterBounds(delhi).filterDate(season[0], season[1]).map(lst).mean().clip(delhi);

// Sentinel-2 L2A NDVI, cloud-masked with the scene classification band.
var ndvi = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(delhi).filterDate(season[0], season[1])
  .map(function (img) {
    var scl = img.select('SCL');
    var clear = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10));
    return img.normalizedDifference(['B8', 'B4']).updateMask(clear);
  }).median().clip(delhi);

// WorldPop people per 100 m pixel.
var pop = ee.ImageCollection('WorldPop/GP/100m/pop').filter(ee.Filter.eq('country', 'IND'))
  .filter(ee.Filter.eq('year', 2020)).first().clip(delhi);

function exportTif(image, name, scale) {
  Export.image.toDrive({image: image.toFloat(), description: name, folder: 'heatshield', region: delhi,
                        crs: 'EPSG:4326', scale: scale, maxPixels: 1e10});
}
exportTif(lstC, 'delhi_lst_summer_c', 30);
exportTif(ndvi, 'delhi_ndvi_summer', 10);
exportTif(pop, 'delhi_worldpop_2020', 100);
```

**Fallback (PRD risk):** if Landsat processing takes too long, swap the LST block for MODIS `MODIS/061/MOD11A2` `LST_Day_1km` (× 0.02 − 273.15) at 1 km. Coarser, but `lstOffset` still separates hot and green wards.

### 2. Build and load the ward layer

```bash
uv run data/scripts/build_ward_layer.py \
  --wards data/raw/delhi_mcd_wards.geojson --id-field Ward_No --name-field Ward_Name \
  --lst data/raw/delhi_lst_summer_c.tif --ndvi data/raw/delhi_ndvi_summer.tif \
  --pop data/raw/delhi_worldpop_2020.tif \
  --out data/processed/delhi_wards.geojson        # optional: --groups data/raw/ward_groups.csv

make seed WARDS_FILE=data/processed/delhi_wards.geojson
make invoke-risk
```

The script computes the zonal stats per ward, `vulnerabilityScore` from `scripts/vulnerability.py` (weights in [docs/architecture.md](../docs/architecture.md#risk-model)), a centroid for the forecast grid, and simplifies the geometry (`--simplify`, default ~20 m). Ward names should keep the ward number, e.g. "Ward 14 Jahangirpuri". Without `"fixture": true` on the features, the map drops its "Sample wards" note. `make test-data` runs the script's tests against small synthetic rasters.

## Replay data

`make replay-fetch DATE=2024-05-28` pulls the Open-Meteo archive for 27–31 May 2024 at every grid point of the current ward layer and uploads it to `s3://<DataBucket>/replay/delhi/2024-05-28.json`. See [docs/architecture.md](../docs/architecture.md#replay-mode).
