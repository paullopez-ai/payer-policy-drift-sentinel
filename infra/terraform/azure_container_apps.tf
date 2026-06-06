resource "azurerm_container_app_environment" "this" {
  name                       = "cae-payer-drift-${local.suffix}"
  location                   = azurerm_resource_group.this.location
  resource_group_name        = azurerm_resource_group.this.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.this.id
  tags                       = local.tags
}

resource "azurerm_container_app" "api" {
  name                         = "ca-drift-sentinel-api"
  container_app_environment_id = azurerm_container_app_environment.this.id
  resource_group_name          = azurerm_resource_group.this.name
  revision_mode                = "Single"
  tags                         = local.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.api.id]
  }

  registry {
    server   = azurerm_container_registry.this.login_server
    identity = azurerm_user_assigned_identity.api.id
  }

  template {
    min_replicas = 0
    max_replicas = 1

    container {
      name   = "drift-sentinel-api"
      image  = "${azurerm_container_registry.this.login_server}/drift-sentinel-api:${var.container_image_tag}"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "APP_ENV"
        value = "live"
      }
      env {
        name  = "MOCK_LLM"
        value = "false"
      }
      env {
        name  = "EXTERNAL_CLIENT_MODE"
        value = "live"
      }
      env {
        name  = "KEY_VAULT_URI"
        value = azurerm_key_vault.this.vault_uri
      }
      env {
        name  = "AZURE_OPENAI_ENDPOINT"
        value = azurerm_cognitive_account.openai.endpoint
      }
      env {
        name  = "AZURE_OPENAI_DEPLOYMENT"
        value = var.azure_openai_deployment
      }
      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.this.connection_string
      }
      env {
        name  = "SNOWFLAKE_DATABASE"
        value = "PAYER_DRIFT_SENTINEL"
      }
      env {
        name  = "SNOWFLAKE_WAREHOUSE"
        value = "PAYER_DRIFT_WH"
      }
      env {
        name  = "DATABRICKS_HOST"
        value = "https://${azurerm_databricks_workspace.this.workspace_url}"
      }
      env {
        name  = "MAX_RUN_COST_USD"
        value = "5.00"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
