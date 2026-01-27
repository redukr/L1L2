"""Admin management dialog."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QSplitter,
)
from ..controllers.admin_controller import AdminController
from ..models.database import Database
from ..ui.dialogs import (
    PasswordDialog,
    TeacherDialog,
    ProgramDialog,
    TopicDialog,
    LessonDialog,
    QuestionDialog,
    MaterialDialog,
)


class AdminDialog(QDialog):
    """Admin dialog with CRUD and association management."""

    def __init__(self, database: Database, parent=None):
        super().__init__(parent)
        self.controller = AdminController(database)
        self.setWindowTitle("Admin Panel")
        self.resize(1200, 760)
        if not self._authorize():
            self.reject()
            return
        self._build_ui()
        self._refresh_all()

    def _authorize(self) -> bool:
        dialog = PasswordDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return False
        if not self.controller.verify_password(dialog.get_password()):
            QMessageBox.warning(self, "Access denied", "Invalid admin password.")
            return False
        return True

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self._build_teachers_tab(), "Teachers")
        self.tabs.addTab(self._build_programs_tab(), "Programs")
        self.tabs.addTab(self._build_topics_tab(), "Topics")
        self.tabs.addTab(self._build_lessons_tab(), "Lessons")
        self.tabs.addTab(self._build_questions_tab(), "Questions")
        self.tabs.addTab(self._build_materials_tab(), "Materials")

    def _build_teachers_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.teachers_table = QTableWidget(0, 5)
        self.teachers_table.setHorizontalHeaderLabels(
            ["Full name", "Position", "Department", "Email", "Phone"]
        )
        self.teachers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.teachers_table)
        btn_layout = QHBoxLayout()
        self.teacher_add = QPushButton("Add")
        self.teacher_edit = QPushButton("Edit")
        self.teacher_delete = QPushButton("Delete")
        btn_layout.addWidget(self.teacher_add)
        btn_layout.addWidget(self.teacher_edit)
        btn_layout.addWidget(self.teacher_delete)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        self.teacher_add.clicked.connect(self._add_teacher)
        self.teacher_edit.clicked.connect(self._edit_teacher)
        self.teacher_delete.clicked.connect(self._delete_teacher)
        return tab

    def _build_programs_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.programs_table = QTableWidget(0, 3)
        self.programs_table.setHorizontalHeaderLabels(["Name", "Level", "Duration"])
        self.programs_table.horizontalHeader().setStretchLastSection(True)
        top_layout.addWidget(self.programs_table)
        btn_layout = QHBoxLayout()
        self.program_add = QPushButton("Add")
        self.program_edit = QPushButton("Edit")
        self.program_delete = QPushButton("Delete")
        btn_layout.addWidget(self.program_add)
        btn_layout.addWidget(self.program_edit)
        btn_layout.addWidget(self.program_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.addWidget(QLabel("Program topics"))
        self.program_topics_assigned = QListWidget()
        self.program_topics_available = QListWidget()
        mid_layout = QVBoxLayout()
        self.program_topic_add = QPushButton("Add ->")
        self.program_topic_remove = QPushButton("<- Remove")
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.program_topic_add)
        mid_layout.addWidget(self.program_topic_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.program_topics_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.program_topics_assigned)
        splitter.addWidget(bottom)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)

        self.program_add.clicked.connect(self._add_program)
        self.program_edit.clicked.connect(self._edit_program)
        self.program_delete.clicked.connect(self._delete_program)
        self.programs_table.itemSelectionChanged.connect(self._refresh_program_topics)
        self.program_topic_add.clicked.connect(self._add_topic_to_program)
        self.program_topic_remove.clicked.connect(self._remove_topic_from_program)
        return tab

    def _build_topics_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.topics_table = QTableWidget(0, 2)
        self.topics_table.setHorizontalHeaderLabels(["Title", "Order"])
        self.topics_table.horizontalHeader().setStretchLastSection(True)
        top_layout.addWidget(self.topics_table)
        btn_layout = QHBoxLayout()
        self.topic_add = QPushButton("Add")
        self.topic_edit = QPushButton("Edit")
        self.topic_delete = QPushButton("Delete")
        btn_layout.addWidget(self.topic_add)
        btn_layout.addWidget(self.topic_edit)
        btn_layout.addWidget(self.topic_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.addWidget(QLabel("Topic lessons"))
        self.topic_lessons_available = QListWidget()
        self.topic_lessons_assigned = QListWidget()
        mid_layout = QVBoxLayout()
        self.topic_lesson_add = QPushButton("Add ->")
        self.topic_lesson_remove = QPushButton("<- Remove")
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.topic_lesson_add)
        mid_layout.addWidget(self.topic_lesson_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.topic_lessons_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.topic_lessons_assigned)
        splitter.addWidget(bottom)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)

        self.topic_add.clicked.connect(self._add_topic)
        self.topic_edit.clicked.connect(self._edit_topic)
        self.topic_delete.clicked.connect(self._delete_topic)
        self.topics_table.itemSelectionChanged.connect(self._refresh_topic_lessons)
        self.topic_lesson_add.clicked.connect(self._add_lesson_to_topic)
        self.topic_lesson_remove.clicked.connect(self._remove_lesson_from_topic)
        return tab

    def _build_lessons_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.lessons_table = QTableWidget(0, 3)
        self.lessons_table.setHorizontalHeaderLabels(["Title", "Duration", "Order"])
        self.lessons_table.horizontalHeader().setStretchLastSection(True)
        top_layout.addWidget(self.lessons_table)
        btn_layout = QHBoxLayout()
        self.lesson_add = QPushButton("Add")
        self.lesson_edit = QPushButton("Edit")
        self.lesson_delete = QPushButton("Delete")
        btn_layout.addWidget(self.lesson_add)
        btn_layout.addWidget(self.lesson_edit)
        btn_layout.addWidget(self.lesson_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.addWidget(QLabel("Lesson questions"))
        self.lesson_questions_available = QListWidget()
        self.lesson_questions_assigned = QListWidget()
        mid_layout = QVBoxLayout()
        self.lesson_question_add = QPushButton("Add ->")
        self.lesson_question_remove = QPushButton("<- Remove")
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.lesson_question_add)
        mid_layout.addWidget(self.lesson_question_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.lesson_questions_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.lesson_questions_assigned)
        splitter.addWidget(bottom)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)

        self.lesson_add.clicked.connect(self._add_lesson)
        self.lesson_edit.clicked.connect(self._edit_lesson)
        self.lesson_delete.clicked.connect(self._delete_lesson)
        self.lessons_table.itemSelectionChanged.connect(self._refresh_lesson_questions)
        self.lesson_question_add.clicked.connect(self._add_question_to_lesson)
        self.lesson_question_remove.clicked.connect(self._remove_question_from_lesson)
        return tab

    def _build_questions_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.questions_table = QTableWidget(0, 2)
        self.questions_table.setHorizontalHeaderLabels(["Question", "Difficulty"])
        self.questions_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.questions_table)
        btn_layout = QHBoxLayout()
        self.question_add = QPushButton("Add")
        self.question_edit = QPushButton("Edit")
        self.question_delete = QPushButton("Delete")
        btn_layout.addWidget(self.question_add)
        btn_layout.addWidget(self.question_edit)
        btn_layout.addWidget(self.question_delete)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        self.question_add.clicked.connect(self._add_question)
        self.question_edit.clicked.connect(self._edit_question)
        self.question_delete.clicked.connect(self._delete_question)
        return tab

    def _build_materials_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.materials_table = QTableWidget(0, 3)
        self.materials_table.setHorizontalHeaderLabels(["Title", "Type", "File"])
        self.materials_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.materials_table)
        btn_layout = QHBoxLayout()
        self.material_add = QPushButton("Add")
        self.material_edit = QPushButton("Edit")
        self.material_delete = QPushButton("Delete")
        self.material_attach = QPushButton("Attach File")
        btn_layout.addWidget(self.material_add)
        btn_layout.addWidget(self.material_edit)
        btn_layout.addWidget(self.material_delete)
        btn_layout.addWidget(self.material_attach)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        assignment_layout = QHBoxLayout()
        teacher_group = QVBoxLayout()
        teacher_group.addWidget(QLabel("Material teachers"))
        self.material_teachers_available = QListWidget()
        self.material_teachers_assigned = QListWidget()
        teacher_btns = QHBoxLayout()
        self.material_teacher_add = QPushButton("Add ->")
        self.material_teacher_remove = QPushButton("<- Remove")
        teacher_btns.addWidget(self.material_teacher_add)
        teacher_btns.addWidget(self.material_teacher_remove)
        teacher_group.addWidget(QLabel("Available"))
        teacher_group.addWidget(self.material_teachers_available)
        teacher_group.addLayout(teacher_btns)
        teacher_group.addWidget(QLabel("Assigned"))
        teacher_group.addWidget(self.material_teachers_assigned)
        assignment_layout.addLayout(teacher_group)

        association_group = QVBoxLayout()
        association_group.addWidget(QLabel("Associations"))
        self.material_assoc_type = QComboBox()
        self.material_assoc_type.addItems(["program", "topic", "lesson"])
        self.material_assoc_available = QListWidget()
        self.material_assoc_assigned = QListWidget()
        assoc_btns = QHBoxLayout()
        self.material_assoc_add = QPushButton("Link ->")
        self.material_assoc_remove = QPushButton("<- Unlink")
        assoc_btns.addWidget(self.material_assoc_add)
        assoc_btns.addWidget(self.material_assoc_remove)
        association_group.addWidget(self.material_assoc_type)
        association_group.addWidget(QLabel("Available"))
        association_group.addWidget(self.material_assoc_available)
        association_group.addLayout(assoc_btns)
        association_group.addWidget(QLabel("Linked"))
        association_group.addWidget(self.material_assoc_assigned)
        assignment_layout.addLayout(association_group)
        layout.addLayout(assignment_layout)

        self.material_add.clicked.connect(self._add_material)
        self.material_edit.clicked.connect(self._edit_material)
        self.material_delete.clicked.connect(self._delete_material)
        self.material_attach.clicked.connect(self._attach_material_file)
        self.materials_table.itemSelectionChanged.connect(self._refresh_material_assignments)
        self.material_teacher_add.clicked.connect(self._add_teacher_to_material)
        self.material_teacher_remove.clicked.connect(self._remove_teacher_from_material)
        self.material_assoc_type.currentTextChanged.connect(self._refresh_material_associations)
        self.material_assoc_add.clicked.connect(self._link_material_association)
        self.material_assoc_remove.clicked.connect(self._unlink_material_association)
        return tab

    def _refresh_all(self) -> None:
        self._refresh_teachers()
        self._refresh_programs()
        self._refresh_topics()
        self._refresh_lessons()
        self._refresh_questions()
        self._refresh_materials()

    # Teachers
    def _refresh_teachers(self) -> None:
        self.teachers_table.setRowCount(0)
        for teacher in self.controller.get_teachers():
            row = self.teachers_table.rowCount()
            self.teachers_table.insertRow(row)
            self.teachers_table.setItem(row, 0, QTableWidgetItem(teacher.full_name))
            self.teachers_table.setItem(row, 1, QTableWidgetItem(teacher.position or ""))
            self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher.department or ""))
            self.teachers_table.setItem(row, 3, QTableWidgetItem(teacher.email or ""))
            self.teachers_table.setItem(row, 4, QTableWidgetItem(teacher.phone or ""))
            self.teachers_table.item(row, 0).setData(Qt.UserRole, teacher)

    def _add_teacher(self) -> None:
        dialog = TeacherDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        teacher = dialog.get_teacher()
        if not teacher.full_name:
            QMessageBox.warning(self, "Validation", "Full name is required.")
            return
        self.controller.add_teacher(teacher)
        self._refresh_teachers()

    def _edit_teacher(self) -> None:
        teacher = self._current_entity(self.teachers_table)
        if not teacher:
            return
        dialog = TeacherDialog(teacher, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_teacher(dialog.get_teacher())
        self._refresh_teachers()

    def _delete_teacher(self) -> None:
        teacher = self._current_entity(self.teachers_table)
        if not teacher:
            return
        if QMessageBox.question(self, "Confirm", "Delete selected teacher?") != QMessageBox.Yes:
            return
        self.controller.delete_teacher(teacher.id)
        self._refresh_teachers()

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
        self._refresh_program_topics()

    def _add_program(self) -> None:
        dialog = ProgramDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        program = dialog.get_program()
        if not program.name:
            QMessageBox.warning(self, "Validation", "Program name is required.")
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
        program = self._current_entity(self.programs_table)
        if not program:
            return
        if QMessageBox.question(self, "Confirm", "Delete selected program?") != QMessageBox.Yes:
            return
        self.controller.delete_program(program.id)
        self._refresh_programs()

    def _refresh_program_topics(self) -> None:
        self.program_topics_assigned.clear()
        self.program_topics_available.clear()
        program = self._current_entity(self.programs_table)
        topics = self.controller.get_topics()
        assigned = []
        if program:
            assigned = self.controller.get_program_topics(program.id)
        assigned_ids = {t.id for t in assigned}
        for topic in topics:
            item = QListWidgetItem(topic.title)
            item.setData(Qt.UserRole, topic)
            if topic.id in assigned_ids:
                self.program_topics_assigned.addItem(item)
            else:
                self.program_topics_available.addItem(item)

    def _add_topic_to_program(self) -> None:
        program = self._current_entity(self.programs_table)
        item = self.program_topics_available.currentItem()
        if not program or not item:
            return
        topic = item.data(Qt.UserRole)
        self.controller.add_topic_to_program(program.id, topic.id, topic.order_index)
        self._refresh_program_topics()

    def _remove_topic_from_program(self) -> None:
        program = self._current_entity(self.programs_table)
        item = self.program_topics_assigned.currentItem()
        if not program or not item:
            return
        topic = item.data(Qt.UserRole)
        self.controller.remove_topic_from_program(program.id, topic.id)
        self._refresh_program_topics()

    # Topics
    def _refresh_topics(self) -> None:
        self.topics_table.setRowCount(0)
        for topic in self.controller.get_topics():
            row = self.topics_table.rowCount()
            self.topics_table.insertRow(row)
            self.topics_table.setItem(row, 0, QTableWidgetItem(topic.title))
            self.topics_table.setItem(row, 1, QTableWidgetItem(str(topic.order_index)))
            self.topics_table.item(row, 0).setData(Qt.UserRole, topic)
        self._refresh_topic_lessons()

    def _add_topic(self) -> None:
        dialog = TopicDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        topic = dialog.get_topic()
        if not topic.title:
            QMessageBox.warning(self, "Validation", "Topic title is required.")
            return
        self.controller.add_topic(topic)
        self._refresh_topics()

    def _edit_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        if not topic:
            return
        dialog = TopicDialog(topic, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_topic(dialog.get_topic())
        self._refresh_topics()

    def _delete_topic(self) -> None:
        topic = self._current_entity(self.topics_table)
        if not topic:
            return
        if QMessageBox.question(self, "Confirm", "Delete selected topic?") != QMessageBox.Yes:
            return
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

    # Lessons
    def _refresh_lessons(self) -> None:
        self.lessons_table.setRowCount(0)
        for lesson in self.controller.get_lessons():
            row = self.lessons_table.rowCount()
            self.lessons_table.insertRow(row)
            self.lessons_table.setItem(row, 0, QTableWidgetItem(lesson.title))
            self.lessons_table.setItem(row, 1, QTableWidgetItem(str(lesson.duration_hours)))
            self.lessons_table.setItem(row, 2, QTableWidgetItem(str(lesson.order_index)))
            self.lessons_table.item(row, 0).setData(Qt.UserRole, lesson)
        self._refresh_lesson_questions()

    def _add_lesson(self) -> None:
        dialog = LessonDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        lesson = dialog.get_lesson()
        if not lesson.title:
            QMessageBox.warning(self, "Validation", "Lesson title is required.")
            return
        self.controller.add_lesson(lesson)
        self._refresh_lessons()

    def _edit_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        if not lesson:
            return
        dialog = LessonDialog(lesson, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_lesson(dialog.get_lesson())
        self._refresh_lessons()

    def _delete_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        if not lesson:
            return
        if QMessageBox.question(self, "Confirm", "Delete selected lesson?") != QMessageBox.Yes:
            return
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

    def _add_question_to_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        item = self.lesson_questions_available.currentItem()
        if not lesson or not item:
            return
        question = item.data(Qt.UserRole)
        self.controller.add_question_to_lesson(lesson.id, question.id, question.order_index)
        self._refresh_lesson_questions()

    def _remove_question_from_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        item = self.lesson_questions_assigned.currentItem()
        if not lesson or not item:
            return
        question = item.data(Qt.UserRole)
        self.controller.remove_question_from_lesson(lesson.id, question.id)
        self._refresh_lesson_questions()

    # Questions
    def _refresh_questions(self) -> None:
        self.questions_table.setRowCount(0)
        for question in self.controller.get_questions():
            row = self.questions_table.rowCount()
            self.questions_table.insertRow(row)
            title = question.content if len(question.content) <= 80 else f"{question.content[:80]}..."
            self.questions_table.setItem(row, 0, QTableWidgetItem(title))
            self.questions_table.setItem(row, 1, QTableWidgetItem(str(question.difficulty_level)))
            self.questions_table.item(row, 0).setData(Qt.UserRole, question)

    def _add_question(self) -> None:
        dialog = QuestionDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        question = dialog.get_question()
        if not question.content:
            QMessageBox.warning(self, "Validation", "Question text is required.")
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
        question = self._current_entity(self.questions_table)
        if not question:
            return
        if QMessageBox.question(self, "Confirm", "Delete selected question?") != QMessageBox.Yes:
            return
        self.controller.delete_question(question.id)
        self._refresh_questions()

    # Materials
    def _refresh_materials(self) -> None:
        self.materials_table.setRowCount(0)
        for material in self.controller.get_materials():
            row = self.materials_table.rowCount()
            self.materials_table.insertRow(row)
            self.materials_table.setItem(row, 0, QTableWidgetItem(material.title))
            self.materials_table.setItem(row, 1, QTableWidgetItem(material.material_type))
            self.materials_table.setItem(row, 2, QTableWidgetItem(material.file_name or ""))
            self.materials_table.item(row, 0).setData(Qt.UserRole, material)
        self._refresh_material_assignments()

    def _add_material(self) -> None:
        dialog = MaterialDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        material = dialog.get_material()
        if not material.title:
            QMessageBox.warning(self, "Validation", "Material title is required.")
            return
        self.controller.add_material(material)
        self._refresh_materials()

    def _edit_material(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        dialog = MaterialDialog(material, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_material(dialog.get_material())
        self._refresh_materials()

    def _delete_material(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        if QMessageBox.question(self, "Confirm", "Delete selected material?") != QMessageBox.Yes:
            return
        self.controller.delete_material(material.id)
        self._refresh_materials()

    def _attach_material_file(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach File",
            "",
            "Documents (*.pdf *.pptx *.docx)",
        )
        if not path:
            return
        updated = self.controller.attach_material_file(material, path)
        if updated:
            self._refresh_materials()

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
            item = QListWidgetItem(f"{entity_type}: {title}")
            item.setData(Qt.UserRole, (entity_type, entity_id))
            self.material_assoc_assigned.addItem(item)

        self._refresh_material_associations()

    def _refresh_material_associations(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        self.material_assoc_available.clear()
        entity_type = self.material_assoc_type.currentText()
        if entity_type == "program":
            entities = self.controller.get_programs()
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
        entity_type = self.material_assoc_type.currentText()
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

    def _current_entity(self, table: QTableWidget):
        row = table.currentRow()
        if row < 0:
            return None
        item = table.item(row, 0)
        if not item:
            return None
        return item.data(Qt.UserRole)
