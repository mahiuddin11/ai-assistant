import sys
import os
import structlog
from pydantic import BaseModel
from fastapi import HTTPException
from llm_client import send_message
from fastapi import FastAPI, Request

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

DATABASE_URL = get_secret("DATABASE_URL", vault_path="conversation-service")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

app = FastAPI(title="Conversational Agent Service")


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


@app.get("/")
def root():
    return {"message": "Conversational Agent Service - v1.0 MVP"}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "conversation-service", "environment": ENVIRONMENT}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


class ChatTestRequest(BaseModel):
    message: str


@app.post("/v1/test/chat")
def test_chat(payload: ChatTestRequest):
    try:
        result = send_message(payload.message)
        return result
    except RuntimeError as e:
        logger.error("chat_test_failed", error=str(e))
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")