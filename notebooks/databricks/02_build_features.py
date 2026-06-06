# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Build Features
# MAGIC Creates denial rate, appeal reversal rate, and provider cohort features from bronze data.

# COMMAND ----------

CATALOG = "payer_drift"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Denial Rate Features

# COMMAND ----------

from pyspark.sql import functions as F

claims = spark.table(f"{BRONZE}.claim_lines")
denials = spark.table(f"{BRONZE}.denial_events")

# Denial rate by procedure group and policy version
denial_features = (
    denials.groupBy("procedure_group", "policy_version_id")
    .agg(
        F.count("*").alias("denial_count"),
        F.sum("denied_amount").alias("total_denied_amount"),
        F.avg("denied_amount").alias("avg_denied_amount"),
    )
    .join(
        claims.groupBy("procedure_group", "policy_version_id")
        .agg(F.count("*").alias("total_claims")),
        on=["procedure_group", "policy_version_id"],
        how="left",
    )
    .withColumn(
        "denial_rate",
        F.when(F.col("total_claims") > 0, F.col("denial_count") / F.col("total_claims")).otherwise(0),
    )
)

denial_features.write.mode("overwrite").saveAsTable(f"{SILVER}.denial_features")
print(f"Denial features: {denial_features.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Provider Cohort Features

# COMMAND ----------

providers = spark.table(f"{BRONZE}.provider_dim")

provider_denial_features = (
    denials.groupBy("provider_id", "procedure_group")
    .agg(
        F.count("*").alias("provider_denial_count"),
        F.sum("denied_amount").alias("provider_denied_amount"),
    )
    .join(providers.select("provider_id", "provider_type", "market", "volume_group"), on="provider_id", how="left")
)

provider_denial_features.write.mode("overwrite").saveAsTable(f"{SILVER}.provider_denial_features")
print(f"Provider denial features: {provider_denial_features.count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Appeal Reversal Features

# COMMAND ----------

appeals = spark.table(f"{BRONZE}.appeals")

reversal_features = (
    appeals.join(denials.select("denial_id", "procedure_group", "denial_reason_group"), on="denial_id", how="left")
    .groupBy("procedure_group", "denial_reason_group")
    .agg(
        F.count("*").alias("total_appeals"),
        F.sum(F.when(F.col("appeal_outcome") == "OVERTURNED", 1).otherwise(0)).alias("overturned_count"),
        F.sum("admin_cost_estimate").alias("total_admin_cost"),
        F.avg("days_to_resolution").alias("avg_resolution_days"),
    )
    .withColumn(
        "reversal_rate",
        F.when(F.col("total_appeals") > 0, F.col("overturned_count") / F.col("total_appeals")).otherwise(0),
    )
)

reversal_features.write.mode("overwrite").saveAsTable(f"{SILVER}.reversal_features")
print(f"Reversal features: {reversal_features.count()} rows")

print("Feature build complete.")
