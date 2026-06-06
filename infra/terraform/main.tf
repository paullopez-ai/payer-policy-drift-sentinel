terraform {
  required_version = ">= 1.8.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }

    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }

    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }

    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 1.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

provider "azuread" {}

provider "databricks" {
  host  = azurerm_databricks_workspace.this.workspace_url
  token = var.databricks_token
}

provider "snowflake" {
  organization_name = var.snowflake_organization
  account_name      = var.snowflake_account
  user              = var.snowflake_admin_user
  authenticator     = "SNOWFLAKE_JWT"
  private_key_path  = var.snowflake_private_key_path
}

provider "random" {}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  project_name = var.project_name
  environment  = var.environment
  location     = var.location
  suffix       = random_string.suffix.result
  tags = {
    project     = local.project_name
    environment = local.environment
    managed_by  = "terraform"
  }
}

data "azurerm_client_config" "current" {}
