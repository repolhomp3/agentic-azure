# Agentic Workflows Platform - Azure Architecture

> **Technical architecture specification for the Azure-native implementation of the agentic workflows platform.**

## System Overview

The Agentic Workflows Platform on Azure is a cloud-native, AI-powered orchestration system that combines Model Context Protocol (MCP) servers with intelligent agents to execute autonomous workflows on Azure Kubernetes Service (AKS).

## High-Level Architecture Layers

### Layer 1: External Access & Load Balancing
- **Application Gateway**: Azure-managed Layer 7 load balancer
  - **Public IP**: Static IP for external access
  - **Listeners**: HTTP:80 (HTTPS:443 optional)
  - **Backend Pools**: AKS worker nodes
  - **Health Probes**: `/health` endpoints on backend services

### Layer 2: Kubernetes Ingress & Routing
- **Application Gateway Ingress Controller (AGIC)**: Kubernetes controller managing Application Gateway
- **Ingress Resource**: `agentic-ingress`
  - **Path Routing**:
    - `/` → Frontend Service (Dashboard UI)
    - `/api` → Agent Core Service (Orchestration API)
  - **Annotations**:
    - `kubernetes.io/ingress.class: azure/application-gateway`

### Layer 3: Application Services Layer
- **Frontend Service** (`agentic-frontend-service`)
  - **Type**: ClusterIP
  - **Port**: 80 → 80 (container)
  - **Purpose**: Serves interactive dashboard UI
  
- **Agent Core Service** (`agent-core-service`)
  - **Type**: ClusterIP  
  - **Port**: 80 → 8000 (container)
  - **Purpose**: AI orchestration and workflow execution

- **MCP Services** (Internal ClusterIP services)
  - `azure-mcp-service`: Port 80 → 8000
  - `database-mcp-service`: Port 80 → 8000
  - `custom-mcp-service`: Port 80 → 8000

### Layer 4: Container Orchestration (Kubernetes)
- **Default Namespace**: Application services
  - `agentic-frontend`: 1 replica (Nginx + static files)
  - `agent-core`: 2 replicas (Python HTTP server)
  - `azure-mcp`: 1 replica (Python HTTP server)
  - `database-mcp`: 1 replica (Python + SQLite)
  - `custom-mcp`: 1 replica (Python HTTP server)
- **K8s-Admin Namespace**: Cluster management
  - `k8s-mcp`: 1 replica (Python + Kubernetes client)

### Layer 5: Infrastructure Layer (Azure Kubernetes Service)
- **AKS Control Plane**: Managed Kubernetes API server (Free tier)
- **Worker Nodes**: Virtual Machines in private subnet
- **Node Pools**: 
  - **System Node Pool**: 2x Standard_B2s (initial capacity)
  - **User Node Pool**: 2x Standard_B2s (application workloads)
  - **Cluster Autoscaler**: Dynamic scaling based on demand

## Network Architecture

### Virtual Network Configuration
```
VNet: 10.0.0.0/16 (agentic-cluster-vnet)
├── AKS Subnet: 10.0.1.0/24
│   └── Worker Nodes (Private IPs)
└── Application Gateway Subnet: 10.0.2.0/24
    └── Application Gateway (Private IP + Public IP)
```

### Network Components
- **Public IP**: Static IP for Application Gateway external access
- **Network Security Groups**: Managed by AKS + Application Gateway
- **Service Endpoints**: For secure access to Azure services

## Azure Service Integrations

### Azure OpenAI Service
```yaml
Integration:
  Service: Azure OpenAI
  Model: GPT-4o-mini
  Authentication: API Key + Workload Identity
  Usage: AI reasoning and workflow analysis
```

### Azure Blob Storage
```yaml
Integration:
  Service: Azure Storage Account
  Authentication: Workload Identity
  Usage: File storage and data persistence
```

### Azure Data Factory
```yaml
Integration:
  Service: Azure Data Factory
  Authentication: Workload Identity
  Usage: ETL pipeline orchestration and monitoring
```

## Security Architecture

### Workload Identity Configuration
```yaml
Workload Identity:
  User Assigned Identity: agentic-workload-identity
  Federated Credential: Links AKS service account to Azure identity
  Service Account: agentic-service-account
  Namespace: default
  
Role Assignments:
  - Storage Blob Data Contributor
  - Data Factory Contributor
  - Cognitive Services User
```

### Network Security
```yaml
Network Isolation:
  - Private subnets for AKS nodes
  - Application Gateway in dedicated subnet
  - Network Security Groups for traffic control
  - Service endpoints for Azure service access
```

### Container Security
```yaml
Security Context:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  readOnlyRootFilesystem: true (where possible)

Resource Limits:
  CPU: 100m-500m per container
  Memory: 128Mi-512Mi per container
```

## Scaling Architecture

### Horizontal Pod Autoscaler (HPA)
```yaml
Agent Core HPA:
  Min Replicas: 2
  Max Replicas: 10
  Target CPU: 80%

MCP Services HPA:
  Min Replicas: 1
  Max Replicas: 5
  Target CPU: 70%
```

### Cluster Autoscaler
```yaml
Node Scaling:
  VM Types: [Standard_B2s, Standard_B4ms]
  Min Nodes: 2
  Max Nodes: 10
  Scale Up: Based on pending pods
  Scale Down: After 10 minutes of low utilization
```

## Monitoring & Observability Architecture

### Prometheus Stack
```yaml
Components:
  - Prometheus Server (metrics collection)
  - Grafana (visualization dashboard)
  - Node Exporter (system metrics)
  - kube-state-metrics (K8s object metrics)

Access:
  Grafana: LoadBalancer service
  Credentials: admin / admin123
  Retention: 7 days
```

### Application Metrics
```yaml
Agent Core Metrics:
  Endpoint: /metrics (Prometheus format)
  Metrics:
    - agent_core_requests_total (counter)
    - agent_core_active_workflows (gauge)
    - agent_core_request_duration (histogram)
```

## Deployment Architecture

### Infrastructure as Code (Terraform)
```hcl
# Module Structure
├── main.tf (Provider configuration)
├── variables.tf (Input parameters)
├── resource-group.tf (Resource group)
├── network.tf (VNet and subnets)
├── aks.tf (Kubernetes cluster)
├── workload-identity.tf (Security configuration)
├── application-gateway.tf (Ingress)
├── addons.tf (Cluster addons)
└── outputs.tf (Resource references)
```

### Application Deployment (Helm)
```yaml
# Chart Structure
├── Chart.yaml (Metadata)
├── values.yaml (Configuration)
└── templates/
    ├── serviceaccount.yaml
    ├── agent-core.yaml
    ├── azure-mcp.yaml
    ├── database-mcp.yaml
    ├── custom-mcp.yaml
    ├── k8s-mcp.yaml
    ├── frontend.yaml
    └── ingress.yaml
```

## Cost Optimization

### Resource Efficiency
```yaml
VM Sizing:
  - Standard_B2s for development (2 vCPU, 4GB RAM)
  - Burstable performance for cost efficiency
  - Cluster autoscaler for demand-based scaling

Storage:
  - Standard SSD for OS disks
  - Ephemeral storage for temporary data
  - Azure Blob Storage for persistent data
```

### Azure-Specific Optimizations
```yaml
Cost Savings:
  - AKS control plane is free
  - Spot instances for non-critical workloads
  - Reserved instances for predictable workloads
  - Auto-shutdown for development environments
```

## Disaster Recovery

### High Availability
```yaml
Multi-Zone Deployment:
  - AKS nodes distributed across availability zones
  - Application Gateway with zone redundancy
  - Azure services with built-in redundancy

Backup Strategy:
  - Infrastructure: Terraform state backup
  - Applications: Helm chart versioning
  - Data: Azure Backup for persistent volumes
```

## Performance Optimization

### Latency Optimization
```yaml
Network:
  - Application Gateway in same region as AKS
  - Private endpoints for Azure services
  - CDN for static content (future)

Caching:
  - In-memory caching in MCP servers
  - Azure Redis Cache (future)
  - Application Gateway caching
```

### Throughput Optimization
```yaml
Concurrency:
  - Multi-threaded HTTP servers
  - Connection pooling for Azure services
  - Async processing patterns

Resource Allocation:
  - CPU limits prevent resource contention
  - Memory limits prevent OOM conditions
  - Proper resource requests for scheduling
```

This architecture provides a comprehensive foundation for building and scaling the agentic workflows platform on Azure, with emphasis on security, cost optimization, and operational excellence.