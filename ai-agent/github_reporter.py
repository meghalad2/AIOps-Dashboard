import os
import logging
import requests

logger = logging.getLogger("ai-agent")

class GitHubReporter:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO") # Format: "username/repo"
        
        if not self.github_token or not self.github_repo:
            logger.warning("GitHub credentials are not configured. Issue reporting will be skipped.")

    def create_incident_report(self, alert_name: str, pod_name: str, namespace: str, analysis: dict, execution_log: str) -> str:
        """
        Creates a structured incident issue in the target GitHub repository.
        """
        if not self.github_token or not self.github_repo:
            return "Skipped - GitHub configuration missing."

        url = f"https://api.github.com/repos/{self.github_repo}/issues"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        title = f"🚨 [INCIDENT-{analysis.get('SEVERITY', 'HIGH')}] {alert_name} in {namespace}/{pod_name}"
        
        body = (
            f"# Autonomous Self-Healing Incident Report\n\n"
            f"An incident alert was caught by Alertmanager and automatically analyzed by the **AI Ops SRE Agent**.\n\n"
            f"## Incident Summary\n"
            f"- **Alert Name**: `{alert_name}`\n"
            f"- **Target Pod**: `{pod_name}`\n"
            f"- **Namespace**: `{namespace}`\n"
            f"- **Severity**: `{analysis.get('SEVERITY', 'UNKNOWN')}`\n\n"
            f"## AI Diagnostic Root Cause Analysis\n"
            f"> {analysis.get('ROOT_CAUSE', 'No diagnostic root cause returned by LLM.')}\n\n"
            f"## Automated Healing Action Details\n"
            f"- **Suggested Action**: `{analysis.get('REMEDIATION', 'NONE')}`\n"
            f"- **Triggered Command**: `{analysis.get('COMMAND', 'None')}`\n\n"
            f"### Execution Logs\n"
            f"```text\n"
            f"{execution_log}\n"
            f"```\n\n"
            f"--- \n"
            f"*Report generated automatically by the AI Self-Healing Infrastructure Agent.*"
        )

        try:
            response = requests.post(url, headers=headers, json={"title": title, "body": body}, timeout=10)
            if response.status_code == 201:
                issue_url = response.json().get("html_url")
                logger.info(f"GitHub incident issue created successfully: {issue_url}")
                return issue_url
            else:
                logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
                return f"Error: Status code {response.status_code}"
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return f"Error: {str(e)}"
