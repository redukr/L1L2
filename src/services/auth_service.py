"""Local admin authentication service."""
import hmac
import json
import secrets
import hashlib
from .app_paths import get_data_dir
from typing import Dict
from .app_paths import get_settings_dir


class AuthService:
    """Handles admin/editor password verification using local storage."""

    def __init__(self):
        self.admin_credentials_path = get_settings_dir() / "admin_credentials.json"
        self.editor_credentials_path = get_settings_dir() / "editor_credentials.json"
        self._ensure_credentials(self.admin_credentials_path, legacy_name="admin_credentials.json")
        self._ensure_credentials(self.editor_credentials_path, legacy_name=None)

    def _ensure_credentials(self, path, legacy_name: str | None) -> None:
        if path.exists():
            return
        if legacy_name:
            legacy_path = get_data_dir() / legacy_name
            if legacy_path.exists():
                path.write_bytes(legacy_path.read_bytes())
    
    def has_admin_password(self) -> bool:
        return self.admin_credentials_path.exists()

    def has_editor_password(self) -> bool:
        return self.editor_credentials_path.exists()

    def set_admin_password(self, password: str) -> None:
        self._set_password(self.admin_credentials_path, password)

    def set_editor_password(self, password: str) -> None:
        self._set_password(self.editor_credentials_path, password)

    def _set_password(self, path, password: str) -> None:
        password = (password or "").strip()
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        payload = {"salt": salt, "password_hash": password_hash}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def verify_password(self, password: str) -> bool:
        return self.verify_admin_password(password)

    def verify_admin_password(self, password: str) -> bool:
        return self._verify_password(self.admin_credentials_path, password)

    def verify_editor_password(self, password: str) -> bool:
        return self._verify_password(self.editor_credentials_path, password)

    def _verify_password(self, path, password: str) -> bool:
        if not path.exists():
            return False
        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, str] = json.load(f)
        salt = data.get("salt", "")
        stored_hash = data.get("password_hash", "")
        return hmac.compare_digest(self._hash_password(password, salt), stored_hash)

    def _hash_password(self, password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120000,
        )
        return digest.hex()
