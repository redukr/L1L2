"""Internet database synchronization service."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Callable
from uuid import uuid4

from .internet_sync_schema import ENTITY_TABLES, LINK_TABLES, MYSQL_SYNC_SCHEMA_DDL


class InternetSyncService:
    """Encapsulates SQLite <-> MySQL synchronization logic."""

    _IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    ENTITY_TABLES = ENTITY_TABLES
    LINK_TABLES = LINK_TABLES

    def internet_sync_tables(self) -> list[str]:
        return self.ENTITY_TABLES + self.LINK_TABLES

    def _validate_sync_table(self, table: str) -> str:
        if table not in set(self.internet_sync_tables()):
            raise ValueError(f"Unsupported sync table: {table}")
        return table

    def _validate_identifier(self, identifier: str) -> str:
        if not self._IDENTIFIER_RE.match(identifier or ""):
            raise ValueError(f"Unsafe SQL identifier: {identifier}")
        return identifier

    def _sqlite_ident(self, table: str) -> str:
        return f'"{self._validate_identifier(self._validate_sync_table(table))}"'

    def _mysql_ident(self, table: str) -> str:
        return f"`{self._validate_identifier(self._validate_sync_table(table))}`"

    def _sqlite_column_ident(self, column: str) -> str:
        return f'"{self._validate_identifier(column)}"'

    def _mysql_column_ident(self, column: str) -> str:
        return f"`{self._validate_identifier(column)}`"

    def _validated_sync_columns(self, columns: list[str]) -> list[str]:
        return [self._validate_identifier(col) for col in columns]

    def fetch_sqlite_table(self, sqlite_conn, table: str) -> tuple[list[str], list[dict]]:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        cursor = sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_sql}")
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(row) for row in cursor.fetchall()]
        return columns, rows

    def sqlite_table_columns(self, sqlite_conn, table: str) -> list[str]:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        cursor = sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_sql})")
        return [row["name"] for row in cursor.fetchall()]

    def fetch_mysql_table(self, mysql_conn, table: str) -> tuple[list[str], list[dict]]:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_sql}")
            rows = cursor.fetchall()
            if not rows:
                cursor.execute(f"SHOW COLUMNS FROM {table_sql}")
                columns = [row["Field"] for row in cursor.fetchall()]
                return columns, []
            columns = list(rows[0].keys())
        return columns, rows

    def mysql_table_exists(self, mysql_conn, table: str) -> bool:  # noqa: ANN001
        self._validate_sync_table(table)
        with mysql_conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE %s", (table,))
            return cursor.fetchone() is not None

    def mysql_table_columns(self, mysql_conn, table: str) -> list[str]:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {table_sql}")
            return [row["Field"] for row in cursor.fetchall()]

    def sqlite_primary_keys(self, sqlite_conn, table: str) -> list[str]:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        cursor = sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_sql})")
        info = cursor.fetchall()
        ordered = sorted((row for row in info if row["pk"]), key=lambda row: row["pk"])
        return [row["name"] for row in ordered]

    def mysql_primary_keys(self, mysql_conn, table: str) -> list[str]:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SHOW KEYS FROM {table_sql} WHERE Key_name = 'PRIMARY'")
            rows = cursor.fetchall()
        rows = sorted(rows, key=lambda row: row.get("Seq_in_index", 0))
        return [row["Column_name"] for row in rows]

    def map_sqlite_type_to_mysql(self, sqlite_type: str) -> str:
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

    def ensure_mysql_table_columns(self, mysql_conn, sqlite_conn, table: str) -> None:  # noqa: ANN001
        table_sql_sqlite = self._sqlite_ident(table)
        table_sql_mysql = self._mysql_ident(table)
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"PRAGMA table_info({table_sql_sqlite})")
        sqlite_info = sqlite_cursor.fetchall()
        mysql_columns = set(self.mysql_table_columns(mysql_conn, table))
        with mysql_conn.cursor() as cursor:
            for col in sqlite_info:
                col_name = col["name"]
                if col_name in mysql_columns:
                    continue
                mysql_col_name = self._mysql_column_ident(col_name)
                col_type = self.map_sqlite_type_to_mysql(col["type"] or "")
                cursor.execute(f"ALTER TABLE {table_sql_mysql} ADD COLUMN {mysql_col_name} {col_type} NULL")
        mysql_conn.commit()

    def ensure_mysql_sync_schema(self, mysql_conn) -> None:  # noqa: ANN001
        with mysql_conn.cursor() as cursor:
            for stmt in MYSQL_SYNC_SCHEMA_DDL:
                cursor.execute(stmt)
        mysql_conn.commit()

    def ensure_sqlite_sync_uuid(self, sqlite_conn, table: str) -> None:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        columns = set(self.sqlite_table_columns(sqlite_conn, table))
        if "sync_uuid" not in columns:
            sqlite_conn.execute(f"ALTER TABLE {table_sql} ADD COLUMN sync_uuid TEXT")
        sqlite_conn.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_sync_uuid ON {table_sql}(sync_uuid)"
        )
        cursor = sqlite_conn.cursor()
        cursor.execute(f'SELECT id FROM {table_sql} WHERE sync_uuid IS NULL OR sync_uuid = ""')
        for row in cursor.fetchall():
            sqlite_conn.execute(
                f"UPDATE {table_sql} SET sync_uuid = ? WHERE id = ?",
                (str(uuid4()), row["id"]),
            )

    def ensure_mysql_sync_uuid(self, mysql_conn, table: str) -> None:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        columns = set(self.mysql_table_columns(mysql_conn, table))
        with mysql_conn.cursor() as cursor:
            if "sync_uuid" not in columns:
                cursor.execute(f"ALTER TABLE {table_sql} ADD COLUMN sync_uuid VARCHAR(36) NULL")
            cursor.execute(
                f"UPDATE {table_sql} SET sync_uuid = UUID() WHERE sync_uuid IS NULL OR sync_uuid = ''"
            )
            cursor.execute(f"SHOW INDEX FROM {table_sql} WHERE Column_name = 'sync_uuid'")
            if cursor.fetchone() is None:
                cursor.execute(f"CREATE UNIQUE INDEX idx_{table}_sync_uuid ON {table_sql}(sync_uuid)")
        mysql_conn.commit()

    def normalize_sync_value(self, value):  # noqa: ANN001
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        if isinstance(value, (int, float)):
            return float(value)
        return str(value)

    def rows_differ(self, left: dict, right: dict, columns: list[str]) -> bool:
        for col in columns:
            if self.normalize_sync_value(left.get(col)) != self.normalize_sync_value(right.get(col)):
                return True
        return False

    def conflict_compare_columns(self, columns: list[str]) -> list[str]:
        ignored = {"id", "sync_uuid", "created_at", "updated_at"}
        return [col for col in columns if col not in ignored]

    def format_conflict_row(self, row: dict, columns: list[str]) -> str:
        payload = {col: row.get(col) for col in columns}
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    def mysql_insert_entity(self, mysql_conn, table: str, row: dict, common_columns: list[str]) -> None:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        insert_columns = self._validated_sync_columns([col for col in common_columns if col != "id"])
        if not insert_columns:
            return
        with mysql_conn.cursor() as cursor:
            cols_sql = ", ".join(self._mysql_column_ident(col) for col in insert_columns)
            placeholders = ", ".join(["%s"] * len(insert_columns))
            sql = f"INSERT INTO {table_sql} ({cols_sql}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row.get(col) for col in insert_columns))

    def mysql_update_entity_by_uuid(self, mysql_conn, table: str, row: dict, common_columns: list[str]) -> None:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        update_columns = self._validated_sync_columns([col for col in common_columns if col not in {"id", "sync_uuid"}])
        if not update_columns:
            return
        set_clause = ", ".join(f"{self._mysql_column_ident(col)} = %s" for col in update_columns)
        values = [row.get(col) for col in update_columns]
        values.append(row.get("sync_uuid"))
        with mysql_conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE {table_sql} SET {set_clause} WHERE sync_uuid = %s",
                tuple(values),
            )

    def sqlite_insert_entity(self, sqlite_conn, table: str, row: dict, common_columns: list[str]) -> None:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        insert_columns = self._validated_sync_columns([col for col in common_columns if col != "id"])
        if not insert_columns:
            return
        cols_sql = ", ".join(self._sqlite_column_ident(col) for col in insert_columns)
        placeholders = ", ".join(["?"] * len(insert_columns))
        sqlite_conn.execute(
            f"INSERT INTO {table_sql} ({cols_sql}) VALUES ({placeholders})",
            tuple(row.get(col) for col in insert_columns),
        )

    def sqlite_update_entity_by_uuid(self, sqlite_conn, table: str, row: dict, common_columns: list[str]) -> None:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        update_columns = self._validated_sync_columns([col for col in common_columns if col not in {"id", "sync_uuid"}])
        if not update_columns:
            return
        set_clause = ", ".join(f"{self._sqlite_column_ident(col)} = ?" for col in update_columns)
        values = [row.get(col) for col in update_columns]
        values.append(row.get("sync_uuid"))
        sqlite_conn.execute(
            f"UPDATE {table_sql} SET {set_clause} WHERE sync_uuid = ?",
            tuple(values),
        )

    def uuid_maps_sqlite(self, sqlite_conn, table: str) -> tuple[dict[int, str], dict[str, int]]:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        cursor = sqlite_conn.cursor()
        cursor.execute(f'SELECT id, sync_uuid FROM {table_sql} WHERE sync_uuid IS NOT NULL AND sync_uuid <> ""')
        id_to_uuid: dict[int, str] = {}
        uuid_to_id: dict[str, int] = {}
        for row in cursor.fetchall():
            id_to_uuid[row["id"]] = row["sync_uuid"]
            uuid_to_id[row["sync_uuid"]] = row["id"]
        return id_to_uuid, uuid_to_id

    def uuid_maps_mysql(self, mysql_conn, table: str) -> tuple[dict[int, str], dict[str, int]]:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SELECT id, sync_uuid FROM {table_sql} WHERE sync_uuid IS NOT NULL AND sync_uuid <> ''")
            rows = cursor.fetchall()
        id_to_uuid: dict[int, str] = {}
        uuid_to_id: dict[str, int] = {}
        for row in rows:
            id_to_uuid[row["id"]] = row["sync_uuid"]
            uuid_to_id[row["sync_uuid"]] = row["id"]
        return id_to_uuid, uuid_to_id

    def link_fk_table_map(self) -> dict[str, dict[str, str]]:
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

    def entity_type_to_table(self, entity_type: str) -> str | None:
        mapping = {
            "program": "educational_programs",
            "discipline": "disciplines",
            "topic": "topics",
            "lesson": "lessons",
        }
        return mapping.get(entity_type)

    def upsert_mysql_link_row(self, mysql_conn, table: str, row: dict) -> bool:  # noqa: ANN001
        table_sql = self._mysql_ident(table)
        columns = [col for col in self.mysql_table_columns(mysql_conn, table) if col in row]
        if not columns:
            return False
        pk_columns = self.mysql_primary_keys(mysql_conn, table)
        non_pk_columns = [col for col in columns if col not in pk_columns]
        cols_sql = ", ".join(self._mysql_column_ident(col) for col in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        if non_pk_columns:
            update_sql = ", ".join(
                f"{self._mysql_column_ident(col)} = VALUES({self._mysql_column_ident(col)})"
                for col in non_pk_columns
            )
            sql = (
                f"INSERT INTO {table_sql} ({cols_sql}) VALUES ({placeholders}) "
                f"ON DUPLICATE KEY UPDATE {update_sql}"
            )
        else:
            sql = f"INSERT IGNORE INTO {table_sql} ({cols_sql}) VALUES ({placeholders})"
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql, tuple(row.get(col) for col in columns))
        return True

    def upsert_sqlite_link_row(self, sqlite_conn, table: str, row: dict) -> bool:  # noqa: ANN001
        table_sql = self._sqlite_ident(table)
        sqlite_columns = set(self.sqlite_table_columns(sqlite_conn, table))
        columns = [col for col in row if col in sqlite_columns]
        if not columns:
            return False
        pk_columns = self.sqlite_primary_keys(sqlite_conn, table)
        non_pk_columns = [col for col in columns if col not in pk_columns]
        cols_sql = ", ".join(self._sqlite_column_ident(col) for col in columns)
        placeholders = ", ".join(["?"] * len(columns))
        if pk_columns and non_pk_columns:
            conflict_cols = ", ".join(self._sqlite_column_ident(col) for col in pk_columns)
            update_sql = ", ".join(
                f'{self._sqlite_column_ident(col)} = excluded.{self._sqlite_column_ident(col)}'
                for col in non_pk_columns
            )
            sql = (
                f"INSERT INTO {table_sql} ({cols_sql}) VALUES ({placeholders}) "
                f"ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_sql}"
            )
        elif pk_columns:
            sql = f"INSERT OR IGNORE INTO {table_sql} ({cols_sql}) VALUES ({placeholders})"
        else:
            sql = f"INSERT INTO {table_sql} ({cols_sql}) VALUES ({placeholders})"
        sqlite_conn.execute(sql, tuple(row.get(col) for col in columns))
        return True

    def sync_entity_tables(
        self,
        sqlite_conn,
        mysql_conn,
        direction: str,
        conflict_resolver: Callable[[str, str, dict, dict, list[str]], str],
    ) -> list[str]:  # noqa: ANN001
        stats: list[str] = []
        for table in self.ENTITY_TABLES:
            if not self.mysql_table_exists(mysql_conn, table):
                raise ValueError(f"Internet DB is missing table: {table}")
            self.ensure_mysql_table_columns(mysql_conn, sqlite_conn, table)
            self.ensure_sqlite_sync_uuid(sqlite_conn, table)
            self.ensure_mysql_sync_uuid(mysql_conn, table)
            sqlite_columns = self.sqlite_table_columns(sqlite_conn, table)
            mysql_columns = self.mysql_table_columns(mysql_conn, table)
            common_columns = [col for col in sqlite_columns if col in set(mysql_columns)]
            compare_columns = self.conflict_compare_columns(common_columns)

            _, local_rows = self.fetch_sqlite_table(sqlite_conn, table)
            _, remote_rows = self.fetch_mysql_table(mysql_conn, table)
            local_by_uuid = {row.get("sync_uuid"): row for row in local_rows if row.get("sync_uuid")}
            remote_by_uuid = {row.get("sync_uuid"): row for row in remote_rows if row.get("sync_uuid")}

            inserted = 0
            updated = 0
            conflicts = 0

            if direction == "push":
                for sync_uuid, local_row in local_by_uuid.items():
                    remote_row = remote_by_uuid.get(sync_uuid)
                    if remote_row is None:
                        self.mysql_insert_entity(mysql_conn, table, local_row, common_columns)
                        inserted += 1
                        continue
                    if self.rows_differ(local_row, remote_row, compare_columns):
                        conflicts += 1
                        choice = conflict_resolver(table, sync_uuid, local_row, remote_row, compare_columns)
                        if choice == "local":
                            self.mysql_update_entity_by_uuid(mysql_conn, table, local_row, common_columns)
                            updated += 1
                        elif choice == "remote":
                            self.sqlite_update_entity_by_uuid(sqlite_conn, table, remote_row, common_columns)
                            updated += 1
            else:
                for sync_uuid, remote_row in remote_by_uuid.items():
                    local_row = local_by_uuid.get(sync_uuid)
                    if local_row is None:
                        self.sqlite_insert_entity(sqlite_conn, table, remote_row, common_columns)
                        inserted += 1
                        continue
                    if self.rows_differ(local_row, remote_row, compare_columns):
                        conflicts += 1
                        choice = conflict_resolver(table, sync_uuid, local_row, remote_row, compare_columns)
                        if choice == "remote":
                            self.sqlite_update_entity_by_uuid(sqlite_conn, table, remote_row, common_columns)
                            updated += 1
                        elif choice == "local":
                            self.mysql_update_entity_by_uuid(mysql_conn, table, local_row, common_columns)
                            updated += 1

            stats.append(f"{table}: inserted={inserted}, updated={updated}, conflicts={conflicts}")
        return stats

    def sync_link_tables(self, sqlite_conn, mysql_conn, direction: str) -> list[str]:  # noqa: ANN001
        stats: list[str] = []
        local_maps: dict[str, dict[str, dict]] = {}
        remote_maps: dict[str, dict[str, dict]] = {}
        for table in self.ENTITY_TABLES:
            l_id_to_uuid, l_uuid_to_id = self.uuid_maps_sqlite(sqlite_conn, table)
            r_id_to_uuid, r_uuid_to_id = self.uuid_maps_mysql(mysql_conn, table)
            local_maps[table] = {"id_to_uuid": l_id_to_uuid, "uuid_to_id": l_uuid_to_id}
            remote_maps[table] = {"id_to_uuid": r_id_to_uuid, "uuid_to_id": r_uuid_to_id}

        fk_map = self.link_fk_table_map()
        for table in self.LINK_TABLES:
            processed = 0
            if direction == "push":
                columns, rows = self.fetch_sqlite_table(sqlite_conn, table)
                if not self.mysql_table_exists(mysql_conn, table):
                    raise ValueError(f"Internet DB is missing table: {table}")
                for row in rows:
                    new_row = {col: row.get(col) for col in columns}
                    skip_row = False
                    for fk_col, parent_table in fk_map.get(table, {}).items():
                        if fk_col not in new_row:
                            continue
                        if parent_table == "dynamic":
                            dynamic_parent = self.entity_type_to_table(new_row.get("entity_type"))
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
                    if self.upsert_mysql_link_row(mysql_conn, table, new_row):
                        processed += 1
            else:
                columns, rows = self.fetch_mysql_table(mysql_conn, table)
                for row in rows:
                    new_row = {col: row.get(col) for col in columns}
                    skip_row = False
                    for fk_col, parent_table in fk_map.get(table, {}).items():
                        if fk_col not in new_row:
                            continue
                        if parent_table == "dynamic":
                            dynamic_parent = self.entity_type_to_table(new_row.get("entity_type"))
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
                    if self.upsert_sqlite_link_row(sqlite_conn, table, new_row):
                        processed += 1
            stats.append(f"{table}: merged={processed}")
        return stats
