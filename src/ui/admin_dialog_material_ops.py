"""Material and maintenance workflows extracted from AdminDialog."""

from __future__ import annotations

import sqlite3

from PySide6.QtWidgets import QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout


def add_material(dialog) -> None:  # noqa: ANN001
    target = dialog._current_structure_material_target()
    if not target:
        QMessageBox.warning(dialog, dialog.tr("Validation"), dialog.tr("Select a program, discipline or lesson first."))
        return
    entity_type, entity = target
    teachers = dialog._filtered_teachers_for_target(entity_type, entity)
    material_dialog = dialog._create_material_dialog(teachers=teachers)
    if material_dialog.exec() != QDialog.Accepted:
        return
    material = material_dialog.get_material()
    if not material.title:
        QMessageBox.warning(dialog, dialog.tr("Validation"), dialog.tr("Material title is required."))
        return
    material = dialog.controller.add_material(material)
    dialog.controller.add_material_to_entity(material.id, entity_type, entity.id)
    for teacher_id in material_dialog.get_selected_teacher_ids():
        dialog.controller.add_teacher_to_material(teacher_id, material.id)
    _attach_dialog_material(dialog, material, material_dialog.get_attachment_path(), material_dialog.get_existing_attachment_path())
    dialog._refresh_materials()


def edit_material(dialog) -> None:  # noqa: ANN001
    material = dialog._current_entity(dialog.materials_table)
    if not material:
        return
    target = dialog._current_structure_material_target()
    teachers = dialog.controller.get_teachers()
    if target:
        entity_type, entity = target
        teachers = dialog._filtered_teachers_for_target(entity_type, entity)
        material = dialog.controller.ensure_material_for_edit(material, entity_type, entity.id)
    filtered_ids = {t.id for t in teachers if t.id is not None}
    selected_teacher_ids = [teacher.id for teacher in material.teachers if teacher.id is not None]
    if filtered_ids:
        extra_teachers = [t for t in material.teachers if t.id not in filtered_ids]
        if extra_teachers:
            teachers = teachers + extra_teachers
    material_dialog = dialog._create_material_dialog(
        material=material,
        teachers=teachers,
        selected_teacher_ids=selected_teacher_ids,
    )
    if material_dialog.exec() != QDialog.Accepted:
        return
    dialog.controller.update_material(material_dialog.get_material())
    new_teacher_ids = set(material_dialog.get_selected_teacher_ids())
    old_teacher_ids = {teacher.id for teacher in material.teachers if teacher.id is not None}
    for teacher_id in new_teacher_ids - old_teacher_ids:
        dialog.controller.add_teacher_to_material(teacher_id, material.id)
    for teacher_id in old_teacher_ids - new_teacher_ids:
        dialog.controller.remove_teacher_from_material(teacher_id, material.id)
    _attach_dialog_material(dialog, material, material_dialog.get_attachment_path(), material_dialog.get_existing_attachment_path())
    dialog._refresh_materials()


def attach_material_file(dialog) -> None:  # noqa: ANN001
    material = dialog._current_entity(dialog.materials_table)
    if not material:
        return
    path, _ = QFileDialog.getOpenFileName(
        dialog,
        dialog.tr("Attach File"),
        "",
        dialog.tr("Documents (*.pdf *.pptx *.docx)"),
    )
    if not path:
        return
    try:
        updated = dialog.controller.attach_material_file(material, path)
    except (ValueError, sqlite3.Error, OSError, RuntimeError) as exc:
        selection = prompt_material_location(dialog)
        if not selection:
            QMessageBox.warning(dialog, dialog.tr("Import error"), f"{exc}\n\n{database_diagnostics(dialog)}")
            return
        program_id, discipline_id = selection
        try:
            updated = dialog.controller.attach_material_file_with_context(material, path, program_id, discipline_id)
        except (ValueError, sqlite3.Error, OSError, RuntimeError) as inner_exc:
            QMessageBox.warning(dialog, dialog.tr("Import error"), f"{inner_exc}\n\n{database_diagnostics(dialog)}")
            return
    if updated:
        dialog._refresh_materials()


def attach_existing_material_file(dialog) -> None:  # noqa: ANN001
    material = dialog._current_entity(dialog.materials_table)
    if not material:
        return
    path, _ = QFileDialog.getOpenFileName(
        dialog,
        dialog.tr("Attach existing file"),
        "",
        dialog.tr("All files (*)"),
    )
    if not path:
        return
    try:
        updated = dialog.controller.attach_existing_material_file(material, path)
    except (ValueError, sqlite3.Error, OSError, RuntimeError) as exc:
        QMessageBox.warning(dialog, dialog.tr("Import error"), f"{exc}\n\n{database_diagnostics(dialog)}")
        return
    if updated:
        dialog._refresh_materials()


def prompt_material_location(dialog):  # noqa: ANN001
    chooser = QDialog(dialog)
    chooser.setWindowTitle(dialog.tr("Select material location"))
    layout = QVBoxLayout(chooser)
    form = QHBoxLayout()
    program_label = QLabel(dialog.tr("Program"))
    program_combo = QComboBox()
    discipline_label = QLabel(dialog.tr("Discipline"))
    discipline_combo = QComboBox()
    form.addWidget(program_label)
    form.addWidget(program_combo)
    form.addWidget(discipline_label)
    form.addWidget(discipline_combo)
    layout.addLayout(form)

    for program in dialog.controller.get_programs():
        program_combo.addItem(program.name, program.id)

    def refresh_disciplines() -> None:
        discipline_combo.clear()
        program_id = program_combo.currentData()
        if program_id is None:
            return
        for discipline in dialog.controller.get_program_disciplines(program_id):
            discipline_combo.addItem(discipline.name, discipline.id)

    program_combo.currentIndexChanged.connect(refresh_disciplines)
    refresh_disciplines()

    buttons = QHBoxLayout()
    ok_btn = QPushButton(dialog.tr("OK"))
    cancel_btn = QPushButton(dialog.tr("Cancel"))
    buttons.addStretch(1)
    buttons.addWidget(ok_btn)
    buttons.addWidget(cancel_btn)
    layout.addLayout(buttons)
    ok_btn.clicked.connect(chooser.accept)
    cancel_btn.clicked.connect(chooser.reject)

    if chooser.exec() != QDialog.Accepted:
        return None
    return program_combo.currentData(), discipline_combo.currentData()


def database_diagnostics(dialog) -> str:  # noqa: ANN001
    path = dialog.controller.db.db_path
    status = "unknown"
    con = None
    try:
        con = sqlite3.connect(path)
        rows = con.execute("PRAGMA integrity_check;").fetchall()
        status = ", ".join(row[0] for row in rows)
    except (sqlite3.Error, OSError) as exc:
        status = f"error: {exc}"
    finally:
        if con is not None:
            con.close()
    return f"DB: {path}\nIntegrity: {status}"


def check_database(dialog) -> None:  # noqa: ANN001
    QMessageBox.information(dialog, dialog.tr("Check database"), database_diagnostics(dialog))


def cleanup_unused_data(dialog) -> None:  # noqa: ANN001
    counts = dialog.controller.get_unused_data_counts()
    total = sum(counts.values())
    if total == 0:
        QMessageBox.information(dialog, dialog.tr("Cleanup unused data"), dialog.tr("No unused data found."))
        return
    details = [
        f"{dialog.tr('Programs')}: {counts['programs']}",
        f"{dialog.tr('Disciplines')}: {counts['disciplines']}",
        f"{dialog.tr('Topics')}: {counts['topics']}",
        f"{dialog.tr('Lessons')}: {counts['lessons']}",
        f"{dialog.tr('Questions')}: {counts['questions']}",
        f"{dialog.tr('Materials')}: {counts['materials']}",
    ]
    message = dialog.tr("Unused data will be deleted:") + "\n" + "\n".join(details)
    if QMessageBox.question(dialog, dialog.tr("Confirm"), message) != QMessageBox.Yes:
        return
    result = dialog.controller.cleanup_unused_data()
    backup_path = result.get("backup_path") if isinstance(result, dict) else None
    completed_message = dialog.tr("Cleanup completed.")
    if backup_path:
        completed_message += "\n" + dialog.tr("Backup saved to: {0}").format(backup_path)
    QMessageBox.information(dialog, dialog.tr("Cleanup unused data"), completed_message)


def _attach_dialog_material(dialog, material, attach_path: str, existing_path: str) -> None:  # noqa: ANN001
    try:
        if attach_path:
            dialog.controller.attach_material_file(material, attach_path)
        elif existing_path:
            dialog.controller.attach_existing_material_file(material, existing_path)
    except (ValueError, sqlite3.Error, OSError, RuntimeError) as exc:
        QMessageBox.warning(dialog, dialog.tr("Import error"), str(exc))
