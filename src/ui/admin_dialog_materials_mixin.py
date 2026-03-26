"""Materials CRUD and association helpers extracted from AdminDialog."""

from __future__ import annotations

from typing import Callable
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
)

from .dialogs import MaterialDialog, MaterialTypeDialog


class AdminDialogMaterialsMixin:
    """Materials actions, files and associations for AdminDialog."""

    def _refresh_materials(self) -> None:
        self.materials_table.setRowCount(0)
        target = self._current_structure_material_target()
        self._set_material_buttons_enabled(bool(target))
        if not target:
            return
        entity_type, entity = target
        for material in self.controller.get_materials_for_entity(entity_type, entity.id):
            row = self.materials_table.rowCount()
            self.materials_table.insertRow(row)
            self.materials_table.setItem(row, 0, QTableWidgetItem(material.title))
            self.materials_table.setItem(row, 1, QTableWidgetItem(self._translate_material_type(material.material_type)))
            filename = material.original_filename or material.file_name or ""
            self.materials_table.setItem(row, 2, QTableWidgetItem(filename))
            authors = ", ".join(t.full_name for t in material.teachers) if material.teachers else ""
            self.materials_table.setItem(row, 3, QTableWidgetItem(authors))
            self.materials_table.item(row, 0).setData(Qt.UserRole, material)

    def _add_material(self) -> None:
        target = self._current_structure_material_target()
        if not target:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a program, discipline or lesson first."))
            return
        entity_type, entity = target
        teachers = self._filtered_teachers_for_target(entity_type, entity)
        dialog = MaterialDialog(
            parent=self,
            material_types=self.controller.get_material_types(),
            teachers=teachers,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        material = dialog.get_material()
        if not material.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Material title is required."))
            return
        material = self.controller.add_material(material)
        self.controller.add_material_to_entity(material.id, entity_type, entity.id)
        for teacher_id in dialog.get_selected_teacher_ids():
            self.controller.add_teacher_to_material(teacher_id, material.id)
        attach_path = dialog.get_attachment_path()
        existing_path = dialog.get_existing_attachment_path()
        try:
            if attach_path:
                self.controller.attach_material_file(material, attach_path)
            elif existing_path:
                self.controller.attach_existing_material_file(material, existing_path)
        except (ValueError, RuntimeError, OSError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
        self._refresh_materials()

    def _edit_material(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        target = self._current_structure_material_target()
        teachers = self.controller.get_teachers()
        if target:
            entity_type, entity = target
            teachers = self._filtered_teachers_for_target(entity_type, entity)
            material = self.controller.ensure_material_for_edit(material, entity_type, entity.id)
        filtered_ids = {t.id for t in teachers if t.id is not None}
        selected_teacher_ids = [teacher.id for teacher in material.teachers if teacher.id is not None]
        if filtered_ids:
            extra_teachers = [t for t in material.teachers if t.id not in filtered_ids]
            if extra_teachers:
                teachers = teachers + extra_teachers
        dialog = MaterialDialog(
            material,
            material_types=self.controller.get_material_types(),
            teachers=teachers,
            selected_teacher_ids=selected_teacher_ids,
            parent=self,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_material(dialog.get_material())
        new_teacher_ids = set(dialog.get_selected_teacher_ids())
        old_teacher_ids = {teacher.id for teacher in material.teachers if teacher.id is not None}
        for teacher_id in new_teacher_ids - old_teacher_ids:
            self.controller.add_teacher_to_material(teacher_id, material.id)
        for teacher_id in old_teacher_ids - new_teacher_ids:
            self.controller.remove_teacher_from_material(teacher_id, material.id)
        attach_path = dialog.get_attachment_path()
        existing_path = dialog.get_existing_attachment_path()
        try:
            if attach_path:
                self.controller.attach_material_file(material, attach_path)
            elif existing_path:
                self.controller.attach_existing_material_file(material, existing_path)
        except (ValueError, RuntimeError, OSError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
        self._refresh_materials()

    def _delete_material(self) -> None:
        materials = self._selected_entities(self.materials_table)
        if not materials:
            return
        confirm_text = (
            self.tr("Delete selected material?")
            if len(materials) == 1
            else self.tr("Delete selected material?") + f" ({len(materials)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for material in materials:
            self.controller.delete_material(material.id)
        self._refresh_materials()

    def _refresh_material_types(self) -> None:
        if not hasattr(self, "material_types_table"):
            return
        self.material_types_table.setRowCount(0)
        for material_type in self.controller.get_material_types():
            row = self.material_types_table.rowCount()
            self.material_types_table.insertRow(row)
            self.material_types_table.setItem(row, 0, QTableWidgetItem(material_type.name))
            self.material_types_table.item(row, 0).setData(Qt.UserRole, material_type)

    def _add_material_type(self) -> None:
        dialog = MaterialTypeDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        material_type = dialog.get_material_type()
        if not material_type.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Name is required."))
            return
        self.controller.add_material_type(material_type)
        self._refresh_material_types()

    def _edit_material_type(self) -> None:
        material_type = self._current_entity(self.material_types_table)
        if not material_type:
            return
        dialog = MaterialTypeDialog(material_type, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_material_type(dialog.get_material_type())
        self._refresh_material_types()
        self._refresh_materials()

    def _delete_material_type(self) -> None:
        material_types = self._selected_entities(self.material_types_table)
        if not material_types:
            return
        confirm_text = (
            self.tr("Delete selected material type?")
            if len(material_types) == 1
            else self.tr("Delete selected material type?") + f" ({len(material_types)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for material_type in material_types:
            self.controller.delete_material_type(material_type.id)
        self._refresh_material_types()

    def _attach_material_file(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Attach File"),
            "",
            self.tr("Documents (*.pdf *.pptx *.docx)"),
        )
        if not path:
            return
        try:
            updated = self.controller.attach_material_file(material, path)
        except (ValueError, RuntimeError, OSError, sqlite3.Error) as exc:
            selection = self._prompt_material_location()
            if not selection:
                QMessageBox.warning(self, self.tr("Import error"), f"{exc}\n\n{self._database_diagnostics()}")
                return
            program_id, discipline_id = selection
            try:
                updated = self.controller.attach_material_file_with_context(
                    material, path, program_id, discipline_id
                )
            except (ValueError, RuntimeError, OSError, sqlite3.Error) as inner_exc:
                QMessageBox.warning(self, self.tr("Import error"), f"{inner_exc}\n\n{self._database_diagnostics()}")
                return
        if updated:
            self._refresh_materials()

    def _attach_existing_material_file(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Attach existing file"),
            "",
            self.tr("All files (*)"),
        )
        if not path:
            return
        try:
            updated = self.controller.attach_existing_material_file(material, path)
        except (ValueError, RuntimeError, OSError, sqlite3.Error) as exc:
            QMessageBox.warning(self, self.tr("Import error"), f"{exc}\n\n{self._database_diagnostics()}")
            return
        if updated:
            self._refresh_materials()

    def _prompt_material_location(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Select material location"))
        layout = QVBoxLayout(dialog)
        form = QHBoxLayout()
        program_label = QLabel(self.tr("Program"))
        program_combo = QComboBox()
        discipline_label = QLabel(self.tr("Discipline"))
        discipline_combo = QComboBox()
        form.addWidget(program_label)
        form.addWidget(program_combo)
        form.addWidget(discipline_label)
        form.addWidget(discipline_combo)
        layout.addLayout(form)

        for program in self.controller.get_programs():
            program_combo.addItem(program.name, program.id)

        def refresh_disciplines():
            discipline_combo.clear()
            program_id = program_combo.currentData()
            if program_id is None:
                return
            for discipline in self.controller.get_program_disciplines(program_id):
                discipline_combo.addItem(discipline.name, discipline.id)

        program_combo.currentIndexChanged.connect(refresh_disciplines)
        refresh_disciplines()

        buttons = QHBoxLayout()
        ok_btn = QPushButton(self.tr("OK"))
        cancel_btn = QPushButton(self.tr("Cancel"))
        buttons.addStretch(1)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return None
        return program_combo.currentData(), discipline_combo.currentData()

    def _open_material_file(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        if not material.relative_path:
            QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
            return
        self._run_material_file_action(
            lambda: self.file_storage.open_file(material.relative_path),
            invalid_title=self.tr("Invalid File"),
            invalid_message=self.tr("Stored file path is invalid."),
            missing_title=self.tr("No File"),
            missing_message=self.tr("File is missing in storage."),
        )

    def _show_material_folder(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        if not material.relative_path:
            QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
            return
        self._run_material_file_action(
            lambda: self.file_storage.show_in_folder(material.relative_path),
            invalid_title=self.tr("Invalid File"),
            invalid_message=self.tr("Stored file path is invalid."),
            missing_title=self.tr("No File"),
            missing_message=self.tr("File is missing in storage."),
        )

    def _copy_material_file(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        if not material.relative_path:
            QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
            return
        default_name = material.title
        ext = f".{material.file_type}" if material.file_type else ""
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Copy file as..."),
            f"{default_name}{ext}",
            self.tr("All files (*)"),
        )
        if not path:
            return
        self._run_material_file_action(
            lambda: self.file_storage.copy_file_as(material.relative_path, path),
            invalid_title=self.tr("Invalid File"),
            invalid_message=self.tr("Stored file path is invalid."),
            missing_title=self.tr("No File"),
            missing_message=self.tr("File is missing in storage."),
        )

    @staticmethod
    def _execute_material_file_action(action: Callable[[], bool]) -> tuple[bool | None, str | None]:
        try:
            return action(), None
        except (ValueError, OSError) as exc:
            return None, str(exc)

    def _run_material_file_action(
        self,
        action: Callable[[], bool],
        *,
        invalid_title: str,
        invalid_message: str,
        missing_title: str,
        missing_message: str,
    ) -> bool:
        ok, error = self._execute_material_file_action(action)
        if error is not None:
            QMessageBox.warning(self, invalid_title, invalid_message)
            return False
        if not ok:
            QMessageBox.warning(self, missing_title, missing_message)
            return False
        return True

    def _refresh_material_assignments(self) -> None:
        material = self._current_entity(self.materials_table)
        self.material_teachers_available.clear()
        self.material_teachers_assigned.clear()
        self.material_assoc_assigned.clear()
        self.material_assoc_available.clear()
        if not material:
            return

        teachers = self.controller.get_teachers()
        assigned_teachers = {t.id for t in material.teachers}
        for teacher in teachers:
            item = QListWidgetItem(teacher.full_name)
            item.setData(Qt.UserRole, teacher)
            if teacher.id in assigned_teachers:
                self.material_teachers_assigned.addItem(item)
            else:
                self.material_teachers_available.addItem(item)

        for entity_type, entity_id, title in self.controller.get_material_associations(material.id):
            label = f"{self._translate_entity_type(entity_type)}: {title}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, (entity_type, entity_id))
            self.material_assoc_assigned.addItem(item)

        self._refresh_material_associations()

    def _refresh_material_associations(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        self.material_assoc_available.clear()
        entity_type = self.material_assoc_type.currentData()
        if entity_type == "program":
            entities = self.controller.get_programs()
            for entity in entities:
                item = QListWidgetItem(entity.name)
                item.setData(Qt.UserRole, entity)
                self.material_assoc_available.addItem(item)
        elif entity_type == "discipline":
            entities = self.controller.get_disciplines()
            for entity in entities:
                item = QListWidgetItem(entity.name)
                item.setData(Qt.UserRole, entity)
                self.material_assoc_available.addItem(item)
        elif entity_type == "topic":
            entities = self.controller.get_topics()
            for entity in entities:
                item = QListWidgetItem(entity.title)
                item.setData(Qt.UserRole, entity)
                self.material_assoc_available.addItem(item)
        elif entity_type == "lesson":
            entities = self.controller.get_lessons()
            for entity in entities:
                item = QListWidgetItem(entity.title)
                item.setData(Qt.UserRole, entity)
                self.material_assoc_available.addItem(item)

    def _add_teacher_to_material(self) -> None:
        material = self._current_entity(self.materials_table)
        item = self.material_teachers_available.currentItem()
        if not material or not item:
            return
        teacher = item.data(Qt.UserRole)
        self.controller.add_teacher_to_material(teacher.id, material.id)
        self._refresh_materials()

    def _remove_teacher_from_material(self) -> None:
        material = self._current_entity(self.materials_table)
        item = self.material_teachers_assigned.currentItem()
        if not material or not item:
            return
        teacher = item.data(Qt.UserRole)
        self.controller.remove_teacher_from_material(teacher.id, material.id)
        self._refresh_materials()

    def _link_material_association(self) -> None:
        material = self._current_entity(self.materials_table)
        item = self.material_assoc_available.currentItem()
        if not material or not item:
            return
        entity_type = self.material_assoc_type.currentData()
        entity = item.data(Qt.UserRole)
        self.controller.add_material_to_entity(material.id, entity_type, entity.id)
        self._refresh_materials()

    def _unlink_material_association(self) -> None:
        material = self._current_entity(self.materials_table)
        item = self.material_assoc_assigned.currentItem()
        if not material or not item:
            return
        entity_type, entity_id = item.data(Qt.UserRole)
        self.controller.remove_material_from_entity(material.id, entity_type, entity_id)
        self._refresh_materials()
