from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_name = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)
    namespace = Column(String(255), nullable=False)
    pod = Column(String(255), nullable=False)
    service = Column(String(255), nullable=False)   # derived from pod name
    status = Column(String(50), default="firing")   # firing | resolved | failed
    fired_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    mttr_seconds = Column(Float, nullable=True)

    # AI reasoning
    llm_prompt = Column(Text, nullable=True)
    llm_output = Column(Text, nullable=True)
    remediation_command = Column(String(512), nullable=True)
    remediation_result = Column(String(50), nullable=True)  # success | failure


class ServiceHealth(Base):
    __tablename__ = "service_health"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(255), nullable=False, unique=True)
    incident_count_7d = Column(Integer, default=0)
    incident_count_30d = Column(Integer, default=0)
    last_incident_at = Column(DateTime, nullable=True)
    last_remediation_result = Column(String(50), nullable=True)
    avg_mttr_seconds = Column(Float, nullable=True)
    health_score = Column(Integer, default=100)   # 0-100, computed on write
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
