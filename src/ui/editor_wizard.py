"""Editor mode wizard dialog."""
from PySide6.QtCore import Qt, QProcess
import sys
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QStackedWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
    QWidget,
    QMenuBar,
    QApplication,
)
from ..controllers.admin_controller import AdminController
from ..models.entities import Lesson, Question
from ..ui.dialogs import ProgramDialog, DisciplineDialog, TopicDialog, MaterialDialog


class EditorWizardDialog(QDialog):
    """Step-by-step wizard for editor mode."""

    def __init__(self, database, i18n=None, parent=None):
        super().__init__(parent)
        self.controller = AdminController(database)
        self.i18n = i18n
        self.lesson_context_label = QLabel("")
        self.lesson_context_label.setWordWrap(True)
        self._selected_program_id = None
        self._selected_discipline_id = None
        self._selected_topic_id = None
        self._created_counts = {
            "programs": 0,
            "disciplines": 0,
            "topics": 0,
            "lessons": 0,
            "questions": 0,
            "materials": 0,
        }
        self.setWindowTitle(self.tr("Editor Wizard"))
        self.resize(980, 640)
        self._build_ui()
        self.showMaximized()
        if self.i18n:
            self.i18n.language_changed.connect(self._retranslate_ui)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        menu_bar = QMenuBar()
        app_menu = menu_bar.addMenu(self.tr("Application"))
        action_restart = app_menu.addAction(self.tr("Restart application"))
        action_exit = app_menu.addAction(self.tr("Exit application"))
        action_restart.triggered.connect(self._restart_application)
        action_exit.triggered.connect(self._close_application)
        layout.addWidget(menu_bar)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.page_context = self._build_context_page()
        self.page_lessons = self._build_lessons_page()
        self.page_questions = self._build_questions_page()
        self.page_materials = self._build_materials_page()
        self.page_summary = self._build_summary_page()
        for page in [
            self.page_context,
            self.page_lessons,
            self.page_questions,
            self.page_materials,
            self.page_summary,
        ]:
            self.stack.addWidget(page)

        nav = QHBoxLayout()
        self.back_btn = QPushButton(self.tr("Back"))
        self.next_btn = QPushButton(self.tr("Next"))
        self.finish_btn = QPushButton(self.tr("Finish"))
        self.cancel_btn = QPushButton(self.tr("Cancel"))
        nav.addWidget(self.back_btn)
        nav.addWidget(self.next_btn)
        nav.addStretch(1)
        nav.addWidget(self.finish_btn)
        nav.addWidget(self.cancel_btn)
        layout.addLayout(nav)

        self.back_btn.clicked.connect(self._go_back)
        self.next_btn.clicked.connect(self._go_next)
        self.finish_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self._update_nav()

    def _build_context_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel(self.tr("Step 1: Select context"))
        layout.addWidget(header)

        form = QFormLayout()
        self.program_combo = QComboBox()
        self.discipline_combo = QComboBox()
        self.topic_combo = QComboBox()
        form.addRow(self.tr("Program"), self.program_combo)
        form.addRow(self.tr("Discipline"), self.discipline_combo)
        form.addRow(self.tr("Topic"), self.topic_combo)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.add_program_btn = QPushButton(self.tr("Add program"))
        self.add_discipline_btn = QPushButton(self.tr("Add discipline"))
        self.add_topic_btn = QPushButton(self.tr("Add topic"))
        btns.addWidget(self.add_program_btn)
        btns.addWidget(self.add_discipline_btn)
        btns.addWidget(self.add_topic_btn)
        btns.addStretch(1)
        layout.addLayout(btns)
        layout.addStretch(1)

        self.program_combo.currentIndexChanged.connect(self._refresh_disciplines)
        self.discipline_combo.currentIndexChanged.connect(self._refresh_topics)
        self.add_program_btn.clicked.connect(self._add_program)
        self.add_discipline_btn.clicked.connect(self._add_discipline)
        self.add_topic_btn.clicked.connect(self._add_topic)

        self._refresh_programs()
        return page

    def _build_lessons_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel(self.tr("Step 2: Add lessons"))
        layout.addWidget(header)

        layout.addWidget(self.lesson_context_label)

        form = QFormLayout()
        self.lesson_title = QLineEdit()
        self.lesson_description = QTextEdit()
        self.lesson_duration = QDoubleSpinBox()
        self.lesson_duration.setRange(0.0, 1000.0)
        self.lesson_duration.setSingleStep(0.5)
        self.lesson_classroom = QDoubleSpinBox()
        self.lesson_classroom.setRange(0.0, 1000.0)
        self.lesson_classroom.setSingleStep(0.5)
        self.lesson_self = QDoubleSpinBox()
        self.lesson_self.setRange(0.0, 1000.0)
        self.lesson_self.setSingleStep(0.5)
        self.lesson_type = QComboBox()
        self.lesson_order = QSpinBox()
        self.lesson_order.setRange(0, 999)
        form.addRow(self.tr("Title"), self.lesson_title)
        form.addRow(self.tr("Description"), self.lesson_description)
        form.addRow(self.tr("Total hours"), self.lesson_duration)
        form.addRow(self.tr("Classroom hours"), self.lesson_classroom)
        form.addRow(self.tr("Self-study hours"), self.lesson_self)
        form.addRow(self.tr("Lesson type"), self.lesson_type)
        form.addRow(self.tr("Order index"), self.lesson_order)
        layout.addLayout(form)

        add_row = QHBoxLayout()
        self.lesson_add_btn = QPushButton(self.tr("Add lesson"))
        add_row.addWidget(self.lesson_add_btn)
        add_row.addStretch(1)
        layout.addLayout(add_row)

        self.lessons_list = QListWidget()
        self.lessons_list.setWordWrap(True)
        self.lessons_list.setTextElideMode(Qt.ElideNone)
        self.lessons_list.setUniformItemSizes(False)
        layout.addWidget(self.lessons_list)

        self.lesson_add_btn.clicked.connect(self._add_lesson_from_form)
        self._refresh_lesson_types()
        return page

    def _build_questions_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel(self.tr("Step 3: Add questions"))
        layout.addWidget(header)

        form = QFormLayout()
        self.question_lesson_combo = QComboBox()
        self.question_content = QTextEdit()
        self.question_order = QSpinBox()
        self.question_order.setRange(0, 999)
        form.addRow(self.tr("Lesson"), self.question_lesson_combo)
        form.addRow(self.tr("Question"), self.question_content)
        form.addRow(self.tr("Order index"), self.question_order)
        layout.addLayout(form)

        add_row = QHBoxLayout()
        self.question_add_btn = QPushButton(self.tr("Add question"))
        add_row.addWidget(self.question_add_btn)
        add_row.addStretch(1)
        layout.addLayout(add_row)

        self.questions_list = QListWidget()
        self.questions_list.setWordWrap(True)
        self.questions_list.setTextElideMode(Qt.ElideNone)
        self.questions_list.setUniformItemSizes(False)
        layout.addWidget(self.questions_list)

        self.question_add_btn.clicked.connect(self._add_question_from_form)
        self.question_lesson_combo.currentIndexChanged.connect(self._refresh_questions_list)
        return page

    def _build_materials_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel(self.tr("Step 4: Add materials"))
        layout.addWidget(header)

        form = QFormLayout()
        self.material_target_combo = QComboBox()
        self.material_target_combo.addItem(self.tr("Topic"), "topic")
        self.material_target_combo.addItem(self.tr("Lesson"), "lesson")
        self.material_lesson_combo = QComboBox()
        form.addRow(self.tr("Target"), self.material_target_combo)
        form.addRow(self.tr("Lesson"), self.material_lesson_combo)
        layout.addLayout(form)

        add_row = QHBoxLayout()
        self.material_add_btn = QPushButton(self.tr("Add material"))
        add_row.addWidget(self.material_add_btn)
        add_row.addStretch(1)
        layout.addLayout(add_row)

        self.materials_list = QListWidget()
        self.materials_list.setWordWrap(True)
        self.materials_list.setTextElideMode(Qt.ElideNone)
        self.materials_list.setUniformItemSizes(False)
        layout.addWidget(self.materials_list)

        self.material_target_combo.currentIndexChanged.connect(self._toggle_material_target)
        self.material_add_btn.clicked.connect(self._add_material_from_dialog)
        self._toggle_material_target()
        return page

    def _restart_application(self) -> None:
        QProcess.startDetached(sys.executable, sys.argv)
        QApplication.quit()

    def _close_application(self) -> None:
        QApplication.quit()

    def _build_summary_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel(self.tr("Step 5: Summary"))
        layout.addWidget(header)
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        layout.addStretch(1)
        return page

    def _update_nav(self) -> None:
        idx = self.stack.currentIndex()
        self.back_btn.setEnabled(idx > 0)
        self.next_btn.setEnabled(idx < self.stack.count() - 1)
        self.finish_btn.setEnabled(idx == self.stack.count() - 1)

    def _go_back(self) -> None:
        if self.stack.currentIndex() <= 0:
            return
        self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
        self._update_nav()

    def _go_next(self) -> None:
        if self.stack.currentIndex() == 0:
            if self._current_topic_id() is None:
                QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a topic first."))
                return
            self._selected_program_id = self.program_combo.currentData()
            self._selected_discipline_id = self.discipline_combo.currentData()
            self._selected_topic_id = self.topic_combo.currentData()
        if self.stack.currentIndex() == 1:
            self._refresh_lessons_list()
            self._refresh_lesson_combo()
        if self.stack.currentIndex() == 2:
            self._refresh_materials_list()
            self._refresh_summary()
        if self.stack.currentIndex() >= self.stack.count() - 1:
            return
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
        self._update_nav()

    def _current_program_id(self):
        if self.stack.currentIndex() > 0 and self._selected_program_id is not None:
            return self._selected_program_id
        return self.program_combo.currentData()

    def _current_discipline_id(self):
        if self.stack.currentIndex() > 0 and self._selected_discipline_id is not None:
            return self._selected_discipline_id
        return self.discipline_combo.currentData()

    def _current_topic_id(self):
        if self.stack.currentIndex() > 0 and self._selected_topic_id is not None:
            return self._selected_topic_id
        return self.topic_combo.currentData()

    def _refresh_programs(self) -> None:
        self.program_combo.clear()
        for program in self.controller.get_programs():
            self.program_combo.addItem(program.name, program.id)
        self._refresh_disciplines()

    def _refresh_disciplines(self) -> None:
        self.discipline_combo.clear()
        program_id = self._current_program_id()
        if not program_id:
            self._refresh_topics()
            return
        for discipline in self.controller.get_program_disciplines(program_id):
            self.discipline_combo.addItem(discipline.name, discipline.id)
        self._refresh_topics()

    def _refresh_topics(self) -> None:
        self.topic_combo.clear()
        discipline_id = self._current_discipline_id()
        if not discipline_id:
            self._refresh_context_labels()
            return
        for topic in self.controller.get_discipline_topics(discipline_id):
            self.topic_combo.addItem(topic.title, topic.id)
        self._refresh_context_labels()

    def _refresh_context_labels(self) -> None:
        if not hasattr(self, "lesson_context_label") or self.lesson_context_label is None:
            return
        if self.stack.currentIndex() > 0 and self._selected_topic_id is not None:
            program = self._lookup_program_name(self._selected_program_id) or self.tr("N/A")
            discipline = self._lookup_discipline_name(self._selected_discipline_id) or self.tr("N/A")
            topic = self._lookup_topic_title(self._selected_topic_id) or self.tr("N/A")
        else:
            program = self.program_combo.currentText() or self.tr("N/A")
            discipline = self.discipline_combo.currentText() or self.tr("N/A")
            topic = self.topic_combo.currentText() or self.tr("N/A")
        self.lesson_context_label.setText(
            f"{self.tr('Program')}: {program} | {self.tr('Discipline')}: {discipline} | {self.tr('Topic')}: {topic}"
        )

    def _lookup_program_name(self, program_id: int | None) -> str | None:
        if not program_id:
            return None
        program = self.controller.program_repo.get_by_id(program_id)
        return program.name if program else None

    def _lookup_discipline_name(self, discipline_id: int | None) -> str | None:
        if not discipline_id:
            return None
        discipline = self.controller.discipline_repo.get_by_id(discipline_id)
        return discipline.name if discipline else None

    def _lookup_topic_title(self, topic_id: int | None) -> str | None:
        if not topic_id:
            return None
        topic = self.controller.topic_repo.get_by_id(topic_id)
        return topic.title if topic else None

    def _refresh_lesson_types(self) -> None:
        self.lesson_type.clear()
        for lesson_type in self.controller.get_lesson_types():
            self.lesson_type.addItem(lesson_type.name, lesson_type.id)

    def _refresh_lessons_list(self) -> None:
        self.lessons_list.clear()
        topic_id = self._current_topic_id()
        if not topic_id:
            return
        for lesson in self.controller.get_topic_lessons(topic_id):
            self.lessons_list.addItem(QListWidgetItem(lesson.title))

    def _refresh_lesson_combo(self) -> None:
        self.question_lesson_combo.clear()
        self.material_lesson_combo.clear()
        topic_id = self._current_topic_id()
        if not topic_id:
            return
        for lesson in self.controller.get_topic_lessons(topic_id):
            self.question_lesson_combo.addItem(lesson.title, lesson.id)
            self.material_lesson_combo.addItem(lesson.title, lesson.id)
        self._refresh_questions_list()

    def _refresh_questions_list(self) -> None:
        self.questions_list.clear()
        lesson_id = self.question_lesson_combo.currentData()
        if not lesson_id:
            return
        for question in self.controller.get_lesson_questions(lesson_id):
            label = question.content if len(question.content) <= 80 else f"{question.content[:80]}..."
            self.questions_list.addItem(QListWidgetItem(label))

    def _refresh_materials_list(self) -> None:
        self.materials_list.clear()
        target_type = self.material_target_combo.currentData()
        if target_type == "lesson":
            entity_id = self.material_lesson_combo.currentData()
        else:
            entity_id = self._current_topic_id()
        if not entity_id:
            return
        for material in self.controller.get_materials_for_entity(target_type, entity_id):
            self.materials_list.addItem(QListWidgetItem(material.title))

    def _toggle_material_target(self) -> None:
        is_lesson = self.material_target_combo.currentData() == "lesson"
        self.material_lesson_combo.setEnabled(is_lesson)

    def _add_program(self) -> None:
        dialog = ProgramDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        program = dialog.get_program()
        if not program.name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Program name is required."))
            return
        self.controller.add_program(program)
        self._created_counts["programs"] += 1
        self._refresh_programs()
        idx = self.program_combo.findData(program.id)
        if idx >= 0:
            self.program_combo.setCurrentIndex(idx)

    def _add_discipline(self) -> None:
        program_id = self._current_program_id()
        if not program_id:
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
        self.controller.add_discipline_to_program(program_id, discipline.id, discipline.order_index)
        self._created_counts["disciplines"] += 1
        self._refresh_disciplines()
        idx = self.discipline_combo.findData(discipline.id)
        if idx >= 0:
            self.discipline_combo.setCurrentIndex(idx)

    def _add_topic(self) -> None:
        discipline_id = self._current_discipline_id()
        if not discipline_id:
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
        self.controller.add_topic_to_discipline(discipline_id, topic.id, topic.order_index)
        self._created_counts["topics"] += 1
        self._refresh_topics()
        idx = self.topic_combo.findData(topic.id)
        if idx >= 0:
            self.topic_combo.setCurrentIndex(idx)

    def _add_lesson_from_form(self) -> None:
        topic_id = self._current_topic_id()
        if not topic_id:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a topic first."))
            return
        title = self.lesson_title.text().strip()
        if not title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Lesson title is required."))
            return
        lesson = Lesson(
            title=title,
            description=self.lesson_description.toPlainText().strip() or None,
            duration_hours=self.lesson_duration.value(),
            lesson_type_id=self.lesson_type.currentData(),
            classroom_hours=self.lesson_classroom.value(),
            self_study_hours=self.lesson_self.value(),
            order_index=self.lesson_order.value(),
        )
        lesson = self.controller.add_lesson(lesson)
        self.controller.add_lesson_to_topic(topic_id, lesson.id, lesson.order_index)
        self._created_counts["lessons"] += 1
        self.lesson_title.clear()
        self.lesson_description.clear()
        self.lesson_duration.setValue(0.0)
        self.lesson_classroom.setValue(0.0)
        self.lesson_self.setValue(0.0)
        self.lesson_order.setValue(0)
        self._refresh_lessons_list()
        self._refresh_lesson_combo()

    def _add_question_from_form(self) -> None:
        lesson_id = self.question_lesson_combo.currentData()
        if not lesson_id:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a lesson first."))
            return
        content = self.question_content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Question text is required."))
            return
        question = Question(
            content=content,
            answer=None,
            order_index=self.question_order.value(),
        )
        question = self.controller.add_question(question)
        order_index = question.order_index
        if order_index <= 0:
            order_index = self.controller.get_next_lesson_question_order(lesson_id)
        self.controller.add_question_to_lesson(lesson_id, question.id, order_index)
        self._created_counts["questions"] += 1
        self.question_content.clear()
        self.question_order.setValue(0)
        self._refresh_questions_list()

    def _add_material_from_dialog(self) -> None:
        target_type = self.material_target_combo.currentData()
        if target_type == "lesson":
            entity_id = self.material_lesson_combo.currentData()
        else:
            entity_id = self._current_topic_id()
        if not entity_id:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a target first."))
            return
        dialog = MaterialDialog(
            parent=self,
            material_types=self.controller.get_material_types(),
            teachers=self.controller.get_teachers(),
        )
        if dialog.exec() != QDialog.Accepted:
            return
        material = dialog.get_material()
        if not material.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Material title is required."))
            return
        material = self.controller.add_material(material)
        self.controller.add_material_to_entity(material.id, target_type, entity_id)
        for teacher_id in dialog.get_selected_teacher_ids():
            self.controller.add_teacher_to_material(teacher_id, material.id)
        attach_path = dialog.get_attachment_path()
        existing_path = dialog.get_existing_attachment_path()
        try:
            if attach_path:
                self.controller.attach_material_file(material, attach_path)
            elif existing_path:
                self.controller.attach_existing_material_file(material, existing_path)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
        self._created_counts["materials"] += 1
        self._refresh_materials_list()

    def _refresh_summary(self) -> None:
        lines = [
            f"{self.tr('Programs')}: {self._created_counts['programs']}",
            f"{self.tr('Disciplines')}: {self._created_counts['disciplines']}",
            f"{self.tr('Topics')}: {self._created_counts['topics']}",
            f"{self.tr('Lessons')}: {self._created_counts['lessons']}",
            f"{self.tr('Questions')}: {self._created_counts['questions']}",
            f"{self.tr('Materials')}: {self._created_counts['materials']}",
        ]
        self.summary_label.setText("\n".join(lines))

    def _retranslate_ui(self, *_args) -> None:
        self.setWindowTitle(self.tr("Editor Wizard"))
