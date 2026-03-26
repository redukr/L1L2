"""Teacher CRUD and associations extracted from AdminDialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QDialog, QTableWidgetItem

from .dialogs import TeacherDialog


class AdminDialogTeachersMixin:
    """Teacher tab behavior for AdminDialog."""

    def _refresh_teachers(self) -> None:
        self._teachers_updating = True
        self.teachers_table.setRowCount(0)
        teachers = list(self.controller.get_teachers())
        teachers.sort(key=self._teacher_sort_key)
        for teacher in teachers:
            row = self.teachers_table.rowCount()
            self.teachers_table.insertRow(row)
            self.teachers_table.setItem(row, 0, QTableWidgetItem(teacher.full_name))
            self.teachers_table.setItem(row, 1, QTableWidgetItem(teacher.military_rank or ""))
            self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher.position or ""))
            self.teachers_table.setItem(row, 3, QTableWidgetItem(teacher.department or ""))
            self.teachers_table.setItem(row, 4, QTableWidgetItem(teacher.email or ""))
            self.teachers_table.setItem(row, 5, QTableWidgetItem(teacher.phone or ""))
            self.teachers_table.item(row, 0).setData(Qt.UserRole, teacher)
        self._teachers_updating = False
        self._refresh_teacher_disciplines()

    def _on_teacher_item_changed(self, item: QTableWidgetItem) -> None:
        if getattr(self, "_teachers_updating", False):
            return
        row = item.row()
        teacher_item = self.teachers_table.item(row, 0)
        if not teacher_item:
            return
        teacher = teacher_item.data(Qt.UserRole)
        if not teacher or teacher.id is None:
            return
        value = (item.text() or "").strip()
        if item.column() == 0:
            teacher.full_name = value
        elif item.column() == 1:
            teacher.military_rank = value or None
        elif item.column() == 2:
            teacher.position = value or None
        elif item.column() == 3:
            teacher.department = value or None
        elif item.column() == 4:
            teacher.email = value or None
        elif item.column() == 5:
            teacher.phone = value or None
        else:
            return
        self.controller.update_teacher(teacher)
        self._teachers_updating = True
        try:
            teacher_item.setData(Qt.UserRole, teacher)
        finally:
            self._teachers_updating = False

    def _teacher_sort_key(self, teacher) -> tuple:
        position = (teacher.position or "").lower()
        department = (teacher.department or "").lower()
        rank = (teacher.military_rank or "").strip()
        rank_lower = rank.lower()
        has_rank = bool(rank)

        is_head = "начальник кафедри" in position
        is_deputy = "заступник начальника кафедри" in position
        is_docent = "доцент" in position
        is_senior = "старший викладач" in position
        is_teacher = "викладач" in position
        is_zsu = ("зсу" in position) or ("зсу" in department)

        rank_order = [
            "полковник",
            "підполковник",
            "майор",
            "капітан",
            "старший лейтенант",
            "лейтенант",
            "молодший лейтенант",
        ]
        rank_index = len(rank_order)
        for idx, token in enumerate(rank_order):
            if token in rank_lower:
                rank_index = idx
                break

        if is_zsu:
            group = 6
        elif is_head:
            group = 1
        elif is_deputy:
            group = 2
        elif is_docent and has_rank:
            group = 3
        elif is_senior and has_rank:
            group = 4
        elif is_teacher and has_rank:
            group = 5
        else:
            group = 7

        sub = 0
        if group == 6:
            sub = 0 if is_docent else 1

        return (group, sub, rank_index, teacher.full_name.lower())

    def _refresh_teacher_disciplines(self) -> None:
        if not hasattr(self, "teacher_disciplines_available"):
            return
        self.teacher_disciplines_available.clear()
        self.teacher_disciplines_assigned.clear()
        teacher = self._current_entity(self.teachers_table)
        if not teacher:
            return
        assigned = {d.id for d in self.controller.get_teacher_disciplines(teacher.id)}
        discipline_programs = {}
        for program in self.controller.get_programs():
            for discipline in self.controller.get_program_disciplines(program.id):
                discipline_programs.setdefault(discipline.id, []).append(program.name)
        for discipline in self.controller.get_disciplines():
            programs = discipline_programs.get(discipline.id, [])
            if programs:
                label = "\n".join(f"{program} | {discipline.name}" for program in programs)
            else:
                label = discipline.name
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, discipline)
            if discipline.id in assigned:
                self.teacher_disciplines_assigned.addItem(item)
            else:
                self.teacher_disciplines_available.addItem(item)

    def _add_discipline_to_teacher(self) -> None:
        teacher = self._current_entity(self.teachers_table)
        item = self.teacher_disciplines_available.currentItem()
        if not teacher or not item:
            return
        discipline = item.data(Qt.UserRole)
        self.controller.add_discipline_to_teacher(teacher.id, discipline.id)
        self._refresh_teacher_disciplines()

    def _remove_discipline_from_teacher(self) -> None:
        teacher = self._current_entity(self.teachers_table)
        item = self.teacher_disciplines_assigned.currentItem()
        if not teacher or not item:
            return
        discipline = item.data(Qt.UserRole)
        self.controller.remove_discipline_from_teacher(teacher.id, discipline.id)
        self._refresh_teacher_disciplines()

    def _add_teacher(self) -> None:
        dialog = TeacherDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        teacher = dialog.get_teacher()
        if not teacher.full_name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Full name is required."))
            return
        self.controller.add_teacher(teacher)
        self._log_action("add_teacher", teacher.full_name or "")
        self._refresh_teachers()

    def _edit_teacher(self) -> None:
        teacher = self._current_entity(self.teachers_table)
        if not teacher:
            return
        dialog = TeacherDialog(teacher, self)
        if dialog.exec() != QDialog.Accepted:
            return
        updated = dialog.get_teacher()
        if updated.id is None:
            updated.id = teacher.id
        self.controller.update_teacher(updated)
        self._log_action("edit_teacher", updated.full_name or "")
        self._refresh_teachers()

    def _delete_teacher(self) -> None:
        teachers = self._selected_entities(self.teachers_table)
        if not teachers:
            return
        confirm_text = (
            self.tr("Delete selected teacher?")
            if len(teachers) == 1
            else self.tr("Delete selected teacher?") + f" ({len(teachers)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for teacher in teachers:
            self.controller.delete_teacher(teacher.id)
            self._log_action("delete_teacher", teacher.full_name or "")
        self._refresh_teachers()
