import os
import json
import logging
import requests
from openai import OpenAI

logger = logging.getLogger("ai-agent")

class LLMReasoner:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.model = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
        
        # Initialize OpenAI if selected
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("LLM_PROVIDER is set to openai, but OPENAI_API_KEY is not defined.")
            self.openai_client = OpenAI(api_key=api_key)
            self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        self.system_prompt = (
            "You are a Senior Site Reliability Engineer (SRE) and AI Ops Specialist. "
            "You analyze production Kubernetes incidents, determine their root cause, "
            "and suggest safe, non-destructive automated remediation actions. "
            "You MUST output your response in EXACT JSON format with the following keys:\n"
            "{\n"
            '  "ROOT_CAUSE": "Detailed explanation of what failed and why.",\n'
            '  "SEVERITY": "HIGH, MEDIUM, or LOW.",\n'
            '  "REMEDIATION": "RESTART, SCALE, ROLLBACK, or DRAIN_NODE.",\n'
            '  "COMMAND": "The exact script execution command to run, e.g., scripts/restart_deployment.sh sre-ai-agent production or scripts/scale_deployment.sh sre-ai-agent production 3.",\n'
            '  "SUMMARY": "A concise 2-sentence summary of the incident and action taken."\n'
            "}\n\n"
            "Rules:\n"
            "1. ONLY output JSON. No markdown code blocks, no leading/trailing conversational text.\n"
            "2. Under 'COMMAND', you can only use scripts in the scripts/ folder: restart_deployment.sh <deployment_name> <namespace>, scale_deployment.sh <deployment_name> <namespace> <replicas>, or rollback_release.sh <deployment_name> <namespace>.\n"
            "3. Choose SCALE if there is memory/CPU exhaustion or resource pressure. Choose RESTART for pod crashing or deadlocks. Choose ROLLBACK if multiple restarts happen immediately after a new version release."
        )

    def analyze_incident(self, alert_name: str, pod_name: str, namespace: str, details: str, logs: str, events: str) -> dict:
        """
        Sends the compiled incident context to the LLM and parses the JSON action response.
        """
        prompt = (
            f"Alert: {alert_name}\n"
            f"Target Pod: {pod_name}\n"
            f"Namespace: {namespace}\n\n"
            f"--- Pod Details ---\n{details}\n\n"
            f"--- Pod Events ---\n{events}\n\n"
            f"--- Pod Logs ---\n{logs}\n\n"
            "Analyze the above incident and choose the best safe remediation path. Return the JSON object."
        )

        try:
            if self.provider == "openai":
                logger.info(f"Analyzing incident via OpenAI ({self.model})...")
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                raw_content = response.choices[0].message.content.strip()
            else:
                # Local Ollama setup
                logger.info(f"Analyzing incident via Local Ollama ({self.model})...")
                ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                response = requests.post(
                    f"{ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False,
                        "options": {"temperature": 0.1}
                    },
                    timeout=60
                )
                response.raise_for_status()
                raw_content = response.json().get("message", {}).get("content", "").strip()

            # Clean raw output if the LLM wrapped it in markdown code blocks
            if raw_content.startswith("```"):
                lines = raw_content.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_content = "\n".join(lines[1:-1]).strip()

            logger.info(f"LLM Raw Output: {raw_content}")
            return json.loads(raw_content)

        except Exception as e:
            logger.error(f"Error communicating with LLM Reasoner: {e}")
            # Safe default fallback action if LLM fails
            return {
                "ROOT_CAUSE": "Unknown - LLM reasoning failure.",
                "SEVERITY": "HIGH",
                "REMEDIATION": "RESTART",
                "COMMAND": f"scripts/restart_deployment.sh sre-ai-agent {namespace}",
                "SUMMARY": f"LLM failed to analyze the alert {alert_name}. Defaulting to deployment rolling restart."
            }
