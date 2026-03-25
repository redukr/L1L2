import tempfile
import unittest
from pathlib import Path

from src.models.database import Database
from src.services.import_service import (
    build_batch_import_plan,
    extract_text_from_file,
    import_teachers_from_docx,
    parse_curriculum_text,
    summarize_curriculum_topics,
)


class ImportRegressionTests(unittest.TestCase):
    def test_curriculum_parser_uses_header_mapping(self):
        text = "\n".join(["Тема 1. Основи", "Заняття 1. Лекція", "1. Q1", "2. Q2"])

        topics = parse_curriculum_text(text)

        self.assertEqual(len(topics), 1)
        lesson = topics[0].lessons[0]
        self.assertEqual(lesson.lesson_type_name, "Лекція")
        self.assertIsNone(lesson.total_hours)
        self.assertIsNone(lesson.classroom_hours)
        self.assertIsNone(lesson.self_study_hours)
        self.assertEqual([question.text for question in lesson.questions][-2:], ["1. Q1", "2. Q2"])

    def test_text_import_supports_cp1251(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sample.txt"
            expected = "\u041f\u0440\u0438\u0432\u0456\u0442"
            path.write_bytes(expected.encode("cp1251"))
            self.assertEqual(extract_text_from_file(str(path)), expected)

    def test_curriculum_preview_summary_counts_entities(self):
        topics = parse_curriculum_text(
            "\n".join(["Тема 1. Основи", "Заняття 1. Intro", "1. Q1", "2. Q2"])
        )

        summary = summarize_curriculum_topics(topics)

        self.assertEqual(summary.topics_count, 1)
        self.assertEqual(summary.lessons_count, 1)
        self.assertEqual(summary.questions_count, 2)

    def test_import_teachers_rejects_duplicate_emails(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            path = tmp_path / "teachers.docx"
            try:
                from docx import Document
            except ImportError:
                self.skipTest("python-docx is not installed")
            doc = Document()
            table = doc.add_table(rows=3, cols=2)
            table.rows[0].cells[0].text = "name"
            table.rows[0].cells[1].text = "email"
            table.rows[1].cells[0].text = "A"
            table.rows[1].cells[1].text = "same@example.com"
            table.rows[2].cells[0].text = "B"
            table.rows[2].cells[1].text = "same@example.com"
            doc.save(path)

            with self.assertRaises(ValueError):
                import_teachers_from_docx(Database(":memory:"), str(path))

    def test_batch_import_plan_uses_filename_targets(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "Program A - Discipline B.txt"
            path.write_text("\n".join(["Тема 1. Основи", "Заняття 1. Intro", "1. Q1"]), encoding="utf-8")

            plan = build_batch_import_plan([str(path)])

            self.assertEqual(len(plan), 1)
            self.assertEqual(plan[0].program_name, "Program A")
            self.assertEqual(plan[0].discipline_name, "Discipline B")
            self.assertEqual(plan[0].summary.topics_count, 1)

    def test_batch_import_plan_rejects_empty_derived_names(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "   .txt"
            path.write_text("\n".join(["Тема 1. Основи", "Заняття 1. Intro", "1. Q1"]), encoding="utf-8")

            with self.assertRaises(ValueError):
                build_batch_import_plan([str(path)])
