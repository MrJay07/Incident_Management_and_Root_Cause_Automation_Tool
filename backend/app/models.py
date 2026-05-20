from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IncidentStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class Severity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    service: Mapped[str] = mapped_column(String(128), default="unknown", nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_line: Mapped[str] = mapped_column(Text, nullable=False)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(SqlEnum(Severity), nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(SqlEnum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_log_id: Mapped[int | None] = mapped_column(ForeignKey("logs.id"), nullable=True)

    source_log: Mapped[LogEntry | None] = relationship()
    alerts: Mapped[list["AlertHistory"]] = relationship(back_populates="incident")


class RCAReport(Base):
    __tablename__ = "rca_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    timeline: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    bottleneck: Mapped[str] = mapped_column(String(255), nullable=False)
    dependencies: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(64), default="email", nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    incident: Mapped[Incident] = relationship(back_populates="alerts")
