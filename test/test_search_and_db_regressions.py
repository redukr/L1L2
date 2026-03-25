import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.models.database import Database
from src.services.search_service import SearchService


class SearchAndDatabaseRegressionTests(unittest.TestCase):
    def test_search_service_sanitizes_special_tokens(self):
        service = SearchService(Database(":memory:"))

        self.assertEqual(service._fts_query("abc-def"), "abc* def*")
        self.assertEqual(service._fts_query("abc*"), "abc*")
        self.assertEqual(service._fts_query('"exact phrase"'), '"exact phrase"*')

    def test_database_backfills_fts_for_existing_content(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "education.db"
            database = Database(str(db_path))
            with database.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO educational_programs (name, description, level, year, duration_hours)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    ("Alpha Program", "", "", 2026, 1),
                )

            reopened = Database(str(db_path))
            results = SearchService(reopened).search_all("Alpha")
            self.assertTrue(any(result.entity_type == "program" and result.title == "Alpha Program" for result in results))

    def test_database_rebuilds_fts_only_once_via_migration(self):
        class CountingDatabase(Database):
            rebuild_calls = 0

            def _rebuild_all_fts(self, cursor) -> None:
                type(self).rebuild_calls += 1
                super()._rebuild_all_fts(cursor)

        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "education.db"
            Database(str(db_path))

            CountingDatabase.rebuild_calls = 0
            CountingDatabase(str(db_path))
            self.assertEqual(CountingDatabase.rebuild_calls, 0)

    def test_search_service_does_not_swallow_database_errors(self):
        database = Database(":memory:")
        service = SearchService(database)

        original_get_connection = database.get_connection

        def broken_connection():
            raise sqlite3.OperationalError("fts unavailable")

        database.get_connection = broken_connection
        try:
            with self.assertRaises(sqlite3.OperationalError):
                service.search_all("alpha")
        finally:
            database.get_connection = original_get_connection
