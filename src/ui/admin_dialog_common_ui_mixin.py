"""Shared UI helper methods for AdminDialog."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QProcess
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QTableWidget


class AdminDialogCommonUiMixin:
    """Generic entity/table helper methods and common UI actions."""

    def _current_entity(self, table: QTableWidget):
        row = table.currentRow()
        if row < 0:
            return None
        item = table.item(row, 0)
        if not item:
            return None
        return item.data(Qt.UserRole)

    def _selected_entities(self, table: QTableWidget):
        entities = []
        rows = {index.row() for index in table.selectionModel().selectedRows()}
        for row in sorted(rows):
            item = table.item(row, 0)
            if item:
                entity = item.data(Qt.UserRole)
                if entity:
                    entities.append(entity)
        return entities

    def _translate_entity_type(self, entity_type: str) -> str:
        mapping = {
            "program": self.tr("Program"),
            "discipline": self.tr("Discipline"),
            "topic": self.tr("Topic"),
            "lesson": self.tr("Lesson"),
            "question": self.tr("Question"),
            "teacher": self.tr("Teacher"),
            "material": self.tr("Material"),
        }
        return mapping.get(entity_type, entity_type)

    def _translate_material_type(self, material_type: str) -> str:
        mapping = {
            "plan": self.tr("plan"),
            "guide": self.tr("guide"),
            "presentation": self.tr("presentation"),
            "attachment": self.tr("attachment"),
        }
        return mapping.get(material_type or "", material_type or "")

    def _show_context_menu(self, table: QTableWidget, pos, on_edit, on_delete) -> None:  # noqa: ANN001
        item = table.itemAt(pos)
        if not item:
            return
        table.selectRow(item.row())
        menu = QMenu(table)
        edit_action = menu.addAction(self.tr("Edit"))
        delete_action = menu.addAction(self.tr("Delete"))
        action = menu.exec(table.viewport().mapToGlobal(pos))
        if action == edit_action:
            on_edit()
        elif action == delete_action:
            on_delete()

    def _show_structure_context_menu(self, pos) -> None:  # noqa: ANN001
        item = self.structure_tree.itemAt(pos)
        if not item:
            return
        self.structure_tree.setCurrentItem(item)
        menu = QMenu(self.structure_tree)
        edit_action = menu.addAction(self.tr("Edit"))
        delete_action = menu.addAction(self.tr("Delete"))
        duplicate_action = menu.addAction(self.tr("Duplicate"))
        copy_action = menu.addAction(self.tr("Copy"))
        action = menu.exec(self.structure_tree.viewport().mapToGlobal(pos))
        if action == edit_action:
            self._edit_structure_selected()
        elif action == delete_action:
            self._delete_structure_selected()
        elif action == duplicate_action:
            self._duplicate_structure_selected()
        elif action == copy_action:
            self._copy_structure_selected()

    def _show_about(self) -> None:
        text = "\n".join(
            [
                self.tr(
                    "Copyright on the program idea belongs to the Department of Military Leadership "
                    "of the Military Academy, Odesa."
                ),
                self.tr("Developer: Lieutenant Heorhii FYLYPOVYCH."),
                self.tr(
                    "Special thanks: Major Vitalii SAVCHUK, Lieutenant Colonel Olha Odyntsova."
                ),
            ]
        )
        QMessageBox.information(self, self.tr("About"), text)

    def _restart_application(self) -> None:
        QProcess.startDetached(sys.executable, sys.argv)
        QApplication.quit()

    def _close_application(self) -> None:
        QApplication.quit()
