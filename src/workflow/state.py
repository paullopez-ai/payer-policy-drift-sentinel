from __future__ import annotations

import uuid

from src.contracts.workflow_state import WorkflowState


def create_initial_state(scenario_id: str) -> WorkflowState:
    """Create initial workflow state for a scenario run."""
    return WorkflowState(
        scenario_id=scenario_id,
        run_id=str(uuid.uuid4()),
        data_ready=False,
        readiness_details={},
        findings=[],
        policy_passages=[],
        financial_impact={},
        quality_passed=False,
        quality_issues=[],
        error=None,
    )
