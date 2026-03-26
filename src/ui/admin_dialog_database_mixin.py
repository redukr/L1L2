"""Database/settings path helpers extracted from AdminDialog."""

from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3

from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..services.app_paths import get_settings_dir, make_relative_to_app, resolve_app_path


class AdminDialogDatabaseMixin:
    """Database diagnostics, import/export and path setting operations."""

    def _database_diagnostics(self) -> str:
        path = self.controller.db.db_path
        status = "unknown"
        con = None
        try:
            con = sqlite3.connect(path)
            rows = con.execute("PRAGMA integrity_check;").fetchall()
            status = ", ".join(row[0] for row in rows)
        except sqlite3.Error as exc:
            status = f"error: {exc}"
        finally:
            if con is not None:
                con.close()
        return f"DB: {path}\nIntegrity: {status}"

    def _check_database(self) -> None:
        diagnostics = self._database_diagnostics()
        QMessageBox.information(self, self.tr("Check database"), diagnostics)

    def _cleanup_unused_data(self) -> None:
        counts = self.controller.get_unused_data_counts()
        total = sum(counts.values())
        if total == 0:
            QMessageBox.information(self, self.tr("Cleanup unused data"), self.tr("No unused data found."))
            return
        details = [
            f"{self.tr('Programs')}: {counts['programs']}",
            f"{self.tr('Disciplines')}: {counts['disciplines']}",
            f"{self.tr('Topics')}: {counts['topics']}",
            f"{self.tr('Lessons')}: {counts['lessons']}",
            f"{self.tr('Questions')}: {counts['questions']}",
            f"{self.tr('Materials')}: {counts['materials']}",
        ]
        if QMessageBox.question(
            self,
            self.tr("Cleanup unused data"),
            self.tr("Delete unused records?\n") + "\n".join(details),
        ) != QMessageBox.Yes:
            return
        removed = self.controller.cleanup_unused_data()
        details = [
            f"{self.tr('Programs')}: {removed['programs']}",
            f"{self.tr('Disciplines')}: {removed['disciplines']}",
            f"{self.tr('Topics')}: {removed['topics']}",
            f"{self.tr('Lessons')}: {removed['lessons']}",
            f"{self.tr('Questions')}: {removed['questions']}",
            f"{self.tr('Materials')}: {removed['materials']}",
        ]
        QMessageBox.information(
            self,
            self.tr("Cleanup unused data"),
            self.tr("Deleted records:\n") + "\n".join(details),
        )
        self._refresh_all()

    def _change_database_path(self) -> None:
        current = self.bootstrap_settings.value("app/db_path", "")
        start_dir = str(resolve_app_path(current)) if current else str(self.controller.db.db_path)
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Select database file"),
            start_dir,
            self.tr("Database files (*.db);;All files (*)"),
        )
        if not path:
            return
        self.bootstrap_settings.setValue("app/db_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.database_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Database selection saved. Restart the app to apply changes."),
        )

    def _change_ui_settings_path(self) -> None:
        current = self.bootstrap_settings.value("app/ui_settings_path", "")
        start_dir = str(resolve_app_path(current)) if current else str(get_settings_dir() / "user_settings.ini")
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Select UI settings file"),
            start_dir,
            self.tr("Settings (*.ini);;All files (*)"),
        )
        if not path:
            return
        self.bootstrap_settings.setValue("app/ui_settings_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.ui_settings_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("UI settings path saved. Restart the app to apply changes."),
        )

    def _change_translations_path(self) -> None:
        current = self.bootstrap_settings.value("app/translations_path", "")
        start_dir = str(resolve_app_path(current))
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select translations file"),
            start_dir,
            self.tr("Translation files (*.ts *.qm);;All files (*)"),
        )
        if not path:
            return
        self.bootstrap_settings.setValue("app/translations_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.translations_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Translations path saved. Restart the app to apply changes."),
        )

    def _change_materials_location(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select materials folder"),
            str(self.file_storage.files_root),
        )
        if not path:
            return
        new_root = Path(path)
        try:
            self.file_storage.move_storage(self.controller.db, new_root)
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        self._refresh_settings()

    def _export_database(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export database"),
            "education.db",
            self.tr("Database (*.db);;All files (*)"),
        )
        if not path:
            return
        try:
            self._copy_database_with_backup(Path(self.controller.db.db_path), Path(path))
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(self, self.tr("Export database"), self.tr("Database exported."))

    def _import_database(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import database"),
            "",
            self.tr("Database (*.db);;All files (*)"),
        )
        if not path:
            return
        if QMessageBox.question(
            self,
            self.tr("Confirm"),
            self.tr("Replace the current database with the selected file?"),
        ) != QMessageBox.Yes:
            return
        try:
            self._copy_database_with_backup(Path(path), Path(self.controller.db.db_path))
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(
            self,
            self.tr("Import database"),
            self.tr("Database imported. Restart the app."),
        )

    @staticmethod
    def _copy_database_with_backup(source_path: Path, target_path: Path) -> None:
        source_path = source_path.resolve()
        target_path = target_path.resolve()
        if source_path == target_path:
            return
        if not source_path.exists():
            raise FileNotFoundError(f"Database file not found: {source_path}")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(str(source_path))) as source_conn:
            with closing(sqlite3.connect(str(target_path))) as target_conn:
                source_conn.backup(target_conn)

    def _repair_database(self) -> None:
        src_path = Path(self.controller.db.db_path)
        default_path = src_path.with_name(f"{src_path.stem}_recovered.db")
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Repair database"),
            str(default_path),
            self.tr("Database (*.db);;All files (*)"),
        )
        if not path:
            return
        try:
            conn = sqlite3.connect(src_path)
            conn.text_factory = lambda b: b.decode(errors="ignore")
            try:
                dump_lines = list(conn.iterdump())
            finally:
                conn.close()

            skip_tokens = ("_fts_config", "_fts_docsize", "_fts_data", "_fts_idx")
            filtered = [line for line in dump_lines if not any(t in line.lower() for t in skip_tokens)]

            out = sqlite3.connect(path)
            try:
                out.executescript("\n".join(filtered))
                out.commit()
            finally:
                out.close()
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        self.bootstrap_settings.setValue("app/db_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.database_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Database repaired. Restart the app to apply changes."),
        )
