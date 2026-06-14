import asyncio
import json
from datetime import datetime, timezone
from typing import Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import AsyncSessionLocal
from models import Incident, ServiceHealth


# In-memory set of active WebSocket connections
_subscribers: Set[asyncio.Queue] = set()


def subscribe() -> asyncio.Queue:
    """Dashboard WebSocket connections call this to receive events."""
    q = asyncio.Queue()
    _subscribers.add(q)
    return q


def unsubscribe(q: asyncio.Queue):
    _subscribers.discard(q)


async def _broadcast(event: dict):
    """Push event to all connected WebSocket clients."""
    message = json.dumps(event, default=str)
    dead = set()
    for q in _subscribers:
        try:
            q.put_nowait(message)
        except asyncio.QueueFull:
            dead.add(q)
    for q in dead:
        _subscribers.discard(q)


def _derive_service(pod_name: str) -> str:
    """Extract service name from pod name (strip replica hash suffix)."""
    parts = pod_name.rsplit("-", 2)
    return parts[0] if len(parts) >= 3 else pod_name


def _compute_health_score(incident_count_7d: int, avg_mttr: float,
                           last_result: str) -> int:
    """Simple weighted health score 0-100."""
    score = 100
    score -= min(incident_count_7d * 10, 50)   # up to -50 for frequency
    if avg_mttr:
        score -= min(int(avg_mttr / 60), 20)    # up to -20 for slow MTTR
    if last_result == "failure":
        score -= 20
    return max(score, 0)


async def emit_incident_fired(alert_name: str, severity: str,
                               namespace: str, pod: str,
                               llm_prompt: str = None):
    """Call this when P1 receives and starts processing an alert."""
    service = _derive_service(pod)
    async with AsyncSessionLocal() as db:
        incident = Incident(
            alert_name=alert_name,
            severity=severity,
            namespace=namespace,
            pod=pod,
            service=service,
            status="firing",
            llm_prompt=llm_prompt,
        )
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        incident_id = incident.id

    event = {
        "type": "incident_fired",
        "incident_id": incident_id,
        "alert_name": alert_name,
        "severity": severity,
        "namespace": namespace,
        "pod": pod,
        "service": service,
        "fired_at": datetime.now(timezone.utc).isoformat(),
    }
    await _broadcast(event)
    return incident_id


async def emit_llm_reasoning(incident_id: int, llm_output: str,
                               remediation_command: str):
    """Call this after P1's LLM reasoner produces its output."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = result.scalar_one_or_none()
        if incident:
            incident.llm_output = llm_output
            incident.remediation_command = remediation_command
            await db.commit()

    event = {
        "type": "llm_reasoning",
        "incident_id": incident_id,
        "llm_output": llm_output,
        "remediation_command": remediation_command,
    }
    await _broadcast(event)


async def emit_remediation_result(incident_id: int, result: str):
    """Call this after P1's remediation engine finishes. result = 'success'|'failure'"""
    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = res.scalar_one_or_none()
        if not incident:
            return

        incident.status = "resolved" if result == "success" else "failed"
        incident.resolved_at = now
        incident.remediation_result = result
        if incident.fired_at:
            fired = incident.fired_at.replace(tzinfo=timezone.utc) \
                    if incident.fired_at.tzinfo is None else incident.fired_at
            incident.mttr_seconds = (now - fired).total_seconds()

        service = incident.service
        await db.commit()

    # Recompute ServiceHealth for this service
    await _refresh_service_health(service)

    event = {
        "type": "remediation_result",
        "incident_id": incident_id,
        "result": result,
        "resolved_at": now.isoformat(),
    }
    await _broadcast(event)


async def _refresh_service_health(service: str):
    """Recompute and upsert the ServiceHealth row for a given service."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    async with AsyncSessionLocal() as db:
        count_7d_result = await db.execute(
            select(func.count()).where(
                Incident.service == service,
                Incident.fired_at >= cutoff_7d
            )
        )
        count_7d = count_7d_result.scalar()

        count_30d_result = await db.execute(
            select(func.count()).where(
                Incident.service == service,
                Incident.fired_at >= cutoff_30d
            )
        )
        count_30d = count_30d_result.scalar()

        mttr_result = await db.execute(
            select(func.avg(Incident.mttr_seconds)).where(
                Incident.service == service,
                Incident.mttr_seconds.isnot(None)
            )
        )
        avg_mttr = mttr_result.scalar()

        last_inc_result = await db.execute(
            select(Incident).where(Incident.service == service)
            .order_by(Incident.fired_at.desc()).limit(1)
        )
        last_inc = last_inc_result.scalar_one_or_none()
        last_result = last_inc.remediation_result if last_inc else None
        last_at = last_inc.fired_at if last_inc else None

        health_score = _compute_health_score(count_7d, avg_mttr or 0, last_result or "")

        existing = await db.execute(
            select(ServiceHealth).where(ServiceHealth.service == service)
        )
        sh = existing.scalar_one_or_none()
        if sh:
            sh.incident_count_7d = count_7d
            sh.incident_count_30d = count_30d
            sh.last_incident_at = last_at
            sh.last_remediation_result = last_result
            sh.avg_mttr_seconds = avg_mttr
            sh.health_score = health_score
            sh.updated_at = now
        else:
            sh = ServiceHealth(
                service=service,
                incident_count_7d=count_7d,
                incident_count_30d=count_30d,
                last_incident_at=last_at,
                last_remediation_result=last_result,
                avg_mttr_seconds=avg_mttr,
                health_score=health_score,
            )
            db.add(sh)
        await db.commit()

    await _broadcast({
        "type": "service_health_updated",
        "service": service,
        "health_score": health_score,
        "incident_count_7d": count_7d,
        "last_result": last_result,
    })
