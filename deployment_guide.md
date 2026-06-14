# 👶 Absolute Beginner's Step-by-Step Deployment Guide

Welcome! If you are a school student or new to coding, this guide is made **just for you**. You do not need any prior programming or network knowledge. By simply copying and pasting the commands in this guide into your Mac's **Terminal**, you will be able to launch the complete AI Ops platform!

---

## 📖 Table of Contents
1. [Mac Terminal Basics (Read This First!)](#1-mac-terminal-basics-read-this-first)
2. [Prerequisites & Account Configurations](#2-prerequisites--account-configurations)
3. [Installing the Tools (Step-by-Step)](#3-installing-the-tools-step-by-step)
4. [Setting Up Your Workspace & Virtual Environment](#4-setting-up-your-workspace--virtual-environment)
5. [Creating the Configuration File (No Editor Required!)](#5-creating-the-configuration-file-no-editor-required)
6. [Running the Platform Locally & Launching the Dashboard](#6-running-the-platform-locally--launching-the-dashboard)
7. [Simulating a Live Incident & Watching the AI Self-Heal](#7-simulating-a-live-incident--watching-the-ai-self-heal)
8. [Deploying Real Infrastructure to AWS Cloud (Optional)](#8-deploying-real-infrastructure-to-aws-cloud-optional)
9. [Teardown & Deleting AWS Resources (To Avoid Charges)](#9-teardown--deleting-aws-resources-to-avoid-charges)

---

## 🖥️ 1. Mac Terminal Basics (Read This First!)

To run commands, you need to use the **Terminal** app on your Mac:
1. Press **Command (⌘) + Spacebar** to open Spotlight Search.
2. Type `Terminal` and press **Enter**. A black or white window will open. This is where you will type/paste commands.
3. **How to run a command**: Copy a command from this guide, paste it into the Terminal window, and press **Enter** on your keyboard.
4. **Mac Password Prompts**: Some commands start with `sudo` (which means "Super User Do"). These will ask for your Mac's lock-screen password. 
   * **Important**: When you type your password, the cursor **will not move and no letters/stars will show**. This is a security feature. Just type your password anyway and press **Enter**.

---

## 🔑 2. Prerequisites & Account Configurations

Before we start, you will need to gather credentials from three places:

### A. AWS Account Access Keys (For Cloud Hosting)
1. Sign in to your [AWS Console](https://console.aws.amazon.com).
2. Type `IAM` in the top search bar and click on it.
3. Click **Users** on the left menu, then click **Create user** on the right.
4. Name it `sre-student-user` and click **Next**.
5. Choose **Attach policies directly**, check the box next to **`AdministratorAccess`**, and click **Next** > **Create user**.
6. Click on your newly created user name from the list, click the **Security credentials** tab.
7. Scroll down to **Access keys** and click **Create access key**.
8. Select **Command Line Interface (CLI)**, check the agreement box at the bottom, and click **Next** > **Create access key**.
9. **Copy both the Access Key ID and Secret Access Key** and save them in a text file. You will need them later!

### B. GitHub Personal Access Token (For AI Bug Logging)
1. Log in to [GitHub](https://github.com).
2. Click your profile icon (top right) > **Settings**.
3. Scroll to the bottom of the left menu and click **Developer settings**.
4. Click **Personal access tokens** > **Tokens (classic)**.
5. Click **Generate new token** > **Generate new token (classic)**.
6. Name it `aiops-token`, check the box next to **`repo`**, scroll to the bottom, and click **Generate token**.
7. **Copy the token code** (starts with `ghp_`) immediately and save it. It will disappear forever once you refresh the page.

### C. Gmail App Password (For Email SRE Reports)
1. Log in to your Google Account at [myaccount.google.com](https://myaccount.google.com).
2. Click **Security** on the left menu.
3. Make sure **2-Step Verification** is turned **ON**.
4. Search for `App passwords` in the top Google search bar and click on it.
5. Name it `AIOps Agent` and click **Create**.
6. Copy the **16-letter password** (remove all spaces, e.g. `abcdefghijklmnop`). This will be your SMTP password!

---

## 💻 3. Installing the Tools (Step-by-Step)

Copy and paste these commands one-by-one into your Terminal to install everything we need:

### Step 1: Install Homebrew (Mac Package Installer)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
*Note: Press Enter when prompted, and type your Mac password if asked (remember, it won't show characters on screen!).*

### Step 2: Add Homebrew to your Mac environment path
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### Step 3: Install all Developer Tools
```bash
brew install awscli hashicorp/tap/terraform kubernetes-cli helm python3 node ollama
```

### Step 4: Download and start Ollama (Local AI Engine)
1. Open the **Ollama app** from your Mac's Applications folder (or download it from [ollama.com](https://ollama.com) if it isn't opened).
2. Download the AI model by copy-pasting this command:
   ```bash
   ollama run qwen2.5-coder:1.5b
   ```
   *Keep this Terminal window open! The AI is now ready to reason.*

---

## 🐍 4. Setting Up Your Workspace & Virtual Environment

Open a **new Terminal window** (Command + N) and paste these commands:

```bash
# 1. Go to the project folder
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard

# 2. Create the Python virtual environment folder (venv)
python3 -m venv venv

# 3. Activate the environment
source venv/bin/activate

# 4. Install the backend libraries
pip install -r ai-agent/requirements.txt
```

---

## 📝 5. Creating the Configuration File (No Editor Required!)

Instead of opening an editor, you can write the config file directly from your terminal! 
Copy the block below, **replace the placeholders** with the credentials you gathered in **Section 2**, paste it into your Terminal, and press **Enter**:

```bash
cat << 'EOF' > /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/ai-agent/.env
# AI Ops Agent Configuration Settings

# 1. Local AI model details
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:1.5b
OLLAMA_HOST=http://localhost:11434

# 2. GitHub Token (Replace 'ghp_...' with your GitHub Token)
GITHUB_TOKEN=ghp_YourGitHubTokenHere
GITHUB_REPO=meghalad2/AIOps-Dashboard

# 3. SMTP Email Configuration (Replace with your email and App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SENDER_EMAIL=your-email@gmail.com
RECEIVER_EMAIL=your-email@gmail.com
EOF
```

---

## 🚀 6. Running the Platform Locally & Launching the Dashboard

Now we will start the 3 components that make up the Aegis dashboard. 

### Step 1: Seed the Database
Before running the dashboard, let's pre-load it with some historical simulator logs:
```bash
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
source venv/bin/activate
python ai-agent/seed_data.py
```
*(You will see "Seeded 80 incidents" print in the terminal!)*

### Step 2: Launch the 3 Servers
You need to open **three separate Terminal tabs** (use **Command + T** to open new tabs in the same window):

* **In Tab 1: Start the AI Webhook Agent (Handles alerts)**
  ```bash
  cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
  source venv/bin/activate
  python ai-agent/main.py
  ```

* **In Tab 2: Start the Dashboard API Webserver (Streams data)**
  ```bash
  cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
  source venv/bin/activate
  python ai-agent/run_dashboard.py
  ```

* **In Tab 3: Start the React Frontend Dashboard (Visual interface)**
  ```bash
  cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/dashboard
  npm install
  npm run dev
  ```

Now, open your web browser (Chrome, Safari, etc.) and type: **[http://localhost:3000](http://localhost:3000)**. 
*You should see a stunning dark-theme AIOps Control Plane populated with graphs and logs!*

---

## 🧪 7. Simulating a Live Incident & Watching the AI Self-Heal

Let's test the live self-healing flow:
1. Open a **new Terminal window/tab**.
2. Copy and paste the `curl` command below and hit **Enter**:
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
3. Immediately check your browser at **[http://localhost:3000](http://localhost:3000)**:
   * You will see the new incident appear instantly in the **Incident Feed**.
   * The **AI Reasoning Trace** will show a loader while diagnosing.
   * Once completed, it will show the root cause diagnostic and the remediation scripts triggered.
   * The **Service Health Card** for `payment-service` will change health scores.
   * The **MTTR Trend Chart** will plot the resolution speed.
   * Check your Gmail and GitHub! You will have received an HTML email report and a new bug issue ticket.

---

## ☁️ 8. Deploying Real Infrastructure to AWS Cloud (Optional)

If you want to host this on real cloud servers, do this:

### Step 1: Configure AWS CLI Credentials
Copy and paste this command, replacing with your keys from Section 2:
```bash
export AWS_ACCESS_KEY_ID="your_access_key_id_here"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
export AWS_DEFAULT_REGION="us-east-1"
```
Verify it works:
```bash
aws sts get-caller-identity
```

### Step 2: Create AWS SSH Key Pair
```bash
aws ec2 create-key-pair \
  --key-name devops-key \
  --query 'KeyMaterial' \
  --output text \
  --region us-east-1 > /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/terraform/devops-key.pem

chmod 400 /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/terraform/devops-key.pem
```

### Step 3: Deploy EKS and EC2 Jenkins
```bash
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/terraform
terraform init
terraform validate
terraform apply -auto-approve
```
*(Wait 15 minutes for the AWS cloud servers to spin up!)*

### Step 4: Configure Cluster Access & Install Helm Packages
```bash
# Redirect kubectl to AWS
aws eks update-kubeconfig --region us-east-1 --name self-healing-cluster

# Install Ingress Load Balancer
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx --create-namespace --namespace ingress-nginx

# Install Prometheus Monitor stack
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-stack prometheus-community/kube-prometheus-stack --create-namespace --namespace production -f values.yaml

# Deploy microservices
cd /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
kubectl apply -f kubernetes/ingress.yaml
```

---

## 🧹 9. Teardown & Deleting AWS Resources (To Avoid Charges)

> [!WARNING]
> **Don't Forget This Step!** AWS EKS clusters and EC2 nodes will charge you by the hour. When you are done playing with your project, make sure to delete them to keep your AWS account completely free of charges!

To delete all EKS and VPC cloud servers automatically, paste this command:
```bash
/bin/bash /Users/mymtg/Downloads/AP-PRJ-2-3/AIOps-Dashboard/scripts/destroy_all_resources.sh
```
*(Wait about 10 minutes, and the terminal will confirm that all resources are deleted and billing has stopped!)*
