resource "azurerm_resource_group" "this" {
  name     = "rg-payer-drift-sentinel-${local.environment}"
  location = local.location
  tags     = local.tags
}
