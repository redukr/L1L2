import re
import unittest

from src.models.schema import CORE_TABLE_STATEMENTS
from src.services.internet_sync_schema import ENTITY_TABLES, LINK_TABLES, MYSQL_SYNC_SCHEMA_DDL


def _extract_table_names(statements):
    names = []
    for statement in statements:
        match = re.search(r"CREATE TABLE IF NOT EXISTS\s+([A-Za-z_][A-Za-z0-9_]*)", statement)
        if match:
            names.append(match.group(1))
    return names


class SchemaParityTests(unittest.TestCase):
    def test_sync_schema_covers_all_sync_tables(self):
        mysql_tables = set(_extract_table_names(MYSQL_SYNC_SCHEMA_DDL))
        expected_tables = set(ENTITY_TABLES) | set(LINK_TABLES) | {"schema_migrations"}

        self.assertTrue(expected_tables.issubset(mysql_tables))

    def test_local_schema_contains_all_sync_entity_and_link_tables(self):
        sqlite_tables = set(_extract_table_names(CORE_TABLE_STATEMENTS))
        expected_tables = set(ENTITY_TABLES) | set(LINK_TABLES)

        self.assertTrue(expected_tables.issubset(sqlite_tables))

    def test_key_material_columns_exist_in_both_schemas(self):
        sqlite_material_stmt = next(stmt for stmt in CORE_TABLE_STATEMENTS if "methodical_materials" in stmt)
        mysql_material_stmt = next(stmt for stmt in MYSQL_SYNC_SCHEMA_DDL if "methodical_materials" in stmt)

        for column in ("title", "material_type", "relative_path", "file_type", "file_path", "file_name"):
            self.assertIn(column, sqlite_material_stmt)
            self.assertIn(column, mysql_material_stmt)
