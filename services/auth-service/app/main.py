from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

app = FastAPI(title="Job Autopilot Auth Service", version="0.1.0")

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

USERS: Dict[str, Dict[str, str]] = {}


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = Field(default="user", pattern="^(user|admin)$")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    username: str
    role: str
    mfa_enabled: bool


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(username: str, role: str, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + expires_delta,
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserProfile:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role", "user")
        if username is None or username not in USERS:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = USERS[username]
        return UserProfile(username=username, role=role, mfa_enabled=user.get("mfa_enabled", False))
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "auth-service"}


@app.post("/v1/auth/register", response_model=UserProfile)
async def register(request: RegisterRequest) -> UserProfile:
    if request.username in USERS:
        raise HTTPException(status_code=400, detail="Username already registered")
    USERS[request.username] = {
        "hashed_password": hash_password(request.password),
        "role": request.role,
        "mfa_enabled": False,
    }
    return UserProfile(username=request.username, role=request.role, mfa_enabled=False)


@app.post("/v1/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    user = USERS.get(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_token(request.username, user["role"], timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token(request.username, user["role"], timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(token: str = Depends(oauth2_scheme)) -> TokenResponse:
    user = get_current_user(token)
    access_token = create_token(user.username, user.role, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token(user.username, user.role, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/v1/auth/mfa/setup")
async def setup_mfa(current_user: UserProfile = Depends(get_current_user)) -> dict:
    USERS[current_user.username]["mfa_enabled"] = True
    return {"message": "MFA setup initiated", "method": "totp"}


@app.post("/v1/auth/mfa/verify")
async def verify_mfa(code: str, current_user: UserProfile = Depends(get_current_user)) -> dict:
    if not USERS[current_user.username].get("mfa_enabled"):
        raise HTTPException(status_code=400, detail="MFA not enabled")
    return {"message": "MFA verified", "code": code}


@app.get("/v1/users/me", response_model=UserProfile)
async def read_user_profile(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    return current_user


@app.get("/v1/admin/health")
async def admin_health(current_user: UserProfile = Depends(get_current_user)) -> dict:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"status": "ok", "message": "Admin access verified"}
