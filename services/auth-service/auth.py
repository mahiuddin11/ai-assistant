import sys
import os
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
# pyrefly: ignore [missing-import]
from config_loader import get_secret  # noqa: E402

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


JWT_SECRET = get_secret("JWT_SECRET", vault_path="auth-service")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex


def hash_refresh_token(token: str) -> str:
    return pwd_context.hash(token)


def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    return pwd_context.verify(plain_token, hashed_token)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])