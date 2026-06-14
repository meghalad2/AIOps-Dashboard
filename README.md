# Aegis AIOps Control Plane & Dashboard

This repository contains the complete codebase for **Aegis AIOps Control Plane & Dashboard**, an autonomous self-healing Kubernetes operations platform. It integrates a secure, AI-powered diagnostic/remediation backend with a modern React-based observability dashboard.

Aegis automatically intercepts container incidents (like crashloops and resource pressure), fetches runtime pod telemetry, diagnoses root causes using a local **Ollama AI Agent** (or cloud OpenAI), executes verified bash-based remediation scripts, and streams real-time updates directly to a glassmorphic web control plane via WebSockets.

---

## 🏗️ System Architecture Flow

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │               PHASE A: INFRASTRUCTURE & DEPLOYMENT SETUP               │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
        ┌──────────────────┐   Terraform   ┌──────────────────────────┐
        │   Mac / CLI      ├──────────────►│   AWS Cloud Environment  │
        │   Workspace      │    Deploy     │   (VPC Network, EC2)     │
        └──────────────────┘               └────────────┬─────────────┘
                                                        │
                                                        ▼
                                           ┌──────────────────────────┐
                                           │   AWS EKS Cluster        │
                                           │   (Kubernetes Nodes)     │
                                           └────────────┬─────────────┘
                                                        │
 ┌──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────┐
 │            PHASE B: OPERATIONS                       │             PHASE C: AUTONOMOUS SRE & DASHBOARD      │
 └──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
                                           ┌──────────────────────────┐
                                           │  sre-ai-agent Pod        │
                                           └────────────┬─────────────┘
                                                        │
                                                        ▼  [POD CRASHES!]
                                           ┌──────────────────────────┐
                                           │  Prometheus Database     │
                                           └────────────┬─────────────┘
                                                        │
                                                        ▼  [Fires Alarm]
                                           ┌──────────────────────────┐
                                           │  Alertmanager Webhook    │
                                           └────────────┬─────────────┘
                                                        │
                                                        ▼  [POST Webhook Payload]
  ┌───────────────────────┐  Fetch Specs  ┌──────────────────────────┐  Run Secure  ┌───────────────────────┐
  │  Kubernetes API       │◄──────────────┤     FastAPI AI Agent     ├─────────────►│  Remediation Engine   │
  │  Client               │  Logs/Events  │     Webhook Server       │  Execution   │  (Safe Bash Whitelist)│
  └───────────────────────┘               └────────────┬─────────────┘              └───────────┬───────────┘
                                                       │                                        │
                                                       ├────────────────────────┐               │ [rollout restart]
                                                       ▼  [SRE Prompts]         │ [Events]      ▼
                                          ┌──────────────────────────┐          │           ┌───────────────────────┐
                                          │  Ollama / OpenAI         │          │           │   sre-ai-agent        │
                                          │  (qwen2.5-coder LLM)     │          │           │   is healed!          │
                                          └────────────┬─────────────┘          │           └───────────────────────┘
                                                       │                        ▼
                                                       ▼ [Auto Logs]        ┌──────────────────────────┐
                                      ┌──────────────────────────────────┐  │ SQLite DB & Event Bus    │
                                      │ GitHub Issues & Gmail SMTP Email │  │ (Local pub/sub model)    │
                                      └──────────────────────────────────┘  └───────────┬──────────────┘
                                                                                        │ [WebSocket / REST]
                                                                                        ▼
                                                                            ┌──────────────────────────┐
                                                                            │ React Vite Dashboard     │
                                                                            │ (AIOps Control Plane)    │
                                                                            └──────────────────────────┘
```

---

## 📂 Directory Structure

```text
AIOps-Dashboard/
├── README.md
├── Jenkinsfile                  # CI/CD declarative pipeline configuration
├── project_architecture_and_definitions.md
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
├── ai-agent/                    # AI SRE reasoning agent webhook server & database
│   ├── requirements.txt
│   ├── main.py                  # Self-healing webhook listener
│   ├── event_bus.py             # Pub/Sub broker & SQLite DB client
│   ├── models.py                # SQLAlchemy DB schema
│   ├── database.py              # SQLite session configurations
│   ├── dashboard_api.py         # FastAPI REST & WebSocket server
│   ├── run_dashboard.py         # Server bootstrapper on port 8001
│   ├── seed_data.py             # Seeding script for demonstration
│   ├── alert_listener.py
│   ├── kubernetes_client.py
│   ├── llm_reasoner.py
│   ├── remediation_engine.py
│   ├── github_reporter.py
│   └── email_notifier.py
├── dashboard/                   # React + Vite Observability Frontend
│   ├── vite.config.js           # Proxies API & WebSockets to backend
│   ├── package.json
│   └── src/
│       ├── App.jsx              # Dashboard root and WebSocket binder
│       ├── App.css              # Cyber-ops glassmorphic styling
│       ├── hooks/
│       │   └── useWebSocket.js  # Real-time WebSocket hook
│       └── components/
│           ├── IncidentFeed.jsx
│           ├── ReasoningTrace.jsx
│           ├── MttrChart.jsx
│           ├── ServiceHeatmap.jsx
│           └── RemediationTrigger.jsx
└── scripts/                     # Approved remediation commands
    ├── restart_deployment.sh
    ├── scale_deployment.sh
    ├── rollback_release.sh
    └── drain_node.sh
```

---

## 🛠️ Prerequisites & Local Setup

### 1. Install CLI Tooling
Ensure you have Homebrew installed on macOS, then install Node.js, Python, Terraform, Helm, Kubernetes CLI, and Ollama:
```bash
brew install awscli hashicorp/tap/terraform kubernetes-cli helm python3 node ollama
```

### 2. Private Local LLM Setup (Ollama)
Start the local Ollama background service and download the reasoning model:
```bash
brew services start ollama
ollama run qwen2.5-coder:7b
```

### 3. SMTP & GitHub Developer Tokens
Ensure you configure your Gmail app password and a GitHub classic personal access token inside `.env` inside the `ai-agent/` directory:
```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:7b
OLLAMA_HOST=http://localhost:11434

# GitHub settings
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_username/AIOps-Dashboard

# SMTP settings (Gmail Example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
RECEIVER_EMAIL=your-email@gmail.com
```

---

## 🚀 Running the Stack

To run the complete platform locally, open three separate terminal sessions in this directory:

### Terminal 1: Self-Healing Webhook Listener
```bash
source venv/bin/activate
python ai-agent/main.py
# Webhook server will start on port 8000
```

### Terminal 2: Dashboard REST & WebSocket API
```bash
source venv/bin/activate
python ai-agent/run_dashboard.py
# Dashboard backend server will start on port 8001
```

### Terminal 3: React Dashboard Developer Server
```bash
cd dashboard
npm install
npm run dev
# Dashboard frontend opens on http://localhost:3000
```

---

## 🧪 Seeding & Simulation

### 1. Database Seeding
To populate the dashboard with 60 days of historical operational logs and charts on first launch:
```bash
source venv/bin/activate
python ai-agent/seed_data.py
```

### 2. Simulating a Live Pod Incident
Send a mock Prometheus alert to the agent webhook and watch the dashboard update in real-time:
```bash
curl -X POST http://localhost:8000/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "status": "firing",
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "PodCrashLooping",
        "severity": "critical",
        "action": "auto-heal",
        "namespace": "production",
        "pod": "payment-service-7d9f-xk2pq",
        "container": "payment-service"
      },
      "annotations": {
        "summary": "Readiness probe failures on payment-service",
        "description": "Pod is in CrashLoopBackOff"
      }
    }]
  }'
```

* **Live Action Trace**:
  * An incident is pushed instantly into the **Incident Feed**.
  * The **AI Reasoning Trace** displays diagnostic loading animations.
  * Once diagnosis is ready, Ollama's root cause analysis and the remediation command are shown.
  * The **Service Health score** adapts to the new failure metrics.
  * The **MTTR Trend Chart** plots the new recovery time.
