# Trust Model

## Trust Boundaries

Every drift finding is classified into one of three trust boundaries:

| Boundary | Definition | Action Allowed |
|----------|-----------|---------------|
| AUTONOMOUS | Low-risk finding with high confidence | System may present without manual review |
| SUPERVISED | Medium-risk or medium-confidence finding | Requires human acknowledgment before action |
| RESTRICTED | High-risk, provider-sensitive, policy-change, or low-confidence finding | Blocks all action until manual review is recorded |

## Classification Rules

| Condition | Trust Boundary |
|-----------|---------------|
| Provider outlier finding | RESTRICTED |
| Policy version drift finding | RESTRICTED |
| Critical severity | RESTRICTED |
| Low confidence (<0.6) | RESTRICTED |
| High severity | SUPERVISED |
| Medium severity | SUPERVISED |
| Low severity with high confidence | AUTONOMOUS |

## Review Routing

| Trust Boundary | Review Status |
|---------------|--------------|
| RESTRICTED | REQUIRED |
| SUPERVISED | REQUIRED |
| AUTONOMOUS | NOT_REQUIRED |

## Audit Trail

Every evidence packet includes:
- `input_hash`: SHA-256 of the structured input context
- `model_provider`: Which LLM provider generated the explanation
- `model_deployment`: Specific model deployment name
- `prompt_tokens` / `completion_tokens`: Token counts
- `estimated_llm_cost_usd` / `estimated_platform_cost_usd`: Cost estimates
- `confidence`: Model-reported confidence
- `citation_count`: Number of policy citations
- `trust_boundary`: Classification
- `review_status`: Current review state
- `created_at`: Timestamp

## Design Rationale

A payer AI system should not automatically act on drift patterns that could affect provider relationships, member experience, or compliance posture. The trust model ensures that:

1. Provider-level findings always require human review because provider relationship decisions have business and compliance consequences.
2. Policy version drift always requires review because policy changes may be intentional.
3. Low-confidence findings are blocked to prevent false-positive noise.
4. The audit trail provides reproducibility for compliance and operational review.
