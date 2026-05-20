import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import alerts, incidents, logs, rca
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("incident_tool")

app = FastAPI(title=settings.app_name, version="1.0.0")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    logger.info("Incident tool started")


@app.on_event("shutdown")
def shutdown_event() -> None:
    stop_scheduler()
    logger.info("Incident tool stopped")


@app.middleware("http")
async def add_request_logging(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.2fms)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):  # noqa: ARG001
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


app.include_router(logs.router)
app.include_router(incidents.router)
app.include_router(rca.router)
app.include_router(alerts.router)
