import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("ai-agent")

class EmailNotifier:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "1025"))
        self.smtp_user = os.getenv("SMTP_USERNAME", "")
        self.smtp_pass = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SENDER_EMAIL", "agent@selfhealing.local")
        self.receiver_email = os.getenv("RECEIVER_EMAIL", "")

        if not self.receiver_email:
            logger.warning("RECEIVER_EMAIL environment variable is missing. Email notifications will be skipped.")

    def send_incident_email(self, alert_name: str, pod_name: str, namespace: str, analysis: dict, execution_log: str):
        """
        Sends a rich incident notification email.
        """
        if not self.receiver_email:
            logger.info("Skipping email notification: receiver email is not set.")
            return False

        subject = f"🚨 [K8s AI-Remediation] {analysis.get('SEVERITY', 'HIGH')} Severity: {alert_name} in {namespace}/{pod_name}"
        
        # Build clean HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #d9534f; border-bottom: 2px solid #d9534f; padding-bottom: 10px;">
                    AI Ops Self-Healing Incident Report
                </h2>
                <p>An active Kubernetes production incident was intercepted and successfully resolved by the AI SRE Agent.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f9f9f9;">
                        <td style="padding: 8px; font-weight: bold; border: 1px solid #ddd;">Alert Name:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{alert_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; border: 1px solid #ddd;">Target Pod:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{pod_name}</td>
                    </tr>
                    <tr style="background-color: #f9f9f9;">
                        <td style="padding: 8px; font-weight: bold; border: 1px solid #ddd;">Namespace:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{namespace}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; border: 1px solid #ddd;">Severity:</td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #d9534f; font-weight: bold;">
                            {analysis.get('SEVERITY', 'HIGH')}
                        </td>
                    </tr>
                </table>
                
                <h3>Diagnostic Root Cause Analysis</h3>
                <blockquote style="background-color: #f5f5f5; border-left: 5px solid #ccc; margin: 1.5em 10px; padding: 0.5em 10px;">
                    {analysis.get('ROOT_CAUSE', 'No diagnostic root cause details.')}
                </blockquote>
                
                <h3>Remediation Executed</h3>
                <ul>
                    <li><strong>Action:</strong> {analysis.get('REMEDIATION', 'NONE')}</li>
                    <li><strong>Script Command:</strong> <code>{analysis.get('COMMAND', 'None')}</code></li>
                </ul>
                
                <h3>Execution Log Summary</h3>
                <pre style="background: #272822; color: #f8f8f2; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 13px;">
{execution_log}
                </pre>
                
                <footer style="margin-top: 30px; font-size: 11px; color: #777; border-top: 1px solid #eee; padding-top: 10px;">
                    This is an automated system message. Do not reply directly.
                </footer>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email
        msg.attach(MIMEText(html_content, "html"))

        try:
            # Connect to SMTP server
            # Use SSL if port 465, TLS otherwise
            if self.smtp_port == 465:
                logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port} via SSL...")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=15)
            else:
                logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port} via TLS...")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
                # Enable TLS if supported and we are not using standard local debugging port
                if self.smtp_port != 1025:
                    server.starttls()

            # Authenticate if credentials are provided
            if self.smtp_user and self.smtp_pass:
                logger.info(f"Authenticating SMTP user: {self.smtp_user}...")
                server.login(self.smtp_user, self.smtp_pass)

            logger.info(f"Sending email notification to {self.receiver_email}...")
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            server.quit()
            logger.info("Email notification sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
