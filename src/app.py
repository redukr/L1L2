"""Application entry point."""
import sys
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication
from .models.database import Database
from .controllers.main_controller import MainController
from .ui.main_window import MainWindow
from .services.demo_data import seed_demo_data
from .services.i18n import I18nManager
from .services.app_paths import resolve_app_path, make_relative_to_app
from .services.file_storage import FileStorageManager


def main() -> int:
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("EduDesk")
    QCoreApplication.setOrganizationDomain("local")
    QCoreApplication.setApplicationName("Educational Program Manager")
    bootstrap_settings = QSettings()
    settings_path = bootstrap_settings.value("app/ui_settings_path", "")
    if settings_path:
        resolved_settings = resolve_app_path(settings_path)
        if str(resolved_settings) != str(settings_path):
            bootstrap_settings.setValue("app/ui_settings_path", make_relative_to_app(resolved_settings))
        settings = QSettings(str(resolved_settings), QSettings.IniFormat)
    else:
        settings = QSettings()
    i18n = I18nManager(settings)
    i18n.load_from_settings()
    db_path = bootstrap_settings.value("app/db_path", "")
    resolved_db = resolve_app_path(db_path) if db_path else None
    if db_path and resolved_db and str(resolved_db) != str(db_path):
        bootstrap_settings.setValue("app/db_path", make_relative_to_app(resolved_db))
    database = Database(str(resolved_db) if resolved_db and str(resolved_db) else None)
    FileStorageManager().migrate_legacy_materials(database)
    seed_demo_data(database)
    controller = MainController(database)
    window = MainWindow(controller, i18n, settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
