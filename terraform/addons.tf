# Metrics Server
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.11.0"

  set {
    name  = "args"
    value = "{--kubelet-insecure-tls,--kubelet-preferred-address-types=InternalIP\\,ExternalIP\\,Hostname}"
  }

  depends_on = [azurerm_kubernetes_cluster.main]
}

# Application Gateway Ingress Controller
resource "helm_release" "agic" {
  name       = "ingress-azure"
  repository = "https://appgwingress.blob.core.windows.net/ingress-azure-helm-package/"
  chart      = "ingress-azure"
  namespace  = "default"
  version    = "1.7.2"

  set {
    name  = "appgw.name"
    value = azurerm_application_gateway.main.name
  }

  set {
    name  = "appgw.resourceGroup"
    value = azurerm_resource_group.main.name
  }

  set {
    name  = "appgw.subscriptionId"
    value = data.azurerm_client_config.current.subscription_id
  }

  set {
    name  = "armAuth.type"
    value = "workloadIdentity"
  }

  set {
    name  = "armAuth.identityClientID"
    value = azurerm_user_assigned_identity.agentic.client_id
  }

  set {
    name  = "rbac.enabled"
    value = "true"
  }

  depends_on = [
    azurerm_kubernetes_cluster.main,
    azurerm_application_gateway.main,
    azurerm_user_assigned_identity.agentic
  ]
}

# Prometheus and Grafana monitoring stack
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "monitoring"
  version    = "55.5.0"

  create_namespace = true

  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "grafana.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "grafana.adminPassword"
    value = "admin123"
  }

  set {
    name  = "alertmanager.enabled"
    value = "false"
  }

  depends_on = [azurerm_kubernetes_cluster.main]
}

# Cluster Autoscaler
resource "helm_release" "cluster_autoscaler" {
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  version    = "9.29.0"

  set {
    name  = "autoDiscovery.clusterName"
    value = azurerm_kubernetes_cluster.main.name
  }

  set {
    name  = "azureResourceGroup"
    value = azurerm_resource_group.main.name
  }

  set {
    name  = "azureSubscriptionID"
    value = data.azurerm_client_config.current.subscription_id
  }

  set {
    name  = "azureVMType"
    value = "vmss"
  }

  set {
    name  = "azureUseManagedIdentityExtension"
    value = "true"
  }

  depends_on = [azurerm_kubernetes_cluster.main]
}