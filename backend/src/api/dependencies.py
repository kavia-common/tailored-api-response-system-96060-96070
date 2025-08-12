from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .auth import decode_token
from .storage import db
from .models import UserPublic, PackageTier

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# PUBLIC_INTERFACE
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserPublic:
    """Resolve and return the current authenticated user based on Bearer token.

    Args:
        token: Bearer token extracted by OAuth2PasswordBearer.

    Returns:
        UserPublic: Public user info.

    Raises:
        HTTPException: 401 if token invalid/expired or user not found.
    """
    try:
        claims = decode_token(token)
        user_id = claims.get("sub")
        if not user_id:
            raise ValueError("sub claim missing")
        record = db.get_user_by_id(user_id)
        if not record:
            raise ValueError("user not found")
        return UserPublic(
            id=record["id"],
            email=record["email"],
            package_tier=PackageTier(record["package_tier"]),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
