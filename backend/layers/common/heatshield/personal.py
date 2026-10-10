"""Personal risk: the ward's level, adjusted for the person's home and group.

A ward score describes the average resident. Two things we ask at sign-up change what one
person faces:
  - a tin, asbestos or plastic-sheet roof: rooms under thin roofs heat up to or above the
    outdoor temperature in the afternoon and cool slowly at night, so the person's level is
    one step above the ward's;
  - a hot night: the body can't recover, so for people who spend the night at home in heat
    (elderly people, parents of infants, anyone under a thin roof) it counts as High even
    when the afternoon alone would not.
"""

from heatshield.risk import RiskLevel

ORDER = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.EXTREME]
THIN_ROOF = "tin"
NIGHT_SENSITIVE_GROUPS = {"elderly", "parent"}


def bump(level: RiskLevel, steps: int = 1) -> RiskLevel:
    return ORDER[min(ORDER.index(level) + steps, len(ORDER) - 1)]


def at_least(level: RiskLevel, floor: RiskLevel) -> RiskLevel:
    return level if ORDER.index(level) >= ORDER.index(floor) else floor


def thin_roof(sub: dict) -> bool:
    return sub.get("home") == THIN_ROOF


def night_sensitive(sub: dict) -> bool:
    return sub.get("group") in NIGHT_SENSITIVE_GROUPS or thin_roof(sub)


def personal_level(day: dict, sub: dict) -> RiskLevel:
    """This subscriber's level for one day of their ward's daily summary."""
    level = RiskLevel(day["level"])
    if thin_roof(sub):
        level = bump(level)
    if day.get("hotNight") and night_sensitive(sub):
        level = at_least(level, RiskLevel.HIGH)
    return level


def may_concern(day: dict) -> bool:
    """Could any subscriber of a ward with this day summary be at High or above?"""
    return RiskLevel(day["level"]) != RiskLevel.LOW or bool(day.get("hotNight"))
