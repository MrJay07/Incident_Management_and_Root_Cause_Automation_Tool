from datetime import datetime

from pydantic import BaseModel, Field

from app.models import IncidentStatus, Severity


class LogIngestRequest(BaseModel):
    lines: list[str] = Field(default_factory=list)
    custom_rules: list[dict] = Field(default_factory=list)


class LogEntryResponse(BaseModel):
    id: int
    timestamp: datetime
    service: str
    level: str
    message: str

    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: Severity
    status: IncidentStatus
    service: str
    first_seen: datetime
    last_seen: datetime
    occurrences: int

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class RCAReportResponse(BaseModel):
    id: int
    incident_id: int
    summary: str
    timeline: list[dict]
    bottleneck: str
    dependencies: list[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    id: int
    incident_id: int
    channel: str
    recipient: str
    status: str
    sent_at: datetime
    error_message: str | None

    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    incident_trends: dict[str, int]
    average_recovery_minutes: float
    failure_frequency_by_service: dict[str, int]
    service_health: dict[str, str]
    recent_activity: list[dict]
