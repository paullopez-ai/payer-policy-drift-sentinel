# Model Economics

## Model Deployment

The evidence generation model is controlled by `AZURE_OPENAI_DEPLOYMENT`. Recommended: `gpt-4o` or `gpt-4.1` where available in your Azure region.

## Token Budget

| Parameter | Default | Environment Variable |
|-----------|---------|---------------------|
| Max prompt tokens | 12,000 | `MAX_PROMPT_TOKENS` |
| Max completion tokens | 1,800 | `MAX_COMPLETION_TOKENS` |

Typical evidence packet generation uses 2,000-3,000 prompt tokens and 300-500 completion tokens.

## Cost Per Evidence Packet

| Component | Estimated Cost | Notes |
|-----------|---------------|-------|
| Azure OpenAI (prompt) | ~$0.012 | At $0.005/1K tokens, 2,400 tokens |
| Azure OpenAI (completion) | ~$0.006 | At $0.015/1K tokens, 380 tokens |
| Snowflake queries (3) | ~$0.06 | Proxy estimate per query |
| Databricks job (1) | ~$0.10 | Proxy estimate per job trigger |
| **Total per packet** | **~$0.18** | |

## Platform Cost Proxies

| Platform | Proxy Rate | Notes |
|----------|-----------|-------|
| Snowflake query | $0.02/query | Based on X-Small warehouse with auto-suspend |
| Databricks job | $0.10/job | Based on single-node Standard_DS3_v2 cluster |

## Estimated Value

| Metric | Estimate | Notes |
|--------|----------|-------|
| Reviewer time avoided per finding | 2-4 hours | Structured evidence vs. manual analysis |
| Administrative cost per appeal | $200-$2,500 | Synthetic estimate |
| Exposure per drift event | $10,000-$500,000 | Depends on procedure volume and denial rate |

## Max Run Cost Guardrail

| Parameter | Default | Environment Variable |
|-----------|---------|---------------------|
| Max run cost | $5.00 | `MAX_RUN_COST_USD` |

The quality gate blocks any run whose estimated cost exceeds this threshold.

## Latency Expectations

| Step | Expected Latency |
|------|-----------------|
| Data readiness check | <1s (mock), 2-5s (live) |
| Drift detection | <1s (mock), 5-30s (live, depends on job) |
| Policy retrieval | <1s (mock), 2-5s (live) |
| Financial impact query | <1s (mock), 2-5s (live) |
| Evidence generation | <1s (mock), 5-15s (live Azure OpenAI) |
| Quality gate | <100ms |
| Human review routing | <100ms |
| **Total** | **<1s (mock), 20-60s (live)** |

## Context Window

The evidence prompt is designed to stay within 8K-12K tokens including finding data, policy passages, and financial impact. This fits within the context window of GPT-4o and comparable models.

## Provider Change Note

Azure OpenAI model availability, pricing, and API versions change. Paul must verify current pricing and model availability in the target Azure region before running a live demo. Update the `AZURE_OPENAI_DEPLOYMENT` and `AZURE_OPENAI_API_VERSION` environment variables as needed.

## Known Limitations

- Cost proxies are synthetic estimates, not metered usage.
- Snowflake and Databricks costs depend on warehouse size, cluster configuration, and query complexity.
- Token counts are based on typical scenario runs; actual counts may vary.
- Azure OpenAI pricing varies by model, region, and agreement.
