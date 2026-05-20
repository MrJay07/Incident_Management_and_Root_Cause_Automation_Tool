from app.models import Severity
from app.services.log_parser import detect_incidents, parse_log_line


def test_parse_log_line_extracts_fields():
    parsed = parse_log_line("2026-05-20T15:00:00Z ERROR payments-service - database timeout while creating charge")

    assert parsed is not None
    assert parsed.level == "ERROR"
    assert parsed.service == "payments-service"
    assert "database timeout" in parsed.message


def test_detect_incidents_matches_default_and_custom_rules():
    parsed = parse_log_line("2026-05-20T15:01:00Z WARNING api-gateway - invalid token observed from upstream")

    incidents = detect_incidents(
        parsed,
        [{"name": "gateway_warning", "pattern": "upstream", "severity": "ERROR", "title": "Gateway upstream issue"}],
    )

    assert any(incident.title == "Authentication failures detected" for incident in incidents)
    assert any(incident.title == "Gateway upstream issue" and incident.severity == Severity.ERROR for incident in incidents)
