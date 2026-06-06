"""Runs Databricks jobs manually.

This is a Manual Execution Gate script. Do not run autonomously.

Usage:
    uv run python scripts/run_databricks_jobs.py --job drift_feature_pipeline --wait
"""

from __future__ import annotations

import argparse
import os
import sys
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Databricks jobs")
    parser.add_argument("--job", required=True, help="Job name or ID")
    parser.add_argument("--wait", action="store_true", help="Wait for job completion")
    parser.add_argument("--timeout", type=int, default=900, help="Max wait seconds")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    host = os.environ.get("DATABRICKS_HOST", "")
    token = os.environ.get("DATABRICKS_TOKEN", "")
    job_id = os.environ.get("DATABRICKS_DRIFT_JOB_ID", args.job)

    if not host or not token:
        print("ERROR: DATABRICKS_HOST and DATABRICKS_TOKEN environment variables required")
        sys.exit(1)

    print(f"Databricks host: {host}")
    print(f"Job: {job_id}")
    print(f"Wait: {args.wait}")
    print(f"Timeout: {args.timeout}s")

    if args.dry_run:
        print("DRY RUN - no Databricks API calls will be made")
        return

    try:
        from databricks.sdk import WorkspaceClient  # type: ignore

        client = WorkspaceClient(host=host, token=token)

        print(f"Triggering job run for job_id={job_id}...")
        run = client.jobs.run_now(job_id=int(job_id))
        run_id = run.run_id
        print(f"Run started: run_id={run_id}")

        if args.wait:
            print("Waiting for completion...")
            start = time.time()
            while time.time() - start < args.timeout:
                run_state = client.jobs.get_run(run_id=run_id)
                state = run_state.state
                if state and state.life_cycle_state:
                    lcs = state.life_cycle_state.value
                    print(f"  State: {lcs}")
                    if lcs in ("TERMINATED", "SKIPPED", "INTERNAL_ERROR"):
                        result = state.result_state.value if state.result_state else "UNKNOWN"
                        print(f"  Result: {result}")
                        if result != "SUCCESS":
                            print("ERROR: Job did not succeed")
                            sys.exit(1)
                        break
                time.sleep(15)
            else:
                print(f"ERROR: Timeout after {args.timeout}s")
                sys.exit(1)

        print("Job run complete.")

    except ImportError:
        print("ERROR: databricks-sdk not installed")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
