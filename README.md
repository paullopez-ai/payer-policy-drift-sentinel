# Payer Policy Drift Sentinel

A payer AI reference architecture that detects claim, prior authorization, denial, appeal, and policy drift using Snowflake, Azure Databricks, Azure OpenAI, and Azure-hosted orchestration.

Payer operations teams often discover policy drift only after it becomes provider abrasion, appeal backlog, compliance concern, or avoidable administrative cost. This prototype shows how a payer can combine governed Snowflake data, Databricks analytics, and Azure OpenAI evidence generation into a supervised workflow. The system detects drift, retrieves policy context, estimates exposure, creates a cited evidence packet, and routes high-risk findings to human review.

**Test Track:** Runs locally with zero cloud calls using mocked clients (`MOCK_LLM=true`)
**Live Demo Track:** Real Snowflake + Azure Databricks + Azure OpenAI + Azure Container Apps
**Hyperscaler Track:** Azure
**Related Repos:** `payer-auth-intelligence`, `clinical-rules-mcp-server`, `auth-a2a-agent-network`, `prior-auth-radar`

## Architecture

```text
                                              +------------------------------------+
                                              | Next.js UI Companion                |
                                              | payer-policy-drift-sentinel-ui      |
                                              | Local: localhost:3000               |
                                              | Live: optional Azure Static Web Apps|
                                              +----------------+-------------------+
                                                               | REST / SSE
                                                               v
+----------------------------------------------------------------------------------------------+
| Azure Container Apps: FastAPI Orchestration API                                                |
| Service: drift-sentinel-api                                                                    |
| Port: 8000                                                                                     |
| Runtime: Python 3.12, uv, FastAPI, LangGraph, Pydantic                                         |
| Secrets: Azure Key Vault via managed identity                                                   |
+-----------------------------------+----------------------------------------------------------+
                                    | LangGraph StateGraph
                                    v
+----------------------------------------------------------------------------------------------+
| Agent Workflow                                                                                  |
|                                                                                               |
|  1. DataReadinessNode - validates Snowflake tables, row counts, freshness                      |
|  2. DriftDetectionNode - triggers Databricks job or reads drift output                         |
|  3. PolicyRetrievalNode - retrieves policy passages and citation metadata                      |
|  4. FinancialImpactNode - queries Snowflake for exposure estimates                             |
|  5. EvidencePackNode - calls Azure OpenAI for cited summary                                    |
|  6. QualityGateNode - checks confidence, citations, cost, trust boundary                      |
|  7. HumanReviewNode - blocks restricted findings until manual review                           |
+-------------------+-------------------------+------------------------------------------------+
                    |                         |
                    v                         v
+--------------------------------------+  +---------------------------------------------+
| Snowflake Account                     |  | Azure Databricks Workspace                  |
| Database: PAYER_DRIFT_SENTINEL        |  | Unity Catalog: payer_drift                  |
| Schemas: RAW, MART, POLICY, AUDIT     |  | Jobs: ingest, features, drift, retrieval    |
| Warehouse: PAYER_DRIFT_WH             |  | Feature tables: denial, provider, policy    |
+--------------------------------------+  +---------------------------------------------+
```

<!-- DIAGRAM: insert rendered architecture.mermaid image here -->

Snowflake is the governed synthetic payer data plane. Azure Databricks performs feature engineering, drift scoring, and retrieval preparation. The FastAPI service on Azure Container Apps orchestrates the workflow through LangGraph, calls Azure OpenAI for a cited evidence packet, and writes audit records back to Snowflake. The UI displays findings, citations, confidence, cost, and human review status without directly accessing Snowflake or Databricks.

## Demonstrated Capabilities

### Evaluation and Quality Judgment

> *From the Architect:* In healthcare AI, the hardest part is not getting the model to say something plausible. The hard part is knowing when the answer is good enough to show to an operator. I designed this prototype so every finding is checked against expected scenario behavior, citation coverage, confidence, and review routing before it becomes an evidence packet. The model is not the judge of its own quality. The workflow is.

**Key implementation:** [`src/workflow/nodes/quality_gate.py`](src/workflow/nodes/quality_gate.py) - Blocks unsupported findings before they become review-ready evidence packets.

### Task Decomposition and Multi-Agent Orchestration

> *From the Architect:* I did not want this to be one large agent with a vague instruction to analyze payer data. I split the work into specialized stages because each stage has a different failure mode. Data readiness, drift scoring, policy retrieval, financial impact, explanation, and review routing all need different evidence and different thresholds. That decomposition makes the prototype easier to test, easier to explain, and closer to how enterprise AI systems should be operated.

**Key implementation:** [`src/workflow/graph.py`](src/workflow/graph.py) - Defines the LangGraph workflow and node handoffs.

### Trust and Security Design

> *From the Architect:* A payer AI system should not automatically act on a pattern just because the pattern looks statistically interesting. Provider abrasion, appeal reversals, and policy drift can have compliance and relationship consequences. I designed the trust model so the system can explain, prioritize, and route findings, but it cannot take restricted action by itself. Every high-risk packet carries an audit trail that shows what data was used, which model generated the explanation, what it cost, and who reviewed it.

**Key implementation:** [`src/security/trust_boundaries.py`](src/security/trust_boundaries.py) - Classifies findings and enforces review rules.

### Cost and Token Economics

> *From the Architect:* I wanted the evidence packet to show not only what the AI concluded, but what it cost to reach that conclusion. In real payer environments, model cost is only one part of the economics. Snowflake queries, Databricks jobs, review time, and avoided appeals all matter. This prototype logs cost per run and compares it with estimated administrative exposure so the architecture can be discussed in operational terms, not just AI capability terms.

**Key implementation:** [`src/cost/platform_costs.py`](src/cost/platform_costs.py) - Estimates LLM, Snowflake, Databricks, and administrative cost impact.

## Test Track Setup

```bash
cd ~/MyNewSoftware/payer-policy-drift-sentinel
uv sync

uv run python scripts/generate_synthetic_dataset.py --seed 42 --out data/test-fixtures

MOCK_LLM=true EXTERNAL_CLIENT_MODE=mock uv run pytest

MOCK_LLM=true EXTERNAL_CLIENT_MODE=mock uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Expected:
- API starts at `http://localhost:8000`.
- `GET /health` returns `status=ok`.
- `POST /runs` with `scenario_id=denial-spike-imaging` returns a deterministic evidence packet.
- No Snowflake, Databricks, or Azure service calls are made.

## Live Demo and Hyperscaler Setup

### Azure Region

Set `AZURE_LOCATION` in `infra/terraform/terraform.tfvars` before running plan.
Azure region is a single variable and can be changed before `terraform apply`
if your first choice lacks quota or model availability. Verify your Azure OpenAI
model is available in the chosen region at:
https://learn.microsoft.com/azure/ai-services/openai/concepts/models

Recommended regions with broad model availability: `eastus`, `eastus2`,
`westus`, `swedencentral`.

### Unity Catalog Setup (Azure Portal - manual, before Terraform)

Unity Catalog requires Azure Databricks Premium tier and account-level
enablement. Complete these steps before running `terraform plan`:

1. In the Azure portal, confirm your Azure Databricks workspace is on
   Premium pricing tier (not Standard). If not, upgrade before proceeding.
2. Navigate to accounts.azuredatabricks.net and sign in with your Azure
   account.
3. In the Account console, go to Data and confirm Unity Catalog is enabled
   for your account. If not, enable it.
4. Create a Unity Catalog metastore in the same Azure region as your
   Databricks workspace if one does not already exist.
5. Assign the metastore to your workspace.

Once Unity Catalog is enabled and the metastore is assigned, Terraform
manages all catalog, schema, table, and permission objects under the
`payer_drift` catalog automatically.

### Deploy

```bash
cd infra/terraform

terraform init
terraform fmt -recursive
terraform validate
terraform plan -out tfplan

# Manual gate
terraform apply tfplan
```

Then:

```bash
uv run python scripts/seed_snowflake.py --scenario-set full --seed 42 --warehouse PAYER_DRIFT_WH --database PAYER_DRIFT_SENTINEL

uv run python scripts/run_databricks_jobs.py --job drift_feature_pipeline --wait

uv run python scripts/live_smoke_test.py --api-url "$DRIFT_SENTINEL_API_URL" --scenario-id denial-spike-imaging
```

### Teardown

```bash
cd infra/terraform
terraform destroy
```

**Cost guardrail:**
- Run `terraform destroy` after every live demo.
- Snowflake warehouse must auto-suspend.
- Databricks jobs must not run continuously.
- Keep Azure Container Apps max replicas at 1 for demo.
- Keep `MAX_RUN_COST_USD` low.

## Safety and Data Policy

This repo uses synthetic data only. It does not contain PHI, real patient data, proprietary payer data, real provider contract terms, or real medical policy text. The live demo provisions real Snowflake, Azure Databricks, and Azure resources, but the data loaded into those resources is synthetic. This is a portfolio prototype and is not intended for production use without additional security, privacy, compliance, clinical, legal, and operational review.
