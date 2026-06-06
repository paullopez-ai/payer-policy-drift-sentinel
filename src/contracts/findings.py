from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class FindingType(str, Enum):
    DENIAL_SPIKE = "DENIAL_SPIKE"
    APPEAL_REVERSAL_SPIKE = "APPEAL_REVERSAL_SPIKE"
    PROVIDER_OUTLIER = "PROVIDER_OUTLIER"
    POLICY_VERSION_DRIFT = "POLICY_VERSION_DRIFT"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingStatus(str, Enum):
    NEW = "NEW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    DISMISSED = "DISMISSED"


class DriftFinding(BaseModel):
    finding_id: str
    scenario_id: str
    finding_type: FindingType
    detection_date: date
    procedure_group: str
    provider_id: str | None = None
    baseline_rate: float
    observed_rate: float
    delta: float
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    policy_version_id: str
    status: FindingStatus = FindingStatus.NEW
    created_at: datetime | None = None
