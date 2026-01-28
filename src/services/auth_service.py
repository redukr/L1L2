"""Local admin authentication service."""
import json
import secrets
import hashlib
from .app_paths import get_data_dir
from typing import Dict
from .app_paths import get_settings_dir


class AuthService:
    """Handles admin password verification using local storage."""

    def __init__(self):
        self.credentials_path = get_settings_dir() / "admin_credentials.json"
        self._ensure_credentials()

    def _ensure_credentials(self) -> None:
        if self.credentials_path.exists():
            return
        legacy_path = get_data_dir() / "admin_credentials.json"
        if legacy_path.exists():
            self.credentials_path.write_bytes(legacy_path.read_bytes())
            return
        salt = secrets.token_hex(16)
        password_hash = self._hash_password("admin123", salt)
        payload = {"salt": salt, "password_hash": password_hash}
        with open(self.credentials_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def verify_password(self, password: str) -> bool:
        if not self.credentials_path.exists():
            return False
        with open(self.credentials_path, "r", encoding="utf-8") as f:
            data: Dict[str, str] = json.load(f)
        salt = data.get("salt", "")
        stored_hash = data.get("password_hash", "")
        return self._hash_password(password, salt) == stored_hash

    def _hash_password(self, password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120000,
        )
        return digest.hex()
