from __future__ import annotations

from src.contracts.workflow_state import PolicyPassage


def mmr_rerank(
    passages: list[PolicyPassage],
    k: int = 5,
    diversity_weight: float = 0.3,
) -> list[PolicyPassage]:
    """Simple diversity-aware reranking. Returns top-k passages balancing relevance and diversity.

    This is a simplified MMR that uses policy_version_id as a proxy for diversity.
    In production, this would use embedding similarity.
    """
    if len(passages) <= k:
        return passages

    selected: list[PolicyPassage] = []
    remaining = list(passages)

    # Pick the highest relevance first
    remaining.sort(key=lambda p: p.get("relevance_score", 0.0), reverse=True)
    selected.append(remaining.pop(0))

    while len(selected) < k and remaining:
        best_idx = 0
        best_score = -1.0

        for i, candidate in enumerate(remaining):
            relevance = candidate.get("relevance_score", 0.0)
            # Diversity bonus: penalize if same policy version is already selected
            same_version_count = sum(
                1
                for s in selected
                if s.get("policy_version_id") == candidate.get("policy_version_id")
            )
            diversity_bonus = 1.0 / (1.0 + same_version_count)
            score = (1 - diversity_weight) * relevance + diversity_weight * diversity_bonus

            if score > best_score:
                best_score = score
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected
