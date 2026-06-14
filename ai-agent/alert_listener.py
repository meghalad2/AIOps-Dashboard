import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("ai-agent")

class AlertInfo(BaseModel):
    name: str
    status: str
    severity: str
    namespace: str
    pod: Optional[str] = None
    container: Optional[str] = None
    summary: str
    description: str

def parse_alertmanager_payload(payload: Dict[str, Any]) -> List[AlertInfo]:
    """
    Parses Alertmanager webhook POST payload and extracts clean alert metadata.
    """
    parsed_alerts = []
    
    alerts = payload.get("alerts", [])
    logger.info(f"Received webhook containing {len(alerts)} alerts.")
    
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        alert_info = AlertInfo(
            name=labels.get("alertname", "UnknownAlert"),
            status=alert.get("status", "firing"),
            severity=labels.get("severity", "warning"),
            namespace=labels.get("namespace", "default"),
            pod=labels.get("pod"),
            container=labels.get("container"),
            summary=annotations.get("summary", "No summary provided"),
            description=annotations.get("description", "No description provided")
        )
        
        # Only process alerts that are active ('firing') and have the auto-heal tag
        if alert_info.status == "firing" and labels.get("action") == "auto-heal":
            parsed_alerts.append(alert_info)
            logger.info(f"Target alert parsed successfully: {alert_info.name} on Pod {alert_info.pod}")
        else:
            logger.info(f"Skipping alert: {alert_info.name} (Status: {alert_info.status}, Action: {labels.get('action')})")
            
    return parsed_alerts
