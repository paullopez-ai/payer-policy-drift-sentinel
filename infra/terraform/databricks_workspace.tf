resource "azurerm_databricks_workspace" "this" {
  name                = var.databricks_workspace_name
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = "premium"
  tags                = local.tags
}

resource "azurerm_storage_account" "databricks" {
  name                     = "stpayerdrift${local.suffix}"
  location                 = azurerm_resource_group.this.location
  resource_group_name      = azurerm_resource_group.this.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = local.tags
}
