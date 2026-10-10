import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from heatshield import weather

RECORDED = json.loads((Path(__file__).parent / "fixtures" / "open_meteo_two_points.json").read_text())


def test_parses_a_recorded_multi_location_response(monkeypatch):
    monkeypatch.setattr(weather, "_get_json", lambda url, params: RECORDED)
    pack = weather.fetch_archive([(28.6, 77.2), (28.5, 77.1)], "2024-05-28", "2024-05-28")
    assert pack["source"] == "open-meteo-archive"
    first, second = pack["points"]
    assert (first["lat"], first["lon"]) == (28.6, 77.2)  # our snapped point, not Open-Meteo's cell
    assert first["time"][0] == "2024-05-28T07:00:00Z"
    index = weather.WeatherIndex(pack)
    assert index.at((28.6, 77.2), "2024-05-28T09:00:00Z") == (46.3, 11.0)
    assert index.at((28.5, 77.1), "2024-05-28T09:00:00Z") is None  # null hours are dropped


def test_batches_coordinates_and_requests_gmt(monkeypatch):
    calls = []

    def get_json(url, params):
        calls.append(params)
        n = len(params["latitude"].split(","))
        return [RECORDED[0]] * n if n > 1 else RECORDED[0]

    monkeypatch.setattr(weather, "_get_json", get_json)
    points = [(28.0 + i / 10, 77.0) for i in range(weather.BATCH_SIZE + 3)]
    pack = weather.fetch_forecast(points, datetime(2026, 5, 27, 18, 30, tzinfo=UTC), 4)
    assert len(calls) == 2 and len(pack["points"]) == len(points)
    assert calls[0]["timezone"] == "GMT"
    assert (calls[0]["start_date"], calls[0]["end_date"]) == ("2026-05-27", "2026-05-31")


def test_wrong_location_count_is_an_error(monkeypatch):
    monkeypatch.setattr(weather, "_get_json", lambda url, params: RECORDED[0])
    with pytest.raises(weather.WeatherError):
        weather.fetch_archive([(28.6, 77.2), (28.5, 77.1)], "2024-05-28", "2024-05-28")


def test_network_failure_raises_weather_error(monkeypatch):
    def boom(*_, **__):
        raise OSError("no route")

    monkeypatch.undo()  # drop conftest's fake _get_json
    monkeypatch.setattr(weather.urllib.request, "urlopen", boom)
    with pytest.raises(weather.WeatherError):
        weather._get_json(weather.FORECAST_URL, {})


def test_wards_snap_to_a_shared_grid():
    wards = [{"centroid": [77.23, 28.66]}, {"centroid": [77.21, 28.64]}, {"centroid": [77.05, 28.5]}, {}]
    assert weather.grid_points(wards) == [(28.5, 77.0), (28.6, 77.2), (28.7, 77.2)]


def test_shift_days_and_nearest_point():
    pack = {
        "points": [{"lat": 28.6, "lon": 77.2, "time": ["2024-05-28T08:00:00Z"], "temperature": [46], "humidity": [12]}]
    }
    moved = weather.WeatherIndex(weather.shift_days(pack, 3))
    assert moved.at((28.9, 77.4), "2024-05-31T08:00:00Z") == (46.0, 12.0)  # nearest point is used


def test_ist_half_hours_average_the_neighbouring_utc_hours():
    pack = {
        "points": [
            {
                "lat": 28.6,
                "lon": 77.2,
                "time": ["2024-05-28T08:00:00Z", "2024-05-28T09:00:00Z"],
                "temperature": [44, 46],
                "humidity": [12, 10],
            }
        ]
    }
    index = weather.WeatherIndex(pack)
    assert index.at((28.6, 77.2), "2024-05-28T08:30:00Z") == (45.0, 11.0)
    assert index.at((28.6, 77.2), "2024-05-28T09:30:00Z") == (46.0, 10.0)  # edge: one neighbour
    assert index.at((28.6, 77.2), "2024-05-28T11:30:00Z") is None
