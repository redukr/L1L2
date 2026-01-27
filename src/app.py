"""Application entry point."""
import sys
from PySide6.QtWidgets import QApplication
from .models.database import Database
from .controllers.main_controller import MainController
from .ui.main_window import MainWindow
from .services.demo_data import seed_demo_data


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Educational Program Manager")
    database = Database()
    seed_demo_data(database)
    controller = MainController(database)
    window = MainWindow(controller)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
