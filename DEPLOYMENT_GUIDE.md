# Azure Deployment Guide - Complete Setup for Beginners

> **Step-by-step guide to deploy the Agentic Workflows Platform on Azure from scratch**

## 🎯 Overview

This guide will take you from zero to a fully deployed AI-powered workflow platform on Azure. No prior Azure experience required!

**What you'll build:**
- Azure Kubernetes Service (AKS) cluster
- AI-powered workflow orchestration with Azure OpenAI
- Interactive web dashboard
- Complete monitoring stack

**Time required:** 45-60 minutes  
**Cost:** ~$0.68 for 2-hour demo

---

## 📋 Prerequisites Checklist

Before starting, you'll need:
- [ ] Computer with internet access (Windows, macOS, or Linux)
- [ ] Credit card for Azure account (free tier available)
- [ ] Basic command line familiarity

---

## Step 1: Create Azure Account

### 1.1 Sign Up for Azure

1. **Visit Azure Portal**: Go to [portal.azure.com](https://portal.azure.com)
2. **Click "Create Account"** or "Start Free"
3. **Provide Information**:
   - Email address
   - Phone number for verification
   - Credit card (for identity verification - won't be charged immediately)
4. **Complete Verification**: Follow SMS/email verification steps
5. **Accept Terms**: Review and accept Azure terms of service

### 1.2 Verify Account Access

1. **Login**: Go to [portal.azure.com](https://portal.azure.com)
2. **Check Subscription**: You should see "Azure subscription 1" or similar
3. **Note Subscription ID**: Click on "Subscriptions" → copy your subscription ID

**✅ Checkpoint**: You can access the Azure Portal and see your subscription

---

## Step 2: Install Required Tools

### 2.1 Install Azure CLI

**Windows:**
```powershell
# Download and run installer
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install azure-cli

# Or using curl
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Linux (Ubuntu/Debian):**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Verify Installation:**
```bash
az --version
# Should show version 2.50+ or higher
```

### 2.2 Install Docker

**Windows:**
1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Run installer and restart computer
3. Start Docker Desktop from Start menu

**macOS:**
```bash
# Using Homebrew
brew install --cask docker

# Or download from docker.com and install
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER
# Log out and back in
```

**Verify Installation:**
```bash
docker --version
# Should show version 20.0+ or higher
```

### 2.3 Install Terraform

**Windows:**
```powershell
# Using Chocolatey
choco install terraform

# Or download from terraform.io
```

**macOS:**
```bash
# Using Homebrew
brew install terraform
```

**Linux:**
```bash
# Download and install
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Verify Installation:**
```bash
terraform --version
# Should show version 1.0+ or higher
```

### 2.4 Install kubectl

**Windows:**
```powershell
# Download kubectl
curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
# Move to PATH directory
```

**macOS:**
```bash
# Using Homebrew
brew install kubectl
```

**Linux:**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

**Verify Installation:**
```bash
kubectl version --client
# Should show version 1.28+ or higher
```

### 2.5 Install Helm

**Windows:**
```powershell
# Using Chocolatey
choco install kubernetes-helm
```

**macOS:**
```bash
# Using Homebrew
brew install helm
```

**Linux:**
```bash
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update && sudo apt-get install helm
```

**Verify Installation:**
```bash
helm version
# Should show version 3.12+ or higher
```

**✅ Checkpoint**: All tools installed and showing correct versions

---

## Step 3: Configure Azure Access

### 3.1 Login to Azure CLI

```bash
# Login to Azure
az login
```

This will:
1. Open your web browser
2. Ask you to login to Azure
3. Return to terminal with success message

### 3.2 Set Your Subscription

```bash
# List available subscriptions
az account list --output table

# Set your subscription (replace with your subscription ID)
az account set --subscription "your-subscription-id-here"

# Verify current subscription
az account show
```

### 3.3 Register Required Providers

```bash
# Register Azure providers (takes 2-3 minutes)
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.Network
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.CognitiveServices

# Check registration status
az provider show --namespace Microsoft.ContainerService --query "registrationState"
```

**✅ Checkpoint**: Azure CLI logged in and providers registered

---

## Step 4: Set Up Azure OpenAI (Optional but Recommended)

### 4.1 Request Azure OpenAI Access

1. **Go to Azure Portal**: [portal.azure.com](https://portal.azure.com)
2. **Search "Azure OpenAI"** in the top search bar
3. **Click "Create"** → **"Request Access"**
4. **Fill Application**:
   - Business justification: "Learning and development"
   - Use case: "AI workflow automation"
5. **Submit Request**: Usually approved within 24 hours

### 4.2 Create Azure OpenAI Resource (After Approval)

```bash
# Create resource group for OpenAI
az group create --name agentic-openai-rg --location eastus

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name agentic-openai \
  --resource-group agentic-openai-rg \
  --location eastus \
  --kind OpenAI \
  --sku S0

# Get API key and endpoint
az cognitiveservices account keys list \
  --name agentic-openai \
  --resource-group agentic-openai-rg

az cognitiveservices account show \
  --name agentic-openai \
  --resource-group agentic-openai-rg \
  --query "properties.endpoint"
```

**Save these values** - you'll need them later:
- API Key: `key1` from the keys command
- Endpoint: URL from the endpoint command

**✅ Checkpoint**: Azure OpenAI resource created (or access requested)

---

## Step 5: Create Azure Container Registry

### 5.1 Create Resource Group

```bash
# Create main resource group
az group create --name agentic-rg --location eastus
```

### 5.2 Create Container Registry

```bash
# Create Azure Container Registry
az acr create \
  --resource-group agentic-rg \
  --name agenticsacr \
  --sku Basic \
  --location eastus

# Login to registry
az acr login --name agenticsacr
```

**✅ Checkpoint**: Container registry created and accessible

---

## Step 6: Download and Configure Project

### 6.1 Clone the Repository

```bash
# Clone the project
git clone https://github.com/your-org/agentic-azure.git
cd agentic-azure

# Or download and extract ZIP if no git
```

### 6.2 Configure Registry Settings

```bash
# Update registry in build script
sed -i 's/your-registry/agenticsacr.azurecr.io/g' build.sh

# Update registry in Helm values
sed -i 's/your-registry/agenticsacr.azurecr.io/g' helm/agentic-platform/values.yaml
```

### 6.3 Configure Azure OpenAI (If Available)

Edit `helm/agentic-platform/values.yaml`:

```yaml
azure:
  openai:
    endpoint: "https://agentic-openai.openai.azure.com/"  # Your endpoint
    apiKey: "your-api-key-here"                          # Your API key
  
  storage:
    accountName: "agenticstorage"  # Will be created automatically
```

**✅ Checkpoint**: Project downloaded and configured

---

## Step 7: Deploy the Platform

### 7.1 Make Scripts Executable

```bash
# Make deployment scripts executable
chmod +x build.sh deploy.sh
```

### 7.2 Run One-Command Deployment

```bash
# Deploy everything (takes 10-15 minutes)
./deploy.sh
```

**What this does:**
1. **Builds containers** (2-3 minutes)
2. **Pushes to registry** (2-3 minutes)
3. **Creates infrastructure** (5-8 minutes)
   - Virtual Network
   - AKS cluster
   - Application Gateway
   - Workload Identity
4. **Deploys applications** (2-3 minutes)
5. **Sets up monitoring** (1-2 minutes)

### 7.3 Monitor Deployment Progress

**In another terminal, watch the deployment:**
```bash
# Watch infrastructure creation
cd terraform
terraform show

# Watch Kubernetes pods (after infrastructure is ready)
kubectl get pods --watch
```

**✅ Checkpoint**: Deployment completed successfully

---

## Step 8: Access Your Platform

### 8.1 Get Access URLs

```bash
# Get main dashboard URL
kubectl get ingress agentic-ingress
echo "Dashboard: http://$(kubectl get ingress agentic-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"

# Get Grafana monitoring URL
kubectl get svc -n monitoring prometheus-grafana
echo "Grafana: http://$(kubectl get svc -n monitoring prometheus-grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
```

### 8.2 Test the Platform

1. **Open Dashboard**: Use the dashboard URL from above
2. **Try Workflows**:
   - Click "Test Azure OpenAI" (if configured)
   - Try "Analyze Weather" with a city name
   - Check "Kubernetes Status"
3. **View Monitoring**: Open Grafana URL
   - Username: `admin`
   - Password: `admin123`

**✅ Checkpoint**: Platform accessible and working

---

## Step 9: Verify Everything Works

### 9.1 Health Checks

```bash
# Check all pods are running
kubectl get pods

# Check services are accessible
kubectl get services

# Check ingress is configured
kubectl get ingress
```

### 9.2 Verify Workload Identity

```bash
# Test Azure Workload Identity setup
./verify-workload-identity.sh

# Should show:
# ✅ Workload Identity enabled
# ✅ Service account properly annotated  
# ✅ Workload Identity webhook running
# ✅ Azure authentication working
```

### 9.3 Test Workflows

**From the dashboard, test these workflows:**

1. **Weather Analysis**:
   - Enter city: "Seattle"
   - Click "Analyze Weather"
   - Should return weather data with AI analysis

2. **Database Query**:
   - Click "Query Users"
   - Should return sample user data

3. **Kubernetes Status**:
   - Click "Cluster Status"
   - Should show node information

4. **Azure Blob Storage**:
   - Click "List Blob Containers"
   - Should show storage containers

**✅ Checkpoint**: All workflows functioning correctly

---

## 🎉 Success! You're Done!

### What You've Built

- ✅ **AKS Cluster**: Production-ready Kubernetes cluster
- ✅ **AI Workflows**: Azure OpenAI-powered automation
- ✅ **Web Dashboard**: Interactive control interface
- ✅ **Monitoring**: Prometheus + Grafana observability
- ✅ **Security**: Workload Identity for secure access
- ✅ **Auto-scaling**: Cluster autoscaler for cost optimization

### Next Steps

1. **Explore Workflows**: Try different cities, SQL queries, K8s operations
2. **Monitor Usage**: Check Grafana dashboards for metrics
3. **Customize**: Add your own MCP servers and workflows
4. **Scale**: Increase replicas or add more node pools

### Cost Management

```bash
# Check current costs
az consumption usage list --output table

# Stop cluster to save costs (optional)
az aks stop --name agentic-cluster --resource-group agentic-rg

# Start cluster when needed
az aks start --name agentic-cluster --resource-group agentic-rg
```

---

## 🆘 Troubleshooting

### Common Issues

**"az command not found"**
```bash
# Restart terminal or run:
source ~/.bashrc  # Linux/macOS
# Or restart PowerShell on Windows
```

**"Docker daemon not running"**
```bash
# Start Docker Desktop (Windows/macOS)
# Or start Docker service (Linux):
sudo systemctl start docker
```

**"Terraform apply failed"**
```bash
# Check Azure quotas
az vm list-usage --location eastus --output table

# Retry deployment
terraform apply -auto-approve
```

**"Pods not starting"**
```bash
# Check pod logs
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Check node resources
kubectl top nodes
```

### Getting Help

- **Azure Documentation**: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
- **Kubernetes Docs**: [kubernetes.io/docs](https://kubernetes.io/docs)
- **Project Issues**: Create GitHub issue with error details

---

## 🧹 Cleanup (When Done)

### Complete Cleanup

```bash
# Delete applications
helm uninstall agentic-platform

# Delete infrastructure
cd terraform
terraform destroy -auto-approve

# Delete resource groups
az group delete --name agentic-rg --yes --no-wait
az group delete --name agentic-openai-rg --yes --no-wait
```

**Final cost**: Should be under $1 for the demo session!

---

**🎊 Congratulations! You've successfully deployed an enterprise-grade AI workflow platform on Azure!**