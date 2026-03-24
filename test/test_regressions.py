import tempfile
import unittest
from pathlib import Path
import sqlite3

from src.models.database import Database
from src.repositories.discipline_repository import DisciplineRepository
from src.repositories.teacher_repository import TeacherRepository
from src.repositories.topic_repository import TopicRepository
from src.services.file_storage import FileStorageManager
from src.services.import_service import extract_text_from_file, parse_curriculum_text
from src.services.search_service import SearchService
from src.ui.main_window import MainWindow


class RegressionTests(unittest.TestCase):
    def test_curriculum_parser_uses_header_mapping(self):
        text = "\n".join(
            [
                "Назва теми\tЗаняття\tПитання\tТип заняття\tАудиторні\tСамостійна",
                "Тема 1\tЗаняття 1. Лекція\t1. Q1 2. Q2\tЛекція\t2\t0",
            ]
        )

        topics = parse_curriculum_text(text)

        self.assertEqual(len(topics), 1)
        lesson = topics[0].lessons[0]
        self.assertEqual(lesson.lesson_type_name, "Лекція")
        self.assertEqual(lesson.total_hours, 2.0)
        self.assertEqual(lesson.classroom_hours, 2.0)
        self.assertEqual(lesson.self_study_hours, 0.0)
        self.assertEqual([question.text for question in lesson.questions], ["1. Q1", "2. Q2"])

    def test_text_import_supports_cp1251(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.txt"
            path.write_bytes("Привіт".encode("cp1251"))
            self.assertEqual(extract_text_from_file(str(path)), "Привіт")

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

    def test_file_storage_blocks_path_escape_from_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            files_root = Path(tmp_dir) / "files"
            files_root.mkdir()
            storage = FileStorageManager(files_root)

            with self.assertRaises(ValueError):
                storage._resolve_path("../settings/admin_credentials.json")

    def test_main_window_material_action_reports_invalid_path(self):
        ok, error = MainWindow._execute_material_file_action(
            lambda: (_ for _ in ()).throw(ValueError("bad path"))
        )
        self.assertIsNone(ok)
        self.assertEqual(error, "bad path")

    def test_repository_only_swallows_integrity_errors(self):
        database = Database(":memory:")
        repo = DisciplineRepository(database)

        original_get_connection = database.get_connection

        def broken_connection():
            raise RuntimeError("boom")

        database.get_connection = broken_connection
        try:
            with self.assertRaises(RuntimeError):
                repo.add_topic_to_discipline(1, 1, 1)
        finally:
            database.get_connection = original_get_connection

    def test_teacher_repository_only_swallows_integrity_errors(self):
        database = Database(":memory:")
        repo = TeacherRepository(database)

        original_get_connection = database.get_connection

        def broken_connection():
            raise RuntimeError("boom")

        database.get_connection = broken_connection
        try:
            with self.assertRaises(RuntimeError):
                repo.add_discipline(1, 1)
        finally:
            database.get_connection = original_get_connection

    def test_topic_repository_only_swallows_integrity_errors(self):
        database = Database(":memory:")
        repo = TopicRepository(database)

        original_get_connection = database.get_connection

        def broken_connection():
            raise RuntimeError("boom")

        database.get_connection = broken_connection
        try:
            with self.assertRaises(RuntimeError):
                repo.add_lesson_to_topic(1, 1, 1)
        finally:
            database.get_connection = original_get_connection


if __name__ == "__main__":
    unittest.main()
