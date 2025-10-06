# User-assigned managed identity for workload identity
resource "azurerm_user_assigned_identity" "agentic" {
  name                = "${local.cluster_name}-workload-identity"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}

# Federated identity credential for workload identity
resource "azurerm_federated_identity_credential" "agentic" {
  name                = "${local.cluster_name}-federated-credential"
  resource_group_name = azurerm_resource_group.main.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = azurerm_kubernetes_cluster.main.oidc_issuer_url
  parent_id           = azurerm_user_assigned_identity.agentic.id
  subject             = "system:serviceaccount:default:agentic-service-account"
}

# Role assignments for Azure services
resource "azurerm_role_assignment" "storage_blob_data_contributor" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.agentic.principal_id
}

resource "azurerm_role_assignment" "storage_account_contributor" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Storage Account Contributor"
  principal_id         = azurerm_user_assigned_identity.agentic.principal_id
}

resource "azurerm_role_assignment" "data_factory_contributor" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Data Factory Contributor"
  principal_id         = azurerm_user_assigned_identity.agentic.principal_id
}

resource "azurerm_role_assignment" "cognitive_services_user" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_user_assigned_identity.agentic.principal_id
}

resource "azurerm_role_assignment" "cognitive_services_openai_user" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.agentic.principal_id
}

resource "azurerm_role_assignment" "reader" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Reader"
  principal_id         = azurerm_user_assigned_identity.agentic.principal_id
}