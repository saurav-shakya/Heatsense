"""What the ward office should do on a given day, as short codes the map and CSV translate.

Rules follow the operational steps in Indian heat action plans (Ahmedabad, Delhi DDMA,
NDMA guidelines): open cooling spaces and water points during the hottest hours, move
outdoor work out of them, check on people who live alone, and keep shelters open on nights
that don't cool down. The map turns each code into a sentence in English or Hindi.
"""

from heatshield import resources
from heatshield.risk import RiskLevel

COOLING_GAP_KM = 1.0  # no verified cooling or water point within this of the ward centre


def ward_actions(day: dict, ward: dict, places: list[dict]) -> list[str]:
    level = RiskLevel(day["level"])
    codes: list[str] = []
    if level.alertable:
        codes.append("open_cooling")  # cooling centres + water points during the risky hours
    if any(seg["work"] == 0 for seg in day.get("workPlan") or []):
        codes.append("shift_work")  # move municipal / site outdoor work out of the stop-work hours
    if level == RiskLevel.EXTREME:
        codes.append("check_vulnerable")  # ASHA / volunteer visits to elderly people living alone
    if day.get("hotNight"):
        codes.append("night_shelter")  # keep cooling spaces open overnight
    centroid = ward.get("centroid")
    if level.alertable and centroid:
        near = resources.nearest(
            float(centroid[0]), float(centroid[1]), places, kinds=("cooling", "water"), max_km=COOLING_GAP_KM
        )
        if not near:
            codes.append("cooling_gap")  # nowhere verified to send people: set up a temporary point
    return codes
