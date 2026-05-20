# Incident Management & Root Cause Automation Tool

A full-stack DevOps observability platform that parses production logs, auto-creates incidents, triggers alerts, and simulates RCA workflows.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: React (Vite) + Tailwind CSS
- **Database**: PostgreSQL (Docker compose) with schema in `backend/schema.sql`
- **Task Scheduling**: APScheduler cron trigger (`*/1 * * * *` default)
- **Email Alerts**: SMTP (MailHog in Docker compose for local testing)
- **Log Processing**: Regex parser + rule engine
- **Containerization**: Docker + docker-compose

## Project Structure

- `backend/app/main.py` - FastAPI app, middleware, exception handling, startup/shutdown lifecycle
- `backend/app/routers/*` - REST APIs for logs, incidents, RCA, and alerts
- `backend/app/services/log_parser.py` - regex parsing + incident detection rule engine
- `backend/app/services/incident_service.py` - incident lifecycle and dashboard metrics
- `backend/app/services/rca_service.py` - RCA workflow simulation and dependency tracing
- `backend/app/services/alert_service.py` - email alerting + throttling
- `backend/app/services/scheduler.py` - cron-based monitoring hooks
- `backend/schema.sql` - database schema deliverable
- `sample_logs/production.log` - sample production logs
- `frontend/src/App.jsx` - dark-theme DevOps monitoring dashboard

## Backend APIs

Run backend docs via Swagger UI:
- `http://localhost:8000/docs`

Key endpoints:
- `POST /logs/upload` - upload log file
- `POST /logs/stream` - stream logs as JSON lines
- `GET /logs` - recent parsed logs
- `GET /incidents` - incident list
- `PATCH /incidents/{incident_id}` - update status (`Open`, `In Progress`, `Resolved`)
- `GET /incidents/dashboard/metrics` - trends, recovery time, frequency, health indicators, activity feed
- `POST /rca/{incident_id}/simulate` - run RCA simulation
- `GET /rca` - RCA reports
- `GET /alerts/history` - alert history and throttling outcomes

## Setup Guide

### Local backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
uvicorn app.main:app --reload
```

### Local frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend dashboard runs at `http://localhost:5173` and proxies `/api/*` to backend `http://localhost:8000`.

### Full stack with Docker

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000/docs`
- MailHog: `http://localhost:8025`

## Incident Detection Logic

1. Incoming logs are parsed with regex format:
   - `timestamp level service - message`
2. Each parsed log is evaluated against:
   - default detection rules (`database timeout`, `out of memory`, latency/auth patterns)
   - optional custom rules supplied to `/logs/stream`
3. `ERROR`/`CRITICAL` logs auto-generate incidents even without a custom rule hit.
4. Matching active incidents are upserted (occurrence count and timestamps are updated).

## RCA Workflow Logic

1. Select an incident and call `POST /rca/{incident_id}/simulate`
2. Service dependency map is used to trace likely impacted components.
3. RCA report includes:
   - timeline analysis
   - probable bottleneck
   - dependency tracing graph data
4. RCA output is stored in `rca_reports` and exposed in dashboard activity feed.

## Scalability & Performance Improvements

- Modular service layer and router split for horizontal backend growth
- Database-backed incident upsert avoids duplicate incident explosion
- Alert throttling prevents notification storms
- Cron scheduler enables autonomous periodic checks
- Centralized middleware logging and structured exception handling
- Dashboard consumes aggregate metrics instead of heavy per-widget queries
- Containerized services for independent scaling of frontend/backend/database

## Monitoring Strategy

- Application-level health endpoint: `GET /health`
- Request-level latency logging via middleware
- Incident trend and service health metrics available via `/incidents/dashboard/metrics`
- Optional extension path: scrape API metrics with Prometheus and visualize in Grafana

## Tests

Focused backend tests are in `backend/tests/test_log_engine.py`.

Run:

```bash
cd backend
export PYTHONPATH=$(pwd)
pytest -q tests/test_log_engine.py
```
