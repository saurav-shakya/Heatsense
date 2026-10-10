"""Outbound delivery (Twilio WhatsApp, Amazon SNS SMS) and Twilio webhook verification.

Twilio credentials live in SSM Parameter Store as SecureStrings under
config.TWILIO_SSM_PREFIX (account-sid, auth-token, whatsapp-from) and are read once per
container. When they're missing, WhatsApp sends become logged dry runs, so the stack
works before the Twilio account exists.
"""

import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from functools import cache

import boto3
from aws_lambda_powertools import Logger

from heatshield import config

logger = Logger(child=True)

TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"


@dataclass(frozen=True)
class TwilioCredentials:
    account_sid: str
    auth_token: str
    whatsapp_from: str  # e.g. "whatsapp:+14155238886" (the sandbox number)


@cache
def twilio_credentials() -> TwilioCredentials | None:
    names = {k: f"{config.TWILIO_SSM_PREFIX}/{k}" for k in ("account-sid", "auth-token", "whatsapp-from")}
    try:
        resp = boto3.client("ssm").get_parameters(Names=list(names.values()), WithDecryption=True)
    except Exception as exc:
        logger.warning("could not read Twilio parameters", extra={"error": str(exc)})
        return None
    values = {p["Name"]: p["Value"] for p in resp.get("Parameters", [])}
    if len(values) != len(names):
        logger.info("Twilio not configured, WhatsApp sends are dry runs", extra={"prefix": config.TWILIO_SSM_PREFIX})
        return None
    sender = values[names["whatsapp-from"]]
    return TwilioCredentials(
        account_sid=values[names["account-sid"]],
        auth_token=values[names["auth-token"]],
        whatsapp_from=sender if sender.startswith("whatsapp:") else f"whatsapp:{sender}",
    )


@dataclass
class SendResult:
    ok: bool
    status: str  # Twilio message status / SNS "sent", or "dry-run" / "error"
    id: str | None = None


def send_whatsapp(phone: str, body: str) -> SendResult:
    creds = twilio_credentials()
    if creds is None:
        logger.info("dry run: would send WhatsApp", extra={"chars": len(body)})
        return SendResult(ok=True, status="dry-run")
    data = urllib.parse.urlencode({"From": creds.whatsapp_from, "To": f"whatsapp:{phone}", "Body": body}).encode()
    req = urllib.request.Request(TWILIO_API.format(sid=creds.account_sid), data=data, method="POST")
    token = base64.b64encode(f"{creds.account_sid}:{creds.auth_token}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read())
        return SendResult(ok=True, status=payload.get("status", "queued"), id=payload.get("sid"))
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:300].decode("utf-8", "replace")
        logger.error("Twilio rejected message", extra={"status": exc.code, "detail": detail})
    except Exception as exc:
        logger.error("Twilio unreachable", extra={"error": str(exc)})
    return SendResult(ok=False, status="error")


def send_sms(phone: str, body: str) -> SendResult:
    try:
        resp = boto3.client("sns").publish(
            PhoneNumber=phone,
            Message=body,
            MessageAttributes={"AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"}},
        )
        return SendResult(ok=True, status="sent", id=resp.get("MessageId"))
    except Exception as exc:
        logger.error("SNS publish failed", extra={"error": str(exc)})
        return SendResult(ok=False, status="error")


def twilio_signature(auth_token: str, url: str, params: dict[str, str]) -> str:
    """X-Twilio-Signature: base64(HMAC-SHA1(token, url + each key+value sorted by key))."""
    payload = url + "".join(f"{k}{params[k]}" for k in sorted(params))
    digest = hmac.new(auth_token.encode(), payload.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


def valid_twilio_request(auth_token: str, url: str, params: dict[str, str], signature: str | None) -> bool:
    if not signature:
        return False
    return hmac.compare_digest(twilio_signature(auth_token, url, params), signature)
