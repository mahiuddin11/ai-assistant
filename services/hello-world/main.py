import os

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()


ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
SERVICE_NAME = os.getenv("SERVICE_NAME", "hello-world")

# ---------------------------------------------------------
# Structured (JSON) logging কনফিগারেশন
# ---------------------------------------------------------
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# ---------------------------------------------------------
# FastAPI 
# ---------------------------------------------------------
app = FastAPI(title="Hello World Service")

# Prometheus /metrics endpoint start
Instrumentator().instrument(app).expose(app)


# ---------------------------------------------------------
# Request log middleware
# ---------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(
        "request_handled",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response


# ---------------------------------------------------------
# Route 
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"message": "AI Assistant Platform - Foundation service is running"}


@app.get("/healthz")
def healthz():
    """লাইভনেস চেক - সার্ভিস চালু আছে কিনা"""
    return {"status": "ok", "environment": ENVIRONMENT, "service": SERVICE_NAME}


@app.get("/readyz")
def readyz():
    """readiness check - service is ready to take requests"""
    return {"status": "ready"}