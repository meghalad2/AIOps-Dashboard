# Complete End-to-End Project Deployment & Run Guide

Welcome to the master deployment guide for the **AI-Powered Self-Healing Kubernetes Infrastructure** project. This document provides a complete, step-by-step manual from absolute start to finish, including direct installations for every single tool and CLI dependency.

---

## 📌 Table of Contents
1. [Prerequisites & Accounts Setup](#1-prerequisites--accounts-setup)
2. [CLI Tools Installation Guide (Macbook Air)](#2-cli-tools-installation-guide-macbook-air)
3. [Writing the Project Configuration (`.env`)](#3-writing-the-project-configuration-env)
4. [Running the AI Agent Locally (Offline/Mock Mode)](#4-running-the-ai-agent-locally-offlinemock-mode)
5. [Testing & Simulating the Self-Healing Flow](#5-testing--simulating-the-self-healing-flow)
6. [Deploying Real Infrastructure to AWS (Terraform)](#6-deploying-real-infrastructure-to-aws-terraform)

---

## 🔑 1. Prerequisites & Accounts Setup

Before writing any configuration files, you must gather your access credentials from four sources:

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
8. Click **Generate token at the bottom of the page.**
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

### METHOD A: Direct Native Installers (Recommended & Most Robust)
If Homebrew prompts for a `sudo` password or fails, use these direct, native installer commands. Open your terminal and copy-paste these blocks:

#### 1. Install AWS CLI (Official Amazon Installer)
This installs the official AWS command-line tools onto your Mac directly:
```bash
# Download official macOS AWS CLI installerpkg
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

# Install package (Requires entering your Mac password in the terminal)
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation (This should now print the aws cli version!)
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
brew install awscli hashicorp/tap/terraform kubernetes-cli helm python3 ollama
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
cd /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s

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
📂 `/Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/ai-agent/.env`

Paste the template below, replacing the placeholder values with your exact credentials:

```env
# 1. LOCAL FREE LLM REASONER
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:1.5b
OLLAMA_HOST=http://localhost:11434

# 2. GITHUB REPOSITORY INTEGRATION
GITHUB_TOKEN=ghp_YourGitHubTokenHere     # Paste your 40-character Developer PAT
GITHUB_REPO=your_username/your_repo      # GitHub username/repo (e.g. "mymtg/my-portfolio")

# 3. GMAIL SMTP ALERTING CONFIGURATION
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop           # The 16-character Google App Password (NO SPACES!)
SENDER_EMAIL=your-email@gmail.com
RECEIVER_EMAIL=your-email@gmail.com      # Target inbox
```

---

## 🏃‍♂️ 4. Running the AI Agent Locally (Offline/Mock Mode)

The codebase has been engineered with a built-in **Offline Mock Mode**. If you don't have an active AWS EKS cluster running yet, the SRE Agent will automatically detect this, boot up cleanly, and generate highly realistic simulated pod logs and events for testing!

1. Make sure your virtual environment is active:
   ```bash
   source venv/bin/activate
   ```
2. Launch the SRE FastAPI Webhook Server:
   ```bash
   python3 ai-agent/main.py
   ```

---

## 🧪 5. Testing & Simulating the Self-Healing Flow

With the SRE Agent running on port `8000`, trigger a simulated incident to watch the autonomous healing loop perform diagnostics:

1. Open a **new terminal window** on your Mac.
2. Fire a simulated `PodCrashLooping` alert payload to the webhook endpoint using `curl`:
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
             "pod": "sre-ai-agent-589ff9f75b-abcd",
             "container": "sre-ai-agent"
           },
           "annotations": {
             "summary": "Pod is in CrashLoopBackOff",
             "description": "Sre-ai-agent is failing readiness checks and restarting repeatedly."
           }
         }
       ]
     }'
   ```
3. Watch the terminal logs where `main.py` is running, then check your email inbox and GitHub repository!

---

## ☁️ 6. Deploying Real Infrastructure to AWS (Terraform)

Once you are satisfied with local testing and want to deploy the real-world cloud architecture onto AWS:

### Step A: Authenticate AWS CLI
Ensure AWS CLI is installed using Step 2 above. 

**Recommended (Direct Exports)**: To prevent signature matching errors, export your credentials directly as environment variables in your active terminal session:
```bash
export AWS_ACCESS_KEY_ID="your_access_key_id_here"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
export AWS_DEFAULT_REGION="us-east-1"
```

**Verify the credentials**:
Run this command to check if AWS successfully recognizes you:
```bash
aws sts get-caller-identity
```

*(Alternatively, you can run the interactive config command: `aws configure`)*

### Step A.5: Create the AWS SSH Key Pair (.pem)
Before creating resources, you must provision an SSH Key Pair named `devops-key` in AWS EKS's region (`us-east-1`). This permits secure console access to the Jenkins EC2 instance.

Run this command to create the key pair and securely store your private `.pem` key:
```bash
# Create the key pair in AWS and write to a local .pem file
aws ec2 create-key-pair \
  --key-name devops-key \
  --query 'KeyMaterial' \
  --output text \
  --region us-east-1 > /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/terraform/devops-key.pem

# Restrict file permissions for SSH client compliance
chmod 400 /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/terraform/devops-key.pem
```

### Step B: Initialize and Provision
```bash
# Navigate to Terraform folder
cd /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/terraform

# Download providers
terraform init

# Validate configuration syntax
terraform validate

# Provision EKS, VPC, and Jenkins Server (takes ~15 minutes)
terraform apply -auto-approve
```

### Step C: Connect to Your New AWS EKS Cluster
Once Terraform completes successfully, run this command to redirect your local `kubectl` to your newly created EKS cluster:
```bash
aws eks update-kubeconfig --region us-east-1 --name self-healing-cluster
```

### Step C.1: Deploy the Nginx Ingress Controller (Traffic Router)
We need an Ingress Controller (traffic load-balancer) in EKS to handle incoming web traffic. We use **Helm** to install it:
```bash
# 1. Add the official ingress-nginx repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# 2. Install the controller into your cluster
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-nginx
```

> [!TIP]
> **Troubleshooting pending releases**: If your installation ever hangs or gets canceled midway (throwing `cannot reuse a name that is still in use`), clean up the corrupted release and rerun:
> ```bash
> helm uninstall ingress-nginx -n ingress-nginx
> helm install ingress-nginx ingress-nginx/ingress-nginx --create-namespace --namespace ingress-nginx
> ```

### Step C.2: Deploy Prometheus, Grafana, and Alertmanager via Helm
We will install the complete monitoring stack using our custom routing values, which tells Alertmanager to forward incidents to our AI webhook!
```bash
# 1. Navigate to your project monitoring folder
cd /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/monitoring

# 2. Add the official Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 3. Install the Prometheus Stack (this automatically creates the "production" namespace!)
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --create-namespace \
  --namespace production \
  -f values.yaml
```

### Step C.3: Deploy the Target billing app (`sre-ai-agent`)
Deploy the target billing app that we want our SRE AI Agent to monitor and heal:
```bash
# 1. Navigate to the project root directory
cd /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s

# 2. Deploy namespace, configmaps, secrets, and deployment manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
kubectl apply -f kubernetes/ingress.yaml
```


### Step D: Boot Your Production-Connected AI Agent
Run the agent again:
```bash
cd /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s
source venv/bin/activate
python3 ai-agent/main.py
```

---

### Step E: Exposing Dashboards & Visualizing EKS Health (Grafana, Prometheus & Alertmanager)
> [!NOTE]
> **No accounts or fees required!** You do **NOT** need to create any account or subscription on the Prometheus or Grafana websites. The entire monitoring suite is installed **inside your own private Kubernetes cluster**, meaning it runs completely on your own cloud servers for free.

To access your dashboards, use `kubectl port-forward` to map the cluster services to your Mac's web browser:

#### 1. Open the Grafana Dashboard (Cluster Health Metrics)
Grafana contains pre-built, premium SRE graphs showing EKS CPU, memory load, and pod container status in real-time.
- **Run the port-forward command**:
  ```bash
  kubectl port-forward svc/prometheus-stack-grafana 3000:80 -n production
  ```
- **Open in your browser**: Go to **[http://localhost:3000](http://localhost:3000)**
- **Login Credentials**:
  * **Username**: `admin`
  * **Password**: `admin`
- **View EKS Health Graphs**:
  1. Click **Dashboards** on the left menu.
  2. Open the **"Kubernetes"** folder.
  3. Select **"Kubernetes / Compute Resources / Namespace (Pods)"** or **"Node Exporter"** to see stunning real-time CPU, RAM, and network graphs!

#### 2. Open the Alertmanager Dashboard (Active Firing Alerts)
Alertmanager manages which alerts (like pod crashes or high memory usage) are active and maps their routing to your AI agent.
- **Run the port-forward command**:
  ```bash
  kubectl port-forward svc/prometheus-stack-kube-prom-alertmanager 9093:9093 -n production
  ```
- **Open in your browser**: Go to **[http://localhost:9093](http://localhost:9093)**

#### 3. Open the Prometheus Dashboard (Raw Metrics & Alarm Equations)
Prometheus is the database collecting all cluster metrics and running alerting rules.
- **Run the port-forward command**:
  ```bash
  kubectl port-forward svc/prometheus-stack-kube-prom-prometheus 9090:9090 -n production
  ```
- **Open in your browser**: Go to **[http://localhost:9090](http://localhost:9090)**

---

## 🧹 7. Complete AWS Resource Cleanup (Tearing Down Everything)

> [!WARNING]
> **Avoid Unwanted AWS Charges!** An active EKS Cluster, managed nodes, and EC2 Jenkins build servers run continuously and will incur active AWS hourly billing. Make sure to tear down all resources when you are finished presenting your project portfolio.

I have created a fully automated, safe, and robust teardown script located at:
📂 `scripts/destroy_all_resources.sh`

### How the automated cleanup script works:
1. **Uninstall Helm Releases**: Uninstalls Ingress and Prometheus first. This is critical because Helm controllers automatically spin up AWS **Elastic Load Balancers (ELBs)** inside AWS. If we don't delete them first, the VPC subnets will stay locked by AWS, causing `terraform destroy` to fail or hang!
2. **Deletes Namespaces**: Cleans up all EKS Kubernetes workspaces.
3. **Terraform Destroy**: Completely deletes EKS, Managed Node Groups, VPC networking, security groups, and EC2.
4. **Deletes Key Pairs**: Automatically removes the `devops-key` key pair from your AWS EC2 Console and cleans up the local `.pem` key.

### How to run the cleanup script:
Open your Mac's terminal and run this single command:
```bash
# Execute the complete automated cleanup
/bin/bash /Users/mymtg/.gemini/antigravity-ide/scratch/ai-self-healing-k8s/scripts/destroy_all_resources.sh
```
*Wait about 10 minutes, and the terminal will print a success summary confirming that all AWS cloud charges have stopped!*

### 🔎 Post-Cleanup Audit: Verification Commands
To double-check and guarantee that no active billing assets remain in your AWS account, run these validation commands in your terminal:

```bash
# 1. Verify EKS Cluster is completely deleted
# (Expectation: Should return {"clusters": []})
aws eks list-clusters --region us-east-1

# 2. Verify all EC2 instances and their current states
# (Expectation: Should list zero instances or show "terminated" for all)
aws ec2 describe-instances \
  --region us-east-1 \
  --query "Reservations[*].Instances[*].{ID:InstanceId,State:State.Name,Name:Tags[?Key=='Name']|[0].Value}" \
  --output table

# 3. Verify active Key Pairs in the region
# (Expectation: 'devops-key' should NOT appear in this list)
aws ec2 describe-key-pairs --region us-east-1 --query "KeyPairs[*].KeyName" --output table

# 4. Verify all active VPCs
# (Expectation: 'self-healing-vpc' should NOT appear in this list)
aws ec2 describe-vpcs --region us-east-1 --query "Vpcs[*].{VpcId:VpcId,Name:Tags[?Key=='Name']|[0].Value,IsDefault:IsDefault}" --output table
```



