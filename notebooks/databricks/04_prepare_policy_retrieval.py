# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Prepare Policy Retrieval
# MAGIC Prepares policy passages for retrieval by the API evidence generation step.

# COMMAND ----------

CATALOG = "payer_drift"
BRONZE = f"{CATALOG}.bronze"
GOLD = f"{CATALOG}.gold"

# COMMAND ----------

from pyspark.sql import functions as F
import hashlib

# COMMAND ----------

policies = spark.table(f"{BRONZE}.policy_version")

# Create retrieval-ready policy passages with citation metadata
retrieval_table = (
    policies
    .withColumn("content_hash", F.sha2(F.col("policy_text"), 256))
    .withColumn(
        "citation_id",
        F.concat(
            F.lit("CIT-"),
            F.col("policy_version_id"),
            F.lit("-"),
            F.substring(F.sha2(F.col("policy_text"), 256), 1, 12),
        )
    )
    .select(
        "policy_version_id",
        "policy_name",
        "procedure_group",
        "effective_date",
        "retired_date",
        F.col("policy_text").alias("passage"),
        "content_hash",
        "citation_id",
        "source_type",
        F.lit(0.8).alias("relevance_score"),  # Default score; real system would use embeddings
    )
)

retrieval_table.write.mode("overwrite").saveAsTable(f"{GOLD}.policy_retrieval")
print(f"Policy retrieval table: {retrieval_table.count()} passages")
