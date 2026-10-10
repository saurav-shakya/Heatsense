"""Body heat stress (WBGT, work-rest, hot nights), personal levels, ward actions and nearby places."""

import pytest
from conftest import SAMPLE_RESOURCES

from heatshield import advisory, resources
from heatshield.actions import ward_actions
from heatshield.heat import is_hot_night, wbgt_c, wet_bulb_c, work_minutes_per_hour
from heatshield.personal import may_concern, personal_level
from heatshield.risk import RiskLevel


@pytest.mark.parametrize(
    ("temp_c", "rh", "expected"),
    [
        (20.0, 50, 13.7),  # Stull (2011) worked example
        (35.0, 60, 28.5),
        (46.0, 10, 22.0),
    ],
)
def test_wet_bulb_matches_stull(temp_c, rh, expected):
    assert wet_bulb_c(temp_c, rh) == pytest.approx(expected, abs=0.2)


def test_humid_heat_is_worse_for_work_than_the_air_temperature_suggests():
    # A 35 degC monsoon afternoon stresses the body more than a 40 degC dry one.
    assert wbgt_c(35, 70) > wbgt_c(40, 20)
    assert wbgt_c(35, 70, sun=True) == pytest.approx(wbgt_c(35, 70) + 3.0, abs=0.01)


@pytest.mark.parametrize(
    ("wbgt", "minutes"),
    [(26.0, 60), (28.0, 60), (28.5, 45), (29.5, 30), (31.0, 15), (31.5, 15), (31.6, 0), (35.0, 0)],
)
def test_work_rest_follows_acgih_moderate_work(wbgt, minutes):
    assert work_minutes_per_hour(wbgt) == minutes


def test_hot_night_threshold():
    assert is_hot_night(30.0) and not is_hot_night(29.9) and not is_hot_night(None)


def day(level: str, **extra) -> dict:
    return {
        "date": "2026-05-28",
        "level": level,
        "risk": 0.3,
        "heatIndex": 44,
        "peakAt": "2026-05-28T09:30:00Z",
        **extra,
    }


@pytest.mark.parametrize(
    ("ward_level", "sub", "expected"),
    [
        ("moderate", {"group": "worker"}, RiskLevel.MODERATE),
        ("moderate", {"group": "worker", "home": "tin"}, RiskLevel.HIGH),  # thin roof: one step up
        ("extreme", {"group": "elderly", "home": "tin"}, RiskLevel.EXTREME),  # capped
        ("high", {"group": "elderly", "home": "pucca"}, RiskLevel.HIGH),
    ],
)
def test_personal_level_for_thin_roofs(ward_level, sub, expected):
    assert personal_level(day(ward_level), sub) is expected


def test_hot_night_lifts_people_at_home_but_not_workers():
    hot = day("moderate", hotNight=True, nightMin=31.5)
    assert personal_level(hot, {"group": "elderly"}) is RiskLevel.HIGH
    assert personal_level(hot, {"group": "parent"}) is RiskLevel.HIGH
    assert personal_level(hot, {"group": "worker"}) is RiskLevel.MODERATE
    assert personal_level(hot, {"group": "worker", "home": "tin"}) is RiskLevel.HIGH
    assert may_concern(day("low", hotNight=True)) and not may_concern(day("low"))


PLACES = resources.from_geojson(SAMPLE_RESOURCES)
WARD = {"wardId": "DL-001", "centroid": [77.23, 28.66]}


def test_nearest_skips_unverified_and_closed_places():
    near = resources.nearest(77.23, 28.66, PLACES, kinds=("cooling",))
    assert [r["id"] for r in near] == ["CC-1"]  # the closer sample point is unverified
    assert 0.3 < near[0]["km"] < 1.0
    assert resources.nearest(77.23, 28.66, PLACES, kinds=("cooling",), open_at=21) == []  # closes at 19:00
    assert resources.nearest(77.23, 28.66, PLACES, kinds=("cooling",), verified_only=False)[0]["id"] == "S-1"
    assert resources.label(near[0], "hi").startswith("सामुदायिक भवन ठंडा कमरा (")


def test_overnight_opening_hours():
    assert resources.is_open({"hours": [20, 6]}, 23) and resources.is_open({"hours": [20, 6]}, 2)
    assert not resources.is_open({"hours": [20, 6]}, 12)


def test_ward_actions():
    plan = [{"from": 11, "to": 17, "work": 0}]
    extreme = day("extreme", workPlan=plan, hotNight=True)
    assert ward_actions(extreme, WARD, PLACES) == ["open_cooling", "shift_work", "check_vulnerable", "night_shelter"]
    # Same day in a ward with nowhere verified to send people.
    far = {"wardId": "DL-002", "centroid": [77.1, 28.5]}
    assert ward_actions(extreme, far, PLACES)[-1] == "cooling_gap"
    assert ward_actions(day("low"), WARD, PLACES) == []


@pytest.mark.parametrize("lang", ["en", "hi"])
def test_work_plan_line(lang):
    plan = [{"from": 9, "to": 11, "work": 30}, {"from": 11, "to": 17, "work": 0}, {"from": 17, "to": 19, "work": 45}]
    line = advisory.work_plan_line(plan, 33.4, lang)
    assert advisory.format_window(11, 17, lang) in line
    assert "33°C" in line and "30" in line
    assert advisory.work_plan_line([], None, lang) is None


def test_work_plan_line_without_stop_hours():
    line = advisory.work_plan_line([{"from": 12, "to": 16, "work": 45}], 28.6, "en")
    assert line == "In the hot hours, work 45 min and rest 15 min in shade each hour."


@pytest.mark.parametrize("lang", ["en", "hi"])
def test_full_message_keeps_every_line_and_ends_with_stop(lang):
    window = advisory.format_window(12, 16, lang)
    extras = [
        advisory.work_plan_line([{"from": 11, "to": 17, "work": 0}], 33.0, lang),
        advisory.roof_line(window, lang),
        advisory.night_line(31.6, lang),
        advisory.place_line("cooling", "Community Hall (0.6 km)", lang),
        advisory.CHECK_IN[lang],
    ]
    msg = advisory.whatsapp_message(
        "Ward 114 Sangam Vihar East Extension",
        1,
        "extreme",
        47.4,
        advisory.template_advice("extreme", window, "elderly", lang),
        lang,
        extras,
    )
    assert len(msg) <= advisory.WHATSAPP_FULL_MAX
    assert msg.endswith(advisory.FOOTER[lang])
    assert all(line in msg for line in extras)
    assert "32°C" in msg and "SOS" in msg
