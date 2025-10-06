# Storage account for blob storage operations
resource "azurerm_storage_account" "agentic" {
  name                     = "${replace(local.cluster_name, "-", "")}storage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}

# Sample container for testing
resource "azurerm_storage_container" "sample" {
  name                  = "sample-data"
  storage_account_name  = azurerm_storage_account.agentic.name
  container_access_type = "private"
}