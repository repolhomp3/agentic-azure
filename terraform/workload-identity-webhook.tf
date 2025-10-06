# Install Azure Workload Identity webhook
resource "helm_release" "workload_identity_webhook" {
  name       = "workload-identity-webhook"
  repository = "https://azure.github.io/azure-workload-identity/charts"
  chart      = "workload-identity-webhook"
  namespace  = "azure-workload-identity-system"
  version    = "1.1.0"

  create_namespace = true

  set {
    name  = "azureTenantID"
    value = data.azurerm_client_config.current.tenant_id
  }

  depends_on = [azurerm_kubernetes_cluster.main]
}