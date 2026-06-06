resource "snowflake_database" "this" {
  name    = "PAYER_DRIFT_SENTINEL"
  comment = "Payer Policy Drift Sentinel - synthetic demo data"
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.this.name
  name     = "RAW"
  comment  = "Raw synthetic payer data"
}

resource "snowflake_schema" "mart" {
  database = snowflake_database.this.name
  name     = "MART"
  comment  = "Mart layer with aggregated views and drift findings"
}

resource "snowflake_schema" "policy" {
  database = snowflake_database.this.name
  name     = "POLICY"
  comment  = "Synthetic policy versions"
}

resource "snowflake_schema" "audit" {
  database = snowflake_database.this.name
  name     = "AUDIT"
  comment  = "Audit trail for evidence packets and run history"
}

resource "snowflake_warehouse" "this" {
  name           = "PAYER_DRIFT_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
  auto_resume    = true
  comment        = "Compute for payer drift sentinel demo"
}
