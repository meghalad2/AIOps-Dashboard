import os
import logging
from fastapi import FastAPI, Request, BackgroundTasks, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load local .env files if present
load_dotenv()

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai-agent")

# Import modular SRE blocks
from alert_listener import parse_alertmanager_payload
from kubernetes_client import K8sClient
from llm_reasoner import LLMReasoner
from remediation_engine import RemediationEngine
from github_reporter import GitHubReporter
from email_notifier import EmailNotifier

app = FastAPI(
    title="Kubernetes AI Self-Healing Agent API",
    description="FastAPI Webhook for Alertmanager incident routing, automated LLM diagnostic, and secure remediation.",
    version="1.0.0"
)

# Initialize engines
k8s_client = K8sClient()
llm_reasoner = LLMReasoner()
remediation_engine = RemediationEngine()
github_reporter = GitHubReporter()
email_notifier = EmailNotifier()

import event_bus

async def process_remediation_loop(alert_info):
    """
    Asynchronous self-healing pipeline loop.
    Gathers cluster diagnostics, feeds to LLM, runs fix, and notifies SRE team.
    """
    logger.info(f"Kicking off automated remediation for {alert_info.name} on Pod {alert_info.pod}")
    
    # Emit incident fired event
    sre_prompt = (
        f"Alert: {alert_info.name}\n"
        f"Target Pod: {alert_info.pod}\n"
        f"Namespace: {alert_info.namespace}\n"
        f"Container: {alert_info.container}"
    )
    
    incident_id = await event_bus.emit_incident_fired(
        alert_name=alert_info.name,
        severity=alert_info.severity,
        namespace=alert_info.namespace,
        pod=alert_info.pod or "unknown",
        llm_prompt=sre_prompt
    )
    
    # 1. Fetch Pod Diagnostics
    pod_logs = k8s_client.get_pod_logs(alert_info.pod, alert_info.namespace, alert_info.container)
    pod_events = k8s_client.get_pod_events(alert_info.pod, alert_info.namespace)
    pod_details = k8s_client.get_pod_details(alert_info.pod, alert_info.namespace)
    
    # 2. Analyze using AI Ops SRE LLM Reasoner
    analysis = llm_reasoner.analyze_incident(
        alert_name=alert_info.name,
        pod_name=alert_info.pod,
        namespace=alert_info.namespace,
        details=pod_details,
        logs=pod_logs,
        events=pod_events
    )
    
    # Emit LLM reasoning event
    llm_output = analysis.get("ROOT_CAUSE", "No root cause analysis found.") + "\n\n" + analysis.get("SUMMARY", "")
    chosen_script = analysis.get("COMMAND")
    await event_bus.emit_llm_reasoning(
        incident_id=incident_id,
        llm_output=llm_output,
        remediation_command=chosen_script or "None"
    )
    
    # 3. Execute Automated Remediation Script
    command = analysis.get("COMMAND")
    if command:
        logger.info(f"Executing AI selected action: '{command}'")
        execution_log = remediation_engine.execute_fix(command)
    else:
        logger.warning("No command returned by the AI agent. Remediation skipped.")
        execution_log = "Skipped - No remediation command suggested by AI SRE agent."

    # Determine status & emit remediation result
    remediation_outcome = "success" if execution_log.startswith("Success:") else "failure"
    await event_bus.emit_remediation_result(
        incident_id=incident_id,
        result=remediation_outcome
    )
    
    # 4. Create Incident Log on GitHub
    github_url = github_reporter.create_incident_report(
        alert_name=alert_info.name,
        pod_name=alert_info.pod,
        namespace=alert_info.namespace,
        analysis=analysis,
        execution_log=execution_log
    )
    
    # 5. Email Notification
    email_notifier.send_incident_email(
        alert_name=alert_info.name,
        pod_name=alert_info.pod,
        namespace=alert_info.namespace,
        analysis=analysis,
        execution_log=f"{execution_log}\n\nGitHub Issue: {github_url}"
    )
    
    logger.info(f"Automated remediation pipeline completed for {alert_info.pod}.")


@app.post("/alerts", status_code=status.HTTP_202_ACCEPTED)
async def alertmanager_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint exposed to Prometheus Alertmanager.
    Alerts are validated and processed in the background.
    """
    try:
        payload = await request.json()
        active_alerts = parse_alertmanager_payload(payload)
        
        if not active_alerts:
            return JSONResponse(
                content={"message": "No active 'auto-heal' alerts found in payload. Skipping processing."},
                status_code=status.HTTP_200_OK
            )
            
        for alert in active_alerts:
            # Dispatch remediation loop asynchronously
            background_tasks.add_task(process_remediation_loop, alert)
            
        return {"status": "accepted", "message": f"Processing {len(active_alerts)} healing tasks in background."}
        
    except Exception as e:
        logger.error(f"Error handling incoming webhook: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.get("/health")
def liveness_check():
    return {"status": "healthy", "service": "kubernetes-ai-remediator"}

if __name__ == "__main__":
    import uvicorn
    # Start webserver on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
