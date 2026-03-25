"""Internet sync workflows extracted from AdminDialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QMessageBox

from ..ui.dialogs import SyncConflictDialog


def resolve_sync_conflict(dialog, table: str, sync_uuid: str, local_row: dict, remote_row: dict, compare_columns: list[str]) -> str:  # noqa: ANN001,E501
    conflict_dialog = SyncConflictDialog(
        table_name=table,
        record_uuid=sync_uuid,
        local_text=dialog.internet_sync_service.format_conflict_row(local_row, compare_columns),
        remote_text=dialog.internet_sync_service.format_conflict_row(remote_row, compare_columns),
        parent=dialog,
    )
    if conflict_dialog.exec() != QDialog.Accepted:
        raise RuntimeError(dialog.tr("Synchronization canceled by user."))
    return conflict_dialog.get_choice()


def connect_internet_database(dialog) -> None:  # noqa: ANN001
    host = dialog.internet_db_host.text().strip()
    port_text = dialog.internet_db_port.text().strip()
    database = dialog.internet_db_name.text().strip()
    user = dialog.internet_db_user.text().strip()
    password = dialog.internet_db_password.text()

    if not host or not port_text or not database or not user:
        QMessageBox.warning(
            dialog,
            dialog.tr("Validation"),
            dialog.tr("Host, port, database and login are required."),
        )
        return
    try:
        port = int(port_text)
    except ValueError:
        QMessageBox.warning(dialog, dialog.tr("Validation"), dialog.tr("Port must be a number."))
        return

    try:
        import pymysql
    except ImportError:
        QMessageBox.warning(
            dialog,
            dialog.tr("Import error"),
            dialog.tr("PyMySQL is not installed. Install dependencies from requirements.txt."),
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
    except pymysql.MySQLError as exc:
        dialog.internet_db_status.setText(dialog.tr("Connection failed"))
        dialog.internet_db_status.setStyleSheet("color: #a11f1f;")
        dialog._set_internet_db_indicator("error")
        dialog._log_action("internet_connect_failed", str(exc))
        if hasattr(dialog, "log_table"):
            dialog._refresh_log_tab()
        QMessageBox.warning(dialog, dialog.tr("Connection failed"), str(exc))
        return

    active_db = row[0] if row and len(row) > 0 else database
    version = row[1] if row and len(row) > 1 else "-"
    dialog.internet_db_status.setText(
        dialog.tr("Connected: {0} (DB: {1}, MySQL: {2})").format(host, active_db, version)
    )
    dialog.internet_db_status.setStyleSheet("color: #1b7f3b;")
    dialog._set_internet_db_indicator("ok")
    dialog._save_internet_db_settings(show_message=False)
    dialog._log_action("internet_connect_ok", f"{host}:{port}/{database}")
    if hasattr(dialog, "log_table"):
        dialog._refresh_log_tab()


def synchronize_internet_database(dialog) -> None:  # noqa: ANN001
    host = dialog.internet_db_host.text().strip()
    port_text = dialog.internet_db_port.text().strip()
    database = dialog.internet_db_name.text().strip()
    user = dialog.internet_db_user.text().strip()
    password = dialog.internet_db_password.text()
    direction = dialog.internet_sync_direction.currentData() or "push"

    if not host or not port_text or not database or not user:
        QMessageBox.warning(
            dialog,
            dialog.tr("Validation"),
            dialog.tr("Host, port, database and login are required."),
        )
        return
    try:
        port = int(port_text)
    except ValueError:
        QMessageBox.warning(dialog, dialog.tr("Validation"), dialog.tr("Port must be a number."))
        return

    confirm_text = (
        dialog.tr("Synchronize local changes to Internet DB (merge, no full overwrite)?")
        if direction == "push"
        else dialog.tr("Synchronize Internet DB changes to local database (merge, no full overwrite)?")
    )
    if QMessageBox.question(dialog, dialog.tr("Confirm synchronization"), confirm_text) != QMessageBox.Yes:
        return

    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError:
        QMessageBox.warning(
            dialog,
            dialog.tr("Import error"),
            dialog.tr("PyMySQL is not installed. Install dependencies from requirements.txt."),
        )
        return

    try:
        mysql_conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=8,
            read_timeout=30,
            write_timeout=30,
            cursorclass=DictCursor,
            autocommit=False,
        )
    except pymysql.MySQLError as exc:
        dialog.internet_db_status.setText(dialog.tr("Connection failed"))
        dialog.internet_db_status.setStyleSheet("color: #a11f1f;")
        dialog._set_internet_db_indicator("error")
        QMessageBox.warning(dialog, dialog.tr("Connection failed"), str(exc))
        return

    sync_stats: list[str] = []
    try:
        dialog.internet_sync_service.ensure_mysql_sync_schema(mysql_conn)
        if direction == "push":
            with dialog.controller.db.get_connection() as sqlite_conn:
                with mysql_conn.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                sync_stats.extend(
                    dialog.internet_sync_service.sync_entity_tables(
                        sqlite_conn,
                        mysql_conn,
                        direction="push",
                        conflict_resolver=dialog._resolve_sync_conflict,
                    )
                )
                sync_stats.extend(
                    dialog.internet_sync_service.sync_link_tables(
                        sqlite_conn,
                        mysql_conn,
                        direction="push",
                    )
                )
                with mysql_conn.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                mysql_conn.commit()
        else:
            with dialog.controller.db.get_connection() as sqlite_conn:
                sqlite_conn.execute("PRAGMA foreign_keys = OFF")
                sync_stats.extend(
                    dialog.internet_sync_service.sync_entity_tables(
                        sqlite_conn,
                        mysql_conn,
                        direction="pull",
                        conflict_resolver=dialog._resolve_sync_conflict,
                    )
                )
                sync_stats.extend(
                    dialog.internet_sync_service.sync_link_tables(
                        sqlite_conn,
                        mysql_conn,
                        direction="pull",
                    )
                )
                sqlite_conn.execute("PRAGMA foreign_keys = ON")
            dialog._refresh_all()
    except (pymysql.MySQLError, RuntimeError, ValueError) as exc:
        _rollback_sync(dialog, mysql_conn, exc)
        return
    finally:
        mysql_conn.close()

    dialog.internet_db_status.setText(dialog.tr("Synchronization completed"))
    dialog.internet_db_status.setStyleSheet("color: #1b7f3b;")
    dialog._set_internet_db_indicator("ok")
    dialog._save_internet_db_settings(show_message=False)
    QMessageBox.information(
        dialog,
        dialog.tr("Synchronization"),
        dialog.tr("Synchronization completed.\nRows processed:\n{0}").format("\n".join(sync_stats)),
    )
    dialog._log_action("internet_sync_completed", f"direction={direction}")
    if hasattr(dialog, "log_table"):
        dialog._refresh_log_tab()


def _rollback_sync(dialog, mysql_conn, exc: Exception) -> None:  # noqa: ANN001
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    except Exception:
        dialog._log_action("internet_sync_foreign_key_restore_failed", "Could not restore FOREIGN_KEY_CHECKS")
    mysql_conn.rollback()
    dialog.internet_db_status.setText(dialog.tr("Synchronization failed"))
    dialog.internet_db_status.setStyleSheet("color: #a11f1f;")
    dialog._set_internet_db_indicator("error")
    dialog._log_action("internet_sync_failed", str(exc))
    if hasattr(dialog, "log_table"):
        dialog._refresh_log_tab()
    QMessageBox.warning(dialog, dialog.tr("Synchronization failed"), str(exc))
