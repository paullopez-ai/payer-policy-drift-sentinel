resource "databricks_catalog" "payer_drift" {
  name    = "payer_drift"
  comment = "Unity Catalog for Payer Policy Drift Sentinel"

  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.payer_drift.name
  name         = "bronze"
  comment      = "Raw ingested data from Snowflake"
}

resource "databricks_schema" "silver" {
  catalog_name = databricks_catalog.payer_drift.name
  name         = "silver"
  comment      = "Feature engineering output"
}

resource "databricks_schema" "gold" {
  catalog_name = databricks_catalog.payer_drift.name
  name         = "gold"
  comment      = "Drift findings and retrieval-ready data"
}

resource "databricks_schema" "retrieval" {
  catalog_name = databricks_catalog.payer_drift.name
  name         = "retrieval"
  comment      = "Policy retrieval indexes"
}
