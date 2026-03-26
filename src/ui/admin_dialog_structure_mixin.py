"""Structure tree operations extracted from AdminDialog."""

from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem

from .dialogs import DisciplineDialog, LessonDialog, ProgramDialog, QuestionDialog, TopicDialog


class AdminDialogStructureMixin:
    """Structure tree refresh and structure CRUD/copy/duplicate actions."""

    def _refresh_structure_tree(self) -> None:
        expanded_keys = self._structure_expanded_keys()
        selected_key = self._structure_selected_key()
        self.structure_tree.clear()
        item_index = {}
        for program in self.controller.get_programs():
            program_item = QTreeWidgetItem([program.name])
            program_item.setData(0, Qt.UserRole, program)
            program_item.setData(0, Qt.UserRole + 1, "program")
            self.structure_tree.addTopLevelItem(program_item)
            item_index[("program", program.id)] = program_item
            for discipline in self.controller.get_program_disciplines(program.id):
                discipline_item = QTreeWidgetItem([discipline.name])
                discipline_item.setData(0, Qt.UserRole, discipline)
                discipline_item.setData(0, Qt.UserRole + 1, "discipline")
                program_item.addChild(discipline_item)
                item_index[("discipline", discipline.id)] = discipline_item
                for topic in self.controller.get_discipline_topics(discipline.id):
                    topic_item = QTreeWidgetItem([topic.title])
                    topic_item.setData(0, Qt.UserRole, topic)
                    topic_item.setData(0, Qt.UserRole + 1, "topic")
                    discipline_item.addChild(topic_item)
                    item_index[("topic", topic.id)] = topic_item
                    for lesson in self.controller.get_topic_lessons(topic.id):
                        lesson_item = QTreeWidgetItem([lesson.title])
                        lesson_item.setData(0, Qt.UserRole, lesson)
                        lesson_item.setData(0, Qt.UserRole + 1, "lesson")
                        topic_item.addChild(lesson_item)
                        item_index[("lesson", lesson.id)] = lesson_item
                        for question in self.controller.get_lesson_questions(lesson.id):
                            question_item = QTreeWidgetItem([question.content])
                            question_item.setData(0, Qt.UserRole, question)
                            question_item.setData(0, Qt.UserRole + 1, "question")
                            lesson_item.addChild(question_item)
                            item_index[("question", question.id)] = question_item

        for key in expanded_keys:
            item = item_index.get(key)
            if item:
                item.setExpanded(True)
        if selected_key and selected_key in item_index:
            self.structure_tree.setCurrentItem(item_index[selected_key])
        self._resize_structure_tree()

    def _refresh_structure_with_reorder(self) -> None:
        selection = self._current_structure_entity()
        if not selection:
            self._refresh_structure_tree()
            return
        entity_type, entity = selection
        if entity_type == "lesson":
            self.controller.normalize_lesson_question_order(entity.id)
        elif entity_type == "topic":
            self.controller.normalize_topic_lesson_order(entity.id)
            for lesson in self.controller.get_topic_lessons(entity.id):
                self.controller.normalize_lesson_question_order(lesson.id)
        elif entity_type == "discipline":
            for topic in self.controller.get_discipline_topics(entity.id):
                self.controller.normalize_topic_lesson_order(topic.id)
                for lesson in self.controller.get_topic_lessons(topic.id):
                    self.controller.normalize_lesson_question_order(lesson.id)
        elif entity_type == "program":
            for discipline in self.controller.get_program_disciplines(entity.id):
                for topic in self.controller.get_discipline_topics(discipline.id):
                    self.controller.normalize_topic_lesson_order(topic.id)
                    for lesson in self.controller.get_topic_lessons(topic.id):
                        self.controller.normalize_lesson_question_order(lesson.id)
        self._refresh_structure_tree()

    def _structure_selected_key(self):
        selection = self._current_structure_entity()
        if not selection:
            return None
        entity_type, entity = selection
        if not getattr(entity, "id", None):
            return None
        return (entity_type, entity.id)

    def _structure_expanded_keys(self) -> set:
        expanded = set()
        root_count = self.structure_tree.topLevelItemCount()
        for i in range(root_count):
            self._collect_expanded(self.structure_tree.topLevelItem(i), expanded)
        return expanded

    def _collect_expanded(self, item: QTreeWidgetItem, expanded: set) -> None:
        entity_type = item.data(0, Qt.UserRole + 1)
        entity = item.data(0, Qt.UserRole)
        if entity_type and entity and getattr(entity, "id", None) and item.isExpanded():
            expanded.add((entity_type, entity.id))
        for idx in range(item.childCount()):
            self._collect_expanded(item.child(idx), expanded)

    def _on_structure_selection_changed(self) -> None:
        entity = self._current_structure_entity()
        if not entity:
            self.structure_title.setText(self.tr("Select an item"))
            self.structure_details.setText("")
            self._set_structure_buttons(enabled_program=True)
            return
        entity_type, obj = entity
        title = self._structure_title(entity_type, obj)
        details = self._structure_details(entity_type, obj)
        self.structure_title.setText(title)
        self.structure_details.setText(details)
        self._set_structure_buttons_for_type(entity_type)
        self._refresh_materials()
        self._resize_structure_tree()

    def _resize_structure_tree(self) -> None:
        self.structure_tree.doItemsLayout()

    def _set_structure_buttons(self, enabled_program: bool) -> None:
        self.structure_add_program.setEnabled(enabled_program)
        self.structure_add_discipline.setEnabled(False)
        self.structure_add_topic.setEnabled(False)
        self.structure_add_lesson.setEnabled(False)
        self.structure_add_question.setEnabled(False)
        self.structure_edit.setEnabled(False)
        self.structure_delete.setEnabled(False)
        self.structure_duplicate.setEnabled(False)
        self.structure_copy.setEnabled(False)

    def _set_structure_buttons_for_type(self, entity_type: str) -> None:
        self.structure_add_program.setEnabled(True)
        self.structure_add_discipline.setEnabled(entity_type in ("program", "discipline", "topic", "lesson", "question"))
        self.structure_add_topic.setEnabled(entity_type in ("discipline", "topic", "lesson", "question"))
        self.structure_add_lesson.setEnabled(entity_type in ("topic", "lesson", "question"))
        self.structure_add_question.setEnabled(entity_type in ("lesson", "question"))
        self.structure_edit.setEnabled(True)
        self.structure_delete.setEnabled(True)
        self.structure_duplicate.setEnabled(True)
        self.structure_copy.setEnabled(True)

    def _current_structure_entity(self):
        item = self.structure_tree.currentItem()
        if not item:
            return None
        entity = item.data(0, Qt.UserRole)
        entity_type = item.data(0, Qt.UserRole + 1)
        if not entity or not entity_type:
            return None
        return entity_type, entity

    def _current_structure_lesson(self):
        selection = self._current_structure_entity()
        if not selection:
            return None
        entity_type, entity = selection
        return entity if entity_type == "lesson" else None

    def _current_structure_material_target(self):
        selection = self._current_structure_entity()
        if not selection:
            return None
        entity_type, entity = selection
        if entity_type in {"program", "discipline", "lesson"}:
            return entity_type, entity
        return None

    def _select_structure_entity(self, entity_type: str, entity_id: int) -> None:
        root_count = self.structure_tree.topLevelItemCount()
        for i in range(root_count):
            item = self._find_structure_item(self.structure_tree.topLevelItem(i), entity_type, entity_id)
            if item:
                self.structure_tree.setCurrentItem(item)
                return

    def _find_structure_item(self, item: QTreeWidgetItem, entity_type: str, entity_id: int):
        if item.data(0, Qt.UserRole + 1) == entity_type:
            entity = item.data(0, Qt.UserRole)
            if entity and getattr(entity, "id", None) == entity_id:
                return item
        for idx in range(item.childCount()):
            found = self._find_structure_item(item.child(idx), entity_type, entity_id)
            if found:
                return found
        return None

    def _filtered_teachers_for_target(self, entity_type: str, entity):
        if entity_type == "lesson":
            disciplines = self.controller.discipline_repo.get_disciplines_for_lesson(entity.id)
        elif entity_type == "discipline":
            disciplines = [entity]
        elif entity_type == "program":
            disciplines = self.controller.get_program_disciplines(entity.id)
        else:
            disciplines = []
        discipline_ids = [d.id for d in disciplines if d and d.id is not None]
        if not discipline_ids:
            return self.controller.get_teachers()
        teachers = self.controller.get_teachers_for_disciplines(discipline_ids)
        return teachers if teachers else self.controller.get_teachers()

    def _set_material_buttons_enabled(self, enabled: bool) -> None:
        for button in [
            self.material_add,
            self.material_edit,
            self.material_delete,
            self.material_open,
            self.material_show,
            self.material_copy,
        ]:
            button.setEnabled(enabled)

    def _structure_title(self, entity_type: str, entity) -> str:
        if entity_type == "program":
            return f"{self.tr('Program')}: {entity.name}"
        if entity_type == "discipline":
            return f"{self.tr('Discipline')}: {entity.name}"
        if entity_type == "topic":
            return f"{self.tr('Topic')}: {entity.title}"
        if entity_type == "lesson":
            return f"{self.tr('Lesson')}: {entity.title}"
        if entity_type == "question":
            return f"{self.tr('Question')}"
        return self.tr("Select an item")

    def _structure_details(self, entity_type: str, entity) -> str:
        if entity_type == "program":
            return (
                f"{self.tr('Level')}: {entity.level or ''}\n"
                f"{self.tr('Year')}: {entity.year or ''}\n"
                f"{self.tr('Duration')}: {entity.duration_hours or ''}"
            )
        if entity_type == "discipline":
            return entity.description or ""
        if entity_type == "topic":
            return entity.description or ""
        if entity_type == "lesson":
            parts = []
            if entity.lesson_type_name:
                parts.append(f"{self.tr('Type')}: {entity.lesson_type_name}")
            if entity.duration_hours is not None:
                parts.append(f"{self.tr('Total hours')}: {entity.duration_hours}")
            if entity.classroom_hours is not None:
                parts.append(f"{self.tr('Classroom hours')}: {entity.classroom_hours}")
            if entity.self_study_hours is not None:
                parts.append(f"{self.tr('Self-study hours')}: {entity.self_study_hours}")
            return "\n".join(parts)
        if entity_type == "question":
            return entity.content or ""
        return ""

    def _find_parent_entity(self, item: QTreeWidgetItem, entity_type: str):
        current = item
        while current:
            if current.data(0, Qt.UserRole + 1) == entity_type:
                return current.data(0, Qt.UserRole)
            current = current.parent()
        return None

    def _add_structure_program(self) -> None:
        dialog = ProgramDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        program = dialog.get_program()
        if not program.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Program name is required."))
            return
        self.controller.add_program(program)
        self._log_action("add_program", program.name or "")
        self._refresh_structure_tree()

    def _add_structure_discipline(self) -> None:
        item = self.structure_tree.currentItem()
        program = None
        if item:
            program = self._find_parent_entity(item, "program")
        if not program:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a program first."))
            return
        dialog = DisciplineDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        discipline = dialog.get_discipline()
        if not discipline.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Discipline name is required."))
            return
        self.controller.add_discipline(discipline)
        self.controller.add_discipline_to_program(program.id, discipline.id, discipline.order_index)
        self._log_action("add_discipline", discipline.name or "")
        self._refresh_structure_tree()

    def _add_structure_topic(self) -> None:
        item = self.structure_tree.currentItem()
        discipline = None
        if item:
            discipline = self._find_parent_entity(item, "discipline")
        if not discipline:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a discipline first."))
            return
        dialog = TopicDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        topic = dialog.get_topic()
        if not topic.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Topic title is required."))
            return
        self.controller.add_topic(topic)
        self.controller.add_topic_to_discipline(discipline.id, topic.id, topic.order_index)
        self._log_action("add_topic", topic.title or "")
        self._refresh_structure_tree()

    def _add_structure_lesson(self) -> None:
        item = self.structure_tree.currentItem()
        topic = None
        if item:
            topic = self._find_parent_entity(item, "topic")
        if not topic:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a topic first."))
            return
        dialog = LessonDialog(
            lesson_types=self.controller.get_lesson_types(),
            parent=self,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        lesson = dialog.get_lesson()
        if not lesson.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Lesson title is required."))
            return
        self.controller.add_lesson(lesson)
        self.controller.add_lesson_to_topic(topic.id, lesson.id, lesson.order_index)
        self._log_action("add_lesson", lesson.title or "")
        self._attach_new_questions_to_lesson(lesson.id, dialog.get_new_questions())
        self._refresh_structure_tree()

    def _add_structure_question(self) -> None:
        item = self.structure_tree.currentItem()
        lesson = None
        if item:
            lesson = self._find_parent_entity(item, "lesson")
        if not lesson:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a lesson first."))
            return
        dialog = QuestionDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        question = dialog.get_question()
        if not question.content:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Question text is required."))
            return
        if question.order_index <= 0:
            question.order_index = self.controller.get_next_lesson_question_order(lesson.id)
        self.controller.add_question(question)
        self.controller.add_question_to_lesson(lesson.id, question.id, question.order_index)
        self._log_action("add_question", (question.content or "")[:120])
        self._refresh_structure_tree()

    def _edit_structure_selected(self) -> None:
        selection = self._current_structure_entity()
        if not selection:
            return
        entity_type, entity = selection
        item = self.structure_tree.currentItem()
        if entity_type == "program":
            dialog = ProgramDialog(entity, self)
            if dialog.exec() != QDialog.Accepted:
                return
            self.controller.update_program(dialog.get_program())
            self._refresh_structure_tree()
            self._select_structure_entity(entity_type, entity.id)
            return
        if entity_type == "discipline":
            program = self._find_parent_entity(item, "program")
            if program:
                entity = self.controller.ensure_discipline_for_edit(entity.id, program.id)
            programs = [program] if program else self.controller.get_programs()
            disciplines = (
                self.controller.get_program_disciplines(program.id)
                if program
                else self.controller.get_disciplines()
            )
            dialog = DisciplineDialog(
                entity,
                self,
                enable_type_switch=True,
                programs=programs,
                disciplines=disciplines,
                initial_parent_type="program" if program else None,
                initial_parent_id=program.id if program else None,
            )
            if dialog.exec() != QDialog.Accepted:
                return
            updated = dialog.get_discipline()
            new_type, parent_type, parent_id = dialog.get_type_payload()
            if new_type == "discipline":
                self.controller.update_discipline(updated)
                if program and parent_type == "program" and parent_id and parent_id != program.id:
                    self.controller.move_discipline_to_program(updated.id, program.id, parent_id)
                self._refresh_structure_tree()
                self._select_structure_entity("discipline", updated.id)
            else:
                if not parent_id:
                    QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a discipline first."))
                    return
                if program:
                    program_disciplines = {d.id for d in self.controller.get_program_disciplines(program.id)}
                    if parent_id not in program_disciplines:
                        QMessageBox.warning(
                            self, self.tr("Validation"), self.tr("Select a discipline from the same program.")
                        )
                        return
                try:
                    new_topic = self.controller.convert_discipline_to_topic(updated, program.id if program else 0, parent_id)
                except (ValueError, RuntimeError, sqlite3.Error) as exc:
                    QMessageBox.warning(self, self.tr("Validation"), str(exc))
                    return
                self._refresh_structure_tree()
                self._select_structure_entity("topic", new_topic.id)
            return
        if entity_type == "topic":
            discipline = self._find_parent_entity(item, "discipline")
            if discipline:
                entity = self.controller.ensure_topic_for_edit(entity.id, discipline.id)
            program_id, _ = self.controller.get_primary_parent_ids("topic", entity.id)
            programs = (
                [p for p in self.controller.get_programs() if p.id == program_id]
                if program_id
                else self.controller.get_programs()
            )
            disciplines = (
                self.controller.get_program_disciplines(program_id)
                if program_id
                else self.controller.get_disciplines()
            )
            dialog = TopicDialog(
                entity,
                self,
                enable_type_switch=True,
                programs=programs,
                disciplines=disciplines,
                initial_parent_type="discipline" if discipline else None,
                initial_parent_id=discipline.id if discipline else None,
            )
            if dialog.exec() != QDialog.Accepted:
                return
            updated = dialog.get_topic()
            new_type, parent_type, parent_id = dialog.get_type_payload()
            if new_type == "topic":
                self.controller.update_topic(updated)
                if discipline and parent_type == "discipline" and parent_id and parent_id != discipline.id:
                    self.controller.move_topic_to_discipline(updated.id, discipline.id, parent_id)
                self._refresh_structure_tree()
                self._select_structure_entity("topic", updated.id)
            else:
                if not parent_id:
                    QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a program first."))
                    return
                try:
                    new_discipline = self.controller.convert_topic_to_discipline(
                        updated, discipline.id if discipline else 0, parent_id
                    )
                except (ValueError, RuntimeError, sqlite3.Error) as exc:
                    QMessageBox.warning(self, self.tr("Validation"), str(exc))
                    return
                self._refresh_structure_tree()
                self._select_structure_entity("discipline", new_discipline.id)
            return
        if entity_type == "lesson":
            topic = self._find_parent_entity(item, "topic")
            if topic:
                entity = self.controller.ensure_lesson_for_edit(entity.id, topic.id)
            dialog = LessonDialog(entity, self.controller.get_lesson_types(), self)
            if dialog.exec() != QDialog.Accepted:
                return
            updated = dialog.get_lesson()
            self.controller.update_lesson(updated)
            if topic and updated.order_index > 0:
                self.controller.update_topic_lesson_order(topic.id, updated.id, updated.order_index)
            self._refresh_structure_tree()
            self._select_structure_entity(entity_type, entity.id)
            return
        if entity_type == "question":
            lesson = self._find_parent_entity(item, "lesson")
            if lesson:
                entity = self.controller.ensure_question_for_edit(entity.id, lesson.id)
            dialog = QuestionDialog(entity, self)
            if dialog.exec() != QDialog.Accepted:
                return
            updated = dialog.get_question()
            self.controller.update_question(updated)
            if lesson and updated.order_index > 0:
                self.controller.update_lesson_question_order(lesson.id, updated.id, updated.order_index)
            self._refresh_structure_tree()
            self._select_structure_entity(entity_type, entity.id)

    def _delete_structure_selected(self) -> None:
        selection = self._current_structure_entity()
        if not selection:
            return
        entity_type, entity = selection
        confirm = self.tr("Delete selected item?")
        if QMessageBox.question(self, self.tr("Confirm"), confirm) != QMessageBox.Yes:
            return
        if entity_type == "program":
            self.controller.delete_program(entity.id)
            self._log_action("delete_program", entity.name or "")
        elif entity_type == "discipline":
            self.controller.delete_discipline(entity.id)
            self._log_action("delete_discipline", entity.name or "")
        elif entity_type == "topic":
            self.controller.delete_topic(entity.id)
            self._log_action("delete_topic", entity.title or "")
        elif entity_type == "lesson":
            self.controller.delete_lesson(entity.id)
            self._log_action("delete_lesson", entity.title or "")
        elif entity_type == "question":
            self.controller.delete_question(entity.id)
            self._log_action("delete_question", (entity.content or "")[:120])
        self._refresh_structure_tree()

    def _duplicate_structure_selected(self) -> None:
        selection = self._current_structure_entity()
        item = self.structure_tree.currentItem()
        if not selection or not item:
            return
        entity_type, entity = selection
        new_entity = None
        if entity_type == "program":
            new_entity = self.controller.duplicate_program(entity.id)
        elif entity_type == "discipline":
            program = self._find_parent_entity(item, "program")
            if program:
                new_entity = self.controller.duplicate_discipline(entity.id, program.id)
        elif entity_type == "topic":
            discipline = self._find_parent_entity(item, "discipline")
            if discipline:
                new_entity = self.controller.duplicate_topic(entity.id, discipline.id)
        elif entity_type == "lesson":
            topic = self._find_parent_entity(item, "topic")
            if topic:
                new_entity = self.controller.duplicate_lesson(entity.id, topic.id)
        elif entity_type == "question":
            lesson = self._find_parent_entity(item, "lesson")
            if lesson:
                new_entity = self.controller.duplicate_question(entity.id, lesson.id)
        if new_entity:
            self._refresh_structure_tree()
            self._select_structure_entity(entity_type, new_entity.id)

    def _copy_structure_selected(self) -> None:
        selection = self._current_structure_entity()
        item = self.structure_tree.currentItem()
        if not selection or not item:
            return
        entity_type, entity = selection
        new_entity = None
        if entity_type == "program":
            new_entity = self.controller.copy_program(entity.id)
        elif entity_type == "discipline":
            program = self._find_parent_entity(item, "program")
            if program:
                new_entity = self.controller.copy_discipline(entity.id, program.id)
        elif entity_type == "topic":
            discipline = self._find_parent_entity(item, "discipline")
            if discipline:
                new_entity = self.controller.copy_topic(entity.id, discipline.id)
        elif entity_type == "lesson":
            topic = self._find_parent_entity(item, "topic")
            if topic:
                new_entity = self.controller.copy_lesson(entity.id, topic.id)
        elif entity_type == "question":
            lesson = self._find_parent_entity(item, "lesson")
            if lesson:
                new_entity = self.controller.copy_question(entity.id, lesson.id)
        if new_entity:
            self._refresh_structure_tree()
            self._select_structure_entity(entity_type, new_entity.id)
