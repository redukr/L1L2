import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.controllers.admin_controller import AdminController
from src.models.database import Database
from src.models.entities import Discipline, EducationalProgram, MethodicalMaterial
from src.services.file_storage import FileStorageManager


class StorageRegressionTests(unittest.TestCase):
    def test_file_storage_blocks_path_escape_from_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            files_root = Path(tmp_dir) / "files"
            files_root.mkdir()
            storage = FileStorageManager(files_root)

            with self.assertRaises(ValueError):
                storage._resolve_path("../settings/admin_credentials.json")

    def test_attach_material_update_failure_restores_overwritten_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            controller = AdminController(database)
            controller.file_storage = FileStorageManager(tmp_path / "files")

            program = controller.program_repo.add(
                EducationalProgram(name="Program", description="", level="", year=2026, duration_hours=1)
            )
            discipline = controller.discipline_repo.add(Discipline(name="Discipline"))
            controller.program_repo.add_discipline_to_program(program.id, discipline.id, 1)

            material = controller.material_repo.add(
                MethodicalMaterial(
                    title="Material",
                    material_type="guide",
                    relative_path="p01/d01/m_000001.txt",
                    stored_filename="m_000001.txt",
                    original_filename="old.txt",
                    file_name="old.txt",
                    file_path="p01/d01/m_000001.txt",
                    file_type="txt",
                )
            )
            old_path = controller.file_storage.files_root / "p01" / "d01" / "m_000001.txt"
            old_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.write_text("old content", encoding="utf-8")

            source_path = tmp_path / "source.txt"
            source_path.write_text("new content", encoding="utf-8")

            with mock.patch.object(controller.material_repo, "update", side_effect=RuntimeError("db write failed")):
                with self.assertRaises(RuntimeError):
                    controller.attach_material_file_with_context(material, str(source_path), program.id, discipline.id)

            self.assertEqual(old_path.read_text(encoding="utf-8"), "old content")

    def test_delete_material_removes_file_only_after_database_delete(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            controller = AdminController(database)
            controller.file_storage = FileStorageManager(tmp_path / "files")

            material = controller.material_repo.add(
                MethodicalMaterial(
                    title="Material",
                    material_type="guide",
                    relative_path="p01/d01/m_000001.txt",
                    stored_filename="m_000001.txt",
                    original_filename="old.txt",
                    file_name="old.txt",
                    file_path="p01/d01/m_000001.txt",
                    file_type="txt",
                )
            )
            file_path = controller.file_storage.files_root / "p01" / "d01" / "m_000001.txt"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("content", encoding="utf-8")

            with mock.patch.object(controller.material_repo, "delete", return_value=False):
                deleted = controller.delete_material(material.id)

            self.assertFalse(deleted)
            self.assertTrue(file_path.exists())

    def test_delete_material_keeps_shared_file_when_another_material_references_it(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            controller = AdminController(database)
            controller.file_storage = FileStorageManager(tmp_path / "files")

            shared_path = "p01/d01/shared.txt"
            first = controller.material_repo.add(
                MethodicalMaterial(
                    title="First",
                    material_type="guide",
                    relative_path=shared_path,
                    stored_filename="shared.txt",
                    original_filename="shared.txt",
                    file_name="shared.txt",
                    file_path=shared_path,
                    file_type="txt",
                )
            )
            second = controller.material_repo.add(
                MethodicalMaterial(
                    title="Second",
                    material_type="guide",
                    relative_path=shared_path,
                    stored_filename="shared.txt",
                    original_filename="shared.txt",
                    file_name="shared.txt",
                    file_path=shared_path,
                    file_type="txt",
                )
            )

            file_path = controller.file_storage.files_root / "p01" / "d01" / "shared.txt"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("shared content", encoding="utf-8")

            deleted = controller.delete_material(first.id)

            self.assertTrue(deleted)
            self.assertTrue(file_path.exists())
            self.assertIsNotNone(controller.material_repo.get_by_id(second.id))

    def test_attach_existing_material_file_keeps_old_shared_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            controller = AdminController(database)
            controller.file_storage = FileStorageManager(tmp_path / "files")

            old_relative = "p01/d01/shared.txt"
            material = controller.material_repo.add(
                MethodicalMaterial(
                    title="Primary",
                    material_type="guide",
                    relative_path=old_relative,
                    stored_filename="shared.txt",
                    original_filename="shared.txt",
                    file_name="shared.txt",
                    file_path=old_relative,
                    file_type="txt",
                )
            )
            controller.material_repo.add(
                MethodicalMaterial(
                    title="Sibling",
                    material_type="guide",
                    relative_path=old_relative,
                    stored_filename="shared.txt",
                    original_filename="shared.txt",
                    file_name="shared.txt",
                    file_path=old_relative,
                    file_type="txt",
                )
            )

            old_file = controller.file_storage.files_root / "p01" / "d01" / "shared.txt"
            old_file.parent.mkdir(parents=True, exist_ok=True)
            old_file.write_text("shared content", encoding="utf-8")

            new_file = controller.file_storage.files_root / "p01" / "d01" / "replacement.txt"
            new_file.write_text("replacement", encoding="utf-8")

            updated = controller.attach_existing_material_file(material, str(new_file))

            self.assertEqual(updated.relative_path, "p01/d01/replacement.txt")
            self.assertTrue(old_file.exists())
            self.assertTrue(new_file.exists())

    def test_move_storage_rolls_back_copied_files_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            storage = FileStorageManager(tmp_path / "files_old")

            with database.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO methodical_materials (title, material_type, relative_path, file_path)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("Material", "guide", "p01/d01/m_000001.txt", "p01/d01/m_000001.txt"),
                )

            source_path = storage.files_root / "p01" / "d01" / "m_000001.txt"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text("content", encoding="utf-8")
            new_root = tmp_path / "files_new"

            with mock.patch("src.services.file_storage.set_materials_root", side_effect=RuntimeError("settings failed")):
                with self.assertRaises(RuntimeError):
                    storage.move_storage(database, new_root)

            self.assertTrue(source_path.exists())
            self.assertFalse((new_root / "p01" / "d01" / "m_000001.txt").exists())
            self.assertEqual(storage.files_root, tmp_path / "files_old")

    def test_attach_existing_material_rejects_shared_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            controller = AdminController(database)
            controller.file_storage = FileStorageManager(tmp_path / "files")

            existing_relative = "p01/d01/existing.txt"
            owner = controller.material_repo.add(
                MethodicalMaterial(
                    title="Owner",
                    material_type="guide",
                    relative_path=existing_relative,
                    stored_filename="existing.txt",
                    original_filename="existing.txt",
                    file_name="existing.txt",
                    file_path=existing_relative,
                    file_type="txt",
                )
            )
            target = controller.material_repo.add(MethodicalMaterial(title="Target", material_type="guide"))

            existing_file = controller.file_storage.files_root / "p01" / "d01" / "existing.txt"
            existing_file.parent.mkdir(parents=True, exist_ok=True)
            existing_file.write_text("shared", encoding="utf-8")

            with self.assertRaises(ValueError):
                controller.attach_existing_material_file(target, str(existing_file))

            self.assertIsNotNone(controller.material_repo.get_by_id(owner.id))

    def test_cleanup_unused_data_creates_backup_manifest(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            database = Database(str(tmp_path / "education.db"))
            controller = AdminController(database)
            controller.file_storage = FileStorageManager(tmp_path / "files")
            settings_dir = tmp_path / "settings"
            settings_dir.mkdir()

            material = controller.material_repo.add(
                MethodicalMaterial(
                    title="Orphan",
                    material_type="guide",
                    relative_path="p01/d01/orphan.txt",
                    stored_filename="orphan.txt",
                    original_filename="orphan.txt",
                    file_name="orphan.txt",
                    file_path="p01/d01/orphan.txt",
                    file_type="txt",
                )
            )
            orphan_file = controller.file_storage.files_root / "p01" / "d01" / "orphan.txt"
            orphan_file.parent.mkdir(parents=True, exist_ok=True)
            orphan_file.write_text("content", encoding="utf-8")

            with mock.patch("src.controllers.admin_controller.get_settings_dir", return_value=settings_dir):
                result = controller.cleanup_unused_data()

            backup_path = Path(result["backup_path"])
            self.assertTrue((backup_path / "manifest.json").exists())
            self.assertIsNone(controller.material_repo.get_by_id(material.id))
