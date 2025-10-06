# Agentic Workflows Platform - Azure Edition

> **Enterprise-grade AI orchestration platform that combines Model Context Protocol (MCP) servers with intelligent agents on Azure Kubernetes Service for autonomous workflow execution.**

[![Azure](https://img.shields.io/badge/Azure-AKS%20%7C%20OpenAI%20%7C%20Data%20Factory-blue)](https://azure.microsoft.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.33-blue)](https://kubernetes.io)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green)](https://spec.modelcontextprotocol.io/)
[![Cost](https://img.shields.io/badge/Demo%20Cost-$0.68%2F2hrs-brightgreen)](#cost-analysis)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## 🎯 What This Platform Does

The Agentic Workflows Platform transforms traditional tool orchestration into **intelligent, autonomous workflows** by combining:

- **🤖 AI-Powered Orchestration**: Agent Core uses Azure OpenAI to reason about tasks and coordinate multiple services
- **🔧 MCP Server Integration**: Standardized protocol for tool communication and data exchange
- **☁️ Cloud-Native Architecture**: Production-ready deployment on Azure Kubernetes Service with auto-scaling
- **📊 Real-Time Monitoring**: Interactive dashboard for workflow execution and system health

## 🏗️ Architecture Overview

![Agentic Workflows Platform - Azure Architecture](docs/agentic-azure.png)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agentic Workflows Platform - Azure           │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Application Gateway                                         │
│  ├── /dashboard → Frontend (React-like UI)                     │
│  └── /api → Agent Core (Orchestration Engine)                  │
├─────────────────────────────────────────────────────────────────┤
│  🧠 Agent Core (Reasoning & Orchestration)                     │
│  ├── Azure OpenAI Integration (GPT-4o-mini)                    │
│  ├── Workflow State Management                                  │
│  └── MCP Server Coordination                                    │
├─────────────────────────────────────────────────────────────────┤
│  🔧 MCP Server Ecosystem                                       │
│  ├── Azure MCP (Blob Storage, OpenAI, Data Factory)           │
│  ├── Database MCP (SQLite Operations)                          │
│  ├── Kubernetes MCP (Cluster Admin, Pod Management)            │
│  └── Custom MCP (Weather API, Key-Value Storage)               │
├─────────────────────────────────────────────────────────────────┤
│  ⚙️ Infrastructure Layer                                        │
│  ├── Azure Kubernetes Service 1.33 (3 AZ Deployment)          │
│  ├── Cluster Autoscaler (Intelligent Node Provisioning)        │
│  ├── Workload Identity (Secure Azure Service Access)           │
│  ├── Application Gateway (External Access)                     │
│  └── Monitoring Stack (Metrics Server, Prometheus, Grafana)    │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features

### **Intelligent Workflow Orchestration**
- **Multi-Step Reasoning**: Agent Core uses Azure OpenAI to break down complex tasks into executable steps
- **Dynamic Tool Selection**: Automatically chooses appropriate MCP servers based on task requirements
- **Error Recovery**: Built-in retry logic and graceful degradation for failed operations
- **State Management**: Maintains workflow context across multiple service calls

### **Comprehensive MCP Integration**
- **Azure Services**: Blob Storage management, OpenAI inference, Data Factory pipeline orchestration
- **Kubernetes Operations**: Intelligent cluster management, pod scaling, troubleshooting
- **Database Operations**: SQL query execution with SQLite backend
- **External APIs**: Weather data integration with intelligent caching
- **Data Storage**: Persistent key-value storage for workflow results

### **Production-Ready Infrastructure**
- **Auto-Scaling**: Cluster Autoscaler for nodes, HPA for pods
- **High Availability**: Multi-AZ deployment with load balancing
- **Security**: Workload Identity for credential-less Azure access, network policies
- **Monitoring**: Health checks, metrics collection, distributed tracing ready

## 📋 Prerequisites

### **Required Tools**

**macOS (Homebrew)**:
```bash
brew install terraform kubectl helm azure-cli docker
```

**Linux (Ubuntu/Debian)**:
```bash
# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update && sudo apt-get install helm

# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Docker
sudo apt-get update && sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

### **Azure Setup**

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Verify access
az account show
```

### **Container Registry Setup**

**Azure Container Registry (Recommended)**:
```bash
# Create resource group
az group create --name agentic-rg --location eastus

# Create ACR
az acr create --resource-group agentic-rg --name agenticsacr --sku Basic

# Login to ACR
az acr login --name agenticsacr
```

## 🛠️ Installation & Deployment

### **Step 1: Clone and Configure**

```bash
git clone <this-repo>
cd agentic-azure
```

**Update Registry Configuration**:
```bash
# Update registry in build.sh and helm/agentic-platform/values.yaml
sed -i 's/your-registry/agenticsacr.azurecr.io/g' build.sh
sed -i 's/your-registry/agenticsacr.azurecr.io/g' helm/agentic-platform/values.yaml
```

### **Step 2: One-Command Deployment**

```bash
# Make scripts executable
chmod +x deploy.sh build.sh

# Deploy everything (infrastructure + applications)
./deploy.sh
```

**Deployment Includes**:
- ✅ Virtual Network with 3 subnets
- ✅ AKS cluster with system and user node pools
- ✅ Cluster Autoscaler for intelligent scaling
- ✅ Application Gateway for ingress
- ✅ Workload Identity for secure Azure access
- ✅ Metrics Server for resource monitoring
- ✅ Prometheus & Grafana monitoring stack
- ✅ All containerized services
- ✅ Application Gateway ingress for external access

### **Step 3: Access Dashboards**

```bash
# Get main dashboard URL (takes 2-3 minutes for Application Gateway provisioning)
kubectl get ingress agentic-ingress
echo "Main Dashboard: http://$(kubectl get ingress agentic-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"

# Get Grafana monitoring dashboard URL
kubectl get svc -n monitoring prometheus-grafana
echo "Grafana Dashboard: http://$(kubectl get svc -n monitoring prometheus-grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "Grafana Login: admin / admin123"
```

## 💰 Cost Analysis

### **2-Hour Demo Cost: $0.68**

| Component | Cost/Hour | 2-Hour Total |
|-----------|-----------|-------------|
| AKS Control Plane | Free | $0.00 |
| VM Instances (2x Standard_B2s) | $0.092 | $0.18 |
| Application Gateway | $0.125 | $0.25 |
| Azure OpenAI (GPT-4o-mini) | ~$0.02 | $0.04 |
| Storage & Networking | ~$0.01 | $0.02 |
| **Total** | **$0.34** | **$0.68** |

## 🎮 Usage Examples

### **AI-Powered Weather Analysis**
```json
{
  "method": "workflow/execute",
  "params": {
    "task": "weather analysis",
    "city": "Seattle"
  }
}
```

### **Azure Data Factory Pipeline Orchestration**
```json
{
  "method": "workflow/execute",
  "params": {
    "task": "start data factory pipeline",
    "pipeline_name": "customer-etl-pipeline"
  }
}
```

### **Intelligent Kubernetes Management**
```json
{
  "method": "workflow/execute",
  "params": {
    "task": "kubernetes status"
  }
}
```

## 🧹 Cleanup

```bash
# Delete applications
helm uninstall agentic-platform

# Delete infrastructure
cd terraform
terraform destroy -auto-approve

# Verify cleanup
az aks list --resource-group agentic-rg
```

---

**Ready to build intelligent, autonomous workflows on Azure?** 🚀