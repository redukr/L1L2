import tempfile
import unittest
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import sqlite3
from contextlib import closing
from PySide6.QtCore import QSettings

from src.models.database import Database
from src.repositories.discipline_repository import DisciplineRepository
from src.repositories.teacher_repository import TeacherRepository
from src.repositories.topic_repository import TopicRepository
import src.services.auth_service as auth_module
import src.services.activity_log as activity_log_module
import src.ui.admin_dialog_settings_mixin as settings_mixin_module
import src.app as app_module
from src.services.ui_fallback_translations import UK_UI_FALLBACKS
from src.services.file_storage import FileStorageManager
from src.services.file_storage import StorageScopeError
from src.services.import_service import extract_text_from_file, parse_curriculum_text
from src.services.search_service import SearchService
from src.services import storage_settings
import src.services.i18n as i18n_module
from src.models.entities import MethodicalMaterial
from src.controllers.admin_controller import AdminController
from src.ui.admin_dialog_internet_sync_mixin import AdminDialogInternetSyncMixin
from src.ui.admin_dialog import AdminDialog
from src.ui.main_window import MainWindow


class RegressionTests(unittest.TestCase):
    class _FakeLineEdit:
        def __init__(self, value: str = ""):
            self._value = value

        def text(self) -> str:
            return self._value

        def setText(self, value: str) -> None:
            self._value = value

    class _FakeLabel:
        def __init__(self, value: str = ""):
            self._value = value
            self._style = ""

        def text(self) -> str:
            return self._value

        def setText(self, value: str) -> None:
            self._value = value

        def setStyleSheet(self, value: str) -> None:
            self._style = value

    class _FakePasswordDialog:
        def __init__(self, _parent, title="", label=""):
            self._password = "admin-pass-123"

        def exec(self):
            return 1

        def get_password(self):
            return self._password

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

    def test_admin_dialog_copies_database_via_backup_api(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_path = Path(tmp_dir) / "source.db"
            target_path = Path(tmp_dir) / "target.db"
            with closing(sqlite3.connect(str(source_path))) as conn:
                conn.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY, name TEXT)")
                conn.execute("INSERT INTO sample(name) VALUES ('alpha')")
                conn.commit()

            AdminDialog._copy_database_with_backup(source_path, target_path)

            with closing(sqlite3.connect(str(target_path))) as conn:
                row = conn.execute("SELECT name FROM sample").fetchone()
            self.assertEqual(row[0], "alpha")

    def test_admin_dialog_material_action_reports_invalid_path(self):
        ok, error = AdminDialog._execute_material_file_action(
            lambda: (_ for _ in ()).throw(ValueError("bad path"))
        )
        self.assertIsNone(ok)
        self.assertEqual(error, "bad path")

    def test_storage_settings_invalid_json_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_file = Path(tmp_dir) / "storage.json"
            settings_file.write_text("{", encoding="utf-8")
            fallback_dir = Path(tmp_dir) / "files_default"
            fallback_dir.mkdir()

            original_settings_path = storage_settings._settings_path
            original_get_files_dir = storage_settings.get_files_dir
            storage_settings._settings_path = lambda: settings_file
            storage_settings.get_files_dir = lambda: fallback_dir
            try:
                self.assertEqual(storage_settings.get_materials_root(), fallback_dir)
            finally:
                storage_settings._settings_path = original_settings_path
                storage_settings.get_files_dir = original_get_files_dir

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

    def test_auth_service_does_not_create_default_credentials_automatically(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_dir = Path(tmp_dir) / "settings"
            settings_dir.mkdir()

            original_get_settings_dir = auth_module.get_settings_dir
            auth_module.get_settings_dir = lambda: settings_dir
            try:
                service = auth_module.AuthService()
                self.assertFalse(service.has_admin_credentials())
                self.assertFalse(service.has_editor_credentials())
            finally:
                auth_module.get_settings_dir = original_get_settings_dir

    def test_auth_service_can_set_and_verify_passwords(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_dir = Path(tmp_dir) / "settings"
            settings_dir.mkdir()

            original_get_settings_dir = auth_module.get_settings_dir
            auth_module.get_settings_dir = lambda: settings_dir
            try:
                service = auth_module.AuthService()
                service.set_admin_password("admin-pass-123")
                service.set_editor_password("editor-pass-123")
                self.assertTrue(service.verify_admin_password("admin-pass-123"))
                self.assertFalse(service.verify_admin_password("wrong"))
                self.assertTrue(service.verify_editor_password("editor-pass-123"))
                self.assertFalse(service.verify_editor_password("wrong"))
            finally:
                auth_module.get_settings_dir = original_get_settings_dir

    def test_auth_service_rejects_short_passwords(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_dir = Path(tmp_dir) / "settings"
            settings_dir.mkdir()

            original_get_settings_dir = auth_module.get_settings_dir
            auth_module.get_settings_dir = lambda: settings_dir
            try:
                service = auth_module.AuthService()
                with self.assertRaises(ValueError):
                    service.set_admin_password("short")
                with self.assertRaises(ValueError):
                    service.set_editor_password("short")
            finally:
                auth_module.get_settings_dir = original_get_settings_dir

    def test_auth_service_invalid_credentials_json_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_dir = Path(tmp_dir) / "settings"
            settings_dir.mkdir()
            bad_admin = settings_dir / "admin_credentials.json"
            bad_admin.write_text("{", encoding="utf-8")

            original_get_settings_dir = auth_module.get_settings_dir
            auth_module.get_settings_dir = lambda: settings_dir
            try:
                service = auth_module.AuthService()
                self.assertFalse(service.verify_admin_password("any"))
            finally:
                auth_module.get_settings_dir = original_get_settings_dir

    def test_auth_service_password_write_is_atomic_without_tmp_leftovers(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_dir = Path(tmp_dir) / "settings"
            settings_dir.mkdir()

            original_get_settings_dir = auth_module.get_settings_dir
            auth_module.get_settings_dir = lambda: settings_dir
            try:
                service = auth_module.AuthService()
                service.set_admin_password("admin-pass-123")
                self.assertTrue((settings_dir / "admin_credentials.json").exists())
                self.assertEqual(list(settings_dir.glob("admin_credentials.json.*.tmp")), [])
            finally:
                auth_module.get_settings_dir = original_get_settings_dir

    def test_activity_log_read_all_with_limit_returns_tail(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_dir = Path(tmp_dir) / "settings"
            settings_dir.mkdir()

            original_get_settings_dir = activity_log_module.get_settings_dir
            activity_log_module.get_settings_dir = lambda: settings_dir
            try:
                service = activity_log_module.ActivityLogService()
                for idx in range(10):
                    service.log("u", "m", f"a{idx}", "")
                rows = service.read_all(limit=3)
                self.assertEqual(len(rows), 3)
                self.assertEqual([row["action"] for row in rows], ["a7", "a8", "a9"])
            finally:
                activity_log_module.get_settings_dir = original_get_settings_dir

    def test_admin_controller_attach_existing_file_outside_storage_falls_back_to_copy(self):
        dummy = type("Dummy", (), {})()

        class _Storage:
            def attach_existing_file(self, _source_path):
                raise StorageScopeError("outside storage")

        dummy.file_storage = _Storage()
        calls = {}

        def _attach_material_file(material, source_path):
            calls["material"] = material
            calls["source_path"] = source_path
            return "copied"

        dummy.attach_material_file = _attach_material_file
        dummy.material_repo = type("Repo", (), {"update": lambda self, material: material})()

        material = MethodicalMaterial(id=1, title="M")
        result = AdminController.attach_existing_material_file(dummy, material, "C:/tmp/file.pdf")

        self.assertEqual(result, "copied")
        self.assertIs(calls["material"], material)
        self.assertEqual(calls["source_path"], "C:/tmp/file.pdf")

    def test_admin_controller_attach_existing_file_other_value_error_is_not_swallowed(self):
        dummy = type("Dummy", (), {})()

        class _Storage:
            def attach_existing_file(self, _source_path):
                raise ValueError("bad metadata")

        dummy.file_storage = _Storage()
        dummy.attach_material_file = lambda *_args, **_kwargs: "copied"
        dummy.material_repo = type("Repo", (), {"update": lambda self, material: material})()

        material = MethodicalMaterial(id=1, title="M")
        with self.assertRaises(ValueError):
            AdminController.attach_existing_material_file(dummy, material, "C:/tmp/file.pdf")

    def test_internet_sync_tables_combines_entity_and_link_tables(self):
        dummy = type("DummySync", (AdminDialogInternetSyncMixin,), {})()
        tables = dummy._internet_sync_tables()
        self.assertIn("teachers", tables)
        self.assertIn("material_associations", tables)
        self.assertGreaterEqual(len(tables), 10)

    def test_internet_sync_conflict_columns_exclude_meta_fields(self):
        dummy = type("DummySync", (AdminDialogInternetSyncMixin,), {})()
        cols = dummy._conflict_compare_columns(
            ["id", "sync_uuid", "created_at", "updated_at", "title", "description"]
        )
        self.assertEqual(cols, ["title", "description"])

    def test_internet_sync_rows_differ_uses_normalized_values(self):
        dummy = type("DummySync", (AdminDialogInternetSyncMixin,), {})()
        left = {"duration_hours": 1, "title": "A"}
        right = {"duration_hours": 1.0, "title": "A"}
        self.assertFalse(dummy._rows_differ(left, right, ["duration_hours", "title"]))
        right["title"] = "B"
        self.assertTrue(dummy._rows_differ(left, right, ["duration_hours", "title"]))

    def test_internet_sync_entity_type_table_mapping(self):
        dummy = type("DummySync", (AdminDialogInternetSyncMixin,), {})()
        self.assertEqual(dummy._entity_type_to_table("program"), "educational_programs")
        self.assertEqual(dummy._entity_type_to_table("lesson"), "lessons")
        self.assertIsNone(dummy._entity_type_to_table("unknown"))

    def test_editor_password_change_requires_admin_verification(self):
        class Dummy(settings_mixin_module.AdminDialogSettingsMixin):
            def __init__(self):
                self._set_called = False
                self.controller = type("Controller", (), {})()
                self.controller.auth_service = type("Auth", (), {})()
                self.controller.auth_service.verify_admin_password = lambda _pwd: False
                self.controller.auth_service.set_editor_password = lambda _pwd: setattr(self, "_set_called", True)
                self.tr = lambda text: text
                self._prompt_new_password = lambda *_args, **_kwargs: "editor-pass-123"

        dummy = Dummy()
        original_dialog = settings_mixin_module.PasswordDialog
        original_warning = settings_mixin_module.QMessageBox.warning
        original_info = settings_mixin_module.QMessageBox.information
        settings_mixin_module.PasswordDialog = self._FakePasswordDialog
        settings_mixin_module.QMessageBox.warning = lambda *args, **kwargs: None
        settings_mixin_module.QMessageBox.information = lambda *args, **kwargs: None
        try:
            settings_mixin_module.AdminDialogSettingsMixin._change_editor_password(dummy)
            self.assertFalse(dummy._set_called)
        finally:
            settings_mixin_module.PasswordDialog = original_dialog
            settings_mixin_module.QMessageBox.warning = original_warning
            settings_mixin_module.QMessageBox.information = original_info

    def test_admin_dialog_does_not_persist_internet_db_user(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "bootstrap.ini"
            bootstrap = QSettings(str(settings_path), QSettings.IniFormat)
            bootstrap.setValue("internet_db/host", "example.local")
            bootstrap.setValue("internet_db/port", "3306")
            bootstrap.setValue("internet_db/database", "edu")
            bootstrap.setValue("internet_db/user", "old-user")
            bootstrap.sync()

            dummy = type("Dummy", (), {})()
            dummy.bootstrap_settings = bootstrap
            dummy.internet_db_host = self._FakeLineEdit()
            dummy.internet_db_port = self._FakeLineEdit()
            dummy.internet_db_name = self._FakeLineEdit()
            dummy.internet_db_user = self._FakeLineEdit()
            dummy.internet_db_password = self._FakeLineEdit()
            dummy.internet_db_status = self._FakeLabel()
            dummy._set_internet_db_indicator = lambda _state: None
            dummy._default_internet_db_settings = lambda: {
                "host": "localhost",
                "port": "3306",
                "database": "",
            }
            dummy._log_action = lambda *_args, **_kwargs: None
            dummy.tr = lambda text: text

            AdminDialog._load_internet_db_settings(dummy)
            self.assertEqual(dummy.internet_db_user.text(), "")

            dummy.internet_db_user.setText("new-user")
            AdminDialog._save_internet_db_settings(dummy, show_message=False)

            reloaded = QSettings(str(settings_path), QSettings.IniFormat)
            self.assertFalse(reloaded.contains("internet_db/user"))

    def test_admin_dialog_resolves_sync_relative_materials_root_from_sync_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sync_root = Path(tmp_dir) / "sync"
            (sync_root / "settings").mkdir(parents=True)
            expected_root = sync_root / "files" / "shared"
            expected_root.mkdir(parents=True)
            (sync_root / "settings" / "storage.json").write_text(
                '{"materials_root":"files/shared"}',
                encoding="utf-8",
            )

            dummy = type("Dummy", (), {})()
            dummy._log_action = lambda *_args, **_kwargs: None

            resolved = AdminDialog._resolve_sync_files_root(dummy, sync_root)
            self.assertEqual(resolved.resolve(), expected_root.resolve())

    def test_admin_dialog_rejects_absolute_sync_materials_root_outside_sync(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            sync_root = base / "sync"
            (sync_root / "settings").mkdir(parents=True)
            fallback_root = sync_root / "files"
            fallback_root.mkdir(parents=True)
            outside_root = base / "outside_files"
            outside_root.mkdir(parents=True)
            (sync_root / "settings" / "storage.json").write_text(
                json.dumps({"materials_root": str(outside_root)}),
                encoding="utf-8",
            )

            dummy = type("Dummy", (), {})()
            dummy._log_action = lambda *_args, **_kwargs: None

            resolved = AdminDialog._resolve_sync_files_root(dummy, sync_root)
            self.assertEqual(resolved.resolve(), fallback_root.resolve())

    def test_admin_dialog_rejects_relative_sync_materials_root_outside_sync(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            sync_root = base / "sync"
            (sync_root / "settings").mkdir(parents=True)
            fallback_root = sync_root / "files"
            fallback_root.mkdir(parents=True)
            (base / "escape").mkdir(parents=True)
            (sync_root / "settings" / "storage.json").write_text(
                json.dumps({"materials_root": "../escape"}),
                encoding="utf-8",
            )

            dummy = type("Dummy", (), {})()
            dummy._log_action = lambda *_args, **_kwargs: None

            resolved = AdminDialog._resolve_sync_files_root(dummy, sync_root)
            self.assertEqual(resolved.resolve(), fallback_root.resolve())

    def test_admin_dialog_rejects_material_paths_outside_sync_files_root(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sync_files_root = Path(tmp_dir) / "sync_files"
            sync_files_root.mkdir(parents=True)

            dummy = type("Dummy", (), {})()
            dummy.sync_source_files_root = sync_files_root
            dummy._log_action = lambda *_args, **_kwargs: None
            dummy._safe_sync_material_path = lambda path: AdminDialog._safe_sync_material_path(dummy, path)

            escaped_rel = MethodicalMaterial(relative_path="../secret.txt")
            escaped_file = MethodicalMaterial(file_path="../secret.txt")
            absolute_file = MethodicalMaterial(file_path=str((Path(tmp_dir) / "secret.txt").resolve()))
            valid_rel = MethodicalMaterial(relative_path="p01/d01/m_000001.pdf")

            self.assertIsNone(AdminDialog._resolve_source_material_path(dummy, escaped_rel))
            self.assertIsNone(AdminDialog._resolve_source_material_path(dummy, escaped_file))
            self.assertIsNone(AdminDialog._resolve_source_material_path(dummy, absolute_file))
            valid_path = AdminDialog._resolve_source_material_path(dummy, valid_rel)
            self.assertEqual(valid_path.resolve(), (sync_files_root / "p01/d01/m_000001.pdf").resolve())

    def test_material_file_action_helpers_handle_oserror(self):
        ok, error = AdminDialog._execute_material_file_action(
            lambda: (_ for _ in ()).throw(OSError("io-fail"))
        )
        self.assertIsNone(ok)
        self.assertEqual(error, "io-fail")

        ok, error = MainWindow._execute_material_file_action(
            lambda: (_ for _ in ()).throw(OSError("io-fail"))
        )
        self.assertIsNone(ok)
        self.assertEqual(error, "io-fail")

    def test_uk_translation_coverage_for_tr_strings(self):
        root = Path(__file__).resolve().parents[1]
        pattern = re.compile(r'\btr\(\s*"((?:[^"\\]|\\.)*)"\s*\)')
        strings = set()
        for path in (root / "src").rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in pattern.finditer(text):
                strings.add(bytes(match.group(1), "utf-8").decode("unicode_escape"))

        ts_root = ET.parse(root / "translations" / "app_uk.ts").getroot()
        translated = {}
        for message in ts_root.findall(".//message"):
            source = message.findtext("source") or ""
            translation = message.find("translation")
            text = "".join(translation.itertext()).strip() if translation is not None else ""
            translated[source] = text

        missing = [
            source
            for source in sorted(strings)
            if not translated.get(source, "").strip()
            and not str(UK_UI_FALLBACKS.get(source, "")).strip()
        ]
        self.assertEqual(missing, [])

    def test_i18n_derive_language_path_switches_uk_en_suffix(self):
        path = Path("C:/tmp/translations/app_uk.ts")
        derived = i18n_module.I18nManager._derive_language_path(path, "en")
        self.assertEqual(derived.name, "app_en.ts")

        path2 = Path("C:/tmp/translations/custom-en.ts")
        derived2 = i18n_module.I18nManager._derive_language_path(path2, "uk")
        self.assertEqual(derived2.name, "custom_uk.ts")

    def test_i18n_resolve_language_translation_paths_uses_language_sibling_when_present(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            custom_dir = root / "custom"
            custom_dir.mkdir(parents=True)
            (custom_dir / "app_uk.ts").write_text("<TS></TS>", encoding="utf-8")
            (custom_dir / "app_en.ts").write_text("<TS></TS>", encoding="utf-8")

            class FakeQSettings:
                def value(self, key, default=""):
                    if key == "app/translations_path":
                        return str(custom_dir / "app_uk.ts")
                    return default

                def setValue(self, _key, _value):
                    pass

            original_qsettings = i18n_module.QSettings
            original_get_translations_dir = i18n_module.get_translations_dir
            i18n_module.QSettings = FakeQSettings
            i18n_module.get_translations_dir = lambda: root / "fallback"
            try:
                manager = i18n_module.I18nManager(FakeQSettings())
                qm_path, ts_path = manager._resolve_language_translation_paths("en")
                self.assertEqual(ts_path.resolve(), (custom_dir / "app_en.ts").resolve())
                self.assertEqual(qm_path.resolve(), (custom_dir / "app_en.qm").resolve())
            finally:
                i18n_module.QSettings = original_qsettings
                i18n_module.get_translations_dir = original_get_translations_dir

    def test_report_material_type_normalization_supports_ukrainian_names(self):
        self.assertEqual(MainWindow._normalize_report_material_type("План-конспект"), "plan")
        self.assertEqual(MainWindow._normalize_report_material_type("Методичні рекомендації"), "guide")
        self.assertEqual(MainWindow._normalize_report_material_type("Презентація"), "presentation")

    def test_app_resolve_existing_or_fallback_prefers_existing_fallback(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            fallback = Path(tmp_dir) / "settings.ini"
            fallback.write_text("", encoding="utf-8")
            resolved, changed = app_module._resolve_existing_or_fallback("missing/path.ini", fallback)
            self.assertEqual(Path(resolved).resolve(), fallback.resolve())
            self.assertTrue(changed)


if __name__ == "__main__":
    unittest.main()
