import sys
import os
import structlog
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import verify_password

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

DATABASE_URL = get_secret("DATABASE_URL", vault_path="auth-service")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

app = FastAPI(title="Auth & Identity Service")


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
    return {"message": "Auth & Identity Service - v1.0 MVP"}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "auth-service", "environment": ENVIRONMENT}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@app.post("/v1/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning("login_failed", email=payload.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info("login_success", user_id=str(user.id))
    return {"message": "Login successful", "user_id": str(user.id)}