#!/bin/bash
# Rolls back a Kubernetes deployment to the last stable revision
# Usage: ./rollback_release.sh <deployment_name> <namespace>

DEPLOYMENT_NAME=$1
NAMESPACE=$2

if [ -z "$DEPLOYMENT_NAME" ] || [ -z "$NAMESPACE" ]; then
    echo "Error: Deployment name and namespace are required."
    echo "Usage: $0 <deployment_name> <namespace>"
    exit 1
fi

echo "Rolling back deployment '$DEPLOYMENT_NAME' in namespace '$NAMESPACE' to the previous stable revision..."
kubectl rollout undo deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE"

if [ $? -eq 0 ]; then
    echo "Rollback initiated successfully."
    echo "Checking rollout status..."
    kubectl rollout status deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE" --timeout=60s
    exit 0
else
    echo "Error: Failed to rollback deployment."
    exit 1
fi
