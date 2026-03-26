"""Internet database synchronization core for AdminDialog."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from uuid import uuid4

from PySide6.QtWidgets import QDialog, QMessageBox

from .dialogs import SyncConflictDialog
from .internet_sync_schema_sql import MYSQL_SYNC_SCHEMA_DDL


class AdminDialogInternetSyncMixin:
    """MySQL/SQLite schema+data synchronization helpers."""

    def _internet_sync_tables(self) -> list[str]:
        return self._internet_sync_entity_tables() + self._internet_sync_link_tables()

    def _internet_sync_entity_tables(self) -> list[str]:
        return [
            "teachers",
            "educational_programs",
            "disciplines",
            "topics",
            "lesson_types",
            "lessons",
            "questions",
            "material_types",
            "methodical_materials",
        ]

    def _internet_sync_link_tables(self) -> list[str]:
        return [
            "program_disciplines",
            "discipline_topics",
            "program_topics",
            "topic_lessons",
            "lesson_questions",
            "teacher_materials",
            "teacher_disciplines",
            "material_associations",
        ]

    def _fetch_sqlite_table(self, sqlite_conn, table: str) -> tuple[list[str], list[dict]]:  # noqa: ANN001
        cursor = sqlite_conn.cursor()
        cursor.execute(f'SELECT * FROM "{table}"')
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(row) for row in cursor.fetchall()]
        return columns, rows

    def _sqlite_table_columns(self, sqlite_conn, table: str) -> list[str]:  # noqa: ANN001
        cursor = sqlite_conn.cursor()
        cursor.execute(f'PRAGMA table_info("{table}")')
        return [row["name"] for row in cursor.fetchall()]

    def _fetch_mysql_table(self, mysql_conn, table: str) -> tuple[list[str], list[dict]]:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{table}`")
            rows = cursor.fetchall()
            if not rows:
                cursor.execute(f"SHOW COLUMNS FROM `{table}`")
                columns = [row["Field"] for row in cursor.fetchall()]
                return columns, []
            columns = list(rows[0].keys())
        return columns, rows

    def _mysql_table_exists(self, mysql_conn, table: str) -> bool:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE %s", (table,))
            return cursor.fetchone() is not None

    def _mysql_table_columns(self, mysql_conn, table: str) -> list[str]:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            return [row["Field"] for row in cursor.fetchall()]

    def _sqlite_primary_keys(self, sqlite_conn, table: str) -> list[str]:  # noqa: ANN001
        cursor = sqlite_conn.cursor()
        cursor.execute(f'PRAGMA table_info("{table}")')
        info = cursor.fetchall()
        ordered = sorted((row for row in info if row["pk"]), key=lambda row: row["pk"])
        return [row["name"] for row in ordered]

    def _mysql_primary_keys(self, mysql_conn, table: str) -> list[str]:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SHOW KEYS FROM `{table}` WHERE Key_name = 'PRIMARY'")
            rows = cursor.fetchall()
        rows = sorted(rows, key=lambda row: row.get("Seq_in_index", 0))
        return [row["Column_name"] for row in rows]

    def _map_sqlite_type_to_mysql(self, sqlite_type: str) -> str:
        t = (sqlite_type or "").upper()
        if "INT" in t:
            return "BIGINT"
        if "REAL" in t or "FLOA" in t or "DOUB" in t:
            return "DOUBLE"
        if "BLOB" in t:
            return "LONGBLOB"
        if "CHAR" in t or "CLOB" in t or "TEXT" in t:
            return "LONGTEXT"
        if "DATE" in t or "TIME" in t:
            return "DATETIME"
        return "LONGTEXT"

    def _ensure_mysql_table_columns(self, mysql_conn, sqlite_conn, table: str) -> None:  # noqa: ANN001
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f'PRAGMA table_info("{table}")')
        sqlite_info = sqlite_cursor.fetchall()
        mysql_columns = set(self._mysql_table_columns(mysql_conn, table))
        with mysql_conn.cursor() as cursor:
            for col in sqlite_info:
                col_name = col["name"]
                if col_name in mysql_columns:
                    continue
                col_type = self._map_sqlite_type_to_mysql(col["type"] or "")
                cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{col_name}` {col_type} NULL")
        mysql_conn.commit()

    def _ensure_mysql_sync_schema(self, mysql_conn) -> None:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            for stmt in MYSQL_SYNC_SCHEMA_DDL:
                cursor.execute(stmt)
        mysql_conn.commit()

    def _ensure_sqlite_sync_uuid(self, sqlite_conn, table: str) -> None:  # noqa: ANN001
        columns = set(self._sqlite_table_columns(sqlite_conn, table))
        if "sync_uuid" not in columns:
            sqlite_conn.execute(f'ALTER TABLE "{table}" ADD COLUMN sync_uuid TEXT')
        sqlite_conn.execute(
            f'CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_sync_uuid ON "{table}"(sync_uuid)'
        )
        cursor = sqlite_conn.cursor()
        cursor.execute(f'SELECT id FROM "{table}" WHERE sync_uuid IS NULL OR sync_uuid = ""')
        for row in cursor.fetchall():
            sqlite_conn.execute(
                f'UPDATE "{table}" SET sync_uuid = ? WHERE id = ?',
                (str(uuid4()), row["id"]),
            )

    def _ensure_mysql_sync_uuid(self, mysql_conn, table: str) -> None:  # noqa: ANN001
        columns = set(self._mysql_table_columns(mysql_conn, table))
        with mysql_conn.cursor() as cursor:
            if "sync_uuid" not in columns:
                cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN sync_uuid VARCHAR(36) NULL")
            cursor.execute(
                f"UPDATE `{table}` SET sync_uuid = UUID() WHERE sync_uuid IS NULL OR sync_uuid = ''"
            )
            cursor.execute(f"SHOW INDEX FROM `{table}` WHERE Column_name = 'sync_uuid'")
            if cursor.fetchone() is None:
                cursor.execute(f"CREATE UNIQUE INDEX idx_{table}_sync_uuid ON `{table}`(sync_uuid)")
        mysql_conn.commit()

    def _normalize_sync_value(self, value):  # noqa: ANN001
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        if isinstance(value, (int, float)):
            return float(value)
        return str(value)

    def _rows_differ(self, left: dict, right: dict, columns: list[str]) -> bool:
        for col in columns:
            if self._normalize_sync_value(left.get(col)) != self._normalize_sync_value(right.get(col)):
                return True
        return False

    def _conflict_compare_columns(self, columns: list[str]) -> list[str]:
        ignored = {"id", "sync_uuid", "created_at", "updated_at"}
        return [col for col in columns if col not in ignored]

    def _format_conflict_row(self, row: dict, columns: list[str]) -> str:
        payload = {col: row.get(col) for col in columns}
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    def _resolve_sync_conflict(
        self,
        table: str,
        sync_uuid: str,
        local_row: dict,
        remote_row: dict,
        compare_columns: list[str],
    ) -> str:
        dialog = SyncConflictDialog(
            table_name=table,
            record_uuid=sync_uuid,
            local_text=self._format_conflict_row(local_row, compare_columns),
            remote_text=self._format_conflict_row(remote_row, compare_columns),
            parent=self,
        )
        if dialog.exec() != QDialog.Accepted:
            raise RuntimeError(self.tr("Synchronization canceled by user."))
        return dialog.get_choice()

    def _mysql_insert_entity(self, mysql_conn, table: str, row: dict, common_columns: list[str]) -> None:  # noqa: ANN001
        insert_columns = [col for col in common_columns if col != "id"]
        if not insert_columns:
            return
        with mysql_conn.cursor() as cursor:
            cols_sql = ", ".join(f"`{col}`" for col in insert_columns)
            placeholders = ", ".join(["%s"] * len(insert_columns))
            sql = f"INSERT INTO `{table}` ({cols_sql}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row.get(col) for col in insert_columns))

    def _mysql_update_entity_by_uuid(
        self, mysql_conn, table: str, row: dict, common_columns: list[str]
    ) -> None:  # noqa: ANN001
        update_columns = [col for col in common_columns if col not in {"id", "sync_uuid"}]
        if not update_columns:
            return
        set_clause = ", ".join(f"`{col}` = %s" for col in update_columns)
        values = [row.get(col) for col in update_columns]
        values.append(row.get("sync_uuid"))
        with mysql_conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE `{table}` SET {set_clause} WHERE sync_uuid = %s",
                tuple(values),
            )

    def _sqlite_insert_entity(self, sqlite_conn, table: str, row: dict, common_columns: list[str]) -> None:  # noqa: ANN001
        insert_columns = [col for col in common_columns if col != "id"]
        if not insert_columns:
            return
        cols_sql = ", ".join(f'"{col}"' for col in insert_columns)
        placeholders = ", ".join(["?"] * len(insert_columns))
        sqlite_conn.execute(
            f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders})',
            tuple(row.get(col) for col in insert_columns),
        )

    def _sqlite_update_entity_by_uuid(
        self, sqlite_conn, table: str, row: dict, common_columns: list[str]
    ) -> None:  # noqa: ANN001
        update_columns = [col for col in common_columns if col not in {"id", "sync_uuid"}]
        if not update_columns:
            return
        set_clause = ", ".join(f'"{col}" = ?' for col in update_columns)
        values = [row.get(col) for col in update_columns]
        values.append(row.get("sync_uuid"))
        sqlite_conn.execute(
            f'UPDATE "{table}" SET {set_clause} WHERE sync_uuid = ?',
            tuple(values),
        )

    def _uuid_maps_sqlite(self, sqlite_conn, table: str) -> tuple[dict[int, str], dict[str, int]]:  # noqa: ANN001
        cursor = sqlite_conn.cursor()
        cursor.execute(f'SELECT id, sync_uuid FROM "{table}" WHERE sync_uuid IS NOT NULL AND sync_uuid <> ""')
        id_to_uuid: dict[int, str] = {}
        uuid_to_id: dict[str, int] = {}
        for row in cursor.fetchall():
            id_to_uuid[row["id"]] = row["sync_uuid"]
            uuid_to_id[row["sync_uuid"]] = row["id"]
        return id_to_uuid, uuid_to_id

    def _uuid_maps_mysql(self, mysql_conn, table: str) -> tuple[dict[int, str], dict[str, int]]:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SELECT id, sync_uuid FROM `{table}` WHERE sync_uuid IS NOT NULL AND sync_uuid <> ''")
            rows = cursor.fetchall()
        id_to_uuid: dict[int, str] = {}
        uuid_to_id: dict[str, int] = {}
        for row in rows:
            id_to_uuid[row["id"]] = row["sync_uuid"]
            uuid_to_id[row["sync_uuid"]] = row["id"]
        return id_to_uuid, uuid_to_id

    def _sync_entity_tables(self, sqlite_conn, mysql_conn, direction: str) -> list[str]:  # noqa: ANN001
        stats: list[str] = []
        for table in self._internet_sync_entity_tables():
            if not self._mysql_table_exists(mysql_conn, table):
                raise ValueError(f"Internet DB is missing table: {table}")
            self._ensure_mysql_table_columns(mysql_conn, sqlite_conn, table)
            self._ensure_sqlite_sync_uuid(sqlite_conn, table)
            self._ensure_mysql_sync_uuid(mysql_conn, table)
            sqlite_columns = self._sqlite_table_columns(sqlite_conn, table)
            mysql_columns = self._mysql_table_columns(mysql_conn, table)
            common_columns = [col for col in sqlite_columns if col in set(mysql_columns)]
            compare_columns = self._conflict_compare_columns(common_columns)

            _, local_rows = self._fetch_sqlite_table(sqlite_conn, table)
            _, remote_rows = self._fetch_mysql_table(mysql_conn, table)
            local_by_uuid = {row.get("sync_uuid"): row for row in local_rows if row.get("sync_uuid")}
            remote_by_uuid = {row.get("sync_uuid"): row for row in remote_rows if row.get("sync_uuid")}

            inserted = 0
            updated = 0
            conflicts = 0

            if direction == "push":
                for sync_uuid, local_row in local_by_uuid.items():
                    remote_row = remote_by_uuid.get(sync_uuid)
                    if remote_row is None:
                        self._mysql_insert_entity(mysql_conn, table, local_row, common_columns)
                        inserted += 1
                        continue
                    if self._rows_differ(local_row, remote_row, compare_columns):
                        conflicts += 1
                        choice = self._resolve_sync_conflict(
                            table, sync_uuid, local_row, remote_row, compare_columns
                        )
                        if choice == "local":
                            self._mysql_update_entity_by_uuid(mysql_conn, table, local_row, common_columns)
                            updated += 1
                        elif choice == "remote":
                            self._sqlite_update_entity_by_uuid(sqlite_conn, table, remote_row, common_columns)
                            updated += 1
            else:
                for sync_uuid, remote_row in remote_by_uuid.items():
                    local_row = local_by_uuid.get(sync_uuid)
                    if local_row is None:
                        self._sqlite_insert_entity(sqlite_conn, table, remote_row, common_columns)
                        inserted += 1
                        continue
                    if self._rows_differ(local_row, remote_row, compare_columns):
                        conflicts += 1
                        choice = self._resolve_sync_conflict(
                            table, sync_uuid, local_row, remote_row, compare_columns
                        )
                        if choice == "remote":
                            self._sqlite_update_entity_by_uuid(sqlite_conn, table, remote_row, common_columns)
                            updated += 1
                        elif choice == "local":
                            self._mysql_update_entity_by_uuid(mysql_conn, table, local_row, common_columns)
                            updated += 1

            stats.append(
                f"{table}: inserted={inserted}, updated={updated}, conflicts={conflicts}"
            )
        return stats

    def _link_fk_table_map(self) -> dict[str, dict[str, str]]:
        return {
            "program_disciplines": {"program_id": "educational_programs", "discipline_id": "disciplines"},
            "discipline_topics": {"discipline_id": "disciplines", "topic_id": "topics"},
            "program_topics": {"program_id": "educational_programs", "topic_id": "topics"},
            "topic_lessons": {"topic_id": "topics", "lesson_id": "lessons"},
            "lesson_questions": {"lesson_id": "lessons", "question_id": "questions"},
            "teacher_materials": {"teacher_id": "teachers", "material_id": "methodical_materials"},
            "teacher_disciplines": {"teacher_id": "teachers", "discipline_id": "disciplines"},
            "material_associations": {"material_id": "methodical_materials", "entity_id": "dynamic"},
        }

    def _entity_type_to_table(self, entity_type: str) -> str | None:
        mapping = {
            "program": "educational_programs",
            "discipline": "disciplines",
            "topic": "topics",
            "lesson": "lessons",
        }
        return mapping.get(entity_type)

    def _upsert_mysql_link_row(self, mysql_conn, table: str, row: dict) -> bool:  # noqa: ANN001
        columns = [col for col in self._mysql_table_columns(mysql_conn, table) if col in row]
        if not columns:
            return False
        pk_columns = self._mysql_primary_keys(mysql_conn, table)
        non_pk_columns = [col for col in columns if col not in pk_columns]
        cols_sql = ", ".join(f"`{col}`" for col in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        if non_pk_columns:
            update_sql = ", ".join(f"`{col}` = VALUES(`{col}`)" for col in non_pk_columns)
            sql = (
                f"INSERT INTO `{table}` ({cols_sql}) VALUES ({placeholders}) "
                f"ON DUPLICATE KEY UPDATE {update_sql}"
            )
        else:
            sql = f"INSERT IGNORE INTO `{table}` ({cols_sql}) VALUES ({placeholders})"
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql, tuple(row.get(col) for col in columns))
        return True

    def _upsert_sqlite_link_row(self, sqlite_conn, table: str, row: dict) -> bool:  # noqa: ANN001
        sqlite_columns = set(self._sqlite_table_columns(sqlite_conn, table))
        columns = [col for col in row if col in sqlite_columns]
        if not columns:
            return False
        pk_columns = self._sqlite_primary_keys(sqlite_conn, table)
        non_pk_columns = [col for col in columns if col not in pk_columns]
        cols_sql = ", ".join(f'"{col}"' for col in columns)
        placeholders = ", ".join(["?"] * len(columns))
        if pk_columns and non_pk_columns:
            conflict_cols = ", ".join(f'"{col}"' for col in pk_columns)
            update_sql = ", ".join(f'"{col}" = excluded."{col}"' for col in non_pk_columns)
            sql = (
                f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders}) '
                f"ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_sql}"
            )
        elif pk_columns:
            sql = f'INSERT OR IGNORE INTO "{table}" ({cols_sql}) VALUES ({placeholders})'
        else:
            sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders})'
        sqlite_conn.execute(sql, tuple(row.get(col) for col in columns))
        return True

    def _sync_link_tables(self, sqlite_conn, mysql_conn, direction: str) -> list[str]:  # noqa: ANN001
        stats: list[str] = []
        local_maps: dict[str, dict[str, dict]] = {}
        remote_maps: dict[str, dict[str, dict]] = {}
        for table in self._internet_sync_entity_tables():
            l_id_to_uuid, l_uuid_to_id = self._uuid_maps_sqlite(sqlite_conn, table)
            r_id_to_uuid, r_uuid_to_id = self._uuid_maps_mysql(mysql_conn, table)
            local_maps[table] = {"id_to_uuid": l_id_to_uuid, "uuid_to_id": l_uuid_to_id}
            remote_maps[table] = {"id_to_uuid": r_id_to_uuid, "uuid_to_id": r_uuid_to_id}

        fk_map = self._link_fk_table_map()
        for table in self._internet_sync_link_tables():
            processed = 0
            if direction == "push":
                columns, rows = self._fetch_sqlite_table(sqlite_conn, table)
                if not self._mysql_table_exists(mysql_conn, table):
                    raise ValueError(f"Internet DB is missing table: {table}")
                for row in rows:
                    new_row = {col: row.get(col) for col in columns}
                    skip_row = False
                    for fk_col, parent_table in fk_map.get(table, {}).items():
                        if fk_col not in new_row:
                            continue
                        if parent_table == "dynamic":
                            dynamic_parent = self._entity_type_to_table(new_row.get("entity_type"))
                            if not dynamic_parent:
                                skip_row = True
                                break
                            parent_table = dynamic_parent
                        local_id = new_row.get(fk_col)
                        source_uuid = local_maps[parent_table]["id_to_uuid"].get(local_id)
                        target_id = remote_maps[parent_table]["uuid_to_id"].get(source_uuid)
                        if target_id is None:
                            skip_row = True
                            break
                        new_row[fk_col] = target_id
                    if skip_row:
                        continue
                    if self._upsert_mysql_link_row(mysql_conn, table, new_row):
                        processed += 1
            else:
                columns, rows = self._fetch_mysql_table(mysql_conn, table)
                for row in rows:
                    new_row = {col: row.get(col) for col in columns}
                    skip_row = False
                    for fk_col, parent_table in fk_map.get(table, {}).items():
                        if fk_col not in new_row:
                            continue
                        if parent_table == "dynamic":
                            dynamic_parent = self._entity_type_to_table(new_row.get("entity_type"))
                            if not dynamic_parent:
                                skip_row = True
                                break
                            parent_table = dynamic_parent
                        remote_id = new_row.get(fk_col)
                        source_uuid = remote_maps[parent_table]["id_to_uuid"].get(remote_id)
                        target_id = local_maps[parent_table]["uuid_to_id"].get(source_uuid)
                        if target_id is None:
                            skip_row = True
                            break
                        new_row[fk_col] = target_id
                    if skip_row:
                        continue
                    if self._upsert_sqlite_link_row(sqlite_conn, table, new_row):
                        processed += 1
            stats.append(f"{table}: merged={processed}")
        return stats

    def _synchronize_internet_database(self) -> None:
        host = self.internet_db_host.text().strip()
        port_text = self.internet_db_port.text().strip()
        database = self.internet_db_name.text().strip()
        user = self.internet_db_user.text().strip()
        password = self.internet_db_password.text()
        direction = self.internet_sync_direction.currentData() or "push"

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

        if direction == "push":
            confirm_text = self.tr(
                "Synchronize local changes to Internet DB (merge, no full overwrite)?"
            )
        else:
            confirm_text = self.tr(
                "Synchronize Internet DB changes to local database (merge, no full overwrite)?"
            )
        if QMessageBox.question(self, self.tr("Confirm synchronization"), confirm_text) != QMessageBox.Yes:
            return

        try:
            import pymysql
            from pymysql.cursors import DictCursor
        except ImportError:
            QMessageBox.warning(
                self,
                self.tr("Import error"),
                self.tr("PyMySQL is not installed. Install dependencies from requirements.txt."),
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
        except (pymysql.MySQLError, OSError, ValueError, TypeError) as exc:
            self.internet_db_status.setText(self.tr("Connection failed"))
            self.internet_db_status.setStyleSheet("color: #a11f1f;")
            self._set_internet_db_indicator("error")
            QMessageBox.warning(self, self.tr("Connection failed"), str(exc))
            return

        sync_stats: list[str] = []
        try:
            self._ensure_mysql_sync_schema(mysql_conn)
            if direction == "push":
                with self.controller.db.get_connection() as sqlite_conn:
                    with mysql_conn.cursor() as cursor:
                        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                    sync_stats.extend(self._sync_entity_tables(sqlite_conn, mysql_conn, direction="push"))
                    sync_stats.extend(self._sync_link_tables(sqlite_conn, mysql_conn, direction="push"))
                    with mysql_conn.cursor() as cursor:
                        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                    mysql_conn.commit()
            else:
                with self.controller.db.get_connection() as sqlite_conn:
                    sqlite_conn.execute("PRAGMA foreign_keys = OFF")
                    sync_stats.extend(self._sync_entity_tables(sqlite_conn, mysql_conn, direction="pull"))
                    sync_stats.extend(self._sync_link_tables(sqlite_conn, mysql_conn, direction="pull"))
                    sqlite_conn.execute("PRAGMA foreign_keys = ON")
                self._refresh_all()

            self.internet_db_status.setText(self.tr("Synchronization completed"))
            self.internet_db_status.setStyleSheet("color: #1b7f3b;")
            self._set_internet_db_indicator("ok")
            self._save_internet_db_settings(show_message=False)
            QMessageBox.information(
                self,
                self.tr("Synchronization"),
                self.tr("Synchronization completed.\nRows processed:\n{0}").format("\n".join(sync_stats)),
            )
            self._log_action("internet_sync_completed", f"direction={direction}")
            if hasattr(self, "log_table"):
                self._refresh_log_tab()
        except (pymysql.MySQLError, OSError, ValueError, RuntimeError, sqlite3.Error, TypeError) as exc:
            try:
                with mysql_conn.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            except pymysql.MySQLError as restore_exc:
                self._log_action("internet_sync_fk_restore_failed", str(restore_exc))
            mysql_conn.rollback()
            self.internet_db_status.setText(self.tr("Synchronization failed"))
            self.internet_db_status.setStyleSheet("color: #a11f1f;")
            self._set_internet_db_indicator("error")
            self._log_action("internet_sync_failed", str(exc))
            if hasattr(self, "log_table"):
                self._refresh_log_tab()
            QMessageBox.warning(self, self.tr("Synchronization failed"), str(exc))
        finally:
            mysql_conn.close()
