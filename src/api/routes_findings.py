from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.routes_runs import _completed_runs

router = APIRouter()


@router.get("/findings")
async def list_findings() -> list[dict]:
    findings = []
    for run in _completed_runs.values():
        packet = run.get("evidence_packet")
        if packet:
            findings.append({
                "finding_id": packet.get("finding_id"),
                "scenario_id": run.get("scenario_id"),
                "summary": packet.get("summary", ""),
                "confidence": packet.get("confidence", 0),
                "trust_boundary": packet.get("trust_boundary"),
                "review_status": packet.get("review_status"),
                "citation_count": len(packet.get("citations", [])),
            })
    return findings


@router.get("/findings/{finding_id}")
async def get_finding(finding_id: str) -> dict:
    for run in _completed_runs.values():
        packet = run.get("evidence_packet")
        if packet and packet.get("finding_id") == finding_id:
            return packet
    raise HTTPException(status_code=404, detail="Finding not found")
