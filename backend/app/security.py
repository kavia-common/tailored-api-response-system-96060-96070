import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from .storage import MemoryUserStore, UserRecord

# OAuth2 scheme for extracting Bearer token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Helper to read environment variables with default."""
    val = os.environ.get(key)
    return val if val is not None else default


def _int_env(key: str, default: int) -> int:
    """Helper to read integer environment variables safely."""
    try:
        return int(os.environ.get(key, str(default)))
    except Exception:
        return default


def get_jwt_config() -> Dict[str, Any]:
    """
    Read JWT-related configuration from environment variables.

    Required:
        - JWT_SECRET_KEY: Secret key used to sign JWTs.

    Optional:
        - JWT_ALGORITHM: Algorithm for JWT signing (default: HS256).
        - ACCESS_TOKEN_EXPIRE_MINUTES: Token expiry in minutes (default: 1440 = 24 hours).
    """
    secret = _get_env("JWT_SECRET_KEY")
    if not secret:
        # Do not block server startup elsewhere; raise only when token ops are attempted
        raise RuntimeError("JWT_SECRET_KEY environment variable is required but not set.")
    algo = _get_env("JWT_ALGORITHM", "HS256")
    ttl_minutes = _int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
    return {"secret": secret, "algorithm": algo, "ttl_minutes": ttl_minutes}


# PUBLIC_INTERFACE
def create_access_token(*, user: UserRecord) -> str:
    """Create a JWT access token for the given user.

    The token contains the user's id (sub), email, and package_tier.
    """
    cfg = get_jwt_config()
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=cfg["ttl_minutes"])
    payload = {
        "sub": user.id,
        "email": user.email,
        "package_tier": user.package_tier,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, cfg["secret"], algorithm=cfg["algorithm"])


# PUBLIC_INTERFACE
def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT and return its payload."""
    cfg = get_jwt_config()
    return jwt.decode(token, cfg["secret"], algorithms=[cfg["algorithm"]])


# PUBLIC_INTERFACE
def get_current_user(
    token: str = Depends(oauth2_scheme),
    store: MemoryUserStore = Depends(lambda: store_singleton),
) -> UserRecord:
    """Dependency to retrieve the current authenticated user from the Bearer token.

    Raises:
        HTTPException 401 if token is invalid/expired or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_token(token)
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = store.get_by_id(user_id)
        if not user:
            raise credentials_exception
        return user
    except (JWTError, RuntimeError):
        # RuntimeError may occur if JWT_SECRET_KEY is missing
        raise credentials_exception


# Single in-memory store instance for app lifetime
store_singleton = MemoryUserStore()
