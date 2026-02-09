"""Application entry point."""
import sys
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication
from .models.database import Database
from .controllers.main_controller import MainController
from .ui.main_window import MainWindow
from .services.demo_data import seed_demo_data
from .services.i18n import I18nManager
from .services.file_storage import FileStorageManager


def main() -> int:
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("EduDesk")
    QCoreApplication.setOrganizationDomain("local")
    QCoreApplication.setApplicationName("Educational Program Manager")
    bootstrap_settings = QSettings()
    settings_path = bootstrap_settings.value("app/ui_settings_path", "")
    if settings_path:
        settings = QSettings(settings_path, QSettings.IniFormat)
    else:
        settings = QSettings()
    i18n = I18nManager(settings)
    i18n.load_from_settings()
    db_path = bootstrap_settings.value("app/db_path", "")
    database = Database(db_path or None)
    FileStorageManager().migrate_legacy_materials(database)
    seed_demo_data(database)
    controller = MainController(database)
    window = MainWindow(controller, i18n, settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
