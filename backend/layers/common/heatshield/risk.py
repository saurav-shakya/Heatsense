"""Risk levels and score bucketing.

Risk_w = H_w x V_w, both in [0, 1]. Thresholds below are placeholders; Phase 2 tunes
them against IMD heat-index bands so Delhi's hottest recent days land in High/Extreme.
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
    (0.70, RiskLevel.EXTREME),
    (0.50, RiskLevel.HIGH),
    (0.30, RiskLevel.MODERATE),
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
