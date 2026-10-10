"""Incoming WhatsApp messages (Twilio webhook) for the Ask HeatShield bot.

Twilio POSTs application/x-www-form-urlencoded and expects TwiML back.

SKELETON: replies with a fixed message. Phase 3 adds X-Twilio-Signature validation,
STOP -> repo.opt_out, and Bedrock answers grounded in the sender's ward forecast.
Until the signature is validated, this handler must not change any stored state.
"""

import base64
from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from aws_lambda_powertools import Logger

logger = Logger()

REPLY = "HeatShield: the Ask HeatShield bot is coming soon. / HeatShield बॉट जल्द आ रहा है।"


def parse_form(event: dict) -> dict[str, str]:
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    return {k: v[0] for k, v in parse_qs(body).items()}


def twiml(message: str) -> dict:
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/xml"},
        "body": f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escape(message)}</Message></Response>',
    }


@logger.inject_lambda_context
def handler(event, context):
    form = parse_form(event)
    logger.info("inbound message", extra={"chars": len(form.get("Body", ""))})
    return twiml(REPLY)
