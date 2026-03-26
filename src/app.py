"""Application entry point."""
import sys
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication
from .models.database import Database
from .controllers.main_controller import MainController
from .ui.main_window import MainWindow
from .services.i18n import I18nManager
from .services.app_paths import (
    resolve_app_path,
    make_relative_to_app,
    get_database_dir,
    get_settings_dir,
)
from .services.file_storage import FileStorageManager


def _resolve_existing_or_fallback(path_value: str, fallback_path) -> tuple[str, bool]:  # noqa: ANN001
    """Return preferred configured path when it exists, otherwise use fallback if available."""
    if path_value:
        resolved = resolve_app_path(path_value)
        if resolved.exists():
            return str(resolved), str(resolved) != str(path_value)
    if fallback_path and fallback_path.exists():
        return str(fallback_path), True
    if path_value:
        resolved = resolve_app_path(path_value)
        return str(resolved), str(resolved) != str(path_value)
    return "", False


def main() -> int:
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("EduDesk")
    QCoreApplication.setOrganizationDomain("local")
    QCoreApplication.setApplicationName("Educational Program Manager")
    bootstrap_settings = QSettings()
    settings_path = bootstrap_settings.value("app/ui_settings_path", "")
    resolved_settings_path, settings_changed = _resolve_existing_or_fallback(
        str(settings_path or ""),
        get_settings_dir() / "user_settings.ini",
    )
    if resolved_settings_path:
        if settings_changed:
            bootstrap_settings.setValue("app/ui_settings_path", make_relative_to_app(resolved_settings_path))
            bootstrap_settings.sync()
        resolved_settings = resolve_app_path(resolved_settings_path)
        settings = QSettings(str(resolved_settings), QSettings.IniFormat)
    else:
        settings = QSettings()
    i18n = I18nManager(settings)
    i18n.load_from_settings()
    db_path = bootstrap_settings.value("app/db_path", "")
    resolved_db_path, db_changed = _resolve_existing_or_fallback(
        str(db_path or ""),
        get_database_dir() / "education.db",
    )
    resolved_db = resolve_app_path(resolved_db_path) if resolved_db_path else None
    if db_changed and resolved_db:
        bootstrap_settings.setValue("app/db_path", make_relative_to_app(resolved_db))
        bootstrap_settings.sync()
    database = Database(str(resolved_db) if resolved_db and str(resolved_db) else None)
    FileStorageManager().migrate_legacy_materials(database)
    controller = MainController(database)
    window = MainWindow(controller, i18n, settings)
    if not window.ensure_teacher_login():
        return 0
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
