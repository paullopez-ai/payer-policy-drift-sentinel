from __future__ import annotations

from typing import Any

from src.contracts.evidence_packet import EvidencePacket
from src.contracts.findings import DriftFinding


class ScenarioScore:
    def __init__(self) -> None:
        self.detection_correct: bool = False
        self.severity_correct: bool = False
        self.citation_coverage: float = 0.0
        self.confidence_in_range: bool = False
        self.review_routing_correct: bool = False
        self.total_score: float = 0.0

    def compute(self) -> None:
        checks = [
            self.detection_correct,
            self.severity_correct,
            self.citation_coverage >= 0.5,
            self.confidence_in_range,
            self.review_routing_correct,
        ]
        self.total_score = sum(1 for c in checks if c) / len(checks)


def score_scenario(
    finding: DriftFinding,
    packet: EvidencePacket,
    golden: dict[str, Any],
) -> ScenarioScore:
    """Score a workflow result against golden scenario expectations."""
    score = ScenarioScore()

    # Detection correctness
    score.detection_correct = finding.finding_type.value == golden.get("expected_finding_type")

    # Severity calibration
    score.severity_correct = finding.severity.value == golden.get("expected_severity")

    # Citation coverage
    expected_citations = set(golden.get("expected_citations", []))
    actual_citations = {c.citation_id for c in packet.citations}
    if expected_citations:
        score.citation_coverage = len(actual_citations & expected_citations) / len(
            expected_citations
        )
    else:
        score.citation_coverage = 1.0 if packet.citation_count > 0 else 0.0

    # Confidence range
    min_conf = golden.get("expected_confidence_min", 0.5)
    max_conf = golden.get("expected_confidence_max", 1.0)
    score.confidence_in_range = min_conf <= packet.confidence <= max_conf

    # Review routing
    expected_review = golden.get("expected_review_status", "REQUIRED")
    score.review_routing_correct = packet.review_status.value == expected_review

    score.compute()
    return score
