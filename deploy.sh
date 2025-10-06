#!/bin/bash
set -e

echo "🚀 Deploying Agentic Workflows Platform on Azure..."

# Step 1: Build and push container images
echo "📦 Building container images..."
./build.sh

# Step 2: Deploy infrastructure with Terraform
echo "🏗️ Deploying Azure infrastructure..."
cd terraform
terraform init
terraform plan
terraform apply -auto-approve

# Get outputs
RESOURCE_GROUP=$(terraform output -raw resource_group_name)
CLUSTER_NAME=$(terraform output -raw cluster_name)
WORKLOAD_IDENTITY_CLIENT_ID=$(terraform output -raw workload_identity_client_id)
STORAGE_ACCOUNT_NAME=$(terraform output -raw storage_account_name)

echo "✅ Infrastructure deployed!"
echo "Resource Group: $RESOURCE_GROUP"
echo "Cluster Name: $CLUSTER_NAME"

# Step 3: Configure kubectl
echo "⚙️ Configuring kubectl..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --overwrite-existing

# Wait for nodes to be ready
echo "⏳ Waiting for cluster nodes to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Step 4: Update Helm values with workload identity and Azure settings
echo "🔧 Updating Helm values..."
cd ../helm/agentic-platform
sed -i.bak "s/clientId: \"\"/clientId: \"$WORKLOAD_IDENTITY_CLIENT_ID\"/g" values.yaml
sed -i "s/accountName: \"\"/accountName: \"$STORAGE_ACCOUNT_NAME\"/g" values.yaml
sed -i "s/resourceGroup: \"\"/resourceGroup: \"$RESOURCE_GROUP\"/g" values.yaml

# Step 5: Deploy applications with Helm
echo "🚢 Deploying applications..."
helm install agentic-platform . --wait --timeout=10m

# Step 6: Get access information
echo "📊 Getting access information..."
kubectl get ingress agentic-ingress

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Access Information:"
echo "Dashboard URL: http://$(terraform output -raw application_gateway_ip)"
echo "Grafana URL: http://$(kubectl get svc -n monitoring prometheus-grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "Grafana Login: admin / admin123"
echo ""
echo "🔍 Useful commands:"
echo "kubectl get pods                    # Check pod status"
echo "kubectl logs -l app=agent-core     # View agent core logs"
echo "kubectl get ingress                # Check ingress status"
echo ""
echo "⚠️  Note: It may take 2-3 minutes for the Application Gateway to be fully provisioned."