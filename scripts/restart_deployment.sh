#!/bin/bash
# Gracefully restarts a Kubernetes deployment
# Usage: ./restart_deployment.sh <deployment_name> <namespace>

DEPLOYMENT_NAME=$1
NAMESPACE=$2

if [ -z "$DEPLOYMENT_NAME" ] || [ -z "$NAMESPACE" ]; then
    echo "Error: Deployment name and namespace are required."
    echo "Usage: $0 <deployment_name> <namespace>"
    exit 1
fi

echo "Initiating rolling restart of deployment '$DEPLOYMENT_NAME' in namespace '$NAMESPACE'..."
kubectl rollout restart deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE"

if [ $? -eq 0 ]; then
    echo "Successfully triggered rolling restart."
    echo "Waiting for rollout to complete..."
    kubectl rollout status deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=60s
    exit 0
else
    echo "Error: Failed to trigger rollout restart."
    exit 1
fi
