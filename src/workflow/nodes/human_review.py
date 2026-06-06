from __future__ import annotations

import logging

from src.contracts.review import ReviewStatus, TrustBoundary
from src.contracts.workflow_state import WorkflowState
from src.security.trust_boundaries import classify_trust_boundary, determine_review_status

logger = logging.getLogger(__name__)


async def human_review_node(state: WorkflowState) -> WorkflowState:
    """Applies trust boundary classification and review routing."""
    findings = state.get("findings", [])
    packet = state.get("evidence_packet")

    if not findings or packet is None:
        state["trust_boundary"] = TrustBoundary.RESTRICTED
        state["review_status"] = ReviewStatus.REQUIRED
        return state

    primary_finding = findings[0]
    trust_boundary = classify_trust_boundary(primary_finding)
    review_status = determine_review_status(trust_boundary)

    # Update evidence packet
    packet.trust_boundary = trust_boundary
    packet.review_status = review_status

    state["trust_boundary"] = trust_boundary
    state["review_status"] = review_status

    logger.info(
        "Human review routing: finding=%s, trust=%s, review=%s",
        primary_finding.finding_id,
        trust_boundary.value,
        review_status.value,
    )

    return state
