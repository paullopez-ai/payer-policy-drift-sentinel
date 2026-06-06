"""Loads synthetic data into Snowflake tables.

This is a Manual Execution Gate script. Do not run autonomously.

Usage:
    uv run python scripts/seed_snowflake.py \\
        --scenario-set full --seed 42 \\
        --warehouse PAYER_DRIFT_WH \\
        --database PAYER_DRIFT_SENTINEL
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Snowflake with synthetic data")
    parser.add_argument("--scenario-set", default="full", choices=["full", "minimal"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--warehouse", default="PAYER_DRIFT_WH")
    parser.add_argument("--database", default="PAYER_DRIFT_SENTINEL")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    fixtures_dir = Path("data/test-fixtures")
    if not fixtures_dir.exists():
        print("ERROR: Test fixtures not found. Run generate_synthetic_dataset.py first.")
        return

    table_map = {
        "synthetic_claim_lines.json": ("RAW", "CLAIM_LINES"),
        "synthetic_authorizations.json": ("RAW", "AUTHORIZATIONS"),
        "synthetic_denial_events.json": ("RAW", "DENIAL_EVENTS"),
        "synthetic_appeals.json": ("RAW", "APPEALS"),
        "synthetic_providers.json": ("MART", "PROVIDER_DIM"),
        "synthetic_policy_versions.json": ("POLICY", "POLICY_VERSION"),
    }

    print(f"Database: {args.database}")
    print(f"Warehouse: {args.warehouse}")
    print(f"Scenario set: {args.scenario_set}")
    print()

    if args.dry_run:
        print("DRY RUN - no Snowflake connection will be made")
        print()

    for filename, (schema, table) in table_map.items():
        path = fixtures_dir / filename
        if not path.exists():
            print(f"  SKIP {schema}.{table} - fixture not found")
            continue

        data = json.loads(path.read_text())
        print(f"  {schema}.{table}: {len(data)} rows")

        if not args.dry_run:
            _load_to_snowflake(args, schema, table, data)

    print()
    print("Seeding complete." if not args.dry_run else "Dry run complete.")


def _load_to_snowflake(args: argparse.Namespace, schema: str, table: str, data: list) -> None:
    """Load data to Snowflake using the Python connector."""
    try:
        import snowflake.connector  # type: ignore

        account = os.environ.get("SNOWFLAKE_ACCOUNT", "")
        user = os.environ.get("SNOWFLAKE_USER", "")
        role = os.environ.get("SNOWFLAKE_ROLE", "PAYER_DRIFT_APP_ROLE")

        if not account or not user:
            print(f"    ERROR: SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER required")
            return

        conn = snowflake.connector.connect(
            account=account,
            user=user,
            role=role,
            warehouse=args.warehouse,
            database=args.database,
        )

        cursor = conn.cursor()
        cursor.execute(f"USE SCHEMA {schema}")

        # Truncate then insert
        cursor.execute(f"TRUNCATE TABLE IF EXISTS {table}")

        if data:
            columns = list(data[0].keys())
            placeholders = ", ".join(["%s"] * len(columns))
            col_names = ", ".join(columns)
            sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

            rows = [tuple(row.get(c) for c in columns) for row in data]
            cursor.executemany(sql, rows)

        cursor.close()
        conn.close()
        print(f"    Loaded {len(data)} rows to {schema}.{table}")

    except ImportError:
        print(f"    ERROR: snowflake-connector-python not installed")
    except Exception as e:
        print(f"    ERROR: {e}")


if __name__ == "__main__":
    main()
