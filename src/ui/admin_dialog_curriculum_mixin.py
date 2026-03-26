"""Curriculum CRUD helpers extracted from AdminDialog."""

from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidgetItem, QMessageBox, QTableWidgetItem

from .dialogs import DisciplineDialog, LessonDialog, LessonTypeDialog, ProgramDialog, QuestionDialog, TopicDialog


class AdminDialogCurriculumMixin:
    """Program/discipline/topic/lesson/question CRUD behavior for AdminDialog."""

    # Programs
    def _refresh_programs(self) -> None:
        self.programs_table.setRowCount(0)
        for program in self.controller.get_programs():
            row = self.programs_table.rowCount()
            self.programs_table.insertRow(row)
            self.programs_table.setItem(row, 0, QTableWidgetItem(program.name))
            self.programs_table.setItem(row, 1, QTableWidgetItem(program.level or ""))
            self.programs_table.setItem(row, 2, QTableWidgetItem(str(program.duration_hours or "")))
            self.programs_table.item(row, 0).setData(Qt.UserRole, program)
        self._refresh_program_disciplines()

    def _on_program_selection_changed(self) -> None:
        self._refresh_program_disciplines()
        self._refresh_disciplines()
        self._refresh_topics()
        self._refresh_lessons()
        self._refresh_questions()

    def _add_program(self) -> None:
        dialog = ProgramDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        program = dialog.get_program()
        if not program.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Program name is required."))
            return
        self.controller.add_program(program)
        self._refresh_programs()

    def _edit_program(self) -> None:
        program = self._current_entity(self.programs_table)
        if not program:
            return
        dialog = ProgramDialog(program, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_program(dialog.get_program())
        self._refresh_programs()

    def _delete_program(self) -> None:
        programs = self._selected_entities(self.programs_table)
        if not programs:
            return
        confirm_text = (
            self.tr("Delete selected program?")
            if len(programs) == 1
            else self.tr("Delete selected program?") + f" ({len(programs)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for program in programs:
            self.controller.delete_program(program.id)
        self._refresh_programs()

    def _refresh_program_disciplines(self) -> None:
        self.program_disciplines_assigned.clear()
        self.program_disciplines_available.clear()
        program = self._current_entity(self.programs_table)
        disciplines = self.controller.get_disciplines()
        assigned = []
        if program:
            assigned = self.controller.get_program_disciplines(program.id)
        assigned_ids = {d.id for d in assigned}
        for discipline in disciplines:
            item = QListWidgetItem(discipline.name)
            item.setData(Qt.UserRole, discipline)
            if discipline.id in assigned_ids:
                self.program_disciplines_assigned.addItem(item)
            else:
                self.program_disciplines_available.addItem(item)

    def _add_discipline_to_program(self) -> None:
        program = self._current_entity(self.programs_table)
        item = self.program_disciplines_available.currentItem()
        if not program or not item:
            return
        discipline = item.data(Qt.UserRole)
        self.controller.add_discipline_to_program(program.id, discipline.id, discipline.order_index)
        self._refresh_program_disciplines()

    def _remove_discipline_from_program(self) -> None:
        program = self._current_entity(self.programs_table)
        item = self.program_disciplines_assigned.currentItem()
        if not program or not item:
            return
        discipline = item.data(Qt.UserRole)
        self.controller.remove_discipline_from_program(program.id, discipline.id)
        self._refresh_program_disciplines()

    # Disciplines
    def _refresh_disciplines(self) -> None:
        self.disciplines_table.setRowCount(0)
        for discipline in self.controller.get_disciplines():
            row = self.disciplines_table.rowCount()
            self.disciplines_table.insertRow(row)
            self.disciplines_table.setItem(row, 0, QTableWidgetItem(discipline.name))
            self.disciplines_table.setItem(row, 1, QTableWidgetItem(str(discipline.order_index)))
            self.disciplines_table.item(row, 0).setData(Qt.UserRole, discipline)
        self._refresh_discipline_topics()

    def _on_discipline_selection_changed(self) -> None:
        self._refresh_discipline_topics()
        self._refresh_topics()
        self._refresh_lessons()
        self._refresh_questions()

    def _add_discipline(self) -> None:
        dialog = DisciplineDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        discipline = dialog.get_discipline()
        if not discipline.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Discipline name is required."))
            return
        self.controller.add_discipline(discipline)
        self._refresh_disciplines()

    def _edit_discipline(self) -> None:
        discipline = self._current_entity(self.disciplines_table)
        if not discipline:
            return
        program_id, _ = self.controller.get_primary_parent_ids("discipline", discipline.id)
        if program_id:
            discipline = self.controller.ensure_discipline_for_edit(discipline.id, program_id)
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
        dialog = DisciplineDialog(
            discipline,
            self,
            enable_type_switch=True,
            programs=programs,
            disciplines=disciplines,
            initial_parent_type="program" if program_id else None,
            initial_parent_id=program_id,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        updated = dialog.get_discipline()
        new_type, parent_type, parent_id = dialog.get_type_payload()
        if new_type == "discipline":
            self.controller.update_discipline(updated)
            if program_id and parent_type == "program" and parent_id and parent_id != program_id:
                self.controller.move_discipline_to_program(updated.id, program_id, parent_id)
            self._refresh_disciplines()
        else:
            if not parent_id:
                QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a discipline first."))
                return
            if not program_id:
                QMessageBox.warning(
                    self, self.tr("Validation"), self.tr("Discipline is not linked to any program.")
                )
                return
            program_disciplines = {d.id for d in self.controller.get_program_disciplines(program_id)}
            if parent_id not in program_disciplines:
                QMessageBox.warning(
                    self, self.tr("Validation"), self.tr("Select a discipline from the same program.")
                )
                return
            try:
                self.controller.convert_discipline_to_topic(updated, program_id or 0, parent_id)
            except (ValueError, RuntimeError, sqlite3.Error) as exc:
                QMessageBox.warning(self, self.tr("Validation"), str(exc))
                return
            self._refresh_disciplines()
            self._refresh_topics()

    def _delete_discipline(self) -> None:
        disciplines = self._selected_entities(self.disciplines_table)
        if not disciplines:
            return
        confirm_text = (
            self.tr("Delete selected discipline?")
            if len(disciplines) == 1
            else self.tr("Delete selected discipline?") + f" ({len(disciplines)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for discipline in disciplines:
            self.controller.delete_discipline(discipline.id)
        self._refresh_disciplines()

    def _refresh_discipline_topics(self) -> None:
        self.discipline_topics_assigned.clear()
        self.discipline_topics_available.clear()
        discipline = self._current_entity(self.disciplines_table)
        topics = self.controller.get_topics()
        assigned = []
        if discipline:
            assigned = self.controller.get_discipline_topics(discipline.id)
        assigned_ids = {t.id for t in assigned}
        for topic in topics:
            item = QListWidgetItem(topic.title)
            item.setData(Qt.UserRole, topic)
            if topic.id in assigned_ids:
                self.discipline_topics_assigned.addItem(item)
            else:
                self.discipline_topics_available.addItem(item)

    def _add_topic_to_discipline(self) -> None:
        discipline = self._current_entity(self.disciplines_table)
        item = self.discipline_topics_available.currentItem()
        if not discipline or not item:
            return
        topic = item.data(Qt.UserRole)
        self.controller.add_topic_to_discipline(discipline.id, topic.id, topic.order_index)
        self._refresh_discipline_topics()

    def _remove_topic_from_discipline(self) -> None:
        discipline = self._current_entity(self.disciplines_table)
        item = self.discipline_topics_assigned.currentItem()
        if not discipline or not item:
            return
        topic = item.data(Qt.UserRole)
        self.controller.remove_topic_from_discipline(discipline.id, topic.id)
        self._refresh_discipline_topics()

    # Topics
    def _refresh_topics(self) -> None:
        self.topics_table.setRowCount(0)
        for topic in self._filtered_topics():
            row = self.topics_table.rowCount()
            self.topics_table.insertRow(row)
            self.topics_table.setItem(row, 0, QTableWidgetItem(topic.title))
            self.topics_table.setItem(row, 1, QTableWidgetItem(str(topic.order_index)))
            self.topics_table.item(row, 0).setData(Qt.UserRole, topic)
        self._refresh_topic_lessons()
        self._refresh_topic_materials()

    def _on_topic_selection_changed(self) -> None:
        self._refresh_topic_lessons()
        self._refresh_topic_materials()
        self._refresh_lessons()
        self._refresh_questions()

    def _add_topic(self) -> None:
        dialog = TopicDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        topic = dialog.get_topic()
        if not topic.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Topic title is required."))
            return
        self.controller.add_topic(topic)
        self._refresh_topics()

    def _edit_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        if not topic:
            return
        _, discipline_id = self.controller.get_primary_parent_ids("topic", topic.id)
        if discipline_id:
            topic = self.controller.ensure_topic_for_edit(topic.id, discipline_id)
        program_id, _ = self.controller.get_primary_parent_ids("topic", topic.id)
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
            topic,
            self,
            enable_type_switch=True,
            programs=programs,
            disciplines=disciplines,
            initial_parent_type="discipline" if discipline_id else None,
            initial_parent_id=discipline_id,
        )
        if dialog.exec() != QDialog.Accepted:
            return
        updated = dialog.get_topic()
        new_type, parent_type, parent_id = dialog.get_type_payload()
        if new_type == "topic":
            self.controller.update_topic(updated)
            if discipline_id and parent_type == "discipline" and parent_id and parent_id != discipline_id:
                self.controller.move_topic_to_discipline(updated.id, discipline_id, parent_id)
            self._refresh_topics()
        else:
            if not parent_id:
                QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a program first."))
                return
            if not discipline_id:
                QMessageBox.warning(
                    self, self.tr("Validation"), self.tr("Topic is not linked to any discipline.")
                )
                return
            try:
                self.controller.convert_topic_to_discipline(updated, discipline_id or 0, parent_id)
            except (ValueError, RuntimeError, sqlite3.Error) as exc:
                QMessageBox.warning(self, self.tr("Validation"), str(exc))
                return
            self._refresh_topics()
            self._refresh_disciplines()

    def _delete_topic(self) -> None:
        topics = self._selected_entities(self.topics_table)
        if not topics:
            return
        confirm_text = (
            self.tr("Delete selected topic?")
            if len(topics) == 1
            else self.tr("Delete selected topic?") + f" ({len(topics)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for topic in topics:
            self.controller.delete_topic(topic.id)
        self._refresh_topics()

    def _refresh_topic_lessons(self) -> None:
        self.topic_lessons_assigned.clear()
        self.topic_lessons_available.clear()
        topic = self._current_entity(self.topics_table)
        lessons = self.controller.get_lessons()
        assigned = []
        if topic:
            assigned = self.controller.get_topic_lessons(topic.id)
        assigned_ids = {l.id for l in assigned}
        for lesson in lessons:
            item = QListWidgetItem(lesson.title)
            item.setData(Qt.UserRole, lesson)
            if lesson.id in assigned_ids:
                self.topic_lessons_assigned.addItem(item)
            else:
                self.topic_lessons_available.addItem(item)
        self._refresh_topic_materials()

    def _add_lesson_to_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        item = self.topic_lessons_available.currentItem()
        if not topic or not item:
            return
        lesson = item.data(Qt.UserRole)
        self.controller.add_lesson_to_topic(topic.id, lesson.id, lesson.order_index)
        self._refresh_topic_lessons()

    def _remove_lesson_from_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        item = self.topic_lessons_assigned.currentItem()
        if not topic or not item:
            return
        lesson = item.data(Qt.UserRole)
        self.controller.remove_lesson_from_topic(topic.id, lesson.id)
        self._refresh_topic_lessons()

    def _refresh_topic_materials(self) -> None:
        self.topic_materials_assigned.clear()
        self.topic_materials_available.clear()
        topic = self._current_entity(self.topics_table)
        if not topic:
            return
        materials = self.controller.get_materials()
        assigned = self.controller.get_materials_for_entity("topic", topic.id)
        assigned_ids = {m.id for m in assigned}
        for material in materials:
            label = material.title
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, material)
            if material.id in assigned_ids:
                self.topic_materials_assigned.addItem(item)
            else:
                self.topic_materials_available.addItem(item)

    def _add_material_to_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        item = self.topic_materials_available.currentItem()
        if not topic or not item:
            return
        material = item.data(Qt.UserRole)
        self.controller.add_material_to_entity(material.id, "topic", topic.id)
        self._refresh_topic_materials()

    def _remove_material_from_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        item = self.topic_materials_assigned.currentItem()
        if not topic or not item:
            return
        material = item.data(Qt.UserRole)
        self.controller.remove_material_from_entity(material.id, "topic", topic.id)
        self._refresh_topic_materials()

    # Lessons
    def _refresh_lessons(self) -> None:
        self.lessons_table.setRowCount(0)
        for lesson in self._filtered_lessons():
            row = self.lessons_table.rowCount()
            self.lessons_table.insertRow(row)
            self.lessons_table.setItem(row, 0, QTableWidgetItem(lesson.title))
            self.lessons_table.setItem(row, 1, QTableWidgetItem(str(lesson.duration_hours)))
            self.lessons_table.setItem(row, 2, QTableWidgetItem(lesson.lesson_type_name or ""))
            self.lessons_table.setItem(row, 3, QTableWidgetItem(str(lesson.order_index)))
            self.lessons_table.item(row, 0).setData(Qt.UserRole, lesson)
        self._refresh_lesson_questions()
        self._refresh_lesson_materials()

    def _on_lesson_selection_changed(self) -> None:
        self._refresh_lesson_questions()
        self._refresh_lesson_materials()
        self._refresh_questions()

    def _add_lesson(self) -> None:
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
        self._attach_new_questions_to_lesson(lesson.id, dialog.get_new_questions())
        self._refresh_lessons()

    def _edit_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        if not lesson:
            return
        dialog = LessonDialog(lesson, self.controller.get_lesson_types(), self)
        if dialog.exec() != QDialog.Accepted:
            return
        updated = dialog.get_lesson()
        self.controller.update_lesson(updated)
        topic = self._current_entity(self.topics_table) if hasattr(self, "topics_table") else None
        if topic and updated.order_index > 0:
            self.controller.update_topic_lesson_order(topic.id, updated.id, updated.order_index)
        self._refresh_lessons()

    def _delete_lesson(self) -> None:
        lessons = self._selected_entities(self.lessons_table)
        if not lessons:
            return
        confirm_text = (
            self.tr("Delete selected lesson?")
            if len(lessons) == 1
            else self.tr("Delete selected lesson?") + f" ({len(lessons)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for lesson in lessons:
            self.controller.delete_lesson(lesson.id)
        self._refresh_lessons()

    def _refresh_lesson_questions(self) -> None:
        self.lesson_questions_assigned.clear()
        self.lesson_questions_available.clear()
        lesson = self._current_entity(self.lessons_table)
        questions = self.controller.get_questions()
        assigned = []
        if lesson:
            assigned = self.controller.get_lesson_questions(lesson.id)
        assigned_ids = {q.id for q in assigned}
        for question in questions:
            title = question.content if len(question.content) <= 60 else f"{question.content[:60]}..."
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, question)
            if question.id in assigned_ids:
                self.lesson_questions_assigned.addItem(item)
            else:
                self.lesson_questions_available.addItem(item)
        self._refresh_lesson_materials()

    def _add_question_to_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        item = self.lesson_questions_available.currentItem()
        if not lesson or not item:
            return
        question = item.data(Qt.UserRole)
        order_index = question.order_index or self.controller.get_next_lesson_question_order(lesson.id)
        self.controller.add_question_to_lesson(lesson.id, question.id, order_index)
        self._refresh_lesson_questions()

    def _remove_question_from_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        item = self.lesson_questions_assigned.currentItem()
        if not lesson or not item:
            return
        question = item.data(Qt.UserRole)
        self.controller.remove_question_from_lesson(lesson.id, question.id)
        self._refresh_lesson_questions()

    def _refresh_lesson_materials(self) -> None:
        self.lesson_materials_assigned.clear()
        self.lesson_materials_available.clear()
        lesson = self._current_entity(self.lessons_table)
        if not lesson:
            return
        materials = self.controller.get_materials()
        assigned = self.controller.get_materials_for_entity("lesson", lesson.id)
        assigned_ids = {m.id for m in assigned}
        for material in materials:
            label = material.title
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, material)
            if material.id in assigned_ids:
                self.lesson_materials_assigned.addItem(item)
            else:
                self.lesson_materials_available.addItem(item)

    def _add_material_to_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        item = self.lesson_materials_available.currentItem()
        if not lesson or not item:
            return
        material = item.data(Qt.UserRole)
        self.controller.add_material_to_entity(material.id, "lesson", lesson.id)
        self._refresh_lesson_materials()

    def _remove_material_from_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        item = self.lesson_materials_assigned.currentItem()
        if not lesson or not item:
            return
        material = item.data(Qt.UserRole)
        self.controller.remove_material_from_entity(material.id, "lesson", lesson.id)
        self._refresh_lesson_materials()

    def _attach_new_questions_to_lesson(self, lesson_id: int, questions: list) -> None:
        if not questions:
            return
        order_index = self.controller.get_next_lesson_question_order(lesson_id)
        for question in questions:
            if not getattr(question, "content", None):
                continue
            if question.order_index <= 0:
                question.order_index = order_index
            self.controller.add_question(question)
            self.controller.add_question_to_lesson(lesson_id, question.id, question.order_index)
            order_index = max(order_index + 1, question.order_index + 1)

    # Lesson types
    def _refresh_lesson_types(self) -> None:
        self.lesson_types_table.setRowCount(0)
        for lesson_type in self.controller.get_lesson_types():
            row = self.lesson_types_table.rowCount()
            self.lesson_types_table.insertRow(row)
            self.lesson_types_table.setItem(row, 0, QTableWidgetItem(lesson_type.name))
            self.lesson_types_table.setItem(row, 1, QTableWidgetItem(lesson_type.synonyms or ""))
            self.lesson_types_table.item(row, 0).setData(Qt.UserRole, lesson_type)

    def _add_lesson_type(self) -> None:
        dialog = LessonTypeDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        lesson_type = dialog.get_lesson_type()
        if not lesson_type.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Name is required."))
            return
        self.controller.add_lesson_type(lesson_type)
        self._refresh_lesson_types()
        self._refresh_lessons()

    def _edit_lesson_type(self) -> None:
        lesson_type = self._current_entity(self.lesson_types_table)
        if not lesson_type:
            return
        dialog = LessonTypeDialog(lesson_type, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_lesson_type(dialog.get_lesson_type())
        self._refresh_lesson_types()
        self._refresh_lessons()

    def _delete_lesson_type(self) -> None:
        lesson_types = self._selected_entities(self.lesson_types_table)
        if not lesson_types:
            return
        confirm_text = (
            self.tr("Delete selected lesson type?")
            if len(lesson_types) == 1
            else self.tr("Delete selected lesson type?") + f" ({len(lesson_types)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for lesson_type in lesson_types:
            self.controller.delete_lesson_type(lesson_type.id)
        self._refresh_lesson_types()
        self._refresh_lessons()

    # Questions
    def _refresh_questions(self) -> None:
        self.questions_table.setRowCount(0)
        for question in self._filtered_questions():
            row = self.questions_table.rowCount()
            self.questions_table.insertRow(row)
            title = question.content if len(question.content) <= 80 else f"{question.content[:80]}..."
            self.questions_table.setItem(row, 0, QTableWidgetItem(title))
            self.questions_table.item(row, 0).setData(Qt.UserRole, question)

    def _filtered_disciplines(self):
        return self.controller.get_disciplines()

    def _filtered_topics(self):
        return self.controller.get_topics()

    def _filtered_lessons(self):
        return self.controller.get_lessons()

    def _filtered_questions(self):
        return self.controller.get_questions()

    def _lessons_for_topics(self, topics):
        lessons = []
        seen = set()
        for topic in topics:
            for lesson in self.controller.get_topic_lessons(topic.id):
                if lesson.id in seen:
                    continue
                seen.add(lesson.id)
                lessons.append(lesson)
        return lessons

    def _questions_for_lessons(self, lessons):
        questions = []
        seen = set()
        for lesson in lessons:
            for question in self.controller.get_lesson_questions(lesson.id):
                if question.id in seen:
                    continue
                seen.add(question.id)
                questions.append(question)
        return questions

    def _add_question(self) -> None:
        dialog = QuestionDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        question = dialog.get_question()
        if not question.content:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Question text is required."))
            return
        self.controller.add_question(question)
        self._refresh_questions()

    def _edit_question(self) -> None:
        question = self._current_entity(self.questions_table)
        if not question:
            return
        dialog = QuestionDialog(question, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_question(dialog.get_question())
        self._refresh_questions()

    def _delete_question(self) -> None:
        questions = self._selected_entities(self.questions_table)
        if not questions:
            return
        confirm_text = (
            self.tr("Delete selected question?")
            if len(questions) == 1
            else self.tr("Delete selected question?") + f" ({len(questions)})"
        )
        if QMessageBox.question(self, self.tr("Confirm"), confirm_text) != QMessageBox.Yes:
            return
        for question in questions:
            self.controller.delete_question(question.id)
        self._refresh_questions()
