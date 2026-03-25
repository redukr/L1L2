"""Import-related workflows extracted from AdminDialog."""

from __future__ import annotations

import sqlite3

from PySide6.QtWidgets import QDialog, QMessageBox

from ..services.import_service import (
    build_batch_import_plan,
    import_curriculum_structure,
    import_curriculum_structure_by_names,
    import_teachers_from_docx,
    preview_curriculum_text,
)
from .dialogs import BatchImportPreviewDialog, ImportCurriculumDialog


def run_import_curriculum(dialog) -> None:  # noqa: ANN001
    import_dialog = ImportCurriculumDialog(dialog.controller, dialog)
    if import_dialog.exec() != QDialog.Accepted:
        return
    program_id, discipline_id, new_name, raw_text, parsed_topics, file_paths = import_dialog.get_payload()

    if file_paths:
        _run_batch_curriculum_import(dialog, file_paths)
        return

    if not raw_text.strip():
        QMessageBox.warning(dialog, dialog.tr("Import error"), dialog.tr("No input text provided."))
        return
    if parsed_topics is None:
        try:
            parsed_topics, _ = preview_curriculum_text(raw_text)
        except ValueError as exc:
            QMessageBox.warning(dialog, dialog.tr("Import error"), str(exc))
            return
    try:
        topics_added, lessons_added, questions_added = import_curriculum_structure(
            dialog.controller.db,
            program_id,
            discipline_id,
            new_name,
            parsed_topics,
        )
    except (ValueError, sqlite3.Error) as exc:
        QMessageBox.warning(dialog, dialog.tr("Import error"), str(exc))
        return
    QMessageBox.information(
        dialog,
        dialog.tr("Import complete"),
        dialog.tr("Added topics: {0}\nAdded lessons: {1}\nAdded questions: {2}").format(
            topics_added, lessons_added, questions_added
        ),
    )
    dialog._refresh_all()


def run_import_teachers(dialog, path: str) -> tuple[int, int]:  # noqa: ANN001
    return import_teachers_from_docx(dialog.controller.db, path)


def _run_batch_curriculum_import(dialog, file_paths: list[str]) -> None:  # noqa: ANN001
    try:
        plan = build_batch_import_plan(file_paths)
    except ValueError as exc:
        QMessageBox.warning(dialog, dialog.tr("Import error"), str(exc))
        return

    preview_dialog = BatchImportPreviewDialog(plan, dialog)
    if preview_dialog.exec() != QDialog.Accepted:
        return

    totals = {"topics": 0, "lessons": 0, "questions": 0}
    errors: list[str] = []
    for item in plan:
        try:
            t_added, l_added, q_added = import_curriculum_structure_by_names(
                dialog.controller.db,
                item.program_name,
                item.discipline_name,
                item.topics,
            )
            totals["topics"] += t_added
            totals["lessons"] += l_added
            totals["questions"] += q_added
        except (ValueError, sqlite3.Error) as exc:
            errors.append(f"{item.path}: {exc}")

    if errors:
        QMessageBox.warning(dialog, dialog.tr("Import error"), "\n".join(errors))
    QMessageBox.information(
        dialog,
        dialog.tr("Import complete"),
        dialog.tr("Added topics: {0}\nAdded lessons: {1}\nAdded questions: {2}").format(
            totals["topics"], totals["lessons"], totals["questions"]
        ),
    )
    dialog._refresh_all()
