import pytest

from heatshield.risk import RiskLevel, bucket, score
from heatshield.timeutil import ist_date, ist_hour


def test_score_is_product_clamped_to_unit_interval():
    assert score(0.5, 0.5) == 0.25
    assert score(1.5, 0.8) == 0.8
    assert score(-1, 0.8) == 0.0


@pytest.mark.parametrize(
    ("risk", "level"),
    [
        (0.0, RiskLevel.LOW),
        (0.29, RiskLevel.LOW),
        (0.3, RiskLevel.MODERATE),
        (0.5, RiskLevel.HIGH),
        (0.95, RiskLevel.EXTREME),
    ],
)
def test_bucket_boundaries(risk, level):
    assert bucket(risk) is level


def test_only_high_and_extreme_are_alertable():
    assert [lvl for lvl in RiskLevel if lvl.alertable] == [RiskLevel.HIGH, RiskLevel.EXTREME]


def test_ist_conversion_crosses_midnight():
    assert ist_date("2026-10-10T18:30:00Z") == "2026-10-11"
    assert ist_hour("2026-10-10T09:30:00Z") == 15
