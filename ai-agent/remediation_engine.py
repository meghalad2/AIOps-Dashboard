import subprocess
import logging
import os

logger = logging.getLogger("ai-agent")

class RemediationEngine:
    def __init__(self):
        # Allowed scripts to prevent security command injection
        self.allowed_scripts = [
            "scripts/restart_deployment.sh",
            "scripts/scale_deployment.sh",
            "scripts/rollback_release.sh",
            "scripts/drain_node.sh"
        ]

    def execute_fix(self, command_str: str) -> str:
        """
        Validates the command string and runs the remediation script.
        """
        logger.info(f"Remediation Request: {command_str}")
        
        parts = command_str.strip().split()
        if not parts:
            return "Error: Command string is empty."

        script = parts[0]
        args = parts[1:]

        # Validate that the script is within our safe pre-approved list
        if script not in self.allowed_scripts:
            logger.warning(f"Security Alert: Blocked execution of non-approved command '{command_str}'")
            return f"Error: Command '{script}' is not approved for execution."

        # Verify the script exists on disk
        if not os.path.exists(script):
            logger.error(f"Execution Error: Script '{script}' not found.")
            return f"Error: Remediation script '{script}' not found."

        try:
            logger.info(f"Running safe script: {script} with args: {args}")
            # Run bash script with argument list
            result = subprocess.run(
                ["/bin/bash", script] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=30
            )
            logger.info(f"Script stdout: {result.stdout}")
            return f"Success:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            logger.error(f"Remediation execution failed: {e.stderr}")
            return f"Failure (Exit Code {e.returncode}):\n{e.stderr}"
        except subprocess.TimeoutExpired:
            logger.error("Remediation execution timed out.")
            return "Failure: Execution timed out after 30 seconds."
        except Exception as e:
            logger.error(f"Unexpected execution error: {e}")
            return f"Failure: Unexpected error: {str(e)}"
