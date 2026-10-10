"""Hourly weather from Open-Meteo, normalised into a small "weather pack".

The risk engine never talks to Open-Meteo's JSON shape directly. Live forecasts and
replay files (a past heatwave stored in S3) share one format:

    {"source": "...", "fetchedAt": "...Z", "points": [
        {"lat": 28.6, "lon": 77.2,
         "time": ["2024-05-28T00:00:00Z", ...],      # UTC hours
         "temperature": [31.2, ...],                 # 2 m air temperature, degC
         "humidity": [18, ...]}                      # relative humidity, %
    ]}

Wards are snapped to a coarse grid (GRID_STEP degrees, ~11 km) so one batched request
covers the whole city.
"""

import json
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARS = "temperature_2m,relative_humidity_2m"
GRID_STEP = 0.1
BATCH_SIZE = 50  # coordinates per request
TIMEOUT_S = 20
# Used when a ward row has no centroid (e.g. seeded before centroids were stored).
CITY_CENTRES = {"delhi": (28.61, 77.21)}


class WeatherError(RuntimeError):
    """Open-Meteo was unreachable or returned something unusable."""


def snap(lat: float, lon: float) -> tuple[float, float]:
    return round(round(lat / GRID_STEP) * GRID_STEP, 2), round(round(lon / GRID_STEP) * GRID_STEP, 2)


def ward_point(ward: dict, city: str = "delhi") -> tuple[float, float]:
    centroid = ward.get("centroid")
    if centroid:
        lon, lat = centroid
        return snap(float(lat), float(lon))
    return snap(*CITY_CENTRES.get(city, CITY_CENTRES["delhi"]))


def grid_points(wards: list[dict], city: str = "delhi") -> list[tuple[float, float]]:
    return sorted({ward_point(w, city) for w in wards})


def _get_json(url: str, params: dict) -> object:
    full = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(full, timeout=TIMEOUT_S) as resp:
            return json.loads(resp.read())
    except Exception as exc:  # network, HTTP error, bad JSON
        raise WeatherError(f"Open-Meteo request failed: {exc}") from exc


def _normalise_time(value: str) -> str:
    # Open-Meteo with timezone=GMT returns "2024-05-28T00:00".
    return datetime.strptime(value, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_locations(payload: object) -> list[dict]:
    locations = payload if isinstance(payload, list) else [payload]
    points = []
    for loc in locations:
        if not isinstance(loc, dict) or "hourly" not in loc:
            raise WeatherError(f"unexpected Open-Meteo payload: {str(loc)[:200]}")
        hourly = loc["hourly"]
        points.append(
            {
                "time": [_normalise_time(t) for t in hourly["time"]],
                "temperature": hourly["temperature_2m"],
                "humidity": hourly["relative_humidity_2m"],
            }
        )
    return points


def _fetch(url: str, points: list[tuple[float, float]], extra: dict, source: str) -> dict:
    out = []
    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i : i + BATCH_SIZE]
        params = {
            "latitude": ",".join(str(lat) for lat, _ in batch),
            "longitude": ",".join(str(lon) for _, lon in batch),
            "hourly": HOURLY_VARS,
            "timezone": "GMT",
            **extra,
        }
        parsed = _parse_locations(_get_json(url, params))
        if len(parsed) != len(batch):
            raise WeatherError(f"asked for {len(batch)} locations, got {len(parsed)}")
        # Keep our requested (snapped) coordinates, not Open-Meteo's adjusted grid cell.
        out.extend({"lat": lat, "lon": lon, **p} for (lat, lon), p in zip(batch, parsed, strict=True))
    return {"source": source, "fetchedAt": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "points": out}


def fetch_forecast(points: list[tuple[float, float]], start: datetime, days: int) -> dict:
    """Hourly forecast covering the UTC dates spanned by [start, start + days)."""
    end = start + timedelta(days=days)
    return _fetch(
        FORECAST_URL,
        points,
        {
            "start_date": start.astimezone(UTC).strftime("%Y-%m-%d"),
            "end_date": end.astimezone(UTC).strftime("%Y-%m-%d"),
        },
        "open-meteo-forecast",
    )


def fetch_archive(points: list[tuple[float, float]], start_date: str, end_date: str) -> dict:
    """Recorded (reanalysis) hourly weather for past dates, YYYY-MM-DD inclusive."""
    return _fetch(ARCHIVE_URL, points, {"start_date": start_date, "end_date": end_date}, "open-meteo-archive")


def shift_days(pack: dict, days: int) -> dict:
    """Move every timestamp by whole days (replay: map a past heatwave onto today)."""

    def move(t: str) -> str:
        dt = datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=days)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return {**pack, "points": [{**p, "time": [move(t) for t in p["time"]]} for p in pack["points"]]}


class WeatherIndex:
    """Lookup (temperature, humidity) by snapped point and UTC hour."""

    def __init__(self, pack: dict):
        self._by_point: dict[tuple[float, float], dict[str, tuple[float, float]]] = {}
        for p in pack["points"]:
            series = {}
            for t, temp, rh in zip(p["time"], p["temperature"], p["humidity"], strict=True):
                if temp is not None and rh is not None:
                    series[t] = (float(temp), float(rh))
            self._by_point[(round(float(p["lat"]), 2), round(float(p["lon"]), 2))] = series

    def _series(self, point: tuple[float, float]) -> dict[str, tuple[float, float]]:
        if point in self._by_point:
            return self._by_point[point]
        # Nearest available point (a ward added after the pull, or a replay file with fewer points).
        nearest = min(self._by_point, key=lambda k: (k[0] - point[0]) ** 2 + (k[1] - point[1]) ** 2)
        return self._by_point[nearest]

    @staticmethod
    def _lookup(series: dict[str, tuple[float, float]], hour_iso: str) -> tuple[float, float] | None:
        if hour_iso in series:
            return series[hour_iso]
        # IST hours fall on :30 UTC; Open-Meteo is hourly on the UTC hour. Average the two neighbours.
        t = datetime.strptime(hour_iso, "%Y-%m-%dT%H:%M:%SZ")
        before = series.get((t.replace(minute=0)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        after = series.get((t.replace(minute=0) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        if before and after:
            return round((before[0] + after[0]) / 2, 2), round((before[1] + after[1]) / 2, 2)
        return before or after

    def at(self, point: tuple[float, float], hour_iso: str) -> tuple[float, float] | None:
        return self._lookup(self._series(point), hour_iso)

    def covers(self, hours: list[str]) -> bool:
        """True if every point has data for every requested hour."""
        return all(all(self._lookup(s, h) is not None for h in hours) for s in self._by_point.values())
