import tempfile
import unittest
from unittest import mock

from src.models.database import Database
from src.repositories.discipline_repository import DisciplineRepository
from src.repositories.teacher_repository import TeacherRepository
from src.repositories.topic_repository import TopicRepository
from src.services.auth_service import AuthService


class AuthAndRepositoryRegressionTests(unittest.TestCase):
    def test_auth_service_requires_explicit_password_setup(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            from pathlib import Path

            tmp_path = Path(tmp_dir)
            settings_dir = tmp_path / "settings"
            data_dir = tmp_path / "data"
            settings_dir.mkdir()
            data_dir.mkdir()
            with mock.patch("src.services.auth_service.get_settings_dir", return_value=settings_dir), mock.patch(
                "src.services.auth_service.get_data_dir", return_value=data_dir
            ):
                auth = AuthService()
                self.assertFalse(auth.has_admin_password())
                self.assertFalse(auth.verify_admin_password("admin123"))
                auth.set_admin_password("secret123")
                self.assertTrue(auth.verify_admin_password("secret123"))

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
