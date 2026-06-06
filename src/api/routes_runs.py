from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from src.clients.mock_clients import (
    MockAzureOpenAIClient,
    MockDatabricksClient,
    MockSnowflakeClient,
)
from src.config.settings import settings
from src.workflow.graph import DriftSentinelWorkflow

router = APIRouter()

# In-memory store for completed runs (mock mode)
_completed_runs: dict[str, dict] = {}


class RunRequest(BaseModel):
    scenario_id: str


@router.post("/runs")
async def create_run(request: RunRequest) -> dict:
    if settings.is_mock:
        snowflake = MockSnowflakeClient()
        databricks = MockDatabricksClient()
        openai = MockAzureOpenAIClient(scenario_id=request.scenario_id)
    else:
        raise HTTPException(
            status_code=501,
            detail="Live mode requires configured cloud clients. Use MOCK_LLM=true for testing.",
        )

    workflow = DriftSentinelWorkflow(
        snowflake_client=snowflake,
        databricks_client=databricks,
        openai_client=openai,
    )

    state = await workflow.run(request.scenario_id)

    error = state.get("error")
    if error:
        raise HTTPException(status_code=422, detail=error)

    packet = state.get("evidence_packet")
    if packet is None:
        raise HTTPException(status_code=500, detail="No evidence packet produced")

    result = {
        "run_id": state["run_id"],
        "scenario_id": state["scenario_id"],
        "data_ready": state.get("data_ready", False),
        "findings_count": len(state.get("findings", [])),
        "quality_passed": state.get("quality_passed", False),
        "quality_issues": state.get("quality_issues", []),
        "trust_boundary": state.get("trust_boundary", "UNKNOWN"),
        "review_status": state.get("review_status", "UNKNOWN"),
        "evidence_packet": packet.model_dump(mode="json") if packet else None,
    }

    _completed_runs[state["run_id"]] = result

    return result


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    run = _completed_runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
