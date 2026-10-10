"""Risk levels and score bucketing.

Risk_w = H_w x V_w, both in [0, 1]. H comes from heatshield.heat (IMD heat-index bands
and heatwave criteria); V is the ward's static vulnerability score.

Thresholds are tuned so that, for a ward of median vulnerability (V ~ 0.43 in Delhi):
  - a normal pre-monsoon afternoon (40 degC, dry) is Moderate,
  - an IMD heatwave hour (>= 45 degC air) is High,
  - a severe heatwave hour (>= 47 degC air, e.g. Delhi on 28-29 May 2024) is High, and
    Extreme from V ~ 0.5 upward,
  - an October afternoon (33 degC) stays Low.
See tests/test_risk.py for the backtest cases.
"""

from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

    @property
    def alertable(self) -> bool:
        return self in (RiskLevel.HIGH, RiskLevel.EXTREME)


# Lower bound (inclusive) of each level, highest first.
THRESHOLDS: list[tuple[float, RiskLevel]] = [
    (0.45, RiskLevel.EXTREME),
    (0.30, RiskLevel.HIGH),
    (0.18, RiskLevel.MODERATE),
    (0.0, RiskLevel.LOW),
]


def score(hazard: float, vulnerability: float) -> float:
    """Combine hazard and vulnerability into a risk score in [0, 1]."""
    h = min(max(hazard, 0.0), 1.0)
    v = min(max(vulnerability, 0.0), 1.0)
    return round(h * v, 4)


def bucket(risk: float) -> RiskLevel:
    for lower, level in THRESHOLDS:
        if risk >= lower:
            return level
    return RiskLevel.LOW
