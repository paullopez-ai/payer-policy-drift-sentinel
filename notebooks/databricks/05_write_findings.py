# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - Write Findings
# MAGIC Writes drift findings from Databricks gold tables back to Snowflake MART schema.

# COMMAND ----------

CATALOG = "payer_drift"
GOLD = f"{CATALOG}.gold"
SNOWFLAKE_TARGET_DB = "PAYER_DRIFT_SENTINEL"

# COMMAND ----------

sf_options = {
    "sfUrl": dbutils.secrets.get("payer-drift-sf", "snowflake_url"),
    "sfUser": dbutils.secrets.get("payer-drift-sf", "snowflake_user"),
    "sfPassword": dbutils.secrets.get("payer-drift-sf", "snowflake_password"),
    "sfDatabase": SNOWFLAKE_TARGET_DB,
    "sfWarehouse": "PAYER_DRIFT_WH",
    "sfSchema": "MART",
}

# COMMAND ----------

drift_findings = spark.table(f"{GOLD}.drift_findings")
print(f"Writing {drift_findings.count()} drift findings to Snowflake MART.DRIFT_FINDINGS...")

(
    drift_findings.write
    .format("snowflake")
    .options(**sf_options)
    .option("dbtable", "DRIFT_FINDINGS")
    .mode("overwrite")
    .save()
)

print("Findings written to Snowflake.")
