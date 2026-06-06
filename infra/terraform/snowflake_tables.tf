resource "snowflake_table" "claim_lines" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.raw.name
  name     = "CLAIM_LINES"

  column { name = "CLAIM_ID" type = "VARCHAR" }
  column { name = "LINE_ID" type = "VARCHAR" }
  column { name = "MEMBER_TOKEN" type = "VARCHAR" }
  column { name = "PROVIDER_ID" type = "VARCHAR" }
  column { name = "SERVICE_DATE" type = "DATE" }
  column { name = "RECEIVED_DATE" type = "DATE" }
  column { name = "PROCEDURE_GROUP" type = "VARCHAR" }
  column { name = "PROCEDURE_CODE" type = "VARCHAR" }
  column { name = "BILLED_AMOUNT" type = "NUMBER(12,2)" }
  column { name = "ALLOWED_AMOUNT" type = "NUMBER(12,2)" }
  column { name = "PAID_AMOUNT" type = "NUMBER(12,2)" }
  column { name = "POLICY_VERSION_ID" type = "VARCHAR" }
  column { name = "CLAIM_STATUS" type = "VARCHAR" }
}

resource "snowflake_table" "authorizations" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.raw.name
  name     = "AUTHORIZATIONS"

  column { name = "AUTH_ID" type = "VARCHAR" }
  column { name = "MEMBER_TOKEN" type = "VARCHAR" }
  column { name = "PROVIDER_ID" type = "VARCHAR" }
  column { name = "REQUEST_DATE" type = "DATE" }
  column { name = "DECISION_DATE" type = "DATE" }
  column { name = "PROCEDURE_GROUP" type = "VARCHAR" }
  column { name = "DECISION" type = "VARCHAR" }
  column { name = "DENIAL_REASON_GROUP" type = "VARCHAR" }
  column { name = "POLICY_VERSION_ID" type = "VARCHAR" }
  column { name = "TURNAROUND_HOURS" type = "NUMBER" }
  column { name = "EXPEDITED_FLAG" type = "BOOLEAN" }
}

resource "snowflake_table" "denial_events" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.raw.name
  name     = "DENIAL_EVENTS"

  column { name = "DENIAL_ID" type = "VARCHAR" }
  column { name = "CLAIM_ID" type = "VARCHAR" }
  column { name = "AUTH_ID" type = "VARCHAR" }
  column { name = "PROVIDER_ID" type = "VARCHAR" }
  column { name = "DENIAL_DATE" type = "DATE" }
  column { name = "PROCEDURE_GROUP" type = "VARCHAR" }
  column { name = "DENIAL_REASON_GROUP" type = "VARCHAR" }
  column { name = "DENIED_AMOUNT" type = "NUMBER(12,2)" }
  column { name = "POLICY_VERSION_ID" type = "VARCHAR" }
  column { name = "REVIEWER_TYPE" type = "VARCHAR" }
}

resource "snowflake_table" "appeals" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.raw.name
  name     = "APPEALS"

  column { name = "APPEAL_ID" type = "VARCHAR" }
  column { name = "DENIAL_ID" type = "VARCHAR" }
  column { name = "APPEAL_DATE" type = "DATE" }
  column { name = "APPEAL_OUTCOME" type = "VARCHAR" }
  column { name = "REVERSAL_REASON" type = "VARCHAR" }
  column { name = "DAYS_TO_RESOLUTION" type = "NUMBER" }
  column { name = "ADMIN_COST_ESTIMATE" type = "NUMBER(12,2)" }
}

resource "snowflake_table" "provider_dim" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.mart.name
  name     = "PROVIDER_DIM"

  column { name = "PROVIDER_ID" type = "VARCHAR" }
  column { name = "PROVIDER_TYPE" type = "VARCHAR" }
  column { name = "MARKET" type = "VARCHAR" }
  column { name = "CONTRACT_COHORT" type = "VARCHAR" }
  column { name = "VOLUME_GROUP" type = "VARCHAR" }
}

resource "snowflake_table" "drift_findings" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.mart.name
  name     = "DRIFT_FINDINGS"

  column { name = "FINDING_ID" type = "VARCHAR" }
  column { name = "SCENARIO_ID" type = "VARCHAR" }
  column { name = "FINDING_TYPE" type = "VARCHAR" }
  column { name = "DETECTION_DATE" type = "DATE" }
  column { name = "PROCEDURE_GROUP" type = "VARCHAR" }
  column { name = "PROVIDER_ID" type = "VARCHAR" }
  column { name = "BASELINE_RATE" type = "FLOAT" }
  column { name = "OBSERVED_RATE" type = "FLOAT" }
  column { name = "DELTA" type = "FLOAT" }
  column { name = "SEVERITY" type = "VARCHAR" }
  column { name = "CONFIDENCE" type = "FLOAT" }
  column { name = "POLICY_VERSION_ID" type = "VARCHAR" }
  column { name = "STATUS" type = "VARCHAR" }
  column { name = "CREATED_AT" type = "TIMESTAMP_NTZ" }
}

resource "snowflake_table" "policy_version" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.policy.name
  name     = "POLICY_VERSION"

  column { name = "POLICY_VERSION_ID" type = "VARCHAR" }
  column { name = "POLICY_NAME" type = "VARCHAR" }
  column { name = "PROCEDURE_GROUP" type = "VARCHAR" }
  column { name = "EFFECTIVE_DATE" type = "DATE" }
  column { name = "RETIRED_DATE" type = "DATE" }
  column { name = "POLICY_TEXT" type = "VARCHAR" }
  column { name = "SOURCE_TYPE" type = "VARCHAR" }
  column { name = "CONTENT_HASH" type = "VARCHAR" }
  column { name = "CREATED_AT" type = "TIMESTAMP_NTZ" }
}

resource "snowflake_table" "evidence_packet_audit" {
  database = snowflake_database.this.name
  schema   = snowflake_schema.audit.name
  name     = "EVIDENCE_PACKET_AUDIT"

  column { name = "PACKET_ID" type = "VARCHAR" }
  column { name = "FINDING_ID" type = "VARCHAR" }
  column { name = "INPUT_HASH" type = "VARCHAR" }
  column { name = "MODEL_PROVIDER" type = "VARCHAR" }
  column { name = "MODEL_DEPLOYMENT" type = "VARCHAR" }
  column { name = "PROMPT_TOKENS" type = "NUMBER" }
  column { name = "COMPLETION_TOKENS" type = "NUMBER" }
  column { name = "ESTIMATED_LLM_COST_USD" type = "NUMBER(12,6)" }
  column { name = "ESTIMATED_PLATFORM_COST_USD" type = "NUMBER(12,6)" }
  column { name = "CONFIDENCE" type = "FLOAT" }
  column { name = "CITATION_COUNT" type = "NUMBER" }
  column { name = "TRUST_BOUNDARY" type = "VARCHAR" }
  column { name = "REVIEW_STATUS" type = "VARCHAR" }
  column { name = "CREATED_AT" type = "TIMESTAMP_NTZ" }
}
