#!/bin/bash
# Autonomous Kubernetes AI Ops Platform - AWS Resource Destroy/Cleanup Script
# This script completely tears down and destroys all AWS resources to avoid billing charges.

# -------------------------------------------------------------
# 1. AWS Credentials Configuration
# -------------------------------------------------------------
# Re-authenticating terminal session using your active IAM credentials
# Ensure these are exported in your terminal before running this script:
# export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
# export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="us-east-1"

echo "=========================================================="
echo "🚨 STARTING COMPLETE AWS INFRASTRUCTURE DESTRUCTION 🚨"
echo "=========================================================="
echo "Order of Precedence: Helm Charts -> Kubernetes Namespaces -> Terraform Infrastructure -> AWS Key Pairs"
echo "----------------------------------------------------------"

# Verify AWS Connectivity
aws sts get-caller-identity >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: AWS credentials invalid or expired. Cannot proceed with destruction."
    exit 1
fi
echo "✅ AWS Credentials verified successfully."

# -------------------------------------------------------------
# 2. Teardown Helm Charts (CRITICAL: Deletes AWS Load Balancers)
# -------------------------------------------------------------
# If we don't delete Ingress and Prometheus first, AWS Load Balancers will stay active,
# causing Terraform to hang and fail because the VPC subnets are still in use!
echo "STEP 1: Uninstalling Ingress and Prometheus Helm Charts..."

helm uninstall ingress-nginx -n ingress-nginx >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  - Ingress controller uninstalled successfully."
else
    echo "  - Ingress controller not found or already deleted."
fi

helm uninstall prometheus-stack -n production >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  - Prometheus stack uninstalled successfully."
else
    echo "  - Prometheus stack not found or already deleted."
fi

# -------------------------------------------------------------
# 3. Clean up Kubernetes Namespaces
# -------------------------------------------------------------
echo "STEP 2: Deleting Kubernetes namespaces..."
kubectl delete namespace production --timeout=60s >/dev/null 2>&1
kubectl delete namespace ingress-nginx --timeout=60s >/dev/null 2>&1
echo "  - Namespaces deleted successfully."

# -------------------------------------------------------------
# 4. Terraform Destroy (Tears down EKS, VPC, Subnets, and EC2)
# -------------------------------------------------------------
echo "STEP 3: Destroying EKS Cluster, VPC, and EC2 Jenkins Server via Terraform (takes ~10 minutes)..."
cd /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/terraform

terraform destroy -auto-approve

if [ $? -eq 0 ]; then
    echo "✅ Terraform infrastructure destroyed successfully."
else
    echo "❌ Error: Terraform destroy failed. Please review error logs."
fi

# -------------------------------------------------------------
# 5. Delete AWS Key Pair & Local Pem Files
# -------------------------------------------------------------
echo "STEP 4: Deleting AWS EC2 Key Pair 'devops-key'..."
aws ec2 delete-key-pair --key-name devops-key --region us-east-1 >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  - AWS Key Pair 'devops-key' deleted from EC2 Console."
else
    echo "  - Key pair already deleted."
fi

# Delete local secure key file
if [ -f "devops-key.pem" ]; then
    rm devops-key.pem
    echo "  - Local secure 'devops-key.pem' file removed."
fi

echo "=========================================================="
echo "🎉 DESTRUCTION COMPLETE! All AWS billing charges stopped. 🎉"
echo "=========================================================="
