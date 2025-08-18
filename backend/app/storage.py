import uuid
import hashlib
from typing import Dict, Optional


class UserRecord:
    """Internal user representation stored in-memory."""
    def __init__(self, email: str, password_plain: str, package_tier: str = "free") -> None:
        self.id: str = str(uuid.uuid4())
        self.email: str = email.lower().strip()
        self.hashed_password: str = self._hash_password(password_plain)
        self.package_tier: str = package_tier

    @staticmethod
    def _hash_password(password_plain: str) -> str:
        # Simple SHA-256 hash for demo purposes only (do NOT use in production)
        return hashlib.sha256(password_plain.encode("utf-8")).hexdigest()

    def verify_password(self, password_plain: str) -> bool:
        return self.hashed_password == self._hash_password(password_plain)


class MemoryUserStore:
    """
    In-memory user store suitable for demos and development only.
    """
    def __init__(self) -> None:
        self._by_email: Dict[str, UserRecord] = {}
        self._by_id: Dict[str, UserRecord] = {}

    def create_user(self, email: str, password_plain: str, package_tier: str = "free") -> UserRecord:
        email_key = email.lower().strip()
        if email_key in self._by_email:
            raise ValueError("Email already registered")
        user = UserRecord(email=email_key, password_plain=password_plain, package_tier=package_tier or "free")
        self._by_email[email_key] = user
        self._by_id[user.id] = user
        return user

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        return self._by_email.get((email or "").lower().strip())

    def get_by_id(self, user_id: str) -> Optional[UserRecord]:
        return self._by_id.get(user_id)

    def authenticate(self, email: str, password_plain: str) -> Optional[UserRecord]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not user.verify_password(password_plain):
            return None
        return user

    def update_plan(self, user_id: str, package_tier: str) -> Optional[UserRecord]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.package_tier = package_tier
        return user
```

Explanation: Implement security utilities for JWT handling and dependency to get current user
````write file="tailored-api-response-system-96060-96070/backend/app/security.py"
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from .storage import MemoryUserStore, UserRecord

# OAuth2 scheme for extracting Bearer token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Environment-driven configuration
def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    val = os.environ.get(key)
    return val if val is not None else default

def _int_env(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except Exception:
        return default


def get_jwt_config() -> Dict[str, Any]:
    """
    Read JWT-related configuration from environment variables.

    Required:
    - JWT_SECRET_KEY

    Optional:
    - JWT_ALGORITHM (default: HS256)
    - ACCESS_TOKEN_EXPIRE_MINUTES (default: 1440)
    """
    secret = _get_env("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required but not set.")
    algo = _get_env("JWT_ALGORITHM", "HS256")
    ttl_minutes = _int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
    return {"secret": secret, "algorithm": algo, "ttl_minutes": ttl_minutes}


def create_access_token(*, user: UserRecord) -> str:
    """
    Create a JWT access token for the given user.
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


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT and return its payload."""
    cfg = get_jwt_config()
    return jwt.decode(token, cfg["secret"], algorithms=[cfg["algorithm"]])


def get_current_user(token: str = Depends(oauth2_scheme), store: MemoryUserStore = Depends(lambda: store_singleton)) -> UserRecord:
    """
    Dependency to retrieve the current authenticated user from the Bearer token.

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
    except JWTError:
        raise credentials_exception


# Single in-memory store instance for app lifetime
store_singleton = MemoryUserStore()
