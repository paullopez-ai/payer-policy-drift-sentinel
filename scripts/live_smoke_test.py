"""End-to-end live smoke test against the deployed API.

This is a Manual Execution Gate script. Do not run autonomously.

Usage:
    uv run python scripts/live_smoke_test.py \\
        --api-url "$DRIFT_SENTINEL_API_URL" \\
        --scenario-id denial-spike-imaging
"""

from __future__ import annotations

import argparse
import json
import sys

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Live API smoke test")
    parser.add_argument("--api-url", required=True, help="Base URL of the deployed API")
    parser.add_argument("--scenario-id", default="denial-spike-imaging")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base_url = args.api_url.rstrip("/")
    print(f"API URL: {base_url}")
    print(f"Scenario: {args.scenario_id}")

    if args.dry_run:
        print("DRY RUN - no API calls will be made")
        return

    client = httpx.Client(timeout=60.0)

    # Step 1: Health check
    print("\n1. Health check...")
    r = client.get(f"{base_url}/health")
    r.raise_for_status()
    health = r.json()
    print(f"   Status: {health['status']}")
    print(f"   Mode: {health['mode']}")

    # Step 2: Run scenario
    print(f"\n2. Running scenario {args.scenario_id}...")
    r = client.post(f"{base_url}/runs", json={"scenario_id": args.scenario_id})
    r.raise_for_status()
    result = r.json()

    run_id = result.get("run_id", "unknown")
    print(f"   Run ID: {run_id}")
    print(f"   Quality passed: {result.get('quality_passed')}")
    print(f"   Review status: {result.get('review_status')}")

    # Step 3: Validate evidence packet
    packet = result.get("evidence_packet", {})
    if not packet:
        print("   ERROR: No evidence packet in response")
        sys.exit(1)

    print(f"\n3. Evidence packet:")
    print(f"   Confidence: {packet.get('confidence')}")
    print(f"   Citations: {len(packet.get('citations', []))}")
    print(f"   Trust boundary: {packet.get('trust_boundary')}")
    print(f"   Review status: {packet.get('review_status')}")

    cost = packet.get("cost", {})
    print(f"\n4. Cost:")
    print(f"   Prompt tokens: {cost.get('prompt_tokens')}")
    print(f"   Completion tokens: {cost.get('completion_tokens')}")
    print(f"   LLM cost: ${cost.get('estimated_llm_cost_usd', 0):.4f}")
    print(f"   Platform cost: ${cost.get('estimated_platform_cost_usd', 0):.4f}")
    print(f"   Total cost: ${cost.get('total_estimated_cost_usd', 0):.4f}")

    print(f"\n5. Summary (first 200 chars):")
    print(f"   {packet.get('summary', '')[:200]}")

    # Step 4: Validate review endpoint
    print(f"\n6. Findings list...")
    r = client.get(f"{base_url}/findings")
    r.raise_for_status()
    findings = r.json()
    print(f"   Findings count: {len(findings)}")

    print("\nSmoke test PASSED.")


if __name__ == "__main__":
    main()
