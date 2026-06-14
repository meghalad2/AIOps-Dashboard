#!/bin/bash
# Scales a Kubernetes deployment replicas
# Usage: ./scale_deployment.sh <deployment_name> <namespace> <replicas>

DEPLOYMENT_NAME=$1
NAMESPACE=$2
REPLICAS=$3

if [ -z "$DEPLOYMENT_NAME" ] || [ -z "$NAMESPACE" ] || [ -z "$REPLICAS" ]; then
    echo "Error: Deployment name, namespace, and replicas count are required."
    echo "Usage: $0 <deployment_name> <namespace> <replicas>"
    exit 1
fi

# Basic validation to ensure replicas is an integer
if ! [[ "$REPLICAS" =~ ^[0-9]+$ ]]; then
    echo "Error: Replicas count must be a positive integer."
    exit 1
fi

echo "Scaling deployment '$DEPLOYMENT_NAME' in namespace '$NAMESPACE' to $REPLICAS replicas..."
kubectl scale deployment/"$DEPLOYMENT_NAME" -n "$NAMESPACE" --replicas="$REPLICAS"

if [ $? -eq 0 ]; then
    echo "Successfully scaled deployment to $REPLICAS replicas."
    exit 0
else
    echo "Error: Failed to scale deployment."
    exit 1
fi
