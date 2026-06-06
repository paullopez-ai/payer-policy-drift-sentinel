from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.clients.azure_openai_client import AzureOpenAIClientBase
from src.clients.databricks_client import DatabricksClientBase
from src.clients.snowflake_client import SnowflakeClientBase

logger = logging.getLogger(__name__)

FIXTURES_DIR = Path(__file__).parent.parent.parent / "data" / "test-fixtures"


def _load_fixture(name: str) -> list[dict[str, Any]]:
    path = FIXTURES_DIR / name
    if not path.exists():
        logger.warning("Fixture not found: %s", path)
        return []
    return json.loads(path.read_text())


class MockSnowflakeClient(SnowflakeClientBase):
    """Returns deterministic rows from local fixtures."""

    def __init__(self) -> None:
        self._claims = _load_fixture("synthetic_claim_lines.json")
        self._auths = _load_fixture("synthetic_authorizations.json")
        self._denials = _load_fixture("synthetic_denial_events.json")
        self._appeals = _load_fixture("synthetic_appeals.json")
        self._providers = _load_fixture("synthetic_providers.json")
        self._policies = _load_fixture("synthetic_policy_versions.json")
        self._tables: dict[str, list[dict[str, Any]]] = {
            "RAW.CLAIM_LINES": self._claims,
            "RAW.AUTHORIZATIONS": self._auths,
            "RAW.DENIAL_EVENTS": self._denials,
            "RAW.APPEALS": self._appeals,
            "MART.PROVIDER_DIM": self._providers,
            "POLICY.POLICY_VERSION": self._policies,
        }

    async def query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        sql_upper = sql.upper()
        for table_name, data in self._tables.items():
            if table_name in sql_upper:
                if params and "scenario_id" in params:
                    return [
                        r for r in data if r.get("scenario_id") == params["scenario_id"]
                    ]
                return data
        return []

    async def write_rows(self, table: str, rows: list[dict[str, Any]]) -> int:
        key = table.upper()
        if key not in self._tables:
            self._tables[key] = []
        self._tables[key].extend(rows)
        return len(rows)

    async def check_table_exists(self, schema: str, table: str) -> bool:
        key = f"{schema.upper()}.{table.upper()}"
        return key in self._tables

    async def get_row_count(self, schema: str, table: str) -> int:
        key = f"{schema.upper()}.{table.upper()}"
        return len(self._tables.get(key, []))


class MockDatabricksClient(DatabricksClientBase):
    """Returns deterministic drift scores from local fixtures."""

    def __init__(self) -> None:
        self._outputs = _load_fixture("mock_databricks_outputs.json")
        self._retrieval = _load_fixture("mock_policy_retrieval_results.json")

    async def run_job(self, job_id: str, wait: bool = True) -> dict[str, Any]:
        return {"status": "COMPLETED", "job_id": job_id}

    async def query_sql(self, sql: str) -> list[dict[str, Any]]:
        return self._outputs

    async def get_drift_findings(self, scenario_id: str) -> list[dict[str, Any]]:
        return [f for f in self._outputs if f.get("scenario_id") == scenario_id]

    async def get_policy_retrieval(self, procedure_group: str) -> list[dict[str, Any]]:
        return [
            r for r in self._retrieval
            if r.get("procedure_group") == procedure_group
        ]


MOCK_EVIDENCE_RESPONSES: dict[str, dict[str, Any]] = {
    "denial-spike-imaging": {
        "content": json.dumps({
            "summary": "Advanced imaging denials increased from 8% to 23% following policy version PV-2024-IMG-002 effective 2024-07-01. The spike correlates with tighter clinical criteria for outpatient MRI and CT authorization [CIT-PV-2024-IMG-002-a1b2c3d4e5f6]. Prior policy version PV-2024-IMG-001 used broader approval criteria [CIT-PV-2024-IMG-001-f6e5d4c3b2a1].",
            "root_cause_hypothesis": "Policy version PV-2024-IMG-002 introduced narrower clinical necessity criteria for advanced imaging without corresponding provider notification or prior authorization workflow updates. The delta suggests the policy change was operationally significant and not accompanied by adequate provider education.",
            "recommended_review_path": "Clinical policy review of PV-2024-IMG-002 criteria against peer benchmarks, followed by provider communication assessment and appeals trend analysis for the imaging procedure group.",
            "citations_used": [
                "CIT-PV-2024-IMG-002-a1b2c3d4e5f6",
                "CIT-PV-2024-IMG-001-f6e5d4c3b2a1",
            ],
            "confidence": 0.85,
            "limitations": [
                "Synthetic data only; real payer volumes may differ.",
                "Root cause hypothesis is based on temporal correlation, not confirmed causation.",
                "Provider notification history is not available in the synthetic dataset.",
            ],
        }),
        "prompt_tokens": 2400,
        "completion_tokens": 380,
        "model_deployment": "mock-gpt-4o",
    },
    "appeal-reversal-leakage": {
        "content": json.dumps({
            "summary": "Appeal reversals for site-of-care denials increased from 12% to 31%, suggesting original denial logic may be overly aggressive. The reversal pattern is concentrated in outpatient surgical denials [CIT-PV-2024-SOC-001-abc123def456].",
            "root_cause_hypothesis": "Site-of-care denial criteria may not adequately account for clinical scenarios where outpatient settings are medically appropriate. The high reversal rate indicates reviewers consistently find the original denials unsupported.",
            "recommended_review_path": "Appeals audit for site-of-care denial reason group, focused on reversed decisions and reviewer notes. Cross-reference with clinical criteria version.",
            "citations_used": ["CIT-PV-2024-SOC-001-abc123def456"],
            "confidence": 0.78,
            "limitations": [
                "Synthetic data only.",
                "Reversal reasons may not capture full clinical context.",
            ],
        }),
        "prompt_tokens": 2100,
        "completion_tokens": 320,
        "model_deployment": "mock-gpt-4o",
    },
    "provider-outlier-friction": {
        "content": json.dumps({
            "summary": "Provider cohort PRV-IMG-HIGHVOL shows denial rates 2.3x peer average and appeal rates 3.1x peer average for advanced imaging [CIT-PV-2024-IMG-002-a1b2c3d4e5f6]. This pattern suggests potential provider friction requiring relationship management review.",
            "root_cause_hypothesis": "High-volume imaging provider may have different clinical patterns or documentation practices compared to peers. The combination of elevated denials and appeals suggests systemic friction rather than isolated cases.",
            "recommended_review_path": "Provider relationship review with network management. Compare provider documentation quality and clinical patterns against peer cohort before any contract or policy action.",
            "citations_used": ["CIT-PV-2024-IMG-002-a1b2c3d4e5f6"],
            "confidence": 0.72,
            "limitations": [
                "Synthetic data only.",
                "Provider-level analysis is sensitive and requires human review.",
                "Peer comparison uses synthetic cohort averages.",
            ],
        }),
        "prompt_tokens": 2300,
        "completion_tokens": 350,
        "model_deployment": "mock-gpt-4o",
    },
    "policy-version-regression": {
        "content": json.dumps({
            "summary": "Policy version PV-2024-IMG-002 correlates with a 15-point increase in denial rate and a 19-point increase in appeal reversal rate compared to PV-2024-IMG-001 [CIT-PV-2024-IMG-002-a1b2c3d4e5f6] [CIT-PV-2024-IMG-001-f6e5d4c3b2a1]. The version change appears to have introduced unintended operational consequences.",
            "root_cause_hypothesis": "The policy version update tightened criteria without corresponding changes to auto-adjudication rules, creating a gap between policy intent and operational execution.",
            "recommended_review_path": "Version-aware policy diff review comparing PV-2024-IMG-001 and PV-2024-IMG-002 criteria. Assess whether auto-adjudication rules were updated to match the new policy.",
            "citations_used": [
                "CIT-PV-2024-IMG-002-a1b2c3d4e5f6",
                "CIT-PV-2024-IMG-001-f6e5d4c3b2a1",
            ],
            "confidence": 0.81,
            "limitations": [
                "Synthetic data only.",
                "Policy diff analysis is based on synthetic policy text.",
            ],
        }),
        "prompt_tokens": 2500,
        "completion_tokens": 360,
        "model_deployment": "mock-gpt-4o",
    },
}


class MockAzureOpenAIClient(AzureOpenAIClientBase):
    """Returns deterministic evidence packets keyed by scenario_id."""

    def __init__(self, scenario_id: str = "denial-spike-imaging") -> None:
        self._scenario_id = scenario_id

    async def generate_evidence(
        self, prompt: str, max_tokens: int = 1800
    ) -> dict[str, Any]:
        response = MOCK_EVIDENCE_RESPONSES.get(
            self._scenario_id,
            MOCK_EVIDENCE_RESPONSES["denial-spike-imaging"],
        )
        return response
