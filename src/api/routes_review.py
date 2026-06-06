from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.routes_runs import _completed_runs

router = APIRouter()


class ReviewRequest(BaseModel):
    reviewer_id: str
    action: str  # APPROVE, REJECT, REQUEST_MORE_EVIDENCE
    notes: str = ""


@router.post("/review/{finding_id}")
async def submit_review(finding_id: str, request: ReviewRequest) -> dict:
    for run in _completed_runs.values():
        packet = run.get("evidence_packet")
        if packet and packet.get("finding_id") == finding_id:
            if request.action == "APPROVE":
                packet["review_status"] = "APPROVED"
                run["review_status"] = "APPROVED"
            elif request.action == "REJECT":
                packet["review_status"] = "REJECTED"
                run["review_status"] = "REJECTED"
            elif request.action == "REQUEST_MORE_EVIDENCE":
                packet["review_status"] = "REQUIRED"
                run["review_status"] = "REQUIRED"
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {request.action}. Must be APPROVE, REJECT, or REQUEST_MORE_EVIDENCE.",
                )

            return {
                "finding_id": finding_id,
                "action": request.action,
                "reviewer_id": request.reviewer_id,
                "review_status": packet["review_status"],
                "decided_at": datetime.now(timezone.utc).isoformat(),
                "notes": request.notes,
            }

    raise HTTPException(status_code=404, detail="Finding not found")
