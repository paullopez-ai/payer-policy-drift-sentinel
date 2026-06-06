resource "azurerm_cognitive_account" "openai" {
  name                  = "aoai-payer-drift-${local.suffix}"
  location              = azurerm_resource_group.this.location
  resource_group_name   = azurerm_resource_group.this.name
  kind                  = "OpenAI"
  sku_name              = "S0"
  custom_subdomain_name = "aoai-payer-drift-${local.suffix}"
  tags                  = local.tags
}

resource "azurerm_cognitive_deployment" "evidence_model" {
  name                 = var.azure_openai_deployment
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = var.azure_openai_model_name
    version = var.azure_openai_model_version
  }

  sku {
    name     = "Standard"
    capacity = 10
  }
}
