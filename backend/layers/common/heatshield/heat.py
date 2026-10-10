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


# --------------------------------------------------------------------------- body heat stress
#
# The felt temperature above drives ward risk. Two more numbers are what a person can act on:
#
# WBGT (wet-bulb globe temperature) is the occupational standard for heat stress at work
# (ISO 7243, ACGIH TLV, NIOSH). It weights humidity far more than air temperature does, so it
# catches humid monsoon heat that a 38 degC reading hides. Open-Meteo gives no globe or
# natural wet-bulb temperature, so we estimate it:
#   - psychrometric wet bulb from air temperature and humidity (Stull 2011, valid for
#     RH 5-99 % and -20..50 degC, error under 1 degC),
#   - shade WBGT = 0.7 x wet bulb + 0.3 x air temperature (ISO 7243 indoor form, globe ~ air
#     temperature in shade),
#   - in full sun the globe runs well above air temperature; SUN_WBGT_ADD stands in for the
#     solar load (outdoor WBGT = 0.7 Tnw + 0.2 Tg + 0.1 Ta with Tg ~ 12-15 degC above air at
#     midday). Replace with Liljegren et al. (2008) once radiation and wind are pulled.
# This is a screening estimate, not a measured WBGT. Work-rest advice errs to the safe side.

SUN_WBGT_ADD = 3.0

# ACGIH TLV screening limits for acclimatised workers doing moderate work (walking with a load,
# brick laying, delivery riding): (highest WBGT degC, minutes of work per hour). The TLV rows
# are 75-100 %, 50-75 %, 25-50 % and 0-25 % work; we take the lower end of each band. Above the
# last row: no continuous moderate work. Unacclimatised workers (new arrivals, first hot week)
# need limits ~3 degC lower; we warn them through the advice text rather than a second table.
WORK_REST_MODERATE: list[tuple[float, int]] = [
    (28.0, 60),
    (29.0, 45),
    (30.0, 30),
    (31.5, 15),
]

# A night that stays this warm gives the body no chance to recover. Hot nights carry mortality
# risk of their own (Lancet Planet Health 2022; Env Int 2025), and in Ahmedabad deaths roughly
# doubled on >30 degC nights after >45 degC days. Delhi's normal May-June minimum is ~27-29 degC;
# its warmest night in 14 years (May 2026) was 32.4 degC.
HOT_NIGHT_C = 30.0


def wet_bulb_c(temp_c: float, rh: float) -> float:
    """Psychrometric wet-bulb temperature (degC), Stull (2011)."""
    rh = min(max(rh, 5.0), 99.0)
    t = temp_c
    tw = (
        t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(t + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * rh**1.5 * math.atan(0.023101 * rh)
        - 4.686035
    )
    return round(tw, 1)


def wbgt_c(temp_c: float, rh: float, sun: bool = False) -> float:
    """Estimated WBGT (degC) in shade, or in full sun with sun=True."""
    shade = 0.7 * wet_bulb_c(temp_c, rh) + 0.3 * temp_c
    return round(shade + (SUN_WBGT_ADD if sun else 0.0), 1)


def work_minutes_per_hour(wbgt: float) -> int:
    """Safe minutes of moderate outdoor work per hour at this WBGT (ACGIH, acclimatised). 0 = stop."""
    for limit, minutes in WORK_REST_MODERATE:
        if wbgt <= limit:
            return minutes
    return 0


def is_hot_night(night_min_c: float | None) -> bool:
    return night_min_c is not None and night_min_c >= HOT_NIGHT_C
