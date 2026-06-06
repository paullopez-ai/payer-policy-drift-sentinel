from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TrustBoundary(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"
    SUPERVISED = "SUPERVISED"
    RESTRICTED = "RESTRICTED"


class ReviewStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReviewDecision(BaseModel):
    finding_id: str
    reviewer_id: str
    action: str  # APPROVE, REJECT, REQUEST_MORE_EVIDENCE
    notes: str = ""
    decided_at: datetime | None = None
