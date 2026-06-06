from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.contracts.evidence_packet import EvidencePacket
from src.contracts.findings import DriftFinding
from src.evaluation.scorers import ScenarioScore, score_scenario

logger = logging.getLogger(__name__)

GOLDEN_DIR = Path(__file__).parent.parent.parent / "evals" / "golden"


def load_golden_scenarios() -> list[dict[str, Any]]:
    path = GOLDEN_DIR / "golden_drift_scenarios.json"
    if not path.exists():
        logger.warning("Golden scenarios file not found: %s", path)
        return []
    return json.loads(path.read_text())


def evaluate_scenario(
    scenario_id: str,
    finding: DriftFinding,
    packet: EvidencePacket,
) -> ScenarioScore | None:
    """Evaluate a single scenario against golden expectations."""
    golden_scenarios = load_golden_scenarios()
    golden = next((g for g in golden_scenarios if g["scenario_id"] == scenario_id), None)
    if golden is None:
        logger.warning("No golden scenario found for %s", scenario_id)
        return None
    return score_scenario(finding, packet, golden)
