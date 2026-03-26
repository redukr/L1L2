"""Auth and sync helpers extracted from AdminDialog."""

from __future__ import annotations

import json
import time
from pathlib import Path

from PySide6.QtWidgets import QDialog, QMessageBox

from .dialogs import PasswordDialog


class AdminDialogAuthSyncMixin:
    """Authentication and sync-path helpers for AdminDialog."""

    def _authorize(self) -> bool:
        now = time.monotonic()
        blocked_until = type(self)._auth_blocked_until_monotonic
        if blocked_until > now:
            wait_seconds = int(blocked_until - now) + 1
            QMessageBox.warning(
                self,
                self.tr("Access denied"),
                self.tr("Too many failed attempts. Try again in {0} seconds.").format(wait_seconds),
            )
            return False

        attempts_left = self.AUTH_MAX_ATTEMPTS
        while attempts_left > 0:
            dialog = PasswordDialog(
                self,
                title=self.tr("Admin Access"),
                label=self.tr("Enter admin password:"),
            )
            if dialog.exec() != QDialog.Accepted:
                return False
            if self.controller.verify_password(dialog.get_password()):
                type(self)._auth_blocked_until_monotonic = 0.0
                return True
            attempts_left -= 1
            if attempts_left <= 0:
                type(self)._auth_blocked_until_monotonic = time.monotonic() + self.AUTH_COOLDOWN_SECONDS
                QMessageBox.warning(
                    self,
                    self.tr("Access denied"),
                    self.tr("Too many failed attempts. Access is temporarily blocked."),
                )
                return False
            QMessageBox.warning(
                self,
                self.tr("Access denied"),
                self.tr("Invalid admin password. Attempts left: {0}").format(attempts_left),
            )
        return False

    def _unique_program_name(self, name: str) -> str:
        existing = {p.name for p in self.controller.get_programs()}
        if name not in existing:
            return name
        index = 1
        while True:
            suffix = f"_{index:02d}"
            candidate = f"{name}{suffix}"
            if candidate not in existing:
                return candidate
            index += 1

    def _resolve_sync_files_root(self, sync_root: Path) -> Path:
        sync_root_resolved = sync_root.resolve()
        settings_path = sync_root / "settings" / "storage.json"
        if settings_path.exists():
            try:
                data = json.loads(settings_path.read_text(encoding="utf-8"))
                root = data.get("materials_root")
                if root:
                    root_path = Path(str(root).strip())
                    if not root_path.is_absolute():
                        root_path = (sync_root / root_path).resolve()
                    else:
                        root_path = root_path.resolve()
                    try:
                        root_path.relative_to(sync_root_resolved)
                    except ValueError:
                        self._log_action("sync_files_root_rejected", str(root_path))
                        root_path = None
                    if root_path is not None and root_path.exists() and root_path.is_dir():
                        return root_path
                    if root_path is not None:
                        self._log_action("sync_files_root_missing", str(root_path))
            except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
                self._log_action("sync_files_root_error", str(exc))
        files_root = sync_root / "files"
        return files_root
