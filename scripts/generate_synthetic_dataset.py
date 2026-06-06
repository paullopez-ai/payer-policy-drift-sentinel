"""Generates deterministic synthetic fixtures for the test track.

Usage:
    uv run python scripts/generate_synthetic_dataset.py --seed 42 --out data/test-fixtures
"""

from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

SCENARIOS = [
    "denial-spike-imaging",
    "appeal-reversal-leakage",
    "provider-outlier-friction",
    "policy-version-regression",
]

PROCEDURE_GROUPS = [
    "advanced_imaging",
    "outpatient_surgery",
    "physical_therapy",
    "cardiac_procedures",
    "oncology",
]

DENIAL_REASON_GROUPS = [
    "clinical_criteria",
    "missing_information",
    "site_of_care",
    "duplicate",
    "eligibility",
    "coding",
]

PROVIDER_TYPES = ["hospital", "imaging_center", "physician_group", "ambulatory_surgery"]
MARKETS = ["northeast", "southeast", "midwest", "west"]


def _uuid() -> str:
    return str(uuid.uuid4())[:12]


def generate_providers(rng: random.Random, count: int = 20) -> list[dict]:
    providers = []
    for i in range(count):
        providers.append({
            "provider_id": f"PRV-{_uuid()}",
            "provider_type": rng.choice(PROVIDER_TYPES),
            "market": rng.choice(MARKETS),
            "contract_cohort": f"cohort-{rng.randint(1, 5)}",
            "volume_group": rng.choice(["low", "medium", "high"]),
            "scenario_id": SCENARIOS[i % len(SCENARIOS)],
        })
    # Add the specific outlier provider for scenario 3
    providers.append({
        "provider_id": "PRV-IMG-HIGHVOL",
        "provider_type": "imaging_center",
        "market": "northeast",
        "contract_cohort": "cohort-1",
        "volume_group": "high",
        "scenario_id": "provider-outlier-friction",
    })
    return providers


def generate_policy_versions(rng: random.Random) -> list[dict]:
    policies = []
    for pg in ["advanced_imaging", "outpatient_surgery"]:
        # Old version
        policies.append({
            "policy_version_id": f"PV-2024-{pg[:3].upper()}-001",
            "policy_name": f"Synthetic {pg.replace('_', ' ').title()} Policy v1",
            "procedure_group": pg,
            "effective_date": "2024-01-01",
            "retired_date": "2024-06-30",
            "policy_text": f"Synthetic policy for {pg.replace('_', ' ')}. Prior authorization required for all {pg.replace('_', ' ')} services. Clinical criteria: documented medical necessity with supporting clinical notes. Broad approval criteria with standard documentation requirements.",
            "source_type": "SYNTHETIC",
            "content_hash": f"hash-{pg}-v1",
        })
        # New version with tighter criteria
        policies.append({
            "policy_version_id": f"PV-2024-{pg[:3].upper()}-002",
            "policy_name": f"Synthetic {pg.replace('_', ' ').title()} Policy v2",
            "procedure_group": pg,
            "effective_date": "2024-07-01",
            "retired_date": None,
            "policy_text": f"Synthetic policy for {pg.replace('_', ' ')} (updated). Prior authorization required. Clinical criteria: documented medical necessity with peer-reviewed evidence, failed conservative treatment documentation, and site-of-care justification. Narrower approval criteria requiring additional clinical documentation.",
            "source_type": "SYNTHETIC",
            "content_hash": f"hash-{pg}-v2",
        })
    # Site of care policy
    policies.append({
        "policy_version_id": "PV-2024-SOC-001",
        "policy_name": "Synthetic Site of Care Policy",
        "procedure_group": "outpatient_surgery",
        "effective_date": "2024-01-01",
        "retired_date": None,
        "policy_text": "Synthetic site of care policy. Outpatient procedures should be performed in the lowest-cost appropriate setting. Hospital outpatient departments require site-of-care justification when ambulatory surgery center alternatives exist.",
        "source_type": "SYNTHETIC",
        "content_hash": "hash-soc-v1",
    })
    return policies


def generate_claim_lines(
    rng: random.Random, providers: list[dict], count: int = 200
) -> list[dict]:
    claims = []
    base_date = date(2024, 1, 1)
    for i in range(count):
        provider = rng.choice(providers)
        pg = rng.choice(PROCEDURE_GROUPS)
        service_date = base_date + timedelta(days=rng.randint(0, 365))
        billed = round(rng.uniform(500, 15000), 2)
        status = rng.choice(["PAID", "DENIED", "PENDED"])
        allowed = billed * rng.uniform(0.4, 0.9) if status == "PAID" else 0
        paid = allowed * rng.uniform(0.8, 1.0) if status == "PAID" else 0
        pv = "PV-2024-IMG-001" if service_date < date(2024, 7, 1) else "PV-2024-IMG-002"
        claims.append({
            "claim_id": f"CLM-{_uuid()}",
            "line_id": f"LN-{_uuid()}",
            "member_token": f"MBR-{_uuid()}",
            "provider_id": provider["provider_id"],
            "service_date": service_date.isoformat(),
            "received_date": (service_date + timedelta(days=rng.randint(1, 14))).isoformat(),
            "procedure_group": pg,
            "procedure_code": f"SYN-{rng.randint(10000, 99999)}",
            "billed_amount": billed,
            "allowed_amount": round(allowed, 2),
            "paid_amount": round(paid, 2),
            "policy_version_id": pv,
            "claim_status": status,
            "scenario_id": provider["scenario_id"],
        })
    return claims


def generate_authorizations(
    rng: random.Random, providers: list[dict], count: int = 150
) -> list[dict]:
    auths = []
    base_date = date(2024, 1, 1)
    for i in range(count):
        provider = rng.choice(providers)
        pg = rng.choice(PROCEDURE_GROUPS)
        req_date = base_date + timedelta(days=rng.randint(0, 365))
        decision = rng.choice(["APPROVED", "DENIED", "PENDED"])
        auths.append({
            "auth_id": f"AUTH-{_uuid()}",
            "member_token": f"MBR-{_uuid()}",
            "provider_id": provider["provider_id"],
            "request_date": req_date.isoformat(),
            "decision_date": (req_date + timedelta(days=rng.randint(1, 7))).isoformat(),
            "procedure_group": pg,
            "decision": decision,
            "denial_reason_group": rng.choice(DENIAL_REASON_GROUPS) if decision == "DENIED" else None,
            "policy_version_id": "PV-2024-IMG-001" if req_date < date(2024, 7, 1) else "PV-2024-IMG-002",
            "turnaround_hours": rng.randint(2, 168),
            "expedited_flag": rng.random() < 0.1,
            "scenario_id": provider["scenario_id"],
        })
    return auths


def generate_denial_events(
    rng: random.Random, providers: list[dict], count: int = 100
) -> list[dict]:
    denials = []
    base_date = date(2024, 1, 1)
    for i in range(count):
        provider = rng.choice(providers)
        pg = rng.choice(PROCEDURE_GROUPS)
        denial_date = base_date + timedelta(days=rng.randint(0, 365))
        denials.append({
            "denial_id": f"DEN-{_uuid()}",
            "claim_id": f"CLM-{_uuid()}",
            "auth_id": f"AUTH-{_uuid()}" if rng.random() > 0.3 else None,
            "provider_id": provider["provider_id"],
            "denial_date": denial_date.isoformat(),
            "procedure_group": pg,
            "denial_reason_group": rng.choice(DENIAL_REASON_GROUPS),
            "denied_amount": round(rng.uniform(500, 25000), 2),
            "policy_version_id": "PV-2024-IMG-001" if denial_date < date(2024, 7, 1) else "PV-2024-IMG-002",
            "reviewer_type": rng.choice(["AUTO_RULE", "NURSE_REVIEW", "PHYSICIAN_REVIEW"]),
            "scenario_id": provider["scenario_id"],
        })
    return denials


def generate_appeals(rng: random.Random, denials: list[dict], rate: float = 0.3) -> list[dict]:
    appeals = []
    for denial in denials:
        if rng.random() > rate:
            continue
        denial_date = date.fromisoformat(denial["denial_date"])
        appeals.append({
            "appeal_id": f"APP-{_uuid()}",
            "denial_id": denial["denial_id"],
            "appeal_date": (denial_date + timedelta(days=rng.randint(7, 60))).isoformat(),
            "appeal_outcome": rng.choice(["UPHELD", "OVERTURNED", "PARTIAL"]),
            "reversal_reason": rng.choice([
                "insufficient_evidence",
                "policy_mismatch",
                "missing_documentation",
                "reviewer_error",
            ]),
            "days_to_resolution": rng.randint(14, 90),
            "admin_cost_estimate": round(rng.uniform(200, 2500), 2),
            "scenario_id": denial["scenario_id"],
        })
    return appeals


def generate_mock_databricks_outputs() -> list[dict]:
    return [
        {
            "finding_id": "FND-denial-spike-001",
            "scenario_id": "denial-spike-imaging",
            "finding_type": "DENIAL_SPIKE",
            "detection_date": "2024-09-15",
            "procedure_group": "advanced_imaging",
            "provider_id": None,
            "baseline_rate": 0.08,
            "observed_rate": 0.23,
            "delta": 0.15,
            "severity": "HIGH",
            "confidence": 0.87,
            "policy_version_id": "PV-2024-IMG-002",
            "status": "NEW",
        },
        {
            "finding_id": "FND-appeal-rev-001",
            "scenario_id": "appeal-reversal-leakage",
            "finding_type": "APPEAL_REVERSAL_SPIKE",
            "detection_date": "2024-09-15",
            "procedure_group": "outpatient_surgery",
            "provider_id": None,
            "baseline_rate": 0.12,
            "observed_rate": 0.31,
            "delta": 0.19,
            "severity": "HIGH",
            "confidence": 0.78,
            "policy_version_id": "PV-2024-SOC-001",
            "status": "NEW",
        },
        {
            "finding_id": "FND-provider-001",
            "scenario_id": "provider-outlier-friction",
            "finding_type": "PROVIDER_OUTLIER",
            "detection_date": "2024-09-15",
            "procedure_group": "advanced_imaging",
            "provider_id": "PRV-IMG-HIGHVOL",
            "baseline_rate": 0.10,
            "observed_rate": 0.23,
            "delta": 0.13,
            "severity": "MEDIUM",
            "confidence": 0.72,
            "policy_version_id": "PV-2024-IMG-002",
            "status": "NEW",
        },
        {
            "finding_id": "FND-policy-reg-001",
            "scenario_id": "policy-version-regression",
            "finding_type": "POLICY_VERSION_DRIFT",
            "detection_date": "2024-09-15",
            "procedure_group": "advanced_imaging",
            "provider_id": None,
            "baseline_rate": 0.08,
            "observed_rate": 0.23,
            "delta": 0.15,
            "severity": "HIGH",
            "confidence": 0.81,
            "policy_version_id": "PV-2024-IMG-002",
            "status": "NEW",
        },
    ]


def generate_mock_policy_retrieval() -> list[dict]:
    return [
        {
            "policy_version_id": "PV-2024-IMG-002",
            "procedure_group": "advanced_imaging",
            "passage": "Prior authorization required for all advanced imaging services including MRI, CT, and PET scans. Clinical criteria: documented medical necessity with peer-reviewed evidence, failed conservative treatment documentation, and site-of-care justification. Narrower approval criteria requiring additional clinical documentation compared to previous policy version.",
            "relevance_score": 0.92,
        },
        {
            "policy_version_id": "PV-2024-IMG-001",
            "procedure_group": "advanced_imaging",
            "passage": "Prior authorization required for advanced imaging services. Clinical criteria: documented medical necessity with supporting clinical notes. Broad approval criteria with standard documentation requirements.",
            "relevance_score": 0.85,
        },
        {
            "policy_version_id": "PV-2024-SOC-001",
            "procedure_group": "outpatient_surgery",
            "passage": "Outpatient procedures should be performed in the lowest-cost appropriate setting. Hospital outpatient departments require site-of-care justification when ambulatory surgery center alternatives exist.",
            "relevance_score": 0.78,
        },
        {
            "policy_version_id": "PV-2024-OUT-002",
            "procedure_group": "outpatient_surgery",
            "passage": "Updated outpatient surgery authorization criteria require site-of-care review for all procedures with ambulatory alternatives. Documentation must include clinical justification for hospital-based setting.",
            "relevance_score": 0.74,
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic test fixtures")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="data/test-fixtures")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    providers = generate_providers(rng)
    policies = generate_policy_versions(rng)
    claims = generate_claim_lines(rng, providers)
    auths = generate_authorizations(rng, providers)
    denials = generate_denial_events(rng, providers)
    appeals = generate_appeals(rng, denials)
    dbx_outputs = generate_mock_databricks_outputs()
    retrieval = generate_mock_policy_retrieval()

    files = {
        "synthetic_providers.json": providers,
        "synthetic_policy_versions.json": policies,
        "synthetic_claim_lines.json": claims,
        "synthetic_authorizations.json": auths,
        "synthetic_denial_events.json": denials,
        "synthetic_appeals.json": appeals,
        "mock_databricks_outputs.json": dbx_outputs,
        "mock_policy_retrieval_results.json": retrieval,
    }

    for filename, data in files.items():
        path = out_dir / filename
        path.write_text(json.dumps(data, indent=2, default=str))
        print(f"  {filename}: {len(data)} records")

    print(f"\nAll fixtures written to {out_dir}")


if __name__ == "__main__":
    main()
