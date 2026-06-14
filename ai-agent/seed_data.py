"""
Run once to populate the database with 60 days of realistic incident history.
Usage: python seed_data.py
"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
from database import init_db, AsyncSessionLocal
from models import Incident, ServiceHealth

SERVICES = [
    "sre-ai-agent", "api-gateway", "auth-service",
    "payment-service", "notification-worker", "db-proxy"
]
ALERT_TYPES = [
    ("PodCrashLooping", "critical"),
    ("HighMemoryUsage", "warning"),
    ("DeploymentReplicasMismatch", "warning"),
    ("PodNotReady", "critical"),
    ("HighCPUThrottle", "warning"),
]
NAMESPACES = ["production", "staging"]
REMEDIATIONS = ["restart_deployment", "scale_deployment", "rollback_release"]
ROOT_CAUSES = [
    "OOMKilled due to memory leak in request handler",
    "Liveness probe failing after config map update",
    "Deadlock detected in database connection pool",
    "CPU spike caused by inefficient query in pagination endpoint",
    "Image pull backoff after registry credentials rotated",
    "Readiness probe misconfigured after recent deployment",
]


async def seed():
    await init_db()
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        for _ in range(80):
            service = random.choice(SERVICES)
            alert_name, severity = random.choice(ALERT_TYPES)
            namespace = random.choice(NAMESPACES)
            pod = f"{service}-{random.randint(100,999)}-{random.randint(10000,99999)}"
            fired_at = now - timedelta(
                days=random.randint(0, 60),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            mttr = random.uniform(45, 600)   # 45 seconds to 10 minutes
            resolved_at = fired_at + timedelta(seconds=mttr)
            root_cause = random.choice(ROOT_CAUSES)
            rem_cmd = random.choice(REMEDIATIONS)
            result = random.choices(["success", "failure"], weights=[85, 15])[0]

            llm_prompt = (
                f"You are an SRE. Alert: {alert_name} on pod {pod} "
                f"in namespace {namespace}. Logs suggest: {root_cause}. "
                f"What is the root cause and recommended remediation?"
            )
            llm_output = (
                f"Root cause analysis: {root_cause}. "
                f"Recommended action: execute {rem_cmd} on {service} "
                f"in {namespace}. This should resolve the alert within 2 minutes."
            )

            incident = Incident(
                alert_name=alert_name,
                severity=severity,
                namespace=namespace,
                pod=pod,
                service=service,
                status="resolved" if result == "success" else "failed",
                fired_at=fired_at,
                resolved_at=resolved_at,
                mttr_seconds=round(mttr, 1),
                llm_prompt=llm_prompt,
                llm_output=llm_output,
                remediation_command=rem_cmd,
                remediation_result=result,
            )
            db.add(incident)

        await db.commit()
        print("Seeded 80 incidents.")

    # Trigger service health recomputation for all services
    from event_bus import _refresh_service_health
    for svc in SERVICES:
        await _refresh_service_health(svc)
    print("Service health computed.")


if __name__ == "__main__":
    asyncio.run(seed())
