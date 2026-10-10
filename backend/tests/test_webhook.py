from urllib.parse import urlencode

import pytest
from conftest import load_function

from heatshield import messaging
from heatshield.messaging import TwilioCredentials, twilio_signature

TOKEN = "test-auth-token"
HOST = "abc123.execute-api.us-east-1.amazonaws.com"
URL = f"https://{HOST}/webhook/whatsapp"


@pytest.fixture
def webhook(aws, monkeypatch):
    monkeypatch.setattr(
        messaging, "twilio_credentials", lambda: TwilioCredentials("AC123", TOKEN, "whatsapp:+14155238886")
    )
    return load_function("whatsapp_webhook")


def signed_event(form: dict, signature: str | None = None) -> dict:
    headers = {"host": HOST, "content-type": "application/x-www-form-urlencoded"}
    headers["x-twilio-signature"] = signature if signature is not None else twilio_signature(TOKEN, URL, form)
    return {"rawPath": "/webhook/whatsapp", "rawQueryString": "", "headers": headers, "body": urlencode(form)}


def message(body: str, phone: str = "+919876543210") -> dict:
    return {"Body": body, "From": f"whatsapp:{phone}", "To": "whatsapp:+14155238886", "MessageSid": "SM1"}


def subscribe(lang: str = "hi"):
    from heatshield import repo
    from heatshield.models import Channel, Group, Language, Subscriber

    repo.put_subscriber(
        Subscriber(
            phone="+919876543210",
            wardId="DL-001",
            group=Group.WORKER,
            language=Language(lang),
            channel=Channel.WHATSAPP,
        )
    )


def test_signature_covers_url_and_every_field_in_sorted_order():
    import base64
    import hashlib
    import hmac

    params = {"To": "+18005551212", "Body": "hi", "From": "+12349013030"}
    expected = base64.b64encode(
        hmac.new(b"12345", b"https://example.com/myappBodyhiFrom+12349013030To+18005551212", hashlib.sha1).digest()
    ).decode()
    assert twilio_signature("12345", "https://example.com/myapp", params) == expected
    assert twilio_signature("12345", "https://example.com/other", params) != expected
    assert twilio_signature("12345", "https://example.com/myapp", {**params, "Body": "STOP"}) != expected


def test_unsigned_or_forged_requests_are_rejected_without_state_change(webhook, ctx):
    from heatshield import repo

    subscribe()
    for sig in ("", "forged"):
        resp = webhook.handler(signed_event(message("STOP"), signature=sig), ctx)
        assert resp["statusCode"] == 403
    assert repo.get_subscriber("+919876543210")["optedIn"] is True


def test_rejects_everything_when_twilio_is_not_configured(aws, ctx, monkeypatch):
    monkeypatch.setattr(messaging, "twilio_credentials", lambda: None)
    webhook = load_function("whatsapp_webhook")
    assert webhook.handler(signed_event(message("STOP")), ctx)["statusCode"] == 403


def test_stop_then_start(webhook, ctx):
    from heatshield import repo

    subscribe(lang="en")
    resp = webhook.handler(signed_event(message("stop")), ctx)
    assert resp["statusCode"] == 200 and "START" in resp["body"]
    assert repo.get_subscriber("+919876543210")["optedIn"] is False
    resp = webhook.handler(signed_event(message("START")), ctx)
    assert "STOP" in resp["body"]
    assert repo.get_subscriber("+919876543210")["optedIn"] is True


def test_hindi_stop_word(webhook, ctx):
    from heatshield import repo

    subscribe()
    resp = webhook.handler(signed_event(message("बंद")), ctx)
    assert "अलर्ट नहीं मिलेंगे" in resp["body"]
    assert repo.get_subscriber("+919876543210")["optedIn"] is False


def test_unknown_number_is_told_how_to_subscribe(webhook, ctx):
    resp = webhook.handler(signed_event(message("hello", phone="+919000000000")), ctx)
    assert "Subscribe at https://heatshield.pages.dev" in resp["body"]


def test_question_is_answered_by_claude_from_the_ward_forecast(webhook, ctx, monkeypatch):
    from heatshield import advisory

    load_function("risk_engine").handler({}, ctx)
    subscribe()
    prompts = []

    def ask(system, prompt):
        prompts.append((system, prompt))
        return "दोपहर 3 बजे बाहर जाना ठीक नहीं, तब 45°C जैसा महसूस होगा। शाम 6 बजे के बाद जाएं।"

    monkeypatch.setattr(advisory, "ask_claude", ask)
    resp = webhook.handler(signed_event(message("Can I go out at 3 PM?")), ctx)
    assert "दोपहर 3 बजे" in resp["body"]
    system, prompt = prompts[0]
    assert "ONLY" in system and "108" in system
    assert "Ward: Sample A" in prompt and "<question>Can I go out at 3 PM?</question>" in prompt
    assert "<language>Hindi</language>" in prompt


def test_question_falls_back_to_a_template_when_bedrock_fails(webhook, ctx):
    load_function("risk_engine").handler({}, ctx)
    subscribe(lang="en")
    resp = webhook.handler(signed_event(message("Is it safe to run today?")), ctx)
    assert resp["statusCode"] == 200
    assert "Today in Sample A" in resp["body"]


def test_reply_is_escaped_twiml(webhook, ctx):
    resp = webhook.handler(signed_event(message("hi", phone="+919000000000")), ctx)
    assert resp["headers"]["Content-Type"] == "text/xml"
    assert resp["body"].startswith('<?xml version="1.0" encoding="UTF-8"?><Response><Message>')


def subscribe_elderly(caregiver: str | None = "+919811111111", lang: str = "en"):
    from heatshield import repo
    from heatshield.models import Channel, Group, Language, Subscriber

    repo.put_subscriber(
        Subscriber(
            phone="+919876543210",
            wardId="DL-001",
            group=Group.ELDERLY,
            language=Language(lang),
            channel=Channel.WHATSAPP,
            caregiverPhone=caregiver,
        )
    )


def test_ok_reply_records_the_check_in(webhook, ctx):
    from heatshield import repo

    subscribe_elderly(lang="hi")
    repo.set_check_in("+919876543210", "2099-01-01", "asked")  # an evening alert asked about a later day
    resp = webhook.handler(signed_event(message("ठीक")), ctx)
    assert "धन्यवाद" in resp["body"]
    sub = repo.get_subscriber("+919876543210")
    assert sub["checkInStatus"] == "ok" and sub["checkInDate"] == "2099-01-01"


def test_ok_without_an_open_check_in_is_not_counted(webhook, ctx):
    from heatshield import repo

    subscribe_elderly()
    resp = webhook.handler(signed_event(message("OK")), ctx)
    assert "Thank you" in resp["body"]
    assert "checkInStatus" not in repo.get_subscriber("+919876543210")


def test_sos_tells_the_caregiver_and_names_a_cool_place(webhook, ctx, monkeypatch):
    from conftest import put_resources

    from heatshield import repo
    from heatshield.messaging import SendResult

    put_resources()
    subscribe_elderly()
    sent = []
    monkeypatch.setattr(
        webhook.messaging, "send_whatsapp", lambda p, b: sent.append((p, b)) or SendResult(True, "queued")
    )
    monkeypatch.setattr(webhook.resources, "is_open", lambda r, h: True)  # whatever the clock says
    resp = webhook.handler(signed_event(message("sos")), ctx)
    assert "call 108" in resp["body"] and "We have told your contact." in resp["body"]
    assert "Community Hall Cool Room" in resp["body"]
    assert sent[0][0] == "+919811111111" and "+919876543210" in sent[0][1] and "Sample A" in sent[0][1]
    assert repo.get_subscriber("+919876543210")["checkInStatus"] == "help"


def test_sos_without_caregiver_still_gets_emergency_advice(webhook, ctx):
    subscribe_elderly(caregiver=None, lang="hi")
    resp = webhook.handler(signed_event(message("मदद")), ctx)
    assert "108" in resp["body"] and "परिचित" not in resp["body"]
