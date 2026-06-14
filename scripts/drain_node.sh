#!/bin/bash
# Cordon and drain a Kubernetes cluster node in case of hardware or OS failure
# Usage: ./drain_node.sh <node_name>

NODE_NAME=$1

if [ -z "$NODE_NAME" ]; then
    echo "Error: Node name is required."
    echo "Usage: $0 <node_name>"
    exit 1
fi

echo "Step 1: Cordoning node '$NODE_NAME' to prevent new pod scheduling..."
kubectl cordon "$NODE_NAME"

if [ $? -ne 0 ]; then
    echo "Error: Failed to cordon node '$NODE_NAME'."
    exit 1
fi

echo "Step 2: Draining node '$NODE_NAME' to evict active pods..."
# Use ignore-daemonsets and delete-emptydir-data for robust node evacuation
kubectl drain "$NODE_NAME" --ignore-daemonsets --delete-emptydir-data --force --grace-period=30

if [ $? -eq 0 ]; then
    echo "Successfully cordoned and drained node '$NODE_NAME'."
    exit 0
else
    echo "Error: Failed to drain node '$NODE_NAME'."
    exit 1
fi
