from __future__ import annotations

import json
from typing import Any

from src.prompts.schemas import EVIDENCE_PACKET_JSON_SCHEMA


def build_evidence_prompt(context: dict[str, Any]) -> str:
    """Build the structured prompt for evidence packet generation."""
    finding = context["finding"]
    passages = context["policy_passages"]
    impact = context["financial_impact"]

    passages_text = "\n\n".join(
        f"[{p['citation_id']}] (Policy: {p['policy_version_id']}, Relevance: {p['relevance_score']:.2f})\n{p['passage']}"
        for p in passages
    )

    schema_text = json.dumps(EVIDENCE_PACKET_JSON_SCHEMA, indent=2)

    return f"""You are a payer policy drift analyst. Analyze the following drift finding and produce a structured evidence packet.

## Finding
- Type: {finding['finding_type']}
- Procedure Group: {finding['procedure_group']}
- Provider: {finding.get('provider_id', 'N/A')}
- Baseline Rate: {finding['baseline_rate']:.2%}
- Observed Rate: {finding['observed_rate']:.2%}
- Delta: {finding['delta']:.2%}
- Severity: {finding['severity']}
- Confidence: {finding['confidence']:.2f}
- Policy Version: {finding['policy_version_id']}

## Policy Context
{passages_text}

## Financial Impact
- Denied Dollars: ${impact.get('denied_dollars', 0):,.2f}
- Appeal Reversal Dollars: ${impact.get('appeal_reversal_dollars', 0):,.2f}
- Administrative Cost Estimate: ${impact.get('admin_cost_estimate', 0):,.2f}
- Claim Volume: {impact.get('claim_volume', 0)}
- Exposure Estimate: ${impact.get('exposure_estimate', 0):,.2f}

## Instructions
1. Summarize the drift finding in 2-3 sentences, referencing specific citation IDs.
2. Provide a root cause hypothesis that connects policy changes to observed metrics.
3. Recommend a review path (e.g., clinical policy review, provider outreach, appeals audit).
4. List the citation IDs you used.
5. State your confidence (0.0-1.0) in the analysis.
6. List any limitations of your analysis.

## Output Format
Respond ONLY with valid JSON matching this schema:
{schema_text}
"""
