"""Dialog windows for CRUD operations."""
from typing import Optional
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
)
from ..models.entities import Teacher, EducationalProgram, Discipline, Topic, Lesson, Question, MethodicalMaterial


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
        self.position = QLineEdit(teacher.position if teacher else "")
        self.department = QLineEdit(teacher.department if teacher else "")
        self.email = QLineEdit(teacher.email if teacher else "")
        self.phone = QLineEdit(teacher.phone if teacher else "")
        layout.addRow(self.tr("Full name"), self.full_name)
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

    def __init__(self, lesson: Optional[Lesson] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Lesson"))
        self._lesson = lesson
        layout = QFormLayout(self)
        self.title = QLineEdit(lesson.title if lesson else "")
        self.description = QTextEdit(lesson.description if lesson else "")
        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.5, 100.0)
        self.duration.setSingleStep(0.5)
        if lesson:
            self.duration.setValue(lesson.duration_hours)
        self.order_index = QSpinBox()
        self.order_index.setRange(0, 999)
        if lesson:
            self.order_index.setValue(lesson.order_index)
        layout.addRow(self.tr("Title"), self.title)
        layout.addRow(self.tr("Description"), self.description)
        layout.addRow(self.tr("Duration (hours)"), self.duration)
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
        lesson.order_index = self.order_index.value()
        return lesson


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
        self.file_name = QLineEdit(material.file_name if material else "")
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
