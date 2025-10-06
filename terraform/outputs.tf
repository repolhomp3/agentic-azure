output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.name
}

output "cluster_endpoint" {
  description = "Endpoint for the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.host
  sensitive   = true
}

output "application_gateway_ip" {
  description = "Public IP address of the Application Gateway"
  value       = azurerm_public_ip.appgw.ip_address
}

output "workload_identity_client_id" {
  description = "Client ID of the workload identity"
  value       = azurerm_user_assigned_identity.agentic.client_id
}

output "kube_config" {
  description = "Kubernetes configuration"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

output "dashboard_url" {
  description = "URL to access the agentic dashboard"
  value       = "http://${azurerm_public_ip.appgw.ip_address}"
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.agentic.name
}