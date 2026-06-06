# Interview Demo Guide

## Five-Minute Walkthrough

### 1. Open the README (30 seconds)

Explain: This is a payer AI reference architecture that detects policy drift using real enterprise platforms - Snowflake for governed data, Azure Databricks for analytics, and Azure OpenAI for supervised explanation.

### 2. Architecture Diagram (60 seconds)

Point out:
- Snowflake as the governed payer data plane
- Azure Databricks for feature engineering and drift scoring
- LangGraph workflow with 7 specialized nodes
- Azure OpenAI for evidence generation (not autonomous decisions)
- Human review as a first-class workflow node
- Test track with fully mocked clients

### 3. Run the Scenario (60 seconds)

Run or show the `denial-spike-imaging` scenario:
- Advanced imaging denials rose from 8% to 23% after a policy version change
- The workflow detects the spike, retrieves policy context, estimates financial exposure, and generates a cited evidence packet

### 4. Evidence Packet (60 seconds)

Show:
- Structured summary with citation IDs
- Root cause hypothesis linking policy change to denial increase
- Recommended review path
- Confidence score (0.85)
- Limitations listed explicitly

### 5. Cost Panel (30 seconds)

Show:
- Prompt tokens: 2,400
- Completion tokens: 380
- Estimated LLM cost: ~$0.018
- Platform cost (Snowflake + Databricks): ~$0.16
- Total: ~$0.18 per evidence packet
- Compare to estimated administrative cost avoided

### 6. Trust and Review (30 seconds)

Show:
- Trust boundary: SUPERVISED (HIGH severity finding)
- Review status: REQUIRED
- The system cannot take action until a human approves or dismisses
- Audit trail records who reviewed and when

### 7. Closing (30 seconds)

Explain:
- The same pattern applies to prior authorization, appeals, provider abrasion, risk adjustment, or payment integrity
- The architecture separates detection from explanation
- Every step is testable, auditable, and cost-tracked
- The test track runs with zero cloud calls for development

## Key Talking Points

- "Detection before explanation" - the model explains structured findings, it doesn't create ungrounded findings
- "Trust boundary design" - provider-sensitive findings are always restricted
- "Cost visibility from day one" - not added as an afterthought
- "Enterprise platform integration" - not a standalone chatbot
