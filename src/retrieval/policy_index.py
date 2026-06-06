from __future__ import annotations

import hashlib

from src.contracts.workflow_state import PolicyPassage


class PolicyIndex:
    """Normalizes policy chunks with citation IDs and version metadata."""

    def __init__(self) -> None:
        self._passages: list[PolicyPassage] = []

    def add_passage(
        self,
        policy_version_id: str,
        passage: str,
        relevance_score: float = 1.0,
    ) -> PolicyPassage:
        content_hash = hashlib.sha256(passage.encode()).hexdigest()[:12]
        citation_id = f"CIT-{policy_version_id}-{content_hash}"
        entry: PolicyPassage = {
            "citation_id": citation_id,
            "policy_version_id": policy_version_id,
            "passage": passage,
            "relevance_score": relevance_score,
        }
        self._passages.append(entry)
        return entry

    @property
    def passages(self) -> list[PolicyPassage]:
        return list(self._passages)

    def top_k(self, k: int = 5) -> list[PolicyPassage]:
        sorted_passages = sorted(
            self._passages,
            key=lambda p: p.get("relevance_score", 0.0),
            reverse=True,
        )
        return sorted_passages[:k]
