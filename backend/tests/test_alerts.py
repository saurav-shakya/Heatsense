"""Alert text: golden templates, length limits, and the Bedrock fallback rules."""

import pytest

from heatshield import advisory
from heatshield.advisory import (
    FOOTER,
    TEMPLATES,
    Advisor,
    format_window,
    sms_message,
    template_advice,
    whatsapp_message,
)

GROUPS = ["worker", "parent", "elderly"]
LONG_WARD = "Ward 114 Sangam Vihar East Extension"


@pytest.mark.parametrize("lang", ["en", "hi"])
@pytest.mark.parametrize("group", GROUPS)
@pytest.mark.parametrize("level", ["high", "extreme"])
def test_every_template_alert_fits_and_ends_with_stop(lang, group, level):
    window = format_window(12, 16, lang)
    msg = whatsapp_message(LONG_WARD, 1, level, 47.4, template_advice(level, window, group, lang), lang)
    assert len(msg) <= advisory.WHATSAPP_MAX
    assert msg.endswith(FOOTER[lang])
    assert "47°C" in msg  # how bad
    assert window in msg  # when


def test_golden_examples():
    # Reviewed by hand; changes here need a native-speaker check.
    assert whatsapp_message(
        "Ward 14 Jahangirpuri",
        1,
        "extreme",
        47.2,
        template_advice("extreme", format_window(12, 16, "hi"), "worker", "hi"),
        "hi",
    ) == (
        "HeatShield: Ward 14 Jahangirpuri में कल गर्मी का ख़तरा बहुत ज़्यादा, 47°C जैसा महसूस होगा। "
        "दोपहर 12 से 4 बजे तक बाहर भारी काम बंद रखें। हर 20 मिनट पानी पिएं, छांव में रहें, सिर ढकें। "
        "अलर्ट बंद करने के लिए STOP भेजें।"
    )
    assert whatsapp_message(
        "Ward 14 Jahangirpuri",
        0,
        "high",
        44.6,
        template_advice("high", format_window(12, 16, "en"), "parent", "en"),
        "en",
    ) == (
        "HeatShield: HIGH heat risk in Ward 14 Jahangirpuri today, feels like 45°C. "
        "Keep children indoors from noon to 4 pm. Give water often and dress them in light cotton. "
        "Reply STOP to stop alerts."
    )


@pytest.mark.parametrize(
    ("start", "end", "lang", "text"),
    [
        (12, 16, "en", "from noon to 4 pm"),
        (10, 18, "en", "from 10 am to 6 pm"),
        (12, 16, "hi", "दोपहर 12 से 4 बजे तक"),
        (10, 18, "hi", "सुबह 10 से शाम 6 बजे तक"),
    ],
)
def test_format_window(start, end, lang, text):
    assert format_window(start, end, lang) == text


@pytest.mark.parametrize("lang", ["en", "hi"])
def test_sms_fits_one_or_two_segments(lang):
    msg = sms_message(LONG_WARD, 1, "extreme", format_window(11, 17, lang), lang)
    assert len(msg) <= advisory.SMS_MAX[lang]
    assert "STOP" in msg


def test_all_templates_exist():
    for lang in TEMPLATES:
        for group in GROUPS:
            assert set(TEMPLATES[lang][group]) == {"high", "extreme"}


def test_bedrock_advice_is_cached_per_level_window_group_language():
    calls = []

    def ask(system, prompt):
        calls.append(prompt)
        return "दोपहर 12 से 4 बजे तक धूप में काम न करें, हर 20 मिनट पानी पिएं।"

    advisor = Advisor(mode="bedrock", ask=ask)
    window = format_window(12, 16, "hi")
    for _ in range(50):  # 50 subscribers in the same situation
        advisor.advice("extreme", window, "worker", "hi")
    advisor.advice("extreme", window, "parent", "hi")
    assert len(calls) == advisor.ai_calls == 2
    assert "Hindi" in calls[0] and "outdoors" in calls[0]


@pytest.mark.parametrize(
    "reply",
    [
        None,  # Bedrock error or refusal
        "",
        "x" * (advisory.ADVICE_MAX + 1),  # too long
        "Stay safe, see https://example.com",  # links are not allowed
        "Stay indoors and drink water.",  # English when Hindi was asked
    ],
)
def test_bad_or_missing_ai_advice_falls_back_to_the_template(reply):
    advisor = Advisor(mode="bedrock", ask=lambda s, p: reply)
    window = format_window(12, 16, "hi")
    assert advisor.advice("high", window, "elderly", "hi") == template_advice("high", window, "elderly", "hi")


def test_template_mode_never_calls_bedrock():
    advisor = Advisor(mode="template", ask=lambda s, p: pytest.fail("called Bedrock"))
    advisor.advice("high", "from noon to 4 pm", "worker", "en")
    assert advisor.ai_calls == 0


class _Block:
    def __init__(self, type_, text=""):
        self.type, self.text = type_, text


class _Message:
    def __init__(self, stop_reason, blocks):
        self.stop_reason, self.content = stop_reason, blocks


class _Client:
    def __init__(self, message):
        self.message = message
        self.kwargs = None
        self.messages = self

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self.message


def test_ask_claude_reads_text_and_handles_refusal(monkeypatch):
    client = _Client(_Message("end_turn", [_Block("thinking"), _Block("text", '"Drink water often."')]))
    monkeypatch.setattr(advisory, "_client", lambda: client)
    assert advisory.ask_claude("sys", "hi") == "Drink water often."
    assert client.kwargs["model"] == "anthropic.claude-opus-5-5"
    assert client.kwargs["output_config"] == {"effort": "low"}
    client.message = _Message("refusal", [])
    assert advisory.ask_claude("sys", "hi") is None
