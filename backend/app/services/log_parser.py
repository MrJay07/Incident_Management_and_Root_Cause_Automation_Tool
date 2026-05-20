import re
from dataclasses import dataclass
from datetime import datetime

from app.models import Severity


DEFAULT_RULES = [
    {"name": "db_connection_failure", "pattern": r"database.*(timeout|refused|failed)", "severity": "CRITICAL", "title": "Database connectivity failure"},
    {"name": "memory_pressure", "pattern": r"out of memory|memory pressure", "severity": "CRITICAL", "title": "Memory pressure detected"},
    {"name": "latency_degradation", "pattern": r"latency|timeout", "severity": "ERROR", "title": "Service latency degradation"},
    {"name": "auth_failures", "pattern": r"unauthorized|forbidden|invalid token", "severity": "WARNING", "title": "Authentication failures detected"},
]

SEVERITY_ORDER = {
    "WARNING": Severity.WARNING,
    "ERROR": Severity.ERROR,
    "CRITICAL": Severity.CRITICAL,
}


@dataclass
class ParsedLog:
    timestamp: datetime
    level: str
    service: str
    message: str
    raw_line: str


@dataclass
class DetectedIncident:
    title: str
    severity: Severity
    service: str
    description: str



def parse_log_line(line: str) -> ParsedLog | None:
    line = line.strip()
    if " - " not in line:
        return None
    header, message = line.split(" - ", 1)
    parts = header.split(" ", 2)
    if len(parts) != 3:
        return None

    timestamp, level, service = parts
    if level not in {"INFO", "WARNING", "ERROR", "CRITICAL"}:
        return None

    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return ParsedLog(
        timestamp=ts,
        level=level,
        service=service,
        message=message,
        raw_line=line,
    )


def detect_incidents(parsed_log: ParsedLog, custom_rules: list[dict] | None = None) -> list[DetectedIncident]:
    incidents: list[DetectedIncident] = []
    rules = [*DEFAULT_RULES]
    for rule in rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue
        if re.search(pattern, parsed_log.message, flags=re.IGNORECASE):
            sev = SEVERITY_ORDER.get(rule.get("severity", parsed_log.level), SEVERITY_ORDER.get(parsed_log.level, Severity.WARNING))
            incidents.append(
                DetectedIncident(
                    title=rule.get("title", "Rule-triggered incident"),
                    severity=sev,
                    service=parsed_log.service,
                    description=f"{rule.get('name', 'custom_rule')} matched: {parsed_log.message}",
                )
            )

    for rule in custom_rules or []:
        pattern = rule.get("pattern")
        if not pattern:
            continue
        if pattern.lower() in parsed_log.message.lower():
            sev = SEVERITY_ORDER.get(rule.get("severity", parsed_log.level), SEVERITY_ORDER.get(parsed_log.level, Severity.WARNING))
            incidents.append(
                DetectedIncident(
                    title=rule.get("title", "Rule-triggered incident"),
                    severity=sev,
                    service=parsed_log.service,
                    description=f"{rule.get('name', 'custom_rule')} matched: {parsed_log.message}",
                )
            )

    if parsed_log.level in ("ERROR", "CRITICAL"):
        incidents.append(
            DetectedIncident(
                title=f"{parsed_log.level} detected in {parsed_log.service}",
                severity=SEVERITY_ORDER[parsed_log.level],
                service=parsed_log.service,
                description=parsed_log.message,
            )
        )

    return incidents
