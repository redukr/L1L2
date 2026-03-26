"""Settings/password helpers extracted from AdminDialog."""

from __future__ import annotations

import base64
import json

from PySide6.QtCore import QByteArray, QSettings
from PySide6.QtWidgets import QFileDialog, QDialog, QMessageBox

from ..services.app_paths import get_settings_dir
from ..services.auth_service import AuthService
from .dialogs import PasswordDialog


class AdminDialogSettingsMixin:
    """Settings/password operations for AdminDialog."""

    def _export_user_settings(self) -> None:
        default_path = get_settings_dir() / "user_settings.ini"
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export user settings"),
            str(default_path),
            self.tr("Settings (*.ini);;All files (*)"),
        )
        if not path:
            return
        try:
            export_settings = QSettings(path, QSettings.IniFormat)
            export_settings.clear()
            for key in self.settings.allKeys():
                export_settings.setValue(key, self.settings.value(key))
            export_settings.sync()
        except (OSError, ValueError, TypeError) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(self, self.tr("Export user settings"), self.tr("User settings exported."))

    def _import_user_settings(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import user settings"),
            "",
            self.tr("Settings (*.ini);;All files (*)"),
        )
        if not path:
            return
        if QMessageBox.question(
            self,
            self.tr("Confirm"),
            self.tr("Replace the current user settings with the selected file?"),
        ) != QMessageBox.Yes:
            return
        try:
            import_settings = QSettings(path, QSettings.IniFormat)
            self.settings.clear()
            for key in import_settings.allKeys():
                self.settings.setValue(key, import_settings.value(key))
            self.settings.sync()
            self.i18n.load_from_settings()
        except (OSError, ValueError, TypeError) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(
            self,
            self.tr("Import user settings"),
            self.tr("User settings imported. Restart the app."),
        )

    def _save_user_settings(self) -> None:
        try:
            self.settings.sync()
        except (OSError, ValueError, TypeError) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(self, self.tr("Save user settings"), self.tr("User settings saved."))

    def _prompt_new_password(self, title: str, label: str) -> str | None:
        first = PasswordDialog(self, title=title, label=label)
        if first.exec() != QDialog.Accepted:
            return None
        password = first.get_password()
        min_length = AuthService.MIN_PASSWORD_LENGTH
        if len(password) < min_length:
            QMessageBox.warning(
                self,
                self.tr("Validation"),
                self.tr("Password must be at least {0} characters.").format(min_length),
            )
            return None
        confirm = PasswordDialog(self, title=title, label=self.tr("Confirm password:"))
        if confirm.exec() != QDialog.Accepted:
            return None
        if confirm.get_password() != password:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Passwords do not match."))
            return None
        return password

    def _change_admin_password(self) -> None:
        if not self._require_current_admin_password():
            return
        new_password = self._prompt_new_password(
            self.tr("Change admin password"),
            self.tr("New admin password:"),
        )
        if not new_password:
            return
        self.controller.auth_service.set_admin_password(new_password)
        QMessageBox.information(self, self.tr("Settings"), self.tr("Admin password updated."))

    def _change_editor_password(self) -> None:
        if not self._require_current_admin_password():
            return
        new_password = self._prompt_new_password(
            self.tr("Change editor password"),
            self.tr("New editor password:"),
        )
        if not new_password:
            return
        self.controller.auth_service.set_editor_password(new_password)
        QMessageBox.information(self, self.tr("Settings"), self.tr("Editor password updated."))

    def _require_current_admin_password(self) -> bool:
        current_dialog = PasswordDialog(
            self,
            title=self.tr("Admin verification"),
            label=self.tr("Current admin password:"),
        )
        if current_dialog.exec() != QDialog.Accepted:
            return False
        if not self.controller.auth_service.verify_admin_password(current_dialog.get_password()):
            QMessageBox.warning(self, self.tr("Access denied"), self.tr("Invalid admin password."))
            return False
        return True

    def _serialize_settings(self, settings: QSettings) -> str:
        data = {}
        for key in settings.allKeys():
            value = settings.value(key)
            if isinstance(value, QByteArray):
                data[key] = {
                    "__type__": "QByteArray",
                    "data": base64.b64encode(bytes(value)).decode("ascii"),
                }
            else:
                data[key] = value
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _deserialize_settings(self, settings: QSettings, content: str) -> None:
        data = json.loads(content)
        settings.clear()
        for key, value in data.items():
            if isinstance(value, dict) and value.get("__type__") == "QByteArray":
                raw = base64.b64decode(value.get("data", ""))
                settings.setValue(key, QByteArray(raw))
            else:
                settings.setValue(key, value)
