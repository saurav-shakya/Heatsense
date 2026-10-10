# Data

## What's here now

`fixtures/delhi_wards.geojson` is a **synthetic placeholder**: a 1.5 km hex grid clipped to a rough outline of NCT Delhi (289 cells). This is the PRD's fallback for missing ward boundaries. Each cell's `lstOffset`, `ndvi`, `popDensity` and `vulnerabilityScore` come from smooth made-up fields (hot, dense core around Old Delhi; greener Ridge), and every feature is marked `"fixture": true`.

```bash
make seed   # regenerate the grid, upload GeoJSON to S3, write the Wards table
```

## Phase 1: replace the fixture with real inputs

Produce a GeoJSON in the same shape (`wardId`, `name`, `lstOffset`, `ndvi`, `popDensity`, `vulnerabilityScore` per feature) and run `seed.py --file <it>`.

| Input | Source | Per-ward value |
|---|---|---|
| Ward boundaries | MCD ward GeoJSON (Delhi open data / Datameet), else OpenStreetMap `admin_level=10` | polygon, simplified to keep `/wards` small |
| Land surface temperature | Landsat 8/9 Collection 2 L2 (ST_B10), summer scenes | mean LST minus city mean, so `lstOffset` in °C |
| Green cover | Sentinel-2 L2A NDVI, same season | mean NDVI |
| Population density | WorldPop 100 m (India, latest year) | people per km² |

Pre-compute these once, in a notebook under `data/notebooks/`. Raw downloads go in `data/raw/` and intermediates in `data/processed/`; both are gitignored.
