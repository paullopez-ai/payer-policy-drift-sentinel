resource "databricks_notebook" "ingest" {
  path     = "/Shared/payer-drift-sentinel/01_ingest_from_snowflake"
  language = "PYTHON"
  source   = "${path.module}/../../notebooks/databricks/01_ingest_from_snowflake.py"

  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_notebook" "features" {
  path     = "/Shared/payer-drift-sentinel/02_build_features"
  language = "PYTHON"
  source   = "${path.module}/../../notebooks/databricks/02_build_features.py"

  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_notebook" "drift" {
  path     = "/Shared/payer-drift-sentinel/03_detect_drift"
  language = "PYTHON"
  source   = "${path.module}/../../notebooks/databricks/03_detect_drift.py"

  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_notebook" "retrieval" {
  path     = "/Shared/payer-drift-sentinel/04_prepare_policy_retrieval"
  language = "PYTHON"
  source   = "${path.module}/../../notebooks/databricks/04_prepare_policy_retrieval.py"

  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_notebook" "write_findings" {
  path     = "/Shared/payer-drift-sentinel/05_write_findings"
  language = "PYTHON"
  source   = "${path.module}/../../notebooks/databricks/05_write_findings.py"

  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_job" "drift_feature_pipeline" {
  name = "drift_feature_pipeline"

  task {
    task_key = "ingest"
    notebook_task {
      notebook_path = databricks_notebook.ingest.path
    }
    new_cluster {
      num_workers   = 0
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_DS3_v2"
    }
  }

  task {
    task_key = "features"
    depends_on {
      task_key = "ingest"
    }
    notebook_task {
      notebook_path = databricks_notebook.features.path
    }
    new_cluster {
      num_workers   = 0
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_DS3_v2"
    }
  }

  task {
    task_key = "drift"
    depends_on {
      task_key = "features"
    }
    notebook_task {
      notebook_path = databricks_notebook.drift.path
    }
    new_cluster {
      num_workers   = 0
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_DS3_v2"
    }
  }

  task {
    task_key = "retrieval"
    depends_on {
      task_key = "features"
    }
    notebook_task {
      notebook_path = databricks_notebook.retrieval.path
    }
    new_cluster {
      num_workers   = 0
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_DS3_v2"
    }
  }

  task {
    task_key = "write_findings"
    depends_on {
      task_key = "drift"
    }
    notebook_task {
      notebook_path = databricks_notebook.write_findings.path
    }
    new_cluster {
      num_workers   = 0
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_DS3_v2"
    }
  }
}
