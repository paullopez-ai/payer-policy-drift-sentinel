# Live Demo Runbook

## Before Demo

1. Confirm Azure subscription and region
2. Confirm Snowflake account access
3. Confirm Databricks entitlement (Premium tier required)
4. Confirm Azure OpenAI access and model deployment availability
5. Confirm local `.env` and Terraform variables are not committed

## Deploy

```bash
cd infra/terraform

terraform init
terraform fmt -recursive
terraform validate
terraform plan -out tfplan

# MANUAL GATE - review plan before applying
terraform apply tfplan
```

## Seed Data

```bash
uv run python scripts/seed_snowflake.py \
  --scenario-set full --seed 42 \
  --warehouse PAYER_DRIFT_WH \
  --database PAYER_DRIFT_SENTINEL
```

## Run Databricks Pipeline

```bash
uv run python scripts/run_databricks_jobs.py \
  --job drift_feature_pipeline --wait
```

## Smoke Test

```bash
uv run python scripts/live_smoke_test.py \
  --api-url "$DRIFT_SENTINEL_API_URL" \
  --scenario-id denial-spike-imaging
```

## After Demo

```bash
cd infra/terraform
terraform destroy
```

Verify:
- [ ] Snowflake warehouse is suspended
- [ ] Databricks jobs are not running
- [ ] Container Apps resources are deleted
- [ ] No unexpected Azure resources remain

## Cost Warning

Run `terraform destroy` after every live demo session. Leaving resources running will incur costs for:
- Azure Databricks workspace (Premium tier)
- Azure Container Apps
- Azure OpenAI deployment
- Snowflake warehouse (if not auto-suspended)
- Azure Storage Account
