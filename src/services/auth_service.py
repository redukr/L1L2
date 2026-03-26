"""Local admin authentication service."""
import json
import secrets
import hashlib
import os
import tempfile
from typing import Dict
from .app_paths import get_settings_dir


class AuthService:
    """Handles admin/editor password verification using local storage."""
    MIN_PASSWORD_LENGTH = 8

    def __init__(self):
        self.admin_credentials_path = get_settings_dir() / "admin_credentials.json"
        self.editor_credentials_path = get_settings_dir() / "editor_credentials.json"

    def has_admin_credentials(self) -> bool:
        return self.admin_credentials_path.exists()

    def has_editor_credentials(self) -> bool:
        return self.editor_credentials_path.exists()

    def set_admin_password(self, password: str) -> None:
        self._write_credentials(self.admin_credentials_path, password)

    def set_editor_password(self, password: str) -> None:
        self._write_credentials(self.editor_credentials_path, password)

    def _write_credentials(self, path, password: str) -> None:
        if not password:
            raise ValueError("Password must not be empty.")
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters.")
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        payload = {"salt": salt, "password_hash": password_hash}
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(
            prefix=f"{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def verify_password(self, password: str) -> bool:
        return self.verify_admin_password(password)

    def verify_admin_password(self, password: str) -> bool:
        return self._verify_password(self.admin_credentials_path, password)

    def verify_editor_password(self, password: str) -> bool:
        return self._verify_password(self.editor_credentials_path, password)

    def _verify_password(self, path, password: str) -> bool:
        if not path.exists():
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data: Dict[str, str] = json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return False
        salt = data.get("salt", "")
        stored_hash = data.get("password_hash", "")
        return secrets.compare_digest(self._hash_password(password, salt), stored_hash)

    def _hash_password(self, password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120000,
        )
        return digest.hex()
