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
        user = UserRecord(
            email=email_key,
            password_plain=password_plain,
            package_tier=package_tier or "free",
        )
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
