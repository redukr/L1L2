"""Dialog windows for CRUD operations."""
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
)
from ..models.entities import Teacher, EducationalProgram, Discipline, Topic, Lesson, LessonType, Question, MethodicalMaterial
from ..services.import_service import extract_text_from_file, parse_curriculum_text, CurriculumTopic


class PasswordDialog(QDialog):
    """Password prompt dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Admin Access"))
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.tr("Enter admin password:")))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_password(self) -> str:
        return self.password_input.text().strip()


class TeacherDialog(QDialog):
    """Dialog for creating or editing a teacher."""

    def __init__(self, teacher: Optional[Teacher] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Teacher"))
        self._teacher = teacher
        layout = QFormLayout(self)
        self.full_name = QLineEdit(teacher.full_name if teacher else "")
        self.military_rank = QLineEdit(teacher.military_rank if teacher else "")
        self.position = QLineEdit(teacher.position if teacher else "")
        self.department = QLineEdit(teacher.department if teacher else "")
        self.email = QLineEdit(teacher.email if teacher else "")
        self.phone = QLineEdit(teacher.phone if teacher else "")
        layout.addRow(self.tr("Full name"), self.full_name)
        layout.addRow(self.tr("Military rank"), self.military_rank)
        layout.addRow(self.tr("Position"), self.position)
        layout.addRow(self.tr("Department"), self.department)
        layout.addRow(self.tr("Email"), self.email)
        layout.addRow(self.tr("Phone"), self.phone)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_teacher(self) -> Teacher:
        teacher = self._teacher or Teacher()
        teacher.full_name = self.full_name.text().strip()
        teacher.military_rank = self.military_rank.text().strip() or None
        teacher.position = self.position.text().strip() or None
        teacher.department = self.department.text().strip() or None
        teacher.email = self.email.text().strip() or None
        teacher.phone = self.phone.text().strip() or None
        return teacher


class ProgramDialog(QDialog):
    """Dialog for creating or editing a program."""

    def __init__(self, program: Optional[EducationalProgram] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Educational Program"))
        self._program = program
        layout = QFormLayout(self)
        self.name = QLineEdit(program.name if program else "")
        self.description = QTextEdit(program.description if program else "")
        self.level = QLineEdit(program.level if program else "")
        self.duration = QSpinBox()
        self.duration.setRange(1, 1000)
        if program and program.duration_hours:
            self.duration.setValue(program.duration_hours)
        layout.addRow(self.tr("Name"), self.name)
        layout.addRow(self.tr("Description"), self.description)
        layout.addRow(self.tr("Level"), self.level)
        layout.addRow(self.tr("Duration (hours)"), self.duration)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_program(self) -> EducationalProgram:
        program = self._program or EducationalProgram()
        program.name = self.name.text().strip()
        program.description = self.description.toPlainText().strip() or None
        program.level = self.level.text().strip() or None
        program.duration_hours = self.duration.value()
        return program


class DisciplineDialog(QDialog):
    """Dialog for creating or editing a discipline."""

    def __init__(self, discipline: Optional[Discipline] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Discipline"))
        self._discipline = discipline
        layout = QFormLayout(self)
        self.name = QLineEdit(discipline.name if discipline else "")
        self.description = QTextEdit(discipline.description if discipline else "")
        self.order_index = QSpinBox()
        self.order_index.setRange(0, 999)
        if discipline:
            self.order_index.setValue(discipline.order_index)
        layout.addRow(self.tr("Name"), self.name)
        layout.addRow(self.tr("Description"), self.description)
        layout.addRow(self.tr("Order index"), self.order_index)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_discipline(self) -> Discipline:
        discipline = self._discipline or Discipline()
        discipline.name = self.name.text().strip()
        discipline.description = self.description.toPlainText().strip() or None
        discipline.order_index = self.order_index.value()
        return discipline


class TopicDialog(QDialog):
    """Dialog for creating or editing a topic."""

    def __init__(self, topic: Optional[Topic] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Topic"))
        self._topic = topic
        layout = QFormLayout(self)
        self.title = QLineEdit(topic.title if topic else "")
        self.description = QTextEdit(topic.description if topic else "")
        self.order_index = QSpinBox()
        self.order_index.setRange(0, 999)
        if topic:
            self.order_index.setValue(topic.order_index)
        layout.addRow(self.tr("Title"), self.title)
        layout.addRow(self.tr("Description"), self.description)
        layout.addRow(self.tr("Order index"), self.order_index)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_topic(self) -> Topic:
        topic = self._topic or Topic()
        topic.title = self.title.text().strip()
        topic.description = self.description.toPlainText().strip() or None
        topic.order_index = self.order_index.value()
        return topic


class LessonDialog(QDialog):
    """Dialog for creating or editing a lesson."""

    def __init__(self, lesson: Optional[Lesson] = None, lesson_types: Optional[list[LessonType]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Lesson"))
        self._lesson = lesson
        self._lesson_types = lesson_types or []
        layout = QFormLayout(self)
        self.title = QLineEdit(lesson.title if lesson else "")
        self.description = QTextEdit(lesson.description if lesson else "")
        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.0, 1000.0)
        self.duration.setSingleStep(0.5)
        if lesson:
            self.duration.setValue(lesson.duration_hours)
        self.classroom_hours = QDoubleSpinBox()
        self.classroom_hours.setRange(0.0, 1000.0)
        self.classroom_hours.setSingleStep(0.5)
        if lesson and lesson.classroom_hours is not None:
            self.classroom_hours.setValue(lesson.classroom_hours)
        self.self_study_hours = QDoubleSpinBox()
        self.self_study_hours.setRange(0.0, 1000.0)
        self.self_study_hours.setSingleStep(0.5)
        if lesson and lesson.self_study_hours is not None:
            self.self_study_hours.setValue(lesson.self_study_hours)
        self.lesson_type = QComboBox()
        for lesson_type in self._lesson_types:
            self.lesson_type.addItem(lesson_type.name, lesson_type.id)
        if lesson and lesson.lesson_type_id:
            idx = self.lesson_type.findData(lesson.lesson_type_id)
            if idx >= 0:
                self.lesson_type.setCurrentIndex(idx)
        self.order_index = QSpinBox()
        self.order_index.setRange(0, 999)
        if lesson:
            self.order_index.setValue(lesson.order_index)
        layout.addRow(self.tr("Title"), self.title)
        layout.addRow(self.tr("Description"), self.description)
        layout.addRow(self.tr("Total hours"), self.duration)
        layout.addRow(self.tr("Classroom hours"), self.classroom_hours)
        layout.addRow(self.tr("Self-study hours"), self.self_study_hours)
        layout.addRow(self.tr("Lesson type"), self.lesson_type)
        layout.addRow(self.tr("Order index"), self.order_index)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_lesson(self) -> Lesson:
        lesson = self._lesson or Lesson()
        lesson.title = self.title.text().strip()
        lesson.description = self.description.toPlainText().strip() or None
        lesson.duration_hours = self.duration.value()
        lesson.classroom_hours = self.classroom_hours.value()
        lesson.self_study_hours = self.self_study_hours.value()
        lesson.lesson_type_id = self.lesson_type.currentData()
        lesson.order_index = self.order_index.value()
        return lesson


class LessonTypeDialog(QDialog):
    """Dialog for creating or editing a lesson type."""

    def __init__(self, lesson_type: Optional[LessonType] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Lesson type"))
        self._lesson_type = lesson_type
        layout = QFormLayout(self)
        self.name = QLineEdit(lesson_type.name if lesson_type else "")
        layout.addRow(self.tr("Name"), self.name)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_lesson_type(self) -> LessonType:
        lesson_type = self._lesson_type or LessonType()
        lesson_type.name = self.name.text().strip()
        return lesson_type


class QuestionDialog(QDialog):
    """Dialog for creating or editing a question."""

    def __init__(self, question: Optional[Question] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Question"))
        self._question = question
        layout = QFormLayout(self)
        self.content = QTextEdit(question.content if question else "")
        self.answer = QTextEdit(question.answer if question else "")
        self.difficulty = QSpinBox()
        self.difficulty.setRange(1, 5)
        if question:
            self.difficulty.setValue(question.difficulty_level)
        self.order_index = QSpinBox()
        self.order_index.setRange(0, 999)
        if question:
            self.order_index.setValue(question.order_index)
        layout.addRow(self.tr("Question"), self.content)
        layout.addRow(self.tr("Answer"), self.answer)
        layout.addRow(self.tr("Difficulty (1-5)"), self.difficulty)
        layout.addRow(self.tr("Order index"), self.order_index)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_question(self) -> Question:
        question = self._question or Question()
        question.content = self.content.toPlainText().strip()
        question.answer = self.answer.toPlainText().strip() or None
        question.difficulty_level = self.difficulty.value()
        question.order_index = self.order_index.value()
        return question


class MaterialDialog(QDialog):
    """Dialog for creating or editing a material."""

    def __init__(self, material: Optional[MethodicalMaterial] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Methodical Material"))
        self._material = material
        layout = QFormLayout(self)
        self.title = QLineEdit(material.title if material else "")
        self.material_type = QComboBox()
        self._material_types = ["plan", "guide", "presentation", "attachment"]
        for material_type in self._material_types:
            self.material_type.addItem(self.tr(material_type), material_type)
        if material:
            idx = self.material_type.findData(material.material_type)
            if idx >= 0:
                self.material_type.setCurrentIndex(idx)
        self.description = QTextEdit(material.description if material else "")
        filename = material.original_filename if material and material.original_filename else (material.file_name if material else "")
        self.file_name = QLineEdit(filename)
        self.file_name.setReadOnly(True)
        layout.addRow(self.tr("Title"), self.title)
        layout.addRow(self.tr("Type"), self.material_type)
        layout.addRow(self.tr("Description"), self.description)
        layout.addRow(self.tr("Attached file"), self.file_name)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_material(self) -> MethodicalMaterial:
        material = self._material or MethodicalMaterial()
        material.title = self.title.text().strip()
        material.material_type = self.material_type.currentData()
        material.description = self.description.toPlainText().strip() or None
        return material


class ImportPreviewDialog(QDialog):
    """Preview parsed curriculum structure."""

    def __init__(self, topics: list[CurriculumTopic], parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Import preview"))
        layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([self.tr("Title"), self.tr("Details")])
        self.tree.setColumnWidth(0, 420)
        self.tree.setWordWrap(True)
        self.tree.setUniformRowHeights(False)
        self.tree.setTextElideMode(Qt.ElideNone)
        layout.addWidget(self.tree)
        for topic in topics:
            topic_item = QTreeWidgetItem([topic.title, self.tr("Topic")])
            for lesson in topic.lessons:
                details = []
                if lesson.lesson_type_name:
                    details.append(lesson.lesson_type_name)
                if lesson.total_hours is not None:
                    details.append(f"{lesson.total_hours}h")
                lesson_item = QTreeWidgetItem([lesson.title, " | ".join(details)])
                for question in lesson.questions:
                    question_item = QTreeWidgetItem([question.text, self.tr("Question")])
                    lesson_item.addChild(question_item)
                topic_item.addChild(lesson_item)
            self.tree.addTopLevelItem(topic_item)
        self.tree.expandAll()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ImportCurriculumDialog(QDialog):
    """Dialog to collect import inputs and parse curriculum."""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.parsed_topics: Optional[list[CurriculumTopic]] = None
        self.file_paths: list[str] = []
        self.setWindowTitle(self.tr("Import curriculum structure"))
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.program_combo = QComboBox()
        self.discipline_combo = QComboBox()
        self.new_discipline = QLineEdit()
        self.new_discipline.setPlaceholderText(self.tr("New discipline name"))
        self.new_discipline.setVisible(False)
        form.addRow(self.tr("Program"), self.program_combo)
        form.addRow(self.tr("Discipline"), self.discipline_combo)
        form.addRow(self.tr("New discipline"), self.new_discipline)
        layout.addLayout(form)

        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText(self.tr("Paste table text here..."))
        layout.addWidget(self.input_text)

        action_row = QHBoxLayout()
        self.load_file = QPushButton(self.tr("Load file"))
        self.load_files = QPushButton(self.tr("Load files (batch)"))
        self.preview_btn = QPushButton(self.tr("Preview"))
        action_row.addWidget(self.load_file)
        action_row.addWidget(self.load_files)
        action_row.addWidget(self.preview_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.load_file.clicked.connect(self._load_file)
        self.load_files.clicked.connect(self._load_files)
        self.preview_btn.clicked.connect(self._preview)
        self.program_combo.currentIndexChanged.connect(self._refresh_disciplines)
        self.discipline_combo.currentIndexChanged.connect(self._toggle_new_discipline)

        self._load_programs()

    def _load_programs(self) -> None:
        self.program_combo.clear()
        for program in self.controller.get_programs():
            self.program_combo.addItem(program.name, program.id)
        self._refresh_disciplines()

    def _refresh_disciplines(self) -> None:
        self.discipline_combo.clear()
        program_id = self.program_combo.currentData()
        if program_id is None:
            return
        disciplines = self.controller.get_program_disciplines(program_id)
        for discipline in disciplines:
            self.discipline_combo.addItem(discipline.name, discipline.id)
        self.discipline_combo.addItem(self.tr("Create new..."), None)
        self._toggle_new_discipline()

    def _toggle_new_discipline(self) -> None:
        self.new_discipline.setVisible(self.discipline_combo.currentData() is None)

    def _load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open table file"),
            "",
            self.tr("Documents (*.txt *.tsv *.csv *.docx *.doc);;All files (*)"),
        )
        if not path:
            return
        self.file_paths = [path]
        try:
            content = extract_text_from_file(path)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        self.input_text.setPlainText(content)

    def _load_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Open table files"),
            "",
            self.tr("Documents (*.txt *.tsv *.csv *.docx *.doc);;All files (*)"),
        )
        if not paths:
            return
        self.file_paths = paths
        self.input_text.setPlainText("")

    def _preview(self) -> None:
        if len(self.file_paths) > 1:
            QMessageBox.information(
                self,
                self.tr("Preview"),
                self.tr("Preview is available for single-file import only."),
            )
            return
        try:
            topics = parse_curriculum_text(self.input_text.toPlainText())
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        dialog = ImportPreviewDialog(topics, self)
        if dialog.exec() == QDialog.Accepted:
            self.parsed_topics = topics

    def get_payload(self):
        program_id = self.program_combo.currentData()
        discipline_id = self.discipline_combo.currentData()
        new_name = self.new_discipline.text().strip() if discipline_id is None else None
        return program_id, discipline_id, new_name, self.input_text.toPlainText(), self.parsed_topics, self.file_paths
