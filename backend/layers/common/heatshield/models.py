"""Item shapes for the three DynamoDB tables (see docs/architecture.md)."""

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum, StrEnum
from typing import Any


class Group(StrEnum):
    WORKER = "worker"
    PARENT = "parent"
    ELDERLY = "elderly"


class Language(StrEnum):
    EN = "en"
    HI = "hi"


class Channel(StrEnum):
    WHATSAPP = "whatsapp"
    SMS = "sms"


def to_ddb(value: Any) -> Any:
    """DynamoDB rejects Python floats; convert recursively to Decimal."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: to_ddb(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [to_ddb(v) for v in value]
    return value


def from_ddb(value: Any) -> Any:
    """Inverse of to_ddb for JSON responses: Decimal -> int/float."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, dict):
        return {k: from_ddb(v) for k, v in value.items()}
    if isinstance(value, list):
        return [from_ddb(v) for v in value]
    return value


@dataclass
class Ward:
    wardId: str
    name: str
    city: str
    geometryS3Key: str
    lstOffset: float  # degrees C above/below city mean surface temperature
    ndvi: float  # mean green cover, -1..1
    popDensity: float  # people per km^2
    vulnerabilityScore: float  # V in [0, 1]
    centroid: list[float] | None = None  # [lon, lat], used to pick the forecast grid point
    fixture: bool = False  # True for the synthetic placeholder layer

    def to_item(self) -> dict:
        return to_ddb(asdict(self))


@dataclass
class RiskForecast:
    wardId: str
    forecastTime: str  # ISO-8601 UTC hour, e.g. 2026-10-10T09:00:00Z
    heatIndex: float
    hazard: float
    risk: float
    level: str
    generatedAt: str
    expiresAt: int  # epoch seconds, DynamoDB TTL

    def to_item(self) -> dict:
        return to_ddb(asdict(self))


@dataclass
class Subscriber:
    phone: str  # E.164
    wardId: str
    group: Group
    language: Language
    channel: Channel
    optedIn: bool = True
    lastAlertAt: str | None = None
    createdAt: str | None = field(default=None)
    # Alert cap bookkeeping (written by repo.claim_alert): IST date of the last alert,
    # how many went out that day, and "<target date>:<level>:<slot>" of the last one.
    alertDate: str | None = None
    alertsToday: int | None = None
    lastAlertKey: str | None = None

    def to_item(self) -> dict:
        return to_ddb(asdict(self))
