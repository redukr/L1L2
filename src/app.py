"""Application entry point."""
import sys
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication
from .models.database import Database
from .controllers.main_controller import MainController
from .ui.main_window import MainWindow
from .services.demo_data import seed_demo_data
from .services.i18n import I18nManager


def main() -> int:
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("EduDesk")
    QCoreApplication.setOrganizationDomain("local")
    QCoreApplication.setApplicationName("Educational Program Manager")
    settings = QSettings()
    i18n = I18nManager(settings)
    i18n.load_from_settings()
    database = Database()
    seed_demo_data(database)
    controller = MainController(database)
    window = MainWindow(controller, i18n, settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
