# Autonomous AI-Powered Self-Healing Kubernetes Infrastructure

This repository contains the complete end-to-end codebase for an autonomous **AI Ops (Artificial Intelligence for IT Operations) Platform** that runs on AWS EKS. It automatically detects production incidents, utilizes a local **Ollama AI Agent** (or cloud OpenAI) to run diagnostic root-cause analyses on logs/events, and executes secure automated remediation scripts (restarting, scaling, or rolling back pods), notifying the platform team via **real-time email alerts** and **GitHub issues**.

---

## 🏗️ High-Level System Architecture

```text
               +-----------------------+
               |  Kubernetes Pods      | (Failing or resource stressed)
               +-----------+-----------+
                           |
                           v (Scrapes metrics)
               +-----------+-----------+
               |  Prometheus Server    | (Triggers alert rules)
               +-----------+-----------+
                           |
                           v
               +-----------+-----------+
               |  Alertmanager         | (Dispatches webhook alert)
               +-----------+-----------+
                           |
                           v
               +-----------+-----------+
               |  AI Webhook Agent     | (Fetches logs, pod specs, events)
               +-----------+-----------+
                           |
                           +-------------------------------+
                           |                               |
                           v (SRE reasoning prompt)        v (Runs verified bash script)
               +-----------+-----------+       +-----------+-----------+
               | Local Ollama / OpenAI |       | Remediation Scripts   |
               +-----------+-----------+       +-----------+-----------+
                           |                               |
                           +---------------+---------------+
                                           | (Reports results)
                                           v
               +---------------------------+---------------------------+
               |   📧 Email Notification    |   🐙 GitHub Issue Log     |
               +---------------------------+---------------------------+
```

---

## 📂 Repository Directory Layout

```text
ai-self-healing-k8s/
├── README.md
├── Jenkinsfile                  # CI/CD Declarative pipeline configuration
├── terraform/                   # Infrastructure as Code
│   ├── provider.tf
│   ├── vpc.tf
│   ├── iam.tf
│   ├── eks.tf
│   ├── jenkins.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
├── kubernetes/                  # Kubernetes Manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── ingress.yaml
├── monitoring/                  # Prometheus Stack values & configs
│   ├── values.yaml
│   ├── alertmanager-config.yaml
│   └── prometheus-rules.yaml
├── ai-agent/                    # AI SRE reasoning agent webhook server
│   ├── requirements.txt
│   ├── main.py
│   ├── alert_listener.py
│   ├── kubernetes_client.py
│   ├── llm_reasoner.py
│   ├── remediation_engine.py
│   ├── github_reporter.py
│   └── email_notifier.py
└── scripts/                     # Approved remediation commands
    ├── restart_deployment.sh
    ├── scale_deployment.sh
    ├── rollback_release.sh
    └── drain_node.sh
```

---

## 🛠️ Prerequisites & Local Setup (MacBook Air)

### 1. Install CLI Tooling
Make sure Homebrew is installed, then run:
```bash
brew install awscli hashicorp/tap/terraform kubernetes-cli helm python3 ollama
```

### 2. Local free LLM Setup (Ollama)
Start the local Ollama background service and download the coding-optimized reasoning model:
```bash
brew services start ollama
ollama run qwen2.5-coder:7b
```
*(For machines with less than 16GB of RAM, use `qwen2.5-coder:1.5b` for lighter, faster inference).*

### 3. Email (Gmail App Password) Setup
To send automated HTML reports to your inbox:
1. Go to `myaccount.google.com` > **Security**.
2. Turn **2-Step Verification** ON.
3. Search for **App passwords**, create one named `K8s AI Agent`, and copy the 16-character code.

### 4. GitHub Developer Token Setup
To allow the agent to log incidents automatically:
1. Go to `github.com` Settings > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2. Click **Generate token**, choose the `repo` scope, and save the token safely.

---

## 🚀 Running the AI Agent Locally

1. **Clone and enter the directory**:
   ```bash
   cd ai-self-healing-k8s
   ```
2. **Create and activate Python Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r ai-agent/requirements.txt
   ```
3. **Configure Environment Variables** (`.env`):
   Create a `.env` file inside the `ai-agent/` directory:
   ```env
   LLM_PROVIDER=ollama
   LLM_MODEL=qwen2.5-coder:7b
   OLLAMA_HOST=http://localhost:11434

   # GitHub settings
   GITHUB_TOKEN=your_github_token_here
   GITHUB_REPO=your_username/your_repo_name

   # SMTP settings (Gmail Example)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SENDER_EMAIL=your-email@gmail.com
   RECEIVER_EMAIL=your-email@gmail.com
   ```
4. **Launch the FastAPI Server**:
   ```bash
   python3 ai-agent/main.py
   ```
   The agent will boot up and listen for Alertmanager webhooks on `http://localhost:8000/alerts`.

---

## 🧪 Simulating an Incident & Self-Healing Demo

### 1. Bootstrap Target Pods
Deploy the sample microservice to your local/EKS cluster:
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/deployment.yaml
```

### 2. Trigger Mock Webhook Alert
To simulate Prometheus detecting a high-memory/crashloop incident on our target pod, send a POST webhook request:
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

### 3. Observe the Magic!
Watch your terminal logs as the AI Agent:
1. **Parses the Alert**: Identifies pod name and namespace.
2. **Collects Context**: Fetches logs and event statuses automatically.
3. **AI Diagnostic Reasoner**: Analyzes the log output via Ollama, determines the root cause, and returns a remediation command.
4. **Executes safe fix**: Runs `scripts/restart_deployment.sh sre-ai-agent production`.
5. **Creates GitHub Issue**: Automatically creates a beautifully structured incident ticket.
6. **Sends HTML Email**: Delivers a styled SRE notification report to your Gmail inbox.
