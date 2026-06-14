# Complete End-to-End Project Deployment & Run Guide

Welcome to the master deployment guide for the **Aegis AIOps Control Plane & Dashboard** project. This document provides a complete, step-by-step manual from absolute start to finish, including direct installations for every single tool, Python venv setup, database seeding, and React frontend deployment steps.

---

## 📌 Table of Contents
1. [Prerequisites & Accounts Setup](#1-prerequisites--accounts-setup)
2. [CLI Tools Installation Guide (Macbook Air)](#2-cli-tools-installation-guide-macbook-air)
3. [Writing the Project Configuration (`.env`)](#3-writing-the-project-configuration-env)
4. [Database Seeding & Running the App Locally (Offline Mode)](#4-database-seeding--running-the-app-locally-offline-mode)
5. [Testing & Simulating the Self-Healing Flow](#5-testing--simulating-the-self-healing-flow)
6. [Deploying Real Infrastructure to AWS (Terraform)](#6-deploying-real-infrastructure-to-aws-terraform)
7. [AWS Resource Cleanup (Teardown)](#7-aws-resource-cleanup-teardown)

---

## 🔑 1. Prerequisites & Accounts Setup

Before writing any configuration files, you must gather your access credentials from three sources:

### A. AWS Account Access Keys
You need API credentials with Admin permissions to configure the AWS CLI and let Terraform provision infrastructure.
1. Sign in to the **AWS Management Console**.
2. Search for and navigate to **IAM** (Identity and Access Management).
3. Click **Users** in the left menu, then click **Create user**.
4. Enter a name (e.g., `devops-admin-user`) and click **Next**.
5. Select **Attach policies directly**, choose **AdministratorAccess**, and click **Create user**.
6. Click on your newly created user, navigate to the **Security credentials** tab.
7. Scroll down to **Access keys** and click **Create access key**.
8. Select **Command Line Interface (CLI)**, check the confirmation check box, and click **Next**.
9. Copy both the **AWS Access Key ID** and **AWS Secret Access Key**. Keep these safe!

### B. GitHub Developer Token (PAT)
The AI SRE Agent automatically logs incidents in your portfolio repository. It needs a Personal Access Token (PAT) to authorize this.
1. Sign in to your **GitHub Account** (`github.com`).
2. Click your profile picture in the top-right corner and select **Settings**.
3. Scroll down the left sidebar to the very bottom and click **Developer settings**.
4. Navigate to **Personal access tokens** > **Tokens (classic)**.
5. Click **Generate new token** > **Generate new token (classic)**.
6. Enter a description (e.g., `k8s-self-healing-agent-token`).
7. Check the **`repo`** scope box (grants complete control over public and private repositories).
8. Click **Generate token** at the bottom of the page.
9. **CRITICAL**: Copy the generated token immediately! It will disappear forever once you reload the page.

### C. Gmail SMTP App Password (For Real Emails)
To send real, beautifully styled SRE report emails to your inbox whenever an alert triggers:
1. Go to your **Google Account Settings** (`myaccount.google.com`).
2. Navigate to the **Security** tab in the left-hand menu.
3. Under *"How you sign in to Google"*, make sure **2-Step Verification** is turned **ON** (App Passwords cannot be created without this).
4. Search for or select **App passwords**.
5. Give your password a name (e.g., `Kubernetes AI SRE Agent`) and click **Create**.
6. Google will generate a secure **16-character password** (e.g., `abcd efgh ijkl mnop`).
7. Copy this string and remove all spaces (e.g., `abcdefghijklmnop`). This will be your `SMTP_PASSWORD`!

---

## 💻 2. CLI Tools Installation Guide (Macbook Air)

If you run a command like `aws configure` and get `command not found: aws`, it means you need to install the tools. You can install all dependencies either via **Homebrew** or using **Direct Installer Packages**.

---

### METHOD A: Direct Native Installers (Recommended)
If Homebrew prompts for a `sudo` password or fails, use these direct, native installer commands. Open your terminal and copy-paste these blocks:

#### 1. Install AWS CLI (Official Amazon Installer)
This installs the official AWS command-line tools onto your Mac directly:
```bash
# Download official macOS AWS CLI installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

# Install package (Requires entering your Mac password in the terminal)
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation (This should print the aws-cli version!)
aws --version
```

#### 2. Install Kubectl (Kubernetes Command-Line Tool)
This downloaded binary lets you communicate with EKS clusters:
```bash
# Download Darwin ARM64 binary (for Apple Silicon M1/M2/M3 Macbook Air)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"

# Make the downloaded kubectl executable
chmod +x ./kubectl

# Move the executable into your system binaries folder (Requires password)
sudo mv ./kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

#### 3. Install Helm (Kubernetes Package Manager)
```bash
# Download official helm automated install script
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

# Grant script run permissions
chmod 700 get_helm.sh

# Run the installer script
./get_helm.sh

# Verify installation
helm version
```

#### 4. Install Terraform (HashiCorp Infrastructure Engine)
```bash
# Download Terraform macOS arm64 zip binary
curl -LO "https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_darwin_arm64.zip"

# Unzip the downloaded binary
unzip terraform_1.7.5_darwin_arm64.zip

# Move the binary into your system path (Requires password)
sudo mv terraform /usr/local/bin/terraform

# Verify installation
terraform -version
```

#### 5. Install Node.js & npm (Frontend Runtime)
Go to **[nodejs.org](https://nodejs.org)** and download the stable LTS installer, or run:
```bash
curl -o node-install.pkg "https://nodejs.org/dist/v20.11.0/node-v20.11.0.pkg"
sudo installer -pkg node-install.pkg -target /
node --version
npm --version
```

---

### METHOD B: The Homebrew Package Manager Method
If you have Homebrew installed and configured successfully on your Mac, you can install everything using these simple commands:

```bash
# 1. Install Homebrew (Prompts for Mac password)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Add Homebrew to your shell environment path (only if prompted at the end of install)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# 3. Install all DevOps tools in a single command
brew install awscli hashicorp/tap/terraform kubernetes-cli helm python3 node ollama
```

---

### 🧠 Install & Run Ollama (Local AI Engine)
1. Download Ollama directly from the web browser at: **[ollama.com/download](https://ollama.com/download)**
2. Unzip and drag the **Ollama** application into your **Applications** folder.
3. Start the application by double-clicking it.
4. Download the coding model by running this in your terminal:
   ```bash
   ollama run qwen2.5-coder:1.5b
   ```
   *(Keep this terminal process active!)*

---

### 🐍 Initialize Python Virtual Environment
Navigate to your project directory and set up your clean Python interpreter:
```bash
# Enter the project workspace root
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install all AI Agent dependencies
pip install -r ai-agent/requirements.txt
```

---

## 📝 3. Writing the Project Configuration (`.env`)

Create a new file at:
📂 `/Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/ai-agent/.env`

Paste the template below, replacing the placeholder values with your exact credentials:

```env
# 1. LOCAL FREE LLM REASONER
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:1.5b
OLLAMA_HOST=http://localhost:11434

# 2. GITHUB REPOSITORY INTEGRATION
GITHUB_TOKEN=ghp_YourGitHubTokenHere     # Paste your 40-character Developer PAT
GITHUB_REPO=meghalad2/AIOps-Dashboard     # GitHub username/repo

# 3. GMAIL SMTP ALERTING CONFIGURATION
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop           # The 16-character Google App Password (NO SPACES!)
SENDER_EMAIL=your-email@gmail.com
RECEIVER_EMAIL=your-email@gmail.com      # Target inbox
```

---

## 🏃‍♂️ 4. Database Seeding & Running the App Locally (Offline Mode)

We have built a fully featured offline demonstration system that doesn't require an active Kubernetes cluster to verify the dashboard and self-healing loop logic.

### Step 1: Seed the Database
Ensure your virtual environment is active, then run the database seeder to populate the SQLite database:
```bash
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
source venv/bin/activate
python ai-agent/seed_data.py
```
This generates 80 realistic incident logs and sets up baseline service health metrics.

### Step 2: Launch the Services
Open **three separate terminal windows** on your Mac. Run one process in each tab:

* **Terminal 1: Self-Healing Webhook Listener (Port 8000)**
  ```bash
  cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
  source venv/bin/activate
  python ai-agent/main.py
  ```

* **Terminal 2: Dashboard Backend API (Port 8001)**
  ```bash
  cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
  source venv/bin/activate
  python ai-agent/run_dashboard.py
  ```

* **Terminal 3: React Frontend Dashboard (Port 3000)**
  ```bash
  cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/dashboard
  npm install
  npm run dev
  ```

Once all three are running, open your web browser and navigate to **[http://localhost:3000](http://localhost:3000)** to view the live Aegis Control Plane.

---

## 🧪 5. Testing & Simulating the Self-Healing Flow

With all services active, send a mock Prometheus alert to see the dashboard react in real time:

1. Open a **new terminal window** on your Mac.
2. Send a simulated webhook alert:
   ```bash
   curl -X POST http://localhost:8000/alerts \
     -H "Content-Type: application/json" \
     -d '{
       "status": "firing",
       "alerts": [
         {
           "status": "firing",
           "labels": {
             "alertname": "PodCrashLooping",
             "severity": "critical",
             "action": "auto-heal",
             "namespace": "production",
             "pod": "payment-service-598ff-abcd",
             "container": "payment-service"
           },
           "annotations": {
             "summary": "Readiness probe failures on payment-service",
             "description": "Pod is in CrashLoopBackOff"
           }
         }
       ]
     }'
   ```
3. Watch the **Aegis Dashboard at `localhost:3000`**:
   * The new incident will immediately load into the **Incident Feed**.
   * A loading indicator will appear under **AI Reasoning Trace**.
   * The reasoning analysis, root cause, and remediation script will render once completed.
   * The **Service Health** score card for the service will adapt.
   * The **MTTR Trend Chart** will plot the new incident resolution metric.

---

## ☁️ 6. Deploying Real Infrastructure to AWS (Terraform)

Once you are satisfied with local testing and want to deploy the real-world cloud architecture onto AWS:

### Step A: Authenticate AWS CLI
Ensure AWS CLI is installed. Export your credentials directly in your active terminal session:
```bash
export AWS_ACCESS_KEY_ID="your_access_key_id_here"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
export AWS_DEFAULT_REGION="us-east-1"
```

Verify that AWS successfully recognizes you:
```bash
aws sts get-caller-identity
```

### Step B: Create the AWS SSH Key Pair
Run this command to create the key pair and securely store your private `.pem` key:
```bash
# Create the key pair in AWS and write to a local .pem file
aws ec2 create-key-pair \
  --key-name devops-key \
  --query 'KeyMaterial' \
  --output text \
  --region us-east-1 > /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/terraform/devops-key.pem

# Restrict file permissions for SSH client compliance
chmod 400 /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/terraform/devops-key.pem
```

### Step C: Initialize and Provision
```bash
# Navigate to Terraform folder
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/terraform

# Download providers
terraform init

# Validate configuration syntax
terraform validate

# Provision EKS, VPC, and Jenkins Server (takes ~15 minutes)
terraform apply -auto-approve
```

### Step D: Connect to Your New AWS EKS Cluster
Run this command to redirect your local `kubectl` to your newly created EKS cluster:
```bash
aws eks update-kubeconfig --region us-east-1 --name self-healing-cluster
```

### Step E: Deploy the Nginx Ingress Controller (Traffic Router)
We need an Ingress Controller (traffic load-balancer) in EKS to handle incoming web traffic:
```bash
# 1. Add the official ingress-nginx repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# 2. Install the controller into your cluster
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-nginx
```

### Step F: Deploy Prometheus, Grafana, and Alertmanager via Helm
```bash
# 1. Navigate to your project monitoring folder
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/monitoring

# 2. Add the official Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 3. Install the Prometheus Stack
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --create-namespace \
  --namespace production \
  -f values.yaml
```

### Step G: Deploy the Target microservices
Deploy the target applications that we want our SRE AI Agent to monitor and heal:
```bash
# 1. Navigate to the project root directory
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard

# 2. Deploy namespace, configmaps, secrets, and deployment manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
kubectl apply -f kubernetes/ingress.yaml
```

---

## 🧹 7. AWS Resource Cleanup (Teardown)

> [!WARNING]
> **Avoid Unwanted AWS Charges!** An active EKS Cluster, managed nodes, and EC2 Jenkins build servers run continuously and will incur active AWS hourly billing. Make sure to tear down all resources when you are finished.

We have provided an automated, safe, and robust teardown script located at:
📂 `scripts/destroy_all_resources.sh`

To clean up all cloud resources:
```bash
# Execute the complete automated cleanup
/bin/bash /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/scripts/destroy_all_resources.sh
```
*Wait about 10 minutes, and the terminal will print a success summary confirming that all AWS cloud charges have stopped!*
