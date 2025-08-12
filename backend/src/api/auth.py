import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt  # PyJWT

# Read configuration from env with sane defaults for local/dev
JWT_SECRET = os.getenv("JWT_SECRET", "change_me_local_dev_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# PUBLIC_INTERFACE
def create_access_token(subject: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create a JWT access token for the given subject (user_id).

    Args:
        subject: The user id to embed in the token as 'sub'.
        additional_claims: Optional extra claims to include.

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if additional_claims:
        payload.update(additional_claims)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


# PUBLIC_INTERFACE
def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded claims as a dictionary.

    Raises:
        jwt.PyJWTError: When token is invalid or expired.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
