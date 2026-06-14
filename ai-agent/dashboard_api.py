import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import init_db, get_db
from models import Incident, ServiceHealth
import event_bus

app = FastAPI(title="AIOps Dashboard API")

# Allow dashboard frontend on port 3000 to interact with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


# ── REST endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/incidents")
async def get_incidents(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident).order_by(desc(Incident.fired_at)).limit(limit)
    )
    incidents = result.scalars().all()
    return [
        {
            "id": i.id,
            "alert_name": i.alert_name,
            "severity": i.severity,
            "namespace": i.namespace,
            "pod": i.pod,
            "service": i.service,
            "status": i.status,
            "fired_at": i.fired_at.isoformat() if i.fired_at else None,
            "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
            "mttr_seconds": i.mttr_seconds,
            "llm_output": i.llm_output,
            "remediation_command": i.remediation_command,
            "remediation_result": i.remediation_result,
        }
        for i in incidents
    ]


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    i = result.scalar_one_or_none()
    if not i:
        return {"error": "not found"}, 404
    return {
        "id": i.id,
        "alert_name": i.alert_name,
        "severity": i.severity,
        "namespace": i.namespace,
        "pod": i.pod,
        "service": i.service,
        "status": i.status,
        "fired_at": i.fired_at.isoformat() if i.fired_at else None,
        "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
        "mttr_seconds": i.mttr_seconds,
        "llm_prompt": i.llm_prompt,
        "llm_output": i.llm_output,
        "remediation_command": i.remediation_command,
        "remediation_result": i.remediation_result,
    }


@app.get("/api/services")
async def get_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ServiceHealth).order_by(ServiceHealth.health_score)
    )
    services = result.scalars().all()
    return [
        {
            "service": s.service,
            "health_score": s.health_score,
            "incident_count_7d": s.incident_count_7d,
            "incident_count_30d": s.incident_count_30d,
            "last_incident_at": s.last_incident_at.isoformat() if s.last_incident_at else None,
            "last_remediation_result": s.last_remediation_result,
            "avg_mttr_seconds": s.avg_mttr_seconds,
        }
        for s in services
    ]


@app.get("/api/stats/mttr")
async def get_mttr_series(db: AsyncSession = Depends(get_db)):
    """Returns per-incident MTTR for charting — last 30 resolved incidents."""
    result = await db.execute(
        select(Incident)
        .where(Incident.mttr_seconds.isnot(None))
        .order_by(desc(Incident.fired_at))
        .limit(30)
    )
    incidents = result.scalars().all()
    return [
        {
            "fired_at": i.fired_at.isoformat(),
            "service": i.service,
            "mttr_seconds": round(i.mttr_seconds, 1),
            "alert_name": i.alert_name,
        }
        for i in reversed(incidents)
    ]


@app.post("/api/remediate")
async def trigger_remediation(payload: dict):
    """Manual remediation trigger from the dashboard UI."""
    import subprocess
    action = payload.get("action")        # restart | scale | rollback
    deployment = payload.get("deployment")
    namespace = payload.get("namespace", "production")

    script_map = {
        "restart": f"./scripts/restart_deployment.sh {deployment} {namespace}",
        "scale": f"./scripts/scale_deployment.sh {deployment} {namespace}",
        "rollback": f"./scripts/rollback_release.sh {deployment} {namespace}",
    }
    if action not in script_map:
        return {"error": f"unknown action: {action}"}

    try:
        # Note: running from AIOps-Dashboard directory
        result = subprocess.run(
            script_map[action], shell=True, capture_output=True, text=True, timeout=30
        )
        return {
            "status": "success" if result.returncode == 0 else "failure",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"status": "failure", "error": "script timed out"}


# ── WebSocket endpoint ──────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    q = event_bus.subscribe()
    try:
        while True:
            try:
                message = await asyncio.wait_for(q.get(), timeout=30.0)
                await websocket.send_text(message)
            except asyncio.TimeoutError:
                # Send a heartbeat ping so the connection stays alive
                await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        event_bus.unsubscribe(q)
    except Exception:
        event_bus.unsubscribe(q)

