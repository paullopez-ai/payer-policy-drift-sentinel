resource "snowflake_role" "app_role" {
  name    = "PAYER_DRIFT_APP_ROLE"
  comment = "Application role for drift sentinel API"
}

resource "snowflake_role" "databricks_role" {
  name    = "PAYER_DRIFT_DATABRICKS_ROLE"
  comment = "Role for Databricks to read Snowflake data"
}

resource "snowflake_role" "admin_role" {
  name    = "PAYER_DRIFT_ADMIN_ROLE"
  comment = "Admin role for demo management"
}

# App role grants - read all schemas, write to AUDIT
resource "snowflake_grant_privileges_to_account_role" "app_usage_db" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.this.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_usage_wh" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.this.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_usage_raw" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.this.name}\".\"${snowflake_schema.raw.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_select_raw" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.this.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_usage_mart" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.this.name}\".\"${snowflake_schema.mart.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_select_mart" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.this.name}\".\"${snowflake_schema.mart.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_usage_policy" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.this.name}\".\"${snowflake_schema.policy.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_select_policy" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.this.name}\".\"${snowflake_schema.policy.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_usage_audit" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.this.name}\".\"${snowflake_schema.audit.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "app_write_audit" {
  account_role_name = snowflake_role.app_role.name
  privileges        = ["SELECT", "INSERT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.this.name}\".\"${snowflake_schema.audit.name}\""
    }
  }
}

# Databricks role grants - read all schemas
resource "snowflake_grant_privileges_to_account_role" "dbx_usage_db" {
  account_role_name = snowflake_role.databricks_role.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.this.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "dbx_usage_wh" {
  account_role_name = snowflake_role.databricks_role.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.this.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "dbx_usage_raw" {
  account_role_name = snowflake_role.databricks_role.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.this.name}\".\"${snowflake_schema.raw.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "dbx_select_raw" {
  account_role_name = snowflake_role.databricks_role.name
  privileges        = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.this.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}
