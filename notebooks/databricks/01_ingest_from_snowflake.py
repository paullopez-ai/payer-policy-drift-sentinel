# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Ingest from Snowflake
# MAGIC Reads synthetic payer data from Snowflake into Databricks Unity Catalog bronze tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

SNOWFLAKE_SOURCE_DB = "PAYER_DRIFT_SENTINEL"
CATALOG = "payer_drift"
BRONZE_SCHEMA = "bronze"

# Snowflake connection options - uses Databricks secret scope
sf_options = {
    "sfUrl": dbutils.secrets.get("payer-drift-sf", "snowflake_url"),
    "sfUser": dbutils.secrets.get("payer-drift-sf", "snowflake_user"),
    "sfPassword": dbutils.secrets.get("payer-drift-sf", "snowflake_password"),
    "sfDatabase": SNOWFLAKE_SOURCE_DB,
    "sfWarehouse": "PAYER_DRIFT_WH",
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ingest Tables

# COMMAND ----------

tables = [
    ("RAW", "CLAIM_LINES"),
    ("RAW", "AUTHORIZATIONS"),
    ("RAW", "DENIAL_EVENTS"),
    ("RAW", "APPEALS"),
    ("MART", "PROVIDER_DIM"),
    ("POLICY", "POLICY_VERSION"),
]

for schema, table in tables:
    sf_table = f"{SNOWFLAKE_SOURCE_DB}.{schema}.{table}"
    target = f"{CATALOG}.{BRONZE_SCHEMA}.{table.lower()}"

    print(f"Reading {sf_table}...")
    df = (
        spark.read.format("snowflake")
        .options(**sf_options)
        .option("sfSchema", schema)
        .option("dbtable", table)
        .load()
    )

    row_count = df.count()
    print(f"  Rows: {row_count}")

    df.write.mode("overwrite").saveAsTable(target)
    print(f"  Written to {target}")

print("Ingest complete.")
