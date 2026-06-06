resource "azurerm_key_vault" "this" {
  name                       = "kv-payer-drift-${local.suffix}"
  location                   = azurerm_resource_group.this.location
  resource_group_name        = azurerm_resource_group.this.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  tags                       = local.tags

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge",
    ]
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_user_assigned_identity.api.principal_id

    secret_permissions = [
      "Get", "List",
    ]
  }
}

resource "azurerm_key_vault_secret" "snowflake_account" {
  name         = "snowflake-account"
  value        = var.snowflake_account
  key_vault_id = azurerm_key_vault.this.id
}

resource "azurerm_key_vault_secret" "snowflake_user" {
  name         = "snowflake-user"
  value        = var.snowflake_admin_user
  key_vault_id = azurerm_key_vault.this.id
}

resource "azurerm_key_vault_secret" "azure_openai_endpoint" {
  name         = "azure-openai-endpoint"
  value        = azurerm_cognitive_account.openai.endpoint
  key_vault_id = azurerm_key_vault.this.id
}

resource "azurerm_key_vault_secret" "azure_openai_key" {
  name         = "azure-openai-key"
  value        = azurerm_cognitive_account.openai.primary_access_key
  key_vault_id = azurerm_key_vault.this.id
}
