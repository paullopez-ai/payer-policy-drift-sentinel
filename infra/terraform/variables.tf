variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "payer-policy-drift-sentinel"
}

variable "location" {
  description = "Azure region. Verify Azure OpenAI model availability before applying."
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "demo"
}

# Snowflake
variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
}

variable "snowflake_organization" {
  description = "Snowflake organization name"
  type        = string
}

variable "snowflake_admin_user" {
  description = "Snowflake admin user for Terraform"
  type        = string
}

variable "snowflake_private_key_path" {
  description = "Path to Snowflake private key file"
  type        = string
  sensitive   = true
}

# Azure OpenAI
variable "azure_openai_model_name" {
  description = "Azure OpenAI model name (e.g., gpt-4o). Verify availability in your region."
  type        = string
  default     = "gpt-4o"
}

variable "azure_openai_deployment" {
  description = "Azure OpenAI deployment name"
  type        = string
  default     = "drift-evidence-model"
}

variable "azure_openai_model_version" {
  description = "Azure OpenAI model version"
  type        = string
  default     = "2024-08-06"
}

# Databricks
variable "databricks_workspace_name" {
  description = "Azure Databricks workspace name"
  type        = string
  default     = "dbx-payer-drift-demo"
}

variable "databricks_token" {
  description = "Databricks personal access token for provider auth"
  type        = string
  sensitive   = true
  default     = ""
}

# Container
variable "container_image_tag" {
  description = "Container image tag for the API"
  type        = string
  default     = "latest"
}
