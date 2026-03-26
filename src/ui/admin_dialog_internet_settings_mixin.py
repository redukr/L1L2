"""Internet DB settings and connection operations for AdminDialog."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox


class AdminDialogInternetSettingsMixin:
    """Internet DB UI settings storage and connection checks."""

    def _default_internet_db_settings(self) -> dict:
        return {
            "host": "localhost",
            "port": "3306",
            "database": "",
        }

    def _load_internet_db_settings(self) -> None:
        defaults = self._default_internet_db_settings()
        self.internet_db_host.setText(self.bootstrap_settings.value("internet_db/host", defaults["host"]))
        self.internet_db_port.setText(self.bootstrap_settings.value("internet_db/port", defaults["port"]))
        self.internet_db_name.setText(self.bootstrap_settings.value("internet_db/database", defaults["database"]))
        self.internet_db_user.setText("")
        self.internet_db_password.setText("")
        self.internet_db_status.setText(self.tr("Not connected"))
        self.internet_db_status.setStyleSheet("")
        self._set_internet_db_indicator("idle")

    def _set_internet_db_indicator(self, state: str) -> None:
        color = "#9aa0a6"
        if state == "ok":
            color = "#1b7f3b"
        elif state == "error":
            color = "#a11f1f"
        self.internet_db_indicator.setStyleSheet(
            f"background-color: {color}; border-radius: 5px;"
        )

    def _save_internet_db_settings(self, show_message: bool = True) -> None:
        self.bootstrap_settings.setValue("internet_db/host", self.internet_db_host.text().strip())
        self.bootstrap_settings.setValue("internet_db/port", self.internet_db_port.text().strip())
        self.bootstrap_settings.setValue("internet_db/database", self.internet_db_name.text().strip())
        self.bootstrap_settings.remove("internet_db/user")
        self.bootstrap_settings.remove("internet_db/password")
        self.bootstrap_settings.sync()
        self._log_action("save_internet_settings", self.internet_db_host.text().strip())
        if hasattr(self, "log_table"):
            self._refresh_log_tab()
        if show_message:
            QMessageBox.information(self, self.tr("Settings"), self.tr("Internet DB settings saved."))

    def _connect_internet_database(self) -> None:
        host = self.internet_db_host.text().strip()
        port_text = self.internet_db_port.text().strip()
        database = self.internet_db_name.text().strip()
        user = self.internet_db_user.text().strip()
        password = self.internet_db_password.text()

        if not host or not port_text or not database or not user:
            QMessageBox.warning(
                self,
                self.tr("Validation"),
                self.tr("Host, port, database and login are required."),
            )
            return
        try:
            port = int(port_text)
        except ValueError:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Port must be a number."))
            return

        try:
            import pymysql
        except ImportError:
            QMessageBox.warning(
                self,
                self.tr("Import error"),
                self.tr("PyMySQL is not installed. Install dependencies from requirements.txt."),
            )
            return

        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=5,
                read_timeout=5,
                write_timeout=5,
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT DATABASE(), VERSION()")
                row = cursor.fetchone()
            conn.close()
            active_db = row[0] if row and len(row) > 0 else database
            version = row[1] if row and len(row) > 1 else "-"
            self.internet_db_status.setText(
                self.tr("Connected: {0} (DB: {1}, MySQL: {2})").format(host, active_db, version)
            )
            self.internet_db_status.setStyleSheet("color: #1b7f3b;")
            self._set_internet_db_indicator("ok")
            self._save_internet_db_settings(show_message=False)
            self._log_action("internet_connect_ok", f"{host}:{port}/{database}")
            if hasattr(self, "log_table"):
                self._refresh_log_tab()
        except (pymysql.MySQLError, OSError, ValueError, TypeError) as exc:
            self.internet_db_status.setText(self.tr("Connection failed"))
            self.internet_db_status.setStyleSheet("color: #a11f1f;")
            self._set_internet_db_indicator("error")
            self._log_action("internet_connect_failed", str(exc))
            if hasattr(self, "log_table"):
                self._refresh_log_tab()
            QMessageBox.warning(self, self.tr("Connection failed"), str(exc))
