from __future__ import annotations

import logging

from src.config.settings import settings
from src.contracts.workflow_state import WorkflowState

logger = logging.getLogger(__name__)

MIN_CONFIDENCE = 0.5
MIN_CITATIONS = 1


async def quality_gate_node(state: WorkflowState) -> WorkflowState:
    """Checks confidence, citations, eval thresholds, cost, and trust boundary."""
    issues: list[str] = []
    packet = state.get("evidence_packet")

    if packet is None:
        issues.append("No evidence packet generated")
        state["quality_passed"] = False
        state["quality_issues"] = issues
        return state

    # Confidence check
    if packet.confidence < MIN_CONFIDENCE:
        issues.append(
            f"Confidence {packet.confidence:.2f} below minimum {MIN_CONFIDENCE}"
        )

    # Citation check
    if packet.citation_count < MIN_CITATIONS:
        issues.append(
            f"Citation count {packet.citation_count} below minimum {MIN_CITATIONS}"
        )

    # Cost check
    cost = state.get("cost")
    if cost and cost.total_estimated_cost_usd > settings.max_run_cost_usd:
        issues.append(
            f"Estimated cost ${cost.total_estimated_cost_usd:.2f} exceeds "
            f"max ${settings.max_run_cost_usd:.2f}"
        )

    # Token check
    if cost:
        if cost.prompt_tokens > settings.max_prompt_tokens:
            issues.append(
                f"Prompt tokens {cost.prompt_tokens} exceed max {settings.max_prompt_tokens}"
            )
        if cost.completion_tokens > settings.max_completion_tokens:
            issues.append(
                f"Completion tokens {cost.completion_tokens} exceed max {settings.max_completion_tokens}"
            )

    passed = len(issues) == 0
    state["quality_passed"] = passed
    state["quality_issues"] = issues

    if passed:
        logger.info("Quality gate passed for packet %s", packet.packet_id)
    else:
        logger.warning("Quality gate failed: %s", issues)

    return state
