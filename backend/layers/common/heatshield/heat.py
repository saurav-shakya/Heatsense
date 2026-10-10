"""Heat index and hazard H in [0, 1] for one ward-hour.

Felt temperature is the larger of air temperature and the NWS heat index (Rothfusz with
the NOAA low/high humidity adjustments), so Delhi's dry pre-monsoon heat is not
under-counted the way a pure heat index would. The ward's `lstOffset` then shifts it:
built-up wards run hotter than the station-like grid value, green wards cooler.

Hazard is anchored to IMD's heat-index colour bands (green < 35, yellow 35-45,
orange 45-55, red > 55 degC) and to IMD's heatwave criteria on air temperature for the
plains (heatwave at >= 45 degC actual, severe heatwave at >= 47 degC).
"""

import math

# Share of the ward's surface-temperature anomaly that reaches the air people feel.
# Surface (LST) anomalies are several times larger than 2 m air-temperature anomalies.
LST_TO_AIR = 0.35

# (felt temperature degC, hazard) knots, linearly interpolated. Mirrors the IMD bands.
HAZARD_KNOTS: list[tuple[float, float]] = [
    (27.0, 0.0),
    (35.0, 0.25),  # yellow starts
    (45.0, 0.55),  # orange starts
    (55.0, 0.85),  # red starts
    (60.0, 1.0),
]

HEATWAVE_AIR_C = 45.0  # IMD: heatwave on actual max temperature alone
SEVERE_HEATWAVE_AIR_C = 47.0
HEATWAVE_FLOOR = 0.75
SEVERE_HEATWAVE_FLOOR = 0.9


def c_to_f(c: float) -> float:
    return c * 9 / 5 + 32


def f_to_c(f: float) -> float:
    return (f - 32) * 5 / 9


def heat_index_c(temp_c: float, rh: float) -> float:
    """NWS heat index (degC) from air temperature (degC) and relative humidity (%)."""
    t = c_to_f(temp_c)
    rh = min(max(rh, 0.0), 100.0)
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if (simple + t) / 2 < 80:
        return round(f_to_c(simple), 1)
    hi = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t * t
        - 0.05481717 * rh * rh
        + 0.00122874 * t * t * rh
        + 0.00085282 * t * rh * rh
        - 0.00000199 * t * t * rh * rh
    )
    if rh < 13 and 80 <= t <= 112:
        hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
    elif rh > 85 and 80 <= t <= 87:
        hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return round(f_to_c(hi), 1)


def felt_temperature(temp_c: float, rh: float, lst_offset: float = 0.0) -> float:
    """What a person in this ward feels: max(air, heat index), shifted by the ward's surface heat."""
    return round(max(temp_c, heat_index_c(temp_c, rh)) + LST_TO_AIR * lst_offset, 1)


def _interpolate(x: float) -> float:
    if x <= HAZARD_KNOTS[0][0]:
        return HAZARD_KNOTS[0][1]
    for (x0, y0), (x1, y1) in zip(HAZARD_KNOTS, HAZARD_KNOTS[1:], strict=False):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return HAZARD_KNOTS[-1][1]


def hazard(temp_c: float, rh: float, lst_offset: float = 0.0) -> tuple[float, float]:
    """(felt temperature degC, hazard H in [0, 1]) for one hour in one ward."""
    felt = felt_temperature(temp_c, rh, lst_offset)
    h = _interpolate(felt)
    if temp_c >= SEVERE_HEATWAVE_AIR_C:
        h = max(h, SEVERE_HEATWAVE_FLOOR)
    elif temp_c >= HEATWAVE_AIR_C:
        h = max(h, HEATWAVE_FLOOR)
    return felt, round(min(max(h, 0.0), 1.0), 3)
