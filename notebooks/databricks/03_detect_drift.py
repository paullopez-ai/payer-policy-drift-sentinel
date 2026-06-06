# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Detect Drift
# MAGIC Compares current denial and reversal rates against baselines to identify drift findings.

# COMMAND ----------

CATALOG = "payer_drift"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"

# Thresholds
DENIAL_SPIKE_THRESHOLD = 0.10  # 10 percentage point increase
REVERSAL_SPIKE_THRESHOLD = 0.15  # 15 percentage point increase
PROVIDER_OUTLIER_MULTIPLIER = 2.0  # 2x peer average

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window
import uuid
from datetime import date

# COMMAND ----------

# MAGIC %md
# MAGIC ## Denial Spike Detection

# COMMAND ----------

denial_features = spark.table(f"{SILVER}.denial_features")

# Compare versions within same procedure group
w = Window.partitionBy("procedure_group").orderBy("policy_version_id")

denial_drift = (
    denial_features
    .withColumn("prev_denial_rate", F.lag("denial_rate").over(w))
    .withColumn("delta", F.col("denial_rate") - F.coalesce(F.col("prev_denial_rate"), F.lit(0)))
    .filter(F.col("delta") > DENIAL_SPIKE_THRESHOLD)
    .withColumn("finding_id", F.concat(F.lit("FND-DS-"), F.monotonically_increasing_id()))
    .withColumn("finding_type", F.lit("DENIAL_SPIKE"))
    .withColumn("severity", F.when(F.col("delta") > 0.15, "HIGH").otherwise("MEDIUM"))
    .withColumn("confidence", F.lit(0.85))
    .withColumn("detection_date", F.lit(str(date.today())))
    .select(
        "finding_id", "finding_type", "detection_date", "procedure_group",
        F.lit(None).alias("provider_id"),
        F.col("prev_denial_rate").alias("baseline_rate"),
        F.col("denial_rate").alias("observed_rate"),
        "delta", "severity", "confidence", "policy_version_id",
        F.lit("NEW").alias("status"),
    )
)

print(f"Denial spike findings: {denial_drift.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Appeal Reversal Spike Detection

# COMMAND ----------

reversal_features = spark.table(f"{SILVER}.reversal_features")

reversal_drift = (
    reversal_features
    .filter(F.col("reversal_rate") > REVERSAL_SPIKE_THRESHOLD)
    .withColumn("finding_id", F.concat(F.lit("FND-AR-"), F.monotonically_increasing_id()))
    .withColumn("finding_type", F.lit("APPEAL_REVERSAL_SPIKE"))
    .withColumn("severity", F.when(F.col("reversal_rate") > 0.30, "HIGH").otherwise("MEDIUM"))
    .withColumn("confidence", F.lit(0.78))
    .withColumn("detection_date", F.lit(str(date.today())))
    .withColumn("baseline_rate", F.lit(0.12))
    .select(
        "finding_id", "finding_type", "detection_date", "procedure_group",
        F.lit(None).alias("provider_id"),
        "baseline_rate",
        F.col("reversal_rate").alias("observed_rate"),
        (F.col("reversal_rate") - F.col("baseline_rate")).alias("delta"),
        "severity", "confidence",
        F.lit("PV-2024-SOC-001").alias("policy_version_id"),
        F.lit("NEW").alias("status"),
    )
)

print(f"Reversal spike findings: {reversal_drift.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write Combined Findings

# COMMAND ----------

all_findings = denial_drift.unionByName(reversal_drift)
all_findings.write.mode("overwrite").saveAsTable(f"{GOLD}.drift_findings")
print(f"Total drift findings written: {all_findings.count()}")
