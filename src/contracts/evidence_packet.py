from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.contracts.cost import CostEstimate
from src.contracts.review import ReviewStatus, TrustBoundary


class Citation(BaseModel):
    citation_id: str
    policy_version_id: str
    passage: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class EvidencePacket(BaseModel):
    packet_id: str
    finding_id: str
    scenario_id: str
    summary: str
    root_cause_hypothesis: str
    recommended_review_path: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    limitations: list[str] = Field(default_factory=list)
    trust_boundary: TrustBoundary = TrustBoundary.SUPERVISED
    review_status: ReviewStatus = ReviewStatus.NOT_REQUIRED
    cost: CostEstimate = Field(default_factory=CostEstimate)
    input_hash: str = ""
    model_provider: str = "MOCK"
    model_deployment: str = ""
    created_at: datetime | None = None

    @property
    def citation_count(self) -> int:
        return len(self.citations)
