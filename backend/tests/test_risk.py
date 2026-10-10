import pytest

from heatshield.heat import hazard, heat_index_c
from heatshield.risk import RiskLevel, bucket, score
from heatshield.timeutil import ist_date, ist_hour

MEDIAN_V = 0.43  # median vulnerability of the Delhi layer


def test_score_is_product_clamped_to_unit_interval():
    assert score(0.5, 0.5) == 0.25
    assert score(1.5, 0.8) == 0.8
    assert score(-1, 0.8) == 0.0


@pytest.mark.parametrize(
    ("risk", "level"),
    [
        (0.0, RiskLevel.LOW),
        (0.17, RiskLevel.LOW),
        (0.18, RiskLevel.MODERATE),
        (0.30, RiskLevel.HIGH),
        (0.45, RiskLevel.EXTREME),
        (0.95, RiskLevel.EXTREME),
    ],
)
def test_bucket_boundaries(risk, level):
    assert bucket(risk) is level


def test_only_high_and_extreme_are_alertable():
    assert [lvl for lvl in RiskLevel if lvl.alertable] == [RiskLevel.HIGH, RiskLevel.EXTREME]


@pytest.mark.parametrize(
    ("temp_c", "rh", "expected"),
    [
        (32.2, 60, 37.8),  # NWS table: 90 F at 60% -> 100 F
        (35.0, 50, 40.6),  # 95 F at 50% -> 105 F
        (26.0, 50, 26.3),  # below 80 F the simple formula applies
    ],
)
def test_heat_index_matches_nws_table(temp_c, rh, expected):
    assert heat_index_c(temp_c, rh) == pytest.approx(expected, abs=0.6)


def test_dry_heat_is_not_undercounted():
    felt, _ = hazard(46.0, 10)
    assert felt >= 46.0  # the heat index alone would say ~44


def test_built_up_wards_feel_hotter():
    assert hazard(40, 30, lst_offset=4)[0] > hazard(40, 30)[0] > hazard(40, 30, lst_offset=-4)[0]


# Backtest. Delhi on 28-29 May 2024: IMD stations recorded 45-49 degC with ~10% humidity
# (Mungeshpur 49.9). A late-October afternoon is ~33 degC at ~45%.
@pytest.mark.parametrize(
    ("temp_c", "rh", "vulnerability", "levels"),
    [
        (33, 45, MEDIAN_V, {RiskLevel.LOW}),  # October
        (40, 25, MEDIAN_V, {RiskLevel.MODERATE}),  # ordinary pre-monsoon afternoon
        (40, 25, 0.9, {RiskLevel.HIGH}),  # ...but a very vulnerable ward is High
        (45.5, 12, MEDIAN_V, {RiskLevel.HIGH, RiskLevel.EXTREME}),  # IMD heatwave
        (47.5, 10, MEDIAN_V, {RiskLevel.HIGH, RiskLevel.EXTREME}),  # severe heatwave, 28 May 2024
        (47.5, 10, 0.55, {RiskLevel.EXTREME}),
        (49.0, 9, 0.2, {RiskLevel.MODERATE, RiskLevel.HIGH}),  # green, sparse ward still flagged
    ],
)
def test_backtest_delhi_days(temp_c, rh, vulnerability, levels):
    _, h = hazard(temp_c, rh)
    assert bucket(score(h, vulnerability)) in levels


def test_ist_conversion_crosses_midnight():
    assert ist_date("2026-10-10T18:30:00Z") == "2026-10-11"
    assert ist_hour("2026-10-10T09:30:00Z") == 15
