import sys
import os
import structlog
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from permissions import grant_permission, revoke_permission

from database import get_db


from datetime import datetime, timedelta, timezone
from models import User, Session as SessionModel
from auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
    decode_access_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
# pyrefly: ignore [missing-import]
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

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()

    session = SessionModel(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)
    db.commit()

    logger.info("login_success", user_id=str(user.id))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

class RefreshRequest(BaseModel):
    refresh_token: str


@app.post("/v1/auth/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).filter(
        SessionModel.expires_at > datetime.now(timezone.utc)
    ).all()

    matched_session = None
    for s in sessions:
        if verify_refresh_token(payload.refresh_token, s.refresh_token_hash):
            matched_session = s
            break

    if matched_session is None:
        logger.warning("refresh_failed")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


    db.delete(matched_session)

    new_access_token = create_access_token(str(matched_session.user_id))
    new_refresh_token = create_refresh_token()

    new_session = SessionModel(
        user_id=matched_session.user_id,
        refresh_token_hash=hash_refresh_token(new_refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_session)
    db.commit()

    logger.info("refresh_success", user_id=str(matched_session.user_id))
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

class PermissionRequest(BaseModel):
    user_id: str
    tool_name: str


@app.post("/v1/permissions/grant")
def grant_permission_endpoint(payload: PermissionRequest, db: Session = Depends(get_db)):
    permission = grant_permission(db, payload.user_id, payload.tool_name)
    return {"status": "granted", "tool_name": payload.tool_name, "permission_id": str(permission.id)}


@app.post("/v1/permissions/revoke")
def revoke_permission_endpoint(payload: PermissionRequest, db: Session = Depends(get_db)):
    success = revoke_permission(db, payload.user_id, payload.tool_name)
    if not success:
        raise HTTPException(status_code=404, detail="No active permission found to revoke")
    return {"status": "revoked", "tool_name": payload.tool_name}