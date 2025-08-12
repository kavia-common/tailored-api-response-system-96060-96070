import os
import uuid
import hmac
import hashlib
from typing import Optional, Dict, Any

from .models import PackageTier


class InMemoryDB:
    """Very simple in-memory data store for demo purposes."""
    def __init__(self) -> None:
        # user_id -> user_record
        self.users: Dict[str, Dict[str, Any]] = {}
        # email -> user_id
        self.email_index: Dict[str, str] = {}

    def create_user(self, email: str, password: str, package_tier: PackageTier) -> Dict[str, Any]:
        """Create a user with salted hash credentials."""
        user_id = str(uuid.uuid4())
        salt = os.urandom(16)
        password_hash = _hash_password(password, salt)
        record = {
            "id": user_id,
            "email": email.lower(),
            "salt_hex": salt.hex(),
            "password_hash": password_hash,
            "package_tier": package_tier.value,
        }
        self.users[user_id] = record
        self.email_index[email.lower()] = user_id
        return record

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user_id = self.email_index.get(email.lower())
        if not user_id:
            return None
        return self.users.get(user_id)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def verify_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify password for email; returns user record if valid."""
        u = self.get_user_by_email(email)
        if not u:
            return None
        salt = bytes.fromhex(u["salt_hex"])
        expected_hash = u["password_hash"]
        candidate_hash = _hash_password(password, salt)
        if hmac.compare_digest(expected_hash, candidate_hash):
            return u
        return None

    def set_package(self, user_id: str, package_tier: PackageTier) -> Optional[Dict[str, Any]]:
        u = self.users.get(user_id)
        if not u:
            return None
        u["package_tier"] = package_tier.value
        return u


def _hash_password(password: str, salt: bytes) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 and return hex digest."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000, dklen=32)
    return dk.hex()


# Singleton storage for app lifetime
db = InMemoryDB()
