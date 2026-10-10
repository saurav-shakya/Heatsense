"""Alert and bot text: fixed safety templates, plus advisories written by Claude on Amazon Bedrock.

Every alert answers three things (how bad, when, what to do) and ends with how to stop
alerts. The "what to do" part can be written by Claude, but only from SAFETY_GUIDE, and
only if the result passes the checks in `_valid_advice`; otherwise the human-reviewed
template is used. A failure on the AI side never blocks an alert.

Advice is cached per (level, peak window, group, language), so one dispatcher run makes
at most a handful of Bedrock calls however many wards and subscribers it covers.
"""

import re
from functools import cache

from aws_lambda_powertools import Logger

from heatshield import config

logger = Logger(child=True)

WHATSAPP_MAX = 300  # headline + advice + footer
WHATSAPP_FULL_MAX = 900  # with the personal lines below (Twilio allows 1600)
ADVICE_MAX = 170  # the Claude-written part, leaves room for the headline and footer
SMS_MAX = {"en": 160, "hi": 134}  # one GSM-7 segment / two UCS-2 segments
DEVANAGARI = re.compile(r"[ऀ-ॿ]")

# Distilled from NDMA / IMD public heat-wave guidance. Claude may use nothing beyond this.
SAFETY_GUIDE = """\
- Drink water often, even when not thirsty. ORS, lassi, nimbu pani, chaas and buttermilk help.
- Avoid going out and avoid heavy work in the hottest hours (usually 12 noon to 4 pm).
- Outdoor workers: start early, take rest breaks in shade, drink water every 20 minutes.
- Wear light, loose cotton clothes; cover the head with a cloth, cap or umbrella.
- Keep children indoors in the afternoon. Never leave a child in a parked vehicle.
- Elderly people: stay in the coolest room, keep water within reach; neighbours should check on them.
- Use fans, wet cloths and cool baths; keep curtains closed in the afternoon.
- Danger signs: confusion, fainting, hot dry skin, very high body temperature. Call 108 or 112 at once,
  move the person to shade and cool them with water.
"""

# Human-reviewed fallback advice per language, group and level. These are also the golden
# examples in tests/test_alerts.py.
TEMPLATES: dict[str, dict[str, dict[str, str]]] = {
    "en": {
        "worker": {
            "high": "Start work early, rest in shade and drink water every 20 minutes. Avoid heavy work {window}.",
            "extreme": (
                "Stop heavy outdoor work {window}. Drink water every 20 minutes, rest in shade, cover your head."
            ),
        },
        "parent": {
            "high": "Keep children indoors {window}. Give water often and dress them in light cotton.",
            "extreme": "Keep children indoors {window}. Give water often. Never leave a child in a parked vehicle.",
        },
        "elderly": {
            "high": "Stay in the coolest room {window}. Keep water close and sip it often.",
            "extreme": "Stay indoors {window} and drink water often. If dizzy or confused, call 108 at once.",
        },
    },
    "hi": {
        "worker": {
            "high": "काम जल्दी शुरू करें, छांव में आराम करें, हर 20 मिनट पानी पिएं। {window} भारी काम न करें।",
            "extreme": "{window} बाहर भारी काम बंद रखें। हर 20 मिनट पानी पिएं, छांव में रहें, सिर ढकें।",
        },
        "parent": {
            "high": "{window} बच्चों को घर के अंदर रखें। बार-बार पानी दें, हल्के सूती कपड़े पहनाएं।",
            "extreme": "{window} बच्चों को घर के अंदर रखें। बार-बार पानी दें। बच्चे को कभी बंद गाड़ी में न छोड़ें।",
        },
        "elderly": {
            "high": "{window} घर के सबसे ठंडे कमरे में रहें। पानी पास रखें और बार-बार पिएं।",
            "extreme": "{window} घर के अंदर रहें, बार-बार पानी पिएं। चक्कर या बेचैनी हो तो तुरंत 108 पर कॉल करें।",
        },
    },
}

LEVEL_NAMES = {
    "en": {"low": "low", "moderate": "moderate", "high": "HIGH", "extreme": "EXTREME"},
    "hi": {"low": "कम", "moderate": "मध्यम", "high": "ज़्यादा", "extreme": "बहुत ज़्यादा"},
}
DAY_NAMES = {"en": ("today", "tomorrow"), "hi": ("आज", "कल")}
FOOTER = {"en": "Reply STOP to stop alerts.", "hi": "अलर्ट बंद करने के लिए STOP भेजें।"}


def _hour_en(h: int) -> str:
    h %= 24
    if h == 0:
        return "midnight"
    if h == 12:
        return "noon"
    return f"{h % 12} {'am' if h < 12 else 'pm'}"


def format_window(start_hour: int, end_hour: int, lang: str) -> str:
    """IST hour range [start, end) as words, e.g. 'from noon to 4 pm' / 'दोपहर 12 से 4 बजे तक'."""
    if lang == "hi":

        def part(h: int) -> str:
            h %= 24
            return "सुबह" if 4 <= h < 12 else "दोपहर" if 12 <= h < 16 else "शाम" if 16 <= h < 19 else "रात"

        def num(h: int) -> int:
            return (h % 12) or 12

        # The end hour is exclusive, so name its part of day from the hour before it: 12-4 pm is all दोपहर.
        if part(start_hour) == part(end_hour - 1):
            return f"{part(start_hour)} {num(start_hour)} से {num(end_hour)} बजे तक"
        return f"{part(start_hour)} {num(start_hour)} से {part(end_hour - 1)} {num(end_hour)} बजे तक"
    return f"from {_hour_en(start_hour)} to {_hour_en(end_hour)}"


def headline(ward_name: str, day: int, level: str, felt: float, lang: str) -> str:
    day_word = DAY_NAMES[lang][min(day, 1)]
    lvl = LEVEL_NAMES[lang][level]
    if lang == "hi":
        return f"HeatShield: {ward_name} में {day_word} गर्मी का ख़तरा {lvl}, {round(felt)}°C जैसा महसूस होगा।"
    return f"HeatShield: {lvl} heat risk in {ward_name} {day_word}, feels like {round(felt)}°C."


def template_advice(level: str, window: str, group: str, lang: str) -> str:
    text = TEMPLATES[lang][group]["extreme" if level == "extreme" else "high"].format(window=window)
    return text[0].upper() + text[1:]


# --------------------------------------------------------------------------- Bedrock

ADVISORY_SYSTEM = f"""You write one heat-safety advisory for a WhatsApp alert in Delhi.

Use ONLY the advice in this safety guide. Do not add anything else, no medical advice, no drugs,
no links, no greetings, no emoji:
{SAFETY_GUIDE}
Rules:
- At most {ADVICE_MAX} characters, one or two short sentences, plain words a 12-year-old understands.
- Say what to do and mention the risky hours given to you.
- Write for the group given to you. Write in the language given to you (Hindi means Devanagari script).
- Output only the advisory text."""

GROUP_DESC = {
    "worker": "someone who works outdoors (construction, delivery, street vending)",
    "parent": "a parent of young children",
    "elderly": "an elderly person, or someone caring for one",
}


@cache
def _client():
    from anthropic import AnthropicBedrockMantle

    return AnthropicBedrockMantle(aws_region=config.AWS_REGION, timeout=8.0, max_retries=1)


def _text(message) -> str:
    return "".join(b.text for b in message.content if b.type == "text").strip().strip('"').strip()


def _valid_advice(text: str, lang: str) -> bool:
    if not text or len(text) > ADVICE_MAX or "http" in text.lower() or "\n\n" in text:
        return False
    if lang == "hi" and not DEVANAGARI.search(text):
        return False
    return True


def ask_claude(system: str, prompt: str) -> str | None:
    """One short Claude call on Bedrock. None on any failure or refusal (callers fall back)."""
    import anthropic

    try:
        message = _client().messages.create(
            model=config.ADVISORY_MODEL_ID,
            max_tokens=2000,
            output_config={"effort": "low"},
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.RateLimitError:
        logger.warning("bedrock throttled, using fallback")
        return None
    except anthropic.APIStatusError as exc:
        logger.warning("bedrock error, using fallback", extra={"status": exc.status_code})
        return None
    except anthropic.APIConnectionError:
        logger.warning("bedrock unreachable, using fallback")
        return None
    except anthropic.AnthropicError as exc:  # e.g. missing credentials or region
        logger.warning("bedrock client error, using fallback", extra={"error": str(exc)})
        return None
    if message.stop_reason == "refusal":
        logger.warning("bedrock refused, using fallback")
        return None
    if message.stop_reason == "max_tokens":
        return None
    return _text(message)


class Advisor:
    """Writes the advice part of alerts, with a per-instance cache keyed on what the advice depends on."""

    def __init__(self, mode: str | None = None, ask=None):
        self.mode = mode or config.ADVISORY_MODE
        self._ask = ask or ask_claude
        self._cache: dict[tuple[str, str, str, str], str] = {}
        self.ai_calls = 0

    def advice(self, level: str, window: str, group: str, lang: str) -> str:
        key = (level, window, group, lang)
        if key not in self._cache:
            self._cache[key] = self._write(level, window, group, lang)
        return self._cache[key]

    def _write(self, level: str, window: str, group: str, lang: str) -> str:
        fallback = template_advice(level, window, group, lang)
        if self.mode != "bedrock":
            return fallback
        self.ai_calls += 1
        prompt = (
            f"Risk level: {level}\nRisky hours: {window}\nGroup: {GROUP_DESC[group]}\n"
            f"Language: {'Hindi' if lang == 'hi' else 'English'}\n"
            f"Example of the right length and tone:\n{fallback}"
        )
        text = self._ask(ADVISORY_SYSTEM, prompt)
        if text is not None and _valid_advice(text, lang):
            return text
        if text is not None:
            logger.warning("advice failed checks, using template", extra={"chars": len(text)})
        return fallback


def whatsapp_message(
    ward_name: str, day: int, level: str, felt: float, advice: str, lang: str, extras: list[str] | None = None
) -> str:
    """Headline, advice, then any personal lines (work plan, tonight, nearest place, check-in), then STOP."""
    msg = f"{headline(ward_name, day, level, felt, lang)} {advice}"
    if len(msg) + len(FOOTER[lang]) + 1 > WHATSAPP_MAX:  # very long ward name: shorten it
        msg = f"{headline(ward_name[:40], day, level, felt, lang)} {advice}"
    if not extras:
        return f"{msg} {FOOTER[lang]}"
    lines = [msg]
    for line in extras:
        if sum(len(x) + 1 for x in lines) + len(line) + len(FOOTER[lang]) + 1 > WHATSAPP_FULL_MAX:
            break
        lines.append(line)
    return "\n".join([*lines, FOOTER[lang]])


# --------------------------------------------------------------------------- personal lines
#
# Short, fixed sentences added under the advice. They carry numbers the generic advice can't:
# the hours to stop work, tonight's low, where to go. Never written by the model.


def work_plan_line(plan: list[dict], wbgt_max: float | None, lang: str) -> str | None:
    """Stop-work hours and a work-rest ratio for the other hot hours, from a day's workPlan."""
    if not plan:
        return None
    stops = [seg for seg in plan if seg["work"] == 0]
    partial = [seg["work"] for seg in plan if seg["work"] > 0]
    parts = []
    if stops:
        window = format_window(stops[0]["from"], stops[-1]["to"], lang)
        wbgt = f" (WBGT {round(wbgt_max)}°C)" if wbgt_max is not None else ""
        parts.append(
            f"{window} बाहर भारी काम बंद रखें{wbgt}।" if lang == "hi" else f"Stop heavy outdoor work {window}{wbgt}."
        )
    if partial:
        work = min(partial)
        rest = 60 - work
        if lang == "hi":
            parts.append(f"बाकी गर्म घंटों में हर घंटे {work} मिनट काम, {rest} मिनट छांव में आराम।")
        else:
            other = "In the other hot hours" if stops else "In the hot hours"
            parts.append(f"{other}, work {work} min and rest {rest} min in shade each hour.")
    text = " ".join(parts)
    return text[0].upper() + text[1:]


def night_line(night_min: float, lang: str) -> str:
    if lang == "hi":
        return (
            f"आज रात तापमान {round(night_min)}°C से नीचे नहीं जाएगा: सबसे ठंडी जगह सोएं, पानी पास रखें, गीले कपड़े से शरीर ठंडा करें।"
        )
    return (
        f"Tonight stays above {round(night_min)}°C: sleep in the coolest spot, keep water by the bed, "
        "cool down with a wet cloth."
    )


def roof_line(window: str, lang: str) -> str:
    if lang == "hi":
        return f"{window} टीन या शीट की छत वाला कमरा बाहर से भी ज़्यादा गर्म होता है: उस समय छांव या ठंडी जगह पर रहें।"
    return (
        f"Rooms under tin or sheet roofs get hotter than outside {window}: spend those hours in shade or a cool place."
    )


PLACE_INTRO = {
    "cooling": {"en": "Nearest cool place", "hi": "सबसे पास ठंडी जगह"},
    "water": {"en": "Nearest drinking water", "hi": "सबसे पास पीने का पानी"},
    "rest": {"en": "Nearest shaded rest point", "hi": "सबसे पास छांव में आराम की जगह"},
}


def place_line(kind: str, place_label: str, lang: str) -> str:
    return f"{PLACE_INTRO[kind][lang]}: {place_label}{'।' if lang == 'hi' else '.'}"


# SOS rather than HELP: carriers and Twilio treat HELP as a reserved keyword on some routes.
CHECK_IN = {
    "en": "Reply OK if you are fine, or SOS if you need help. HeatShield never asks for money or OTPs.",
    "hi": "ठीक हैं तो OK, मदद चाहिए तो SOS या मदद लिखें। HeatShield कभी पैसे या OTP नहीं मांगता।",
}


SMS_TEMPLATES = {
    "en": "HeatShield {ward}: {level} heat {day}. Stay in shade {window}, drink water. Reply STOP to end",
    "hi": "HeatShield {ward}: {day} गर्मी {level}। {window} छांव में रहें, पानी पिएं। बंद: STOP",
}


def sms_message(ward_name: str, day: int, level: str, window: str, lang: str) -> str:
    """Short SMS for feature phones: one segment in English, two (Unicode) in Hindi."""
    limit = SMS_MAX[lang]
    for name_len in (24, 16, 10, 0):
        msg = SMS_TEMPLATES[lang].format(
            ward=ward_name[:name_len].strip(),
            level=LEVEL_NAMES[lang][level],
            day=DAY_NAMES[lang][min(day, 1)],
            window=window,
        )
        if len(msg) <= limit:
            return msg.replace("HeatShield : ", "HeatShield: ")
    return msg[:limit]
