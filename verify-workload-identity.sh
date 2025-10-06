#!/bin/bash

echo "🔍 Verifying Azure Workload Identity Setup..."

# Check if workload identity is enabled on cluster
echo "1. Checking AKS Workload Identity status..."
kubectl get nodes -o jsonpath='{.items[0].metadata.labels}' | grep -q "azure.workload.identity/use" && echo "✅ Workload Identity enabled" || echo "❌ Workload Identity not enabled"

# Check service account annotations
echo "2. Checking service account configuration..."
kubectl get serviceaccount agentic-service-account -o yaml | grep -q "azure.workload.identity/client-id" && echo "✅ Service account properly annotated" || echo "❌ Service account missing annotations"

# Check workload identity webhook
echo "3. Checking workload identity webhook..."
kubectl get pods -n azure-workload-identity-system | grep -q "workload-identity-webhook" && echo "✅ Workload Identity webhook running" || echo "❌ Workload Identity webhook not found"

# Test Azure authentication from pod
echo "4. Testing Azure authentication..."
kubectl run azure-test --image=mcr.microsoft.com/azure-cli:latest --rm -i --tty --restart=Never --serviceaccount=agentic-service-account -- az account show 2>/dev/null && echo "✅ Azure authentication working" || echo "❌ Azure authentication failed"

echo "🎯 Workload Identity verification complete!"