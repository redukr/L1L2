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
    QMenuBar,
    QAbstractItemView,
    QLineEdit,
    QDialog,
)
from pathlib import Path
from ..controllers.admin_controller import AdminController
from ..models.database import Database
from ..services.i18n import I18nManager
from ..ui.dialogs import (
    PasswordDialog,
    TeacherDialog,
    ProgramDialog,
    DisciplineDialog,
    TopicDialog,
    LessonDialog,
    LessonTypeDialog,
    ImportCurriculumDialog,
    QuestionDialog,
    MaterialDialog,
)
from ..services.import_service import (
    import_curriculum_structure,
    import_curriculum_structure_by_names,
    import_teachers_from_docx,
)
from ..services.file_storage import FileStorageManager


class AdminDialog(QDialog):
    """Admin dialog with CRUD and association management."""

    def __init__(self, database: Database, i18n: I18nManager, parent=None):
        super().__init__(parent)
        self.controller = AdminController(database)
        self.i18n = i18n
        self.file_storage = FileStorageManager()
        self.setWindowTitle(self.tr("Admin Panel"))
        self.resize(1200, 760)
        if not self._authorize():
            self.reject()
            return
        self._build_ui()
        self._refresh_all()
        self.i18n.language_changed.connect(self.retranslate_ui)

    def _authorize(self) -> bool:
        dialog = PasswordDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return False
        if not self.controller.verify_password(dialog.get_password()):
            QMessageBox.warning(self, self.tr("Access denied"), self.tr("Invalid admin password."))
            return False
        return True

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.menu_bar = QMenuBar()
        import_menu = self.menu_bar.addMenu(self.tr("Import"))
        self.import_curriculum_action = import_menu.addAction(self.tr("Import curriculum structure"))
        self.import_teachers_action = import_menu.addAction(self.tr("Import teachers from DOCX"))
        self.import_curriculum_action.triggered.connect(self._on_import_curriculum)
        self.import_teachers_action.triggered.connect(self._on_import_teachers)
        layout.setMenuBar(self.menu_bar)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self._build_teachers_tab(), self.tr("Teachers"))
        self.tabs.addTab(self._build_programs_tab(), self.tr("Programs"))
        self.tabs.addTab(self._build_disciplines_tab(), self.tr("Disciplines"))
        self.tabs.addTab(self._build_topics_tab(), self.tr("Topics"))
        self.tabs.addTab(self._build_lessons_tab(), self.tr("Lessons"))
        self.tabs.addTab(self._build_lesson_types_tab(), self.tr("Lesson types"))
        self.tabs.addTab(self._build_questions_tab(), self.tr("Questions"))
        self.tabs.addTab(self._build_materials_tab(), self.tr("Materials"))
        self.tabs.addTab(self._build_settings_tab(), self.tr("Settings"))

    def _build_teachers_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.teachers_table = QTableWidget(0, 6)
        self.teachers_table.setHorizontalHeaderLabels(
            [
                self.tr("Full name"),
                self.tr("Military rank"),
                self.tr("Position"),
                self.tr("Department"),
                self.tr("Email"),
                self.tr("Phone"),
            ]
        )
        self.teachers_table.horizontalHeader().setStretchLastSection(True)
        self.teachers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.teachers_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.teachers_table)
        btn_layout = QHBoxLayout()
        self.teacher_add = QPushButton(self.tr("Add"))
        self.teacher_edit = QPushButton(self.tr("Edit"))
        self.teacher_delete = QPushButton(self.tr("Delete"))
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
        self.programs_table.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Level"), self.tr("Duration")])
        self.programs_table.horizontalHeader().setStretchLastSection(True)
        self.programs_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.programs_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        top_layout.addWidget(self.programs_table)
        btn_layout = QHBoxLayout()
        self.program_add = QPushButton(self.tr("Add"))
        self.program_edit = QPushButton(self.tr("Edit"))
        self.program_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.program_add)
        btn_layout.addWidget(self.program_edit)
        btn_layout.addWidget(self.program_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        self.program_disciplines_label = QLabel(self.tr("Program disciplines"))
        bottom_layout.addWidget(self.program_disciplines_label)
        self.program_disciplines_assigned = QListWidget()
        self.program_disciplines_available = QListWidget()
        mid_layout = QVBoxLayout()
        self.program_discipline_add = QPushButton(self.tr("Add ->"))
        self.program_discipline_remove = QPushButton(self.tr("<- Remove"))
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.program_discipline_add)
        mid_layout.addWidget(self.program_discipline_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.program_disciplines_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.program_disciplines_assigned)
        splitter.addWidget(bottom)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)

        self.program_add.clicked.connect(self._add_program)
        self.program_edit.clicked.connect(self._edit_program)
        self.program_delete.clicked.connect(self._delete_program)
        self.programs_table.itemSelectionChanged.connect(self._on_program_selection_changed)
        self.program_discipline_add.clicked.connect(self._add_discipline_to_program)
        self.program_discipline_remove.clicked.connect(self._remove_discipline_from_program)
        return tab

    def _build_disciplines_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.disciplines_table = QTableWidget(0, 2)
        self.disciplines_table.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Order")])
        self.disciplines_table.horizontalHeader().setStretchLastSection(True)
        self.disciplines_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.disciplines_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        top_layout.addWidget(self.disciplines_table)
        btn_layout = QHBoxLayout()
        self.discipline_add = QPushButton(self.tr("Add"))
        self.discipline_edit = QPushButton(self.tr("Edit"))
        self.discipline_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.discipline_add)
        btn_layout.addWidget(self.discipline_edit)
        btn_layout.addWidget(self.discipline_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        self.discipline_topics_label = QLabel(self.tr("Discipline topics"))
        bottom_layout.addWidget(self.discipline_topics_label)
        self.discipline_topics_available = QListWidget()
        self.discipline_topics_assigned = QListWidget()
        mid_layout = QVBoxLayout()
        self.discipline_topic_add = QPushButton(self.tr("Add ->"))
        self.discipline_topic_remove = QPushButton(self.tr("<- Remove"))
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.discipline_topic_add)
        mid_layout.addWidget(self.discipline_topic_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.discipline_topics_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.discipline_topics_assigned)
        splitter.addWidget(bottom)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)

        self.discipline_add.clicked.connect(self._add_discipline)
        self.discipline_edit.clicked.connect(self._edit_discipline)
        self.discipline_delete.clicked.connect(self._delete_discipline)
        self.disciplines_table.itemSelectionChanged.connect(self._on_discipline_selection_changed)
        self.discipline_topic_add.clicked.connect(self._add_topic_to_discipline)
        self.discipline_topic_remove.clicked.connect(self._remove_topic_from_discipline)
        return tab

    def _build_topics_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.topics_table = QTableWidget(0, 2)
        self.topics_table.setHorizontalHeaderLabels([self.tr("Title"), self.tr("Order")])
        self.topics_table.horizontalHeader().setStretchLastSection(True)
        self.topics_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.topics_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        top_layout.addWidget(self.topics_table)
        btn_layout = QHBoxLayout()
        self.topic_add = QPushButton(self.tr("Add"))
        self.topic_edit = QPushButton(self.tr("Edit"))
        self.topic_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.topic_add)
        btn_layout.addWidget(self.topic_edit)
        btn_layout.addWidget(self.topic_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        self.topic_lessons_label = QLabel(self.tr("Topic lessons"))
        bottom_layout.addWidget(self.topic_lessons_label)
        self.topic_lessons_available = QListWidget()
        self.topic_lessons_assigned = QListWidget()
        mid_layout = QVBoxLayout()
        self.topic_lesson_add = QPushButton(self.tr("Add ->"))
        self.topic_lesson_remove = QPushButton(self.tr("<- Remove"))
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.topic_lesson_add)
        mid_layout.addWidget(self.topic_lesson_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.topic_lessons_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.topic_lessons_assigned)
        splitter.addWidget(bottom)

        materials_group = QWidget()
        materials_layout = QHBoxLayout(materials_group)
        self.topic_materials_label = QLabel(self.tr("Topic materials"))
        materials_layout.addWidget(self.topic_materials_label)
        self.topic_materials_available = QListWidget()
        self.topic_materials_assigned = QListWidget()
        materials_mid = QVBoxLayout()
        self.topic_material_add = QPushButton(self.tr("Add ->"))
        self.topic_material_remove = QPushButton(self.tr("<- Remove"))
        materials_mid.addStretch(1)
        materials_mid.addWidget(self.topic_material_add)
        materials_mid.addWidget(self.topic_material_remove)
        materials_mid.addStretch(1)
        materials_layout.addWidget(self.topic_materials_available)
        materials_layout.addLayout(materials_mid)
        materials_layout.addWidget(self.topic_materials_assigned)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)
        wrapper.addWidget(materials_group)

        self.topic_add.clicked.connect(self._add_topic)
        self.topic_edit.clicked.connect(self._edit_topic)
        self.topic_delete.clicked.connect(self._delete_topic)
        self.topics_table.itemSelectionChanged.connect(self._on_topic_selection_changed)
        self.topic_lesson_add.clicked.connect(self._add_lesson_to_topic)
        self.topic_lesson_remove.clicked.connect(self._remove_lesson_from_topic)
        self.topic_material_add.clicked.connect(self._add_material_to_topic)
        self.topic_material_remove.clicked.connect(self._remove_material_from_topic)
        return tab

    def _build_lessons_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.lessons_table = QTableWidget(0, 4)
        self.lessons_table.setHorizontalHeaderLabels(
            [self.tr("Title"), self.tr("Total hours"), self.tr("Type"), self.tr("Order")]
        )
        self.lessons_table.horizontalHeader().setStretchLastSection(True)
        self.lessons_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.lessons_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        top_layout.addWidget(self.lessons_table)
        btn_layout = QHBoxLayout()
        self.lesson_add = QPushButton(self.tr("Add"))
        self.lesson_edit = QPushButton(self.tr("Edit"))
        self.lesson_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.lesson_add)
        btn_layout.addWidget(self.lesson_edit)
        btn_layout.addWidget(self.lesson_delete)
        btn_layout.addStretch(1)
        top_layout.addLayout(btn_layout)
        splitter.addWidget(top)

        bottom = QWidget()
        bottom_layout = QHBoxLayout(bottom)
        self.lesson_questions_label = QLabel(self.tr("Lesson questions"))
        bottom_layout.addWidget(self.lesson_questions_label)
        self.lesson_questions_available = QListWidget()
        self.lesson_questions_assigned = QListWidget()
        mid_layout = QVBoxLayout()
        self.lesson_question_add = QPushButton(self.tr("Add ->"))
        self.lesson_question_remove = QPushButton(self.tr("<- Remove"))
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.lesson_question_add)
        mid_layout.addWidget(self.lesson_question_remove)
        mid_layout.addStretch(1)
        bottom_layout.addWidget(self.lesson_questions_available)
        bottom_layout.addLayout(mid_layout)
        bottom_layout.addWidget(self.lesson_questions_assigned)
        splitter.addWidget(bottom)

        materials_group = QWidget()
        materials_layout = QHBoxLayout(materials_group)
        self.lesson_materials_label = QLabel(self.tr("Lesson materials"))
        materials_layout.addWidget(self.lesson_materials_label)
        self.lesson_materials_available = QListWidget()
        self.lesson_materials_assigned = QListWidget()
        materials_mid = QVBoxLayout()
        self.lesson_material_add = QPushButton(self.tr("Add ->"))
        self.lesson_material_remove = QPushButton(self.tr("<- Remove"))
        materials_mid.addStretch(1)
        materials_mid.addWidget(self.lesson_material_add)
        materials_mid.addWidget(self.lesson_material_remove)
        materials_mid.addStretch(1)
        materials_layout.addWidget(self.lesson_materials_available)
        materials_layout.addLayout(materials_mid)
        materials_layout.addWidget(self.lesson_materials_assigned)

        wrapper = QVBoxLayout(tab)
        wrapper.addWidget(splitter)
        wrapper.addWidget(materials_group)

        self.lesson_add.clicked.connect(self._add_lesson)
        self.lesson_edit.clicked.connect(self._edit_lesson)
        self.lesson_delete.clicked.connect(self._delete_lesson)
        self.lessons_table.itemSelectionChanged.connect(self._on_lesson_selection_changed)
        self.lesson_question_add.clicked.connect(self._add_question_to_lesson)
        self.lesson_question_remove.clicked.connect(self._remove_question_from_lesson)
        self.lesson_material_add.clicked.connect(self._add_material_to_lesson)
        self.lesson_material_remove.clicked.connect(self._remove_material_from_lesson)
        return tab

    def _build_lesson_types_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.lesson_types_table = QTableWidget(0, 1)
        self.lesson_types_table.setHorizontalHeaderLabels([self.tr("Name")])
        self.lesson_types_table.horizontalHeader().setStretchLastSection(True)
        self.lesson_types_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.lesson_types_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.lesson_types_table)
        btn_layout = QHBoxLayout()
        self.lesson_type_add = QPushButton(self.tr("Add"))
        self.lesson_type_edit = QPushButton(self.tr("Edit"))
        self.lesson_type_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.lesson_type_add)
        btn_layout.addWidget(self.lesson_type_edit)
        btn_layout.addWidget(self.lesson_type_delete)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        self.lesson_type_add.clicked.connect(self._add_lesson_type)
        self.lesson_type_edit.clicked.connect(self._edit_lesson_type)
        self.lesson_type_delete.clicked.connect(self._delete_lesson_type)
        return tab

    def _build_questions_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.questions_table = QTableWidget(0, 2)
        self.questions_table.setHorizontalHeaderLabels([self.tr("Question"), self.tr("Difficulty")])
        self.questions_table.horizontalHeader().setStretchLastSection(True)
        self.questions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.questions_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.questions_table)
        btn_layout = QHBoxLayout()
        self.question_add = QPushButton(self.tr("Add"))
        self.question_edit = QPushButton(self.tr("Edit"))
        self.question_delete = QPushButton(self.tr("Delete"))
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
        self.materials_table.setHorizontalHeaderLabels([self.tr("Title"), self.tr("Type"), self.tr("File")])
        self.materials_table.horizontalHeader().setStretchLastSection(True)
        self.materials_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.materials_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.materials_table)
        btn_layout = QHBoxLayout()
        self.material_add = QPushButton(self.tr("Add"))
        self.material_edit = QPushButton(self.tr("Edit"))
        self.material_delete = QPushButton(self.tr("Delete"))
        self.material_attach = QPushButton(self.tr("Attach File"))
        self.material_attach_existing = QPushButton(self.tr("Attach existing file"))
        self.material_open = QPushButton(self.tr("Open file"))
        self.material_show = QPushButton(self.tr("Show in folder"))
        self.material_copy = QPushButton(self.tr("Copy file as..."))
        btn_layout.addWidget(self.material_add)
        btn_layout.addWidget(self.material_edit)
        btn_layout.addWidget(self.material_delete)
        btn_layout.addWidget(self.material_attach)
        btn_layout.addWidget(self.material_attach_existing)
        btn_layout.addWidget(self.material_open)
        btn_layout.addWidget(self.material_show)
        btn_layout.addWidget(self.material_copy)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        assignment_layout = QHBoxLayout()
        teacher_group = QVBoxLayout()
        self.material_teachers_label = QLabel(self.tr("Material teachers"))
        teacher_group.addWidget(self.material_teachers_label)
        self.material_teachers_available = QListWidget()
        self.material_teachers_assigned = QListWidget()
        teacher_btns = QHBoxLayout()
        self.material_teacher_add = QPushButton(self.tr("Add ->"))
        self.material_teacher_remove = QPushButton(self.tr("<- Remove"))
        teacher_btns.addWidget(self.material_teacher_add)
        teacher_btns.addWidget(self.material_teacher_remove)
        self.material_teachers_available_label = QLabel(self.tr("Available"))
        teacher_group.addWidget(self.material_teachers_available_label)
        teacher_group.addWidget(self.material_teachers_available)
        teacher_group.addLayout(teacher_btns)
        self.material_teachers_assigned_label = QLabel(self.tr("Assigned"))
        teacher_group.addWidget(self.material_teachers_assigned_label)
        teacher_group.addWidget(self.material_teachers_assigned)
        assignment_layout.addLayout(teacher_group)

        association_group = QVBoxLayout()
        self.material_associations_label = QLabel(self.tr("Associations"))
        association_group.addWidget(self.material_associations_label)
        self.material_assoc_type = QComboBox()
        self.material_assoc_type.addItem(self.tr("Program"), "program")
        self.material_assoc_type.addItem(self.tr("Discipline"), "discipline")
        self.material_assoc_type.addItem(self.tr("Topic"), "topic")
        self.material_assoc_type.addItem(self.tr("Lesson"), "lesson")
        self.material_assoc_available = QListWidget()
        self.material_assoc_assigned = QListWidget()
        assoc_btns = QHBoxLayout()
        self.material_assoc_add = QPushButton(self.tr("Link ->"))
        self.material_assoc_remove = QPushButton(self.tr("<- Unlink"))
        assoc_btns.addWidget(self.material_assoc_add)
        assoc_btns.addWidget(self.material_assoc_remove)
        association_group.addWidget(self.material_assoc_type)
        self.material_assoc_available_label = QLabel(self.tr("Available"))
        association_group.addWidget(self.material_assoc_available_label)
        association_group.addWidget(self.material_assoc_available)
        association_group.addLayout(assoc_btns)
        self.material_assoc_linked_label = QLabel(self.tr("Linked"))
        association_group.addWidget(self.material_assoc_linked_label)
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
        self.material_open.clicked.connect(self._open_material_file)
        self.material_show.clicked.connect(self._show_material_folder)
        self.material_copy.clicked.connect(self._copy_material_file)
        self.material_attach_existing.clicked.connect(self._attach_existing_material_file)
        return tab

    def _build_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        storage_group = QWidget()
        storage_layout = QHBoxLayout(storage_group)
        self.materials_location_label = QLabel(self.tr("Materials location"))
        self.materials_location = QLineEdit()
        self.materials_location.setReadOnly(True)
        self.materials_location_browse = QPushButton(self.tr("Change..."))
        storage_layout.addWidget(self.materials_location_label)
        storage_layout.addWidget(self.materials_location, 1)
        storage_layout.addWidget(self.materials_location_browse)
        layout.addWidget(storage_group)

        db_group = QWidget()
        db_layout = QHBoxLayout(db_group)
        self.db_export = QPushButton(self.tr("Export database"))
        self.db_import = QPushButton(self.tr("Import database"))
        db_layout.addWidget(self.db_export)
        db_layout.addWidget(self.db_import)
        db_layout.addStretch(1)
        layout.addWidget(db_group)
        layout.addStretch(1)

        self.materials_location_browse.clicked.connect(self._change_materials_location)
        self.db_export.clicked.connect(self._export_database)
        self.db_import.clicked.connect(self._import_database)

        self._refresh_settings()
        return tab

    def _refresh_all(self) -> None:
        self._refresh_teachers()
        self._refresh_programs()
        self._refresh_disciplines()
        self._refresh_topics()
        self._refresh_lessons()
        self._refresh_lesson_types()
        self._refresh_questions()
        self._refresh_materials()

    # Teachers
    def _refresh_teachers(self) -> None:
        self.teachers_table.setRowCount(0)
        for teacher in self.controller.get_teachers():
            row = self.teachers_table.rowCount()
            self.teachers_table.insertRow(row)
            self.teachers_table.setItem(row, 0, QTableWidgetItem(teacher.full_name))
            self.teachers_table.setItem(row, 1, QTableWidgetItem(teacher.military_rank or ""))
            self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher.position or ""))
            self.teachers_table.setItem(row, 3, QTableWidgetItem(teacher.department or ""))
            self.teachers_table.setItem(row, 4, QTableWidgetItem(teacher.email or ""))
            self.teachers_table.setItem(row, 5, QTableWidgetItem(teacher.phone or ""))
            self.teachers_table.item(row, 0).setData(Qt.UserRole, teacher)

    def _add_teacher(self) -> None:
        dialog = TeacherDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        teacher = dialog.get_teacher()
        if not teacher.full_name:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Full name is required."))
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
        for discipline in self._filtered_disciplines():
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
        dialog = DisciplineDialog(discipline, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_discipline(dialog.get_discipline())
        self._refresh_disciplines()

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
        dialog = TopicDialog(topic, self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_topic(dialog.get_topic())
        self._refresh_topics()

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
        dialog = LessonDialog(lesson_types=self.controller.get_lesson_types(), parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        lesson = dialog.get_lesson()
        if not lesson.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Lesson title is required."))
            return
        self.controller.add_lesson(lesson)
        self._refresh_lessons()

    def _edit_lesson(self) -> None:
        lesson = self._current_entity(self.lessons_table)
        if not lesson:
            return
        dialog = LessonDialog(lesson, self.controller.get_lesson_types(), self)
        if dialog.exec() != QDialog.Accepted:
            return
        self.controller.update_lesson(dialog.get_lesson())
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

    # Lesson types
    def _refresh_lesson_types(self) -> None:
        self.lesson_types_table.setRowCount(0)
        for lesson_type in self.controller.get_lesson_types():
            row = self.lesson_types_table.rowCount()
            self.lesson_types_table.insertRow(row)
            self.lesson_types_table.setItem(row, 0, QTableWidgetItem(lesson_type.name))
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
            self.questions_table.setItem(row, 1, QTableWidgetItem(str(question.difficulty_level)))
            self.questions_table.item(row, 0).setData(Qt.UserRole, question)

    def _filtered_disciplines(self):
        program = self._current_entity(self.programs_table)
        if program:
            return self.controller.get_program_disciplines(program.id)
        return self.controller.get_disciplines()

    def _filtered_topics(self):
        discipline = self._current_entity(self.disciplines_table)
        if discipline:
            return self.controller.get_discipline_topics(discipline.id)
        program = self._current_entity(self.programs_table)
        if program:
            return self.controller.get_program_topics(program.id)
        return self.controller.get_topics()

    def _filtered_lessons(self):
        topic = self._current_entity(self.topics_table)
        if topic:
            return self.controller.get_topic_lessons(topic.id)
        discipline = self._current_entity(self.disciplines_table)
        if discipline:
            topics = self.controller.get_discipline_topics(discipline.id)
            return self._lessons_for_topics(topics)
        program = self._current_entity(self.programs_table)
        if program:
            topics = self.controller.get_program_topics(program.id)
            return self._lessons_for_topics(topics)
        return self.controller.get_lessons()

    def _filtered_questions(self):
        lesson = self._current_entity(self.lessons_table)
        if lesson:
            return self.controller.get_lesson_questions(lesson.id)
        topic = self._current_entity(self.topics_table)
        if topic:
            lessons = self.controller.get_topic_lessons(topic.id)
            return self._questions_for_lessons(lessons)
        discipline = self._current_entity(self.disciplines_table)
        if discipline:
            topics = self.controller.get_discipline_topics(discipline.id)
            lessons = self._lessons_for_topics(topics)
            return self._questions_for_lessons(lessons)
        program = self._current_entity(self.programs_table)
        if program:
            topics = self.controller.get_program_topics(program.id)
            lessons = self._lessons_for_topics(topics)
            return self._questions_for_lessons(lessons)
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

    # Materials
    def _refresh_materials(self) -> None:
        self.materials_table.setRowCount(0)
        for material in self.controller.get_materials():
            row = self.materials_table.rowCount()
            self.materials_table.insertRow(row)
            self.materials_table.setItem(row, 0, QTableWidgetItem(material.title))
            self.materials_table.setItem(row, 1, QTableWidgetItem(self._translate_material_type(material.material_type)))
            filename = material.original_filename or material.file_name or ""
            self.materials_table.setItem(row, 2, QTableWidgetItem(filename))
            self.materials_table.item(row, 0).setData(Qt.UserRole, material)
        self._refresh_material_assignments()

    def _add_material(self) -> None:
        dialog = MaterialDialog(parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        material = dialog.get_material()
        if not material.title:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Material title is required."))
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
        except Exception as exc:
            selection = self._prompt_material_location()
            if not selection:
                QMessageBox.warning(self, self.tr("Import error"), f"{exc}\n\n{self._database_diagnostics()}")
                return
            program_id, discipline_id = selection
            try:
                updated = self.controller.attach_material_file_with_context(
                    material, path, program_id, discipline_id
                )
            except Exception as inner_exc:
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
        except Exception as exc:
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
        if not self.file_storage.open_file(material.relative_path):
            QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

    def _show_material_folder(self) -> None:
        material = self._current_entity(self.materials_table)
        if not material:
            return
        if not material.relative_path:
            QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
            return
        if not self.file_storage.show_in_folder(material.relative_path):
            QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

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
        if not self.file_storage.copy_file_as(material.relative_path, path):
            QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

    def _database_diagnostics(self) -> str:
        import sqlite3

        path = self.controller.db.db_path
        status = "unknown"
        try:
            con = sqlite3.connect(path)
            rows = con.execute("PRAGMA integrity_check;").fetchall()
            status = ", ".join(row[0] for row in rows)
        except Exception as exc:
            status = f"error: {exc}"
        finally:
            try:
                con.close()
            except Exception:
                pass
        return f"DB: {path}\nIntegrity: {status}"

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

    def _refresh_settings(self) -> None:
        self.materials_location.setText(str(self.file_storage.files_root))

    def _change_materials_location(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select materials folder"),
            str(self.file_storage.files_root),
        )
        if not path:
            return
        new_root = Path(path)
        try:
            self.file_storage.move_storage(self.controller.db, new_root)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        self._refresh_settings()

    def _export_database(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export database"),
            "education.db",
            self.tr("Database (*.db);;All files (*)"),
        )
        if not path:
            return
        try:
            from pathlib import Path as _Path
            import shutil

            shutil.copyfile(self.controller.db.db_path, _Path(path))
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(self, self.tr("Export database"), self.tr("Database exported."))

    def _import_database(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import database"),
            "",
            self.tr("Database (*.db);;All files (*)"),
        )
        if not path:
            return
        if QMessageBox.question(
            self,
            self.tr("Confirm"),
            self.tr("Replace the current database with the selected file?"),
        ) != QMessageBox.Yes:
            return
        try:
            from pathlib import Path as _Path
            import shutil

            shutil.copyfile(_Path(path), self.controller.db.db_path)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(
            self,
            self.tr("Import database"),
            self.tr("Database imported. Restart the app."),
        )

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

    def _on_import_curriculum(self) -> None:
        dialog = ImportCurriculumDialog(self.controller, self)
        if dialog.exec() != QDialog.Accepted:
            return
        program_id, discipline_id, new_name, raw_text, parsed_topics, file_paths = dialog.get_payload()

        if file_paths:
            totals = {"topics": 0, "lessons": 0, "questions": 0}
            errors = []
            from ..services.import_service import extract_text_from_file, parse_curriculum_text, program_discipline_from_filename

            for path in file_paths:
                try:
                    content = extract_text_from_file(path)
                    topics = parse_curriculum_text(content)
                    program_name, discipline_name = program_discipline_from_filename(path)
                    if not discipline_name:
                        discipline_name = program_name
                    t_added, l_added, q_added = import_curriculum_structure_by_names(
                        self.controller.db,
                        program_name,
                        discipline_name,
                        topics,
                    )
                    totals["topics"] += t_added
                    totals["lessons"] += l_added
                    totals["questions"] += q_added
                except Exception as exc:
                    errors.append(f"{path}: {exc}")

            if errors:
                QMessageBox.warning(self, self.tr("Import error"), "\n".join(errors))
            QMessageBox.information(
                self,
                self.tr("Import complete"),
                self.tr("Added topics: {0}\nAdded lessons: {1}\nAdded questions: {2}").format(
                    totals["topics"], totals["lessons"], totals["questions"]
                ),
            )
            self._refresh_all()
            return

        if not raw_text.strip():
            QMessageBox.warning(self, self.tr("Import error"), self.tr("No input text provided."))
            return
        if parsed_topics is None:
            try:
                from ..services.import_service import parse_curriculum_text

                parsed_topics = parse_curriculum_text(raw_text)
            except Exception as exc:
                QMessageBox.warning(self, self.tr("Import error"), str(exc))
                return
        try:
            topics_added, lessons_added, questions_added = import_curriculum_structure(
                self.controller.db,
                program_id,
                discipline_id,
                new_name,
                parsed_topics,
            )
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(
            self,
            self.tr("Import complete"),
            self.tr("Added topics: {0}\nAdded lessons: {1}\nAdded questions: {2}").format(
                topics_added, lessons_added, questions_added
            ),
        )
        self._refresh_all()

    def _on_import_teachers(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import teachers"),
            "",
            self.tr("Word documents (*.docx);;All files (*)"),
        )
        if not path:
            return
        try:
            added, skipped = import_teachers_from_docx(self.controller.db, path)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(
            self,
            self.tr("Import complete"),
            self.tr("Added teachers: {0}\nSkipped: {1}").format(added, skipped),
        )
        self._refresh_teachers()

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

    def retranslate_ui(self, *_args) -> None:
        self.setWindowTitle(self.tr("Admin Panel"))
        self.menu_bar.clear()
        import_menu = self.menu_bar.addMenu(self.tr("Import"))
        self.import_curriculum_action = import_menu.addAction(self.tr("Import curriculum structure"))
        self.import_curriculum_action.triggered.connect(self._on_import_curriculum)
        self.import_teachers_action = import_menu.addAction(self.tr("Import teachers from DOCX"))
        self.import_teachers_action.triggered.connect(self._on_import_teachers)
        self.tabs.setTabText(0, self.tr("Teachers"))
        self.tabs.setTabText(1, self.tr("Programs"))
        self.tabs.setTabText(2, self.tr("Disciplines"))
        self.tabs.setTabText(3, self.tr("Topics"))
        self.tabs.setTabText(4, self.tr("Lessons"))
        self.tabs.setTabText(5, self.tr("Lesson types"))
        self.tabs.setTabText(6, self.tr("Questions"))
        self.tabs.setTabText(7, self.tr("Materials"))
        self.tabs.setTabText(8, self.tr("Settings"))

        self.teachers_table.setHorizontalHeaderLabels(
            [
                self.tr("Full name"),
                self.tr("Military rank"),
                self.tr("Position"),
                self.tr("Department"),
                self.tr("Email"),
                self.tr("Phone"),
            ]
        )
        self.programs_table.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Level"), self.tr("Duration")])
        self.disciplines_table.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Order")])
        self.topics_table.setHorizontalHeaderLabels([self.tr("Title"), self.tr("Order")])
        self.lessons_table.setHorizontalHeaderLabels(
            [self.tr("Title"), self.tr("Total hours"), self.tr("Type"), self.tr("Order")]
        )
        self.lesson_types_table.setHorizontalHeaderLabels([self.tr("Name")])
        self.questions_table.setHorizontalHeaderLabels([self.tr("Question"), self.tr("Difficulty")])
        self.materials_table.setHorizontalHeaderLabels([self.tr("Title"), self.tr("Type"), self.tr("File")])

        self.teacher_add.setText(self.tr("Add"))
        self.teacher_edit.setText(self.tr("Edit"))
        self.teacher_delete.setText(self.tr("Delete"))
        self.program_add.setText(self.tr("Add"))
        self.program_edit.setText(self.tr("Edit"))
        self.program_delete.setText(self.tr("Delete"))
        self.program_disciplines_label.setText(self.tr("Program disciplines"))
        self.program_discipline_add.setText(self.tr("Add ->"))
        self.program_discipline_remove.setText(self.tr("<- Remove"))
        self.program_discipline_remove.setText(self.tr("<- Remove"))

        self.discipline_add.setText(self.tr("Add"))
        self.discipline_edit.setText(self.tr("Edit"))
        self.discipline_delete.setText(self.tr("Delete"))
        self.discipline_topics_label.setText(self.tr("Discipline topics"))
        self.discipline_topic_add.setText(self.tr("Add ->"))
        self.discipline_topic_remove.setText(self.tr("<- Remove"))
        self.discipline_topic_remove.setText(self.tr("<- Remove"))

        self.topic_add.setText(self.tr("Add"))
        self.topic_edit.setText(self.tr("Edit"))
        self.topic_delete.setText(self.tr("Delete"))
        self.topic_lessons_label.setText(self.tr("Topic lessons"))
        self.topic_lesson_add.setText(self.tr("Add ->"))
        self.topic_lesson_remove.setText(self.tr("<- Remove"))
        self.topic_lesson_remove.setText(self.tr("<- Remove"))
        self.topic_materials_label.setText(self.tr("Topic materials"))
        self.topic_material_add.setText(self.tr("Add ->"))
        self.topic_material_remove.setText(self.tr("<- Remove"))

        self.lesson_add.setText(self.tr("Add"))
        self.lesson_edit.setText(self.tr("Edit"))
        self.lesson_delete.setText(self.tr("Delete"))
        self.lesson_questions_label.setText(self.tr("Lesson questions"))
        self.lesson_question_add.setText(self.tr("Add ->"))
        self.lesson_question_remove.setText(self.tr("<- Remove"))
        self.lesson_question_remove.setText(self.tr("<- Remove"))
        self.lesson_materials_label.setText(self.tr("Lesson materials"))
        self.lesson_material_add.setText(self.tr("Add ->"))
        self.lesson_material_remove.setText(self.tr("<- Remove"))

        self.lesson_type_add.setText(self.tr("Add"))
        self.lesson_type_edit.setText(self.tr("Edit"))
        self.lesson_type_delete.setText(self.tr("Delete"))

        self.question_add.setText(self.tr("Add"))
        self.question_edit.setText(self.tr("Edit"))
        self.question_delete.setText(self.tr("Delete"))

        self.material_add.setText(self.tr("Add"))
        self.material_edit.setText(self.tr("Edit"))
        self.material_delete.setText(self.tr("Delete"))
        self.material_attach.setText(self.tr("Attach File"))
        self.material_attach_existing.setText(self.tr("Attach existing file"))
        self.material_open.setText(self.tr("Open file"))
        self.material_show.setText(self.tr("Show in folder"))
        self.material_copy.setText(self.tr("Copy file as..."))
        self.material_teachers_label.setText(self.tr("Material teachers"))
        self.material_teachers_available_label.setText(self.tr("Available"))
        self.material_teachers_assigned_label.setText(self.tr("Assigned"))
        self.material_teacher_add.setText(self.tr("Add ->"))
        self.material_teacher_remove.setText(self.tr("<- Remove"))
        self.material_teacher_remove.setText(self.tr("<- Remove"))
        self.material_associations_label.setText(self.tr("Associations"))
        self.material_assoc_available_label.setText(self.tr("Available"))
        self.material_assoc_linked_label.setText(self.tr("Linked"))
        self.material_assoc_add.setText(self.tr("Link ->"))
        self.material_assoc_remove.setText(self.tr("<- Unlink"))
        self.material_assoc_remove.setText(self.tr("<- Unlink"))

        self.material_assoc_type.setItemText(0, self.tr("Program"))
        self.material_assoc_type.setItemText(1, self.tr("Discipline"))
        self.material_assoc_type.setItemText(2, self.tr("Topic"))
        self.material_assoc_type.setItemText(3, self.tr("Lesson"))

        self.materials_location_label.setText(self.tr("Materials location"))
        self.materials_location_browse.setText(self.tr("Change..."))
        self.db_export.setText(self.tr("Export database"))
        self.db_import.setText(self.tr("Import database"))
