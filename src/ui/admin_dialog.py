"""Admin management dialog."""
from PySide6.QtCore import Qt, QSettings, QByteArray, QSize, QRect
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
    QRadioButton,
    QSplitter,
    QMenuBar,
    QAbstractItemView,
    QLineEdit,
    QDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
    QAbstractScrollArea,
    QMenu,
    QGroupBox,
    QApplication,
    QCheckBox,
    QInputDialog,
    QSizePolicy,
)
import json
import zlib
from PySide6.QtCore import QProcess
import sys
import sqlite3
from PySide6.QtGui import QTextDocument, QBrush, QColor
from pathlib import Path
from ..controllers.admin_controller import AdminController
from ..controllers.main_controller import MainController
from ..models.database import Database
from ..models.entities import (
    EducationalProgram,
    Discipline,
    Topic,
    Lesson,
    Question,
    MethodicalMaterial,
    MaterialType,
    LessonType,
)
from ..services.i18n import I18nManager
from ..services.app_paths import (
    get_settings_dir,
    get_translations_dir,
    get_app_base_dir,
    resolve_app_path,
    make_relative_to_app,
)
from ..ui.dialogs import (
    PasswordDialog,
    TeacherDialog,
    ProgramDialog,
    DisciplineDialog,
    TopicDialog,
    LessonDialog,
    LessonTypeDialog,
    MaterialTypeDialog,
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

    def __init__(self, database: Database, i18n: I18nManager, settings: QSettings, parent=None):
        super().__init__(parent)
        self.controller = AdminController(database)
        self.i18n = i18n
        self.settings = settings
        self.bootstrap_settings = QSettings()
        self.file_storage = FileStorageManager()
        desired_db_path = self.bootstrap_settings.value("app/db_path", "")
        if desired_db_path:
            resolved = resolve_app_path(desired_db_path)
            if str(self.controller.db.db_path) != str(resolved):
                self.controller = AdminController(Database(str(resolved)))
        self.setWindowTitle(self.tr("Admin Panel"))
        self.resize(1200, 760)
        if not self._authorize():
            self.reject()
            return
        self._build_ui()
        self._refresh_all()
        self.showMaximized()
        self.i18n.language_changed.connect(self.retranslate_ui)

    def _authorize(self) -> bool:
        while True:
            dialog = PasswordDialog(
                self,
                title=self.tr("Admin Access"),
                label=self.tr("Enter admin password:"),
            )
            if dialog.exec() != QDialog.Accepted:
                return False
            if self.controller.verify_password(dialog.get_password()):
                return True
            QMessageBox.warning(self, self.tr("Access denied"), self.tr("Invalid admin password."))

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        menu_bar = QMenuBar()
        app_menu = menu_bar.addMenu(self.tr("Application"))
        action_about = app_menu.addAction(self.tr("About"))
        action_restart = app_menu.addAction(self.tr("Restart application"))
        action_exit = app_menu.addAction(self.tr("Exit application"))
        action_about.triggered.connect(self._show_about)
        action_restart.triggered.connect(self._restart_application)
        action_exit.triggered.connect(self._close_application)
        layout.addWidget(menu_bar)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self._build_structure_tab(), self.tr("Structure"))
        self.tabs.addTab(self._build_materials_tab(), self.tr("Materials"))
        self.tabs.addTab(self._build_teachers_tab(), self.tr("Teachers"))
        self.tabs.addTab(self._build_sync_tab(), self.tr("Synchronization"))
        self.tabs.addTab(self._build_settings_tab(), self.tr("Settings"))
        self._apply_word_wrap()

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
        self.teachers_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.teachers_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self.teachers_table, pos, self._edit_teacher, self._delete_teacher)
        )
        self.teachers_table.itemChanged.connect(self._on_teacher_item_changed)
        layout.addWidget(self.teachers_table)
        btn_layout = QHBoxLayout()
        self.teacher_add = QPushButton(self.tr("Add"))
        self.teacher_edit = QPushButton(self.tr("Edit"))
        self.teacher_delete = QPushButton(self.tr("Delete"))
        self.teacher_import = QPushButton(self.tr("Import teachers from DOCX"))
        btn_layout.addWidget(self.teacher_add)
        btn_layout.addWidget(self.teacher_edit)
        btn_layout.addWidget(self.teacher_delete)
        btn_layout.addWidget(self.teacher_import)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        disciplines_group = QWidget()
        disciplines_layout = QHBoxLayout(disciplines_group)
        self.teacher_disciplines_label = QLabel(self.tr("Assigned disciplines"))
        disciplines_layout.addWidget(self.teacher_disciplines_label)
        self.teacher_disciplines_available = QListWidget()
        self.teacher_disciplines_assigned = QListWidget()
        mid_layout = QVBoxLayout()
        self.teacher_discipline_add = QPushButton(self.tr("Add ->"))
        self.teacher_discipline_remove = QPushButton(self.tr("<- Remove"))
        mid_layout.addStretch(1)
        mid_layout.addWidget(self.teacher_discipline_add)
        mid_layout.addWidget(self.teacher_discipline_remove)
        mid_layout.addStretch(1)
        disciplines_layout.addWidget(self.teacher_disciplines_available)
        disciplines_layout.addLayout(mid_layout)
        disciplines_layout.addWidget(self.teacher_disciplines_assigned)
        layout.addWidget(disciplines_group)

        self.teacher_add.clicked.connect(self._add_teacher)
        self.teacher_edit.clicked.connect(self._edit_teacher)
        self.teacher_delete.clicked.connect(self._delete_teacher)
        self.teacher_import.clicked.connect(self._on_import_teachers)
        self.teachers_table.itemSelectionChanged.connect(self._refresh_teacher_disciplines)
        self.teacher_discipline_add.clicked.connect(self._add_discipline_to_teacher)
        self.teacher_discipline_remove.clicked.connect(self._remove_discipline_from_teacher)
        return tab

    def _apply_word_wrap(self) -> None:
        table_names = [
            "teachers_table",
            "lesson_types_table",
            "material_types_table",
            "materials_table",
            "questions_table",
            "lessons_table",
            "topics_table",
            "disciplines_table",
            "programs_table",
        ]
        list_names = [
            "program_disciplines_assigned",
            "program_disciplines_available",
            "discipline_topics_available",
            "discipline_topics_assigned",
            "topic_lessons_available",
            "topic_lessons_assigned",
            "topic_materials_available",
            "topic_materials_assigned",
            "lesson_questions_available",
            "lesson_questions_assigned",
            "lesson_materials_available",
            "lesson_materials_assigned",
            "teacher_disciplines_available",
            "teacher_disciplines_assigned",
            "material_teachers_available",
            "material_teachers_assigned",
            "material_assoc_available",
            "material_assoc_assigned",
        ]
        tree_names = ["structure_tree"]

        for name in table_names:
            table = getattr(self, name, None)
            if not table:
                continue
            table.setWordWrap(True)
            table.setTextElideMode(Qt.ElideNone)
            table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            if name == "materials_table":
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
            else:
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                table.horizontalHeader().setStretchLastSection(True)
                table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        for name in list_names:
            widget = getattr(self, name, None)
            if not widget:
                continue
            widget.setWordWrap(True)
            widget.setTextElideMode(Qt.ElideNone)
            widget.setUniformItemSizes(False)

        for name in tree_names:
            tree = getattr(self, name, None)
            if not tree:
                continue
            tree.setWordWrap(True)
            tree.setUniformRowHeights(False)
            tree.setTextElideMode(Qt.ElideNone)
            tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        for name in [
            "teachers_table",
            "lesson_types_table",
            "questions_table",
            "lessons_table",
            "topics_table",
            "disciplines_table",
            "programs_table",
        ]:
            table = getattr(self, name, None)
            if table:
                table.resizeRowsToContents()
                table.resizeColumnsToContents()
        tree = getattr(self, "structure_tree", None)
        if tree:
            self._resize_structure_tree()
        for name in [
            "program_disciplines_assigned",
            "program_disciplines_available",
            "discipline_topics_available",
            "discipline_topics_assigned",
            "topic_lessons_available",
            "topic_lessons_assigned",
            "topic_materials_available",
            "topic_materials_assigned",
            "lesson_questions_available",
            "lesson_questions_assigned",
            "lesson_materials_available",
            "lesson_materials_assigned",
            "material_teachers_available",
            "material_teachers_assigned",
            "material_assoc_available",
            "material_assoc_assigned",
        ]:
            widget = getattr(self, name, None)
            if widget:
                widget.doItemsLayout()

    def _build_structure_tab(self) -> QWidget:
        tab = QWidget()
        splitter = QSplitter(Qt.Horizontal)

        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels([self.tr("Structure")])
        self.structure_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.structure_tree.setItemDelegateForColumn(0, _WrapItemDelegate(self.structure_tree))
        # Keep splitter responsive; avoid sizing the tree to its content width.
        self.structure_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.structure_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.structure_tree.customContextMenuRequested.connect(self._show_structure_context_menu)
        self.structure_tree.itemSelectionChanged.connect(self._on_structure_selection_changed)
        self.structure_tree.itemDoubleClicked.connect(lambda *_args: self._edit_structure_selected())
        splitter.addWidget(self.structure_tree)

        details = QWidget()
        details_layout = QVBoxLayout(details)
        self.structure_title = QLabel(self.tr("Select an item"))
        self.structure_details = QLabel("")
        self.structure_details.setWordWrap(True)
        details_layout.addWidget(self.structure_title)
        details_layout.addWidget(self.structure_details)

        btn_row = QHBoxLayout()
        self.structure_add_program = QPushButton(self.tr("Add program"))
        self.structure_add_discipline = QPushButton(self.tr("Add discipline"))
        self.structure_add_topic = QPushButton(self.tr("Add topic"))
        self.structure_add_lesson = QPushButton(self.tr("Add lesson"))
        self.structure_add_question = QPushButton(self.tr("Add question"))
        self.structure_import = QPushButton(self.tr("Import curriculum structure"))
        self.structure_refresh = QPushButton(self.tr("Refresh"))
        self.structure_edit = QPushButton(self.tr("Edit"))
        self.structure_delete = QPushButton(self.tr("Delete"))
        self.structure_duplicate = QPushButton(self.tr("Duplicate"))
        self.structure_copy = QPushButton(self.tr("Copy"))
        btn_row.addWidget(self.structure_add_program)
        btn_row.addWidget(self.structure_add_discipline)
        btn_row.addWidget(self.structure_add_topic)
        btn_row.addWidget(self.structure_add_lesson)
        btn_row.addWidget(self.structure_add_question)
        btn_row.addWidget(self.structure_import)
        btn_row.addWidget(self.structure_refresh)
        btn_row.addWidget(self.structure_edit)
        btn_row.addWidget(self.structure_delete)
        btn_row.addWidget(self.structure_duplicate)
        btn_row.addWidget(self.structure_copy)
        btn_row.addStretch(1)
        details_layout.addLayout(btn_row)

        materials_group = QWidget()
        materials_layout = QVBoxLayout(materials_group)
        self.materials_table = QTableWidget(0, 4)
        self.materials_table.setHorizontalHeaderLabels(
            [self.tr("Title"), self.tr("Type"), self.tr("File"), self.tr("Authors")]
        )
        # Stretch columns to available space so the table can shrink/expand with the splitter.
        self.materials_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.materials_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.materials_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.materials_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.materials_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.materials_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self.materials_table, pos, self._edit_material, self._delete_material)
        )
        materials_layout.addWidget(self.materials_table)

        materials_btns = QHBoxLayout()
        self.material_add = QPushButton(self.tr("Add"))
        self.material_edit = QPushButton(self.tr("Edit"))
        self.material_delete = QPushButton(self.tr("Delete"))
        self.material_open = QPushButton(self.tr("Open file"))
        self.material_show = QPushButton(self.tr("Show in folder"))
        self.material_copy = QPushButton(self.tr("Copy file as..."))
        materials_btns.addWidget(self.material_add)
        materials_btns.addWidget(self.material_edit)
        materials_btns.addWidget(self.material_delete)
        materials_btns.addWidget(self.material_open)
        materials_btns.addWidget(self.material_show)
        materials_btns.addWidget(self.material_copy)
        materials_btns.addStretch(1)
        materials_layout.addLayout(materials_btns)

        details_layout.addWidget(QLabel(self.tr("Materials")))
        details_layout.addWidget(materials_group)
        details_layout.addStretch(1)
        splitter.addWidget(details)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout(tab)
        layout.addWidget(splitter)

        self.structure_add_program.clicked.connect(self._add_structure_program)
        self.structure_add_discipline.clicked.connect(self._add_structure_discipline)
        self.structure_add_topic.clicked.connect(self._add_structure_topic)
        self.structure_add_lesson.clicked.connect(self._add_structure_lesson)
        self.structure_add_question.clicked.connect(self._add_structure_question)
        self.structure_import.clicked.connect(self._on_import_curriculum)
        self.structure_refresh.clicked.connect(self._refresh_structure_with_reorder)
        self.structure_edit.clicked.connect(self._edit_structure_selected)
        self.structure_delete.clicked.connect(self._delete_structure_selected)
        self.structure_duplicate.clicked.connect(self._duplicate_structure_selected)
        self.structure_copy.clicked.connect(self._copy_structure_selected)
        self.material_add.clicked.connect(self._add_material)
        self.material_edit.clicked.connect(self._edit_material)
        self.material_delete.clicked.connect(self._delete_material)
        self.material_open.clicked.connect(self._open_material_file)
        self.material_show.clicked.connect(self._show_material_folder)
        self.material_copy.clicked.connect(self._copy_material_file)
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

    def _build_questions_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.questions_table = QTableWidget(0, 1)
        self.questions_table.setHorizontalHeaderLabels([self.tr("Question")])
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
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        self.materials_group = QGroupBox(self.tr("Materials"))
        materials_layout = QVBoxLayout(self.materials_group)
        self.material_types_table = QTableWidget(0, 1)
        self.material_types_table.setHorizontalHeaderLabels([self.tr("Name")])
        self.material_types_table.horizontalHeader().setStretchLastSection(True)
        self.material_types_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.material_types_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.material_types_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.material_types_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(
                self.material_types_table, pos, self._edit_material_type, self._delete_material_type
            )
        )
        materials_layout.addWidget(self.material_types_table)
        btn_layout = QHBoxLayout()
        self.material_type_add = QPushButton(self.tr("Add"))
        self.material_type_edit = QPushButton(self.tr("Edit"))
        self.material_type_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.material_type_add)
        btn_layout.addWidget(self.material_type_edit)
        btn_layout.addWidget(self.material_type_delete)
        btn_layout.addStretch(1)
        materials_layout.addLayout(btn_layout)
        splitter.addWidget(self.materials_group)

        self.lesson_types_group = QGroupBox(self.tr("Lesson types"))
        lesson_types_layout = QVBoxLayout(self.lesson_types_group)
        self.lesson_types_table = QTableWidget(0, 2)
        self.lesson_types_table.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Synonyms")])
        self.lesson_types_table.horizontalHeader().setStretchLastSection(True)
        self.lesson_types_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.lesson_types_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.lesson_types_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lesson_types_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(
                self.lesson_types_table, pos, self._edit_lesson_type, self._delete_lesson_type
            )
        )
        lesson_types_layout.addWidget(self.lesson_types_table)
        btn_layout = QHBoxLayout()
        self.lesson_type_add = QPushButton(self.tr("Add"))
        self.lesson_type_edit = QPushButton(self.tr("Edit"))
        self.lesson_type_delete = QPushButton(self.tr("Delete"))
        btn_layout.addWidget(self.lesson_type_add)
        btn_layout.addWidget(self.lesson_type_edit)
        btn_layout.addWidget(self.lesson_type_delete)
        btn_layout.addStretch(1)
        lesson_types_layout.addLayout(btn_layout)
        splitter.addWidget(self.lesson_types_group)

        self.material_type_add.clicked.connect(self._add_material_type)
        self.material_type_edit.clicked.connect(self._edit_material_type)
        self.material_type_delete.clicked.connect(self._delete_material_type)
        self.lesson_type_add.clicked.connect(self._add_lesson_type)
        self.lesson_type_edit.clicked.connect(self._edit_lesson_type)
        self.lesson_type_delete.clicked.connect(self._delete_lesson_type)

        self._refresh_material_types()
        self._refresh_lesson_types()
        return tab

    def _build_sync_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.sync_mode_panel = QWidget()
        mode_layout = QHBoxLayout(self.sync_mode_panel)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(6)
        self.sync_mode_label = QLabel(self.tr("Mode:"))
        mode_layout.addWidget(self.sync_mode_label)
        self.sync_mode_import = QRadioButton(self.tr("Import program fully"))
        self.sync_mode_sync = QRadioButton(self.tr("Synchronize with existing program"))
        self.sync_mode_sync.setChecked(True)
        mode_layout.addWidget(self.sync_mode_import)
        mode_layout.addWidget(self.sync_mode_sync)
        mode_layout.addStretch(1)
        self.sync_mode_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.sync_mode_panel.setMaximumHeight(self.fontMetrics().height() + 10)
        self.sync_mode_panel.setVisible(False)
        layout.addWidget(self.sync_mode_panel)

        self.sync_import_panel = QWidget()
        import_layout = QHBoxLayout(self.sync_import_panel)
        import_layout.setContentsMargins(0, 0, 0, 0)
        import_layout.setSpacing(6)
        self.sync_import_label = QLabel(self.tr("Program to import:"))
        import_layout.addWidget(self.sync_import_label)
        self.sync_import_program = QComboBox()
        import_layout.addWidget(self.sync_import_program, 1)
        self.sync_import_apply = QPushButton(self.tr("Import program"))
        import_layout.addWidget(self.sync_import_apply)
        self.sync_import_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.sync_import_panel.setMaximumHeight(self.fontMetrics().height() + 14)
        self.sync_import_panel.setVisible(False)
        layout.addWidget(self.sync_import_panel)

        self.sync_start = QPushButton(self.tr("Start synchronization"))
        self.sync_status = QLabel("")
        self.sync_status.setWordWrap(True)
        self.sync_status.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.sync_status.setMaximumHeight(self.fontMetrics().height() * 2 + 6)
        status_row = QHBoxLayout()
        status_row.addWidget(self.sync_status)
        status_row.addStretch(1)
        layout.addWidget(self.sync_start)
        layout.addLayout(status_row)

        self.sync_panel = QWidget()
        panel_layout = QVBoxLayout(self.sync_panel)

        mapping_row = QHBoxLayout()
        self.sync_target_label = QLabel(self.tr("Target program:"))
        self.sync_target_program_combo = QComboBox()
        self.sync_source_label = QLabel(self.tr("Source program:"))
        self.sync_source_program_combo = QComboBox()
        mapping_row.addWidget(self.sync_target_label)
        mapping_row.addWidget(self.sync_target_program_combo, 1)
        mapping_row.addSpacing(10)
        mapping_row.addWidget(self.sync_source_label)
        mapping_row.addWidget(self.sync_source_program_combo, 1)
        panel_layout.addLayout(mapping_row)

        types_row = QHBoxLayout()
        self.sync_type_program = QCheckBox(self.tr("Program"))
        self.sync_type_discipline = QCheckBox(self.tr("Discipline"))
        self.sync_type_topic = QCheckBox(self.tr("Topic"))
        self.sync_type_lesson = QCheckBox(self.tr("Lesson"))
        self.sync_type_question = QCheckBox(self.tr("Question"))
        self.sync_type_materials = QCheckBox(self.tr("Materials"))
        for cb in [
            self.sync_type_program,
            self.sync_type_discipline,
            self.sync_type_topic,
            self.sync_type_lesson,
            self.sync_type_question,
            self.sync_type_materials,
        ]:
            cb.setChecked(True)
            types_row.addWidget(cb)
        types_row.addStretch(1)
        panel_layout.addLayout(types_row)

        self.sync_hide_identical = QCheckBox(self.tr("Hide identical elements"))
        panel_layout.addWidget(self.sync_hide_identical)

        splitter = QSplitter(Qt.Horizontal)
        self.sync_left_tree = QTreeWidget()
        self.sync_left_tree.setHeaderLabels([self.tr("Current structure")])
        self.sync_left_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.sync_left_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.sync_left_tree.setWordWrap(True)
        self.sync_left_tree.setTextElideMode(Qt.ElideNone)
        self.sync_left_tree.setUniformRowHeights(False)
        self.sync_left_tree.setItemDelegateForColumn(0, _WrapItemDelegate(self.sync_left_tree))
        self.sync_right_tree = QTreeWidget()
        self.sync_right_tree.setHeaderLabels([self.tr("Source structure")])
        self.sync_right_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.sync_right_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.sync_right_tree.setWordWrap(True)
        self.sync_right_tree.setTextElideMode(Qt.ElideNone)
        self.sync_right_tree.setUniformRowHeights(False)
        self.sync_right_tree.setItemDelegateForColumn(0, _WrapItemDelegate(self.sync_right_tree))
        splitter.addWidget(self.sync_left_tree)
        splitter.addWidget(self.sync_right_tree)
        panel_layout.addWidget(splitter)

        self.sync_apply = QPushButton(self.tr("Apply synchronization"))
        panel_layout.addWidget(self.sync_apply)

        self.sync_panel.setVisible(False)
        layout.addWidget(self.sync_panel)

        self.sync_start.clicked.connect(self._start_sync)
        self.sync_apply.clicked.connect(self._apply_sync)
        self.sync_import_apply.clicked.connect(self._import_selected_program)
        self.sync_mode_import.toggled.connect(self._on_sync_mode_changed)
        self.sync_mode_sync.toggled.connect(self._on_sync_mode_changed)
        self.sync_target_program_combo.currentIndexChanged.connect(self._on_sync_program_mapping_changed)
        self.sync_source_program_combo.currentIndexChanged.connect(self._on_sync_program_mapping_changed)
        self.sync_left_tree.itemChanged.connect(self._on_sync_target_changed)
        self.sync_right_tree.itemChanged.connect(self._on_sync_source_changed)
        self.sync_hide_identical.stateChanged.connect(self._on_sync_hide_identical_changed)
        return tab

    def _build_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info_group = QWidget()
        info_layout = QVBoxLayout(info_group)
        db_row = QHBoxLayout()
        self.database_path_label = QLabel(self.tr("Database file"))
        self.database_path = QLineEdit()
        self.database_path.setReadOnly(True)
        self.database_path_browse = QPushButton(self.tr("Change..."))
        db_row.addWidget(self.database_path_label)
        db_row.addWidget(self.database_path, 1)
        db_row.addWidget(self.database_path_browse)
        info_layout.addLayout(db_row)

        settings_row = QHBoxLayout()
        self.ui_settings_path_label = QLabel(self.tr("UI settings file"))
        self.ui_settings_path = QLineEdit()
        self.ui_settings_path.setReadOnly(True)
        self.ui_settings_path_browse = QPushButton(self.tr("Change..."))
        settings_row.addWidget(self.ui_settings_path_label)
        settings_row.addWidget(self.ui_settings_path, 1)
        settings_row.addWidget(self.ui_settings_path_browse)
        info_layout.addLayout(settings_row)

        translations_row = QHBoxLayout()
        self.translations_path_label = QLabel(self.tr("Translations file"))
        self.translations_path = QLineEdit()
        self.translations_path.setReadOnly(True)
        self.translations_path_browse = QPushButton(self.tr("Change..."))
        translations_row.addWidget(self.translations_path_label)
        translations_row.addWidget(self.translations_path, 1)
        translations_row.addWidget(self.translations_path_browse)
        info_layout.addLayout(translations_row)
        layout.addWidget(info_group)

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
        self.db_check = QPushButton(self.tr("Check database"))
        self.db_cleanup = QPushButton(self.tr("Cleanup unused data"))
        self.db_repair = QPushButton(self.tr("Repair database"))
        db_layout.addWidget(self.db_export)
        db_layout.addWidget(self.db_import)
        db_layout.addWidget(self.db_check)
        db_layout.addWidget(self.db_cleanup)
        db_layout.addWidget(self.db_repair)
        db_layout.addStretch(1)
        layout.addWidget(db_group)

        user_settings_group = QWidget()
        user_settings_layout = QHBoxLayout(user_settings_group)
        self.user_settings_export = QPushButton(self.tr("Export user settings"))
        self.user_settings_import = QPushButton(self.tr("Import user settings"))
        self.user_settings_save = QPushButton(self.tr("Save user settings"))
        user_settings_layout.addWidget(self.user_settings_export)
        user_settings_layout.addWidget(self.user_settings_import)
        user_settings_layout.addWidget(self.user_settings_save)
        user_settings_layout.addStretch(1)
        layout.addWidget(user_settings_group)
        layout.addStretch(1)

        self.materials_location_browse.clicked.connect(self._change_materials_location)
        self.database_path_browse.clicked.connect(self._change_database_path)
        self.ui_settings_path_browse.clicked.connect(self._change_ui_settings_path)
        self.translations_path_browse.clicked.connect(self._change_translations_path)
        self.db_export.clicked.connect(self._export_database)
        self.db_import.clicked.connect(self._import_database)
        self.db_check.clicked.connect(self._check_database)
        self.db_cleanup.clicked.connect(self._cleanup_unused_data)
        self.db_repair.clicked.connect(self._repair_database)
        self.user_settings_export.clicked.connect(self._export_user_settings)
        self.user_settings_import.clicked.connect(self._import_user_settings)
        self.user_settings_save.clicked.connect(self._save_user_settings)

        self._refresh_settings()
        return tab

    def _refresh_all(self) -> None:
        self._refresh_teachers()
        self._refresh_lesson_types()
        self._refresh_material_types()
        self._refresh_structure_tree()

    # Teachers
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

    # Structure
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
                except Exception as exc:
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
                except Exception as exc:
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
        elif entity_type == "discipline":
            self.controller.delete_discipline(entity.id)
        elif entity_type == "topic":
            self.controller.delete_topic(entity.id)
        elif entity_type == "lesson":
            self.controller.delete_lesson(entity.id)
        elif entity_type == "question":
            self.controller.delete_question(entity.id)
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
            except Exception as exc:
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
            except Exception as exc:
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

    # Materials
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
        except Exception as exc:
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
        except Exception as exc:
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

    def _check_database(self) -> None:
        diagnostics = self._database_diagnostics()
        QMessageBox.information(self, self.tr("Check database"), diagnostics)

    def _cleanup_unused_data(self) -> None:
        counts = self.controller.get_unused_data_counts()
        total = sum(counts.values())
        if total == 0:
            QMessageBox.information(self, self.tr("Cleanup unused data"), self.tr("No unused data found."))
            return
        details = [
            f"{self.tr('Programs')}: {counts['programs']}",
            f"{self.tr('Disciplines')}: {counts['disciplines']}",
            f"{self.tr('Topics')}: {counts['topics']}",
            f"{self.tr('Lessons')}: {counts['lessons']}",
            f"{self.tr('Questions')}: {counts['questions']}",
            f"{self.tr('Materials')}: {counts['materials']}",
        ]
        message = self.tr("Unused data will be deleted:") + "\n" + "\n".join(details)
        if QMessageBox.question(self, self.tr("Confirm"), message) != QMessageBox.Yes:
            return
        self.controller.cleanup_unused_data()
        QMessageBox.information(self, self.tr("Cleanup unused data"), self.tr("Cleanup completed."))

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
        self.database_path.setText(str(resolve_app_path(self.controller.db.db_path)))
        settings_path = self.bootstrap_settings.value("app/ui_settings_path", "")
        if not settings_path:
            settings_path = self.settings.fileName() or ""
        self.ui_settings_path.setText(str(resolve_app_path(settings_path)))
        translations_path = self.bootstrap_settings.value("app/translations_path", "")
        if not translations_path:
            language = self.i18n.current_language() if self.i18n else "uk"
            translations_path = str(get_translations_dir() / f"app_{language}.ts")
        self.translations_path.setText(str(resolve_app_path(translations_path)))

    def _change_database_path(self) -> None:
        current = self.bootstrap_settings.value("app/db_path", "")
        start_dir = str(resolve_app_path(current)) if current else str(self.controller.db.db_path)
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Select database file"),
            start_dir,
            self.tr("Database files (*.db);;All files (*)"),
        )
        if not path:
            return
        self.bootstrap_settings.setValue("app/db_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.database_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Database selection saved. Restart the app to apply changes."),
        )

    def _change_ui_settings_path(self) -> None:
        current = self.bootstrap_settings.value("app/ui_settings_path", "")
        start_dir = str(resolve_app_path(current)) if current else str(get_settings_dir() / "user_settings.ini")
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Select UI settings file"),
            start_dir,
            self.tr("Settings files (*.ini);;All files (*)"),
        )
        if not path:
            return
        self.bootstrap_settings.setValue("app/ui_settings_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.ui_settings_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Settings file selection saved. Restart the app to apply changes."),
        )

    def _change_translations_path(self) -> None:
        current = self.bootstrap_settings.value("app/translations_path", "")
        start_dir = str(resolve_app_path(current)) if current else str(get_translations_dir() / "app_uk.ts")
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select translations file"),
            start_dir,
            self.tr("Translation files (*.ts *.qm);;All files (*)"),
        )
        if not path:
            return
        self.bootstrap_settings.setValue("app/translations_path", make_relative_to_app(path))
        self.bootstrap_settings.sync()
        self.translations_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Translations file selection saved. Restart the app to apply changes."),
        )

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

    def _repair_database(self) -> None:
        src_path = Path(self.controller.db.db_path)
        default_path = src_path.with_name(f"{src_path.stem}_recovered.db")
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Repair database"),
            str(default_path),
            self.tr("Database (*.db);;All files (*)"),
        )
        if not path:
            return
        try:
            conn = sqlite3.connect(src_path)
            conn.text_factory = lambda b: b.decode(errors="ignore")
            try:
                dump_lines = list(conn.iterdump())
            finally:
                conn.close()

            skip_tokens = ("_fts_config", "_fts_docsize", "_fts_data", "_fts_idx")
            filtered = [line for line in dump_lines if not any(t in line.lower() for t in skip_tokens)]

            out = sqlite3.connect(path)
            try:
                out.executescript("\n".join(filtered))
                out.commit()
            finally:
                out.close()
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        self.bootstrap_settings.setValue("app/db_path", path)
        self.bootstrap_settings.sync()
        self.database_path.setText(path)
        QMessageBox.information(
            self,
            self.tr("Restart required"),
            self.tr("Database repaired. Restart the app to apply changes."),
        )

    def _start_sync(self) -> None:
        sync_root = get_app_base_dir() / "sync"
        if not sync_root.exists():
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Sync folder not found."))
            return
        db_candidates = list((sync_root / "database").glob("*.db"))
        if not db_candidates:
            db_candidates = list(sync_root.glob("*.db"))
        if not db_candidates:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Sync database not found."))
            return
        db_path = None
        if len(db_candidates) == 1:
            db_path = db_candidates[0]
        else:
            items = [str(p) for p in sorted(db_candidates)]
            choice, ok = QInputDialog.getItem(
                self,
                self.tr("Select database"),
                self.tr("Select database"),
                items,
                0,
                False,
            )
            if not ok or not choice:
                return
            db_path = Path(choice)

        self.sync_source_db = Database(str(db_path))
        self.sync_source_admin = AdminController(self.sync_source_db)
        self.sync_source_main = MainController(self.sync_source_db)
        self.sync_source_files_root = self._resolve_sync_files_root(sync_root)
        self.sync_target_main = MainController(self.controller.db)

        self.sync_source_programs = []
        for program in self.sync_source_main.get_programs():
            program.disciplines = self.sync_source_main.get_program_structure(program.id)
            self.sync_source_programs.append(program)

        self._sync_compare_index = self._build_sync_compare_index(self.sync_target_main)
        self._populate_sync_program_selectors()
        self._on_sync_program_mapping_changed()
        self._populate_sync_import_programs()
        self.sync_mode_panel.setVisible(True)
        self._on_sync_mode_changed()
        self.sync_status.setText(self.tr("Sync source loaded. Select mode."))

    def _populate_sync_import_programs(self) -> None:
        if not hasattr(self, "sync_import_program"):
            return
        self.sync_import_program.clear()
        if not hasattr(self, "sync_source_programs"):
            return
        for program in self.sync_source_programs:
            self.sync_import_program.addItem(program.name, program)
        if self.sync_import_program.count() > 0:
            self.sync_import_program.setCurrentIndex(0)

    def _populate_sync_program_selectors(self) -> None:
        if not hasattr(self, "sync_target_program_combo"):
            return
        self.sync_target_program_combo.clear()
        for program in self.controller.get_programs():
            self.sync_target_program_combo.addItem(program.name, program)
        if self.sync_target_program_combo.count() > 0:
            self.sync_target_program_combo.setCurrentIndex(0)
        self.sync_source_program_combo.clear()
        if hasattr(self, "sync_source_programs"):
            for program in self.sync_source_programs:
                self.sync_source_program_combo.addItem(program.name, program)
        if self.sync_source_program_combo.count() > 0:
            self.sync_source_program_combo.setCurrentIndex(0)

    def _on_sync_program_mapping_changed(self) -> None:
        if not hasattr(self, "sync_source_main"):
            return
        target_program = self._get_selected_sync_target_program()
        source_program = self._get_selected_sync_source_program()
        if target_program:
            compare = self._build_sync_compare_index_for_program(self.sync_target_main, target_program)
        else:
            compare = self._build_sync_compare_index(self.sync_target_main)
        self._populate_sync_tree(
            self.sync_left_tree,
            self.sync_target_main,
            checkable=True,
            check_children=True,
            programs=[target_program] if target_program else None,
        )
        self._populate_sync_tree(
            self.sync_right_tree,
            self.sync_source_main,
            checkable=True,
            compare_index=compare,
            hide_identical=self.sync_hide_identical.isChecked(),
            programs=[source_program] if source_program else None,
        )

    def _get_selected_sync_source_program(self):
        if hasattr(self, "sync_source_program_combo"):
            index = self.sync_source_program_combo.currentIndex()
            if index >= 0:
                return self.sync_source_program_combo.itemData(index)
            return None
        return None

    def _on_sync_mode_changed(self) -> None:
        if not hasattr(self, "sync_mode_import"):
            return
        import_mode = self.sync_mode_import.isChecked()
        self.sync_import_panel.setVisible(import_mode)
        self.sync_panel.setVisible(not import_mode)

    def _import_selected_program(self) -> None:
        if not hasattr(self, "sync_source_main"):
            return
        index = self.sync_import_program.currentIndex()
        if index < 0:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a program to import."))
            return
        program = self.sync_import_program.itemData(index)
        if program is None:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select a program to import."))
            return
        self._import_full_program(program)
        self._refresh_structure_tree()
        self.sync_status.setText(self.tr("Program imported."))

    def _unique_program_name(self, name: str) -> str:
        existing = {p.name for p in self.controller.get_programs()}
        if name not in existing:
            return name
        index = 1
        while True:
            suffix = f"_{index:02d}"
            candidate = f"{name}{suffix}"
            if candidate not in existing:
                return candidate
            index += 1

    def _import_full_program(self, program: EducationalProgram) -> None:
        target_name = self._unique_program_name(program.name)
        target_program = self.controller.add_program(
            EducationalProgram(
                name=target_name,
                description=program.description,
                level=program.level,
                year=program.year,
                duration_hours=program.duration_hours,
            )
        )
        target_program_id = target_program.id
        target_program_discipline = self._ensure_program_discipline(target_program_id)
        self._sync_materials_for_entity(
            "program",
            program.id,
            "program",
            target_program_id,
            target_program_id,
            target_program_discipline,
        )

        disciplines = self.sync_source_main.get_program_structure(program.id)
        for discipline in disciplines:
            target_discipline = self.controller.add_discipline(
                Discipline(
                    name=discipline.name,
                    description=discipline.description,
                    order_index=discipline.order_index,
                )
            )
            order_index = self.controller._get_next_order_index("program_disciplines", "program_id", target_program_id)
            self.controller.add_discipline_to_program(target_program_id, target_discipline.id, order_index)
            self._sync_materials_for_entity(
                "discipline",
                discipline.id,
                "discipline",
                target_discipline.id,
                target_program_id,
                target_discipline.id,
            )
            for topic in discipline.topics:
                target_topic = self.controller.add_topic(
                    Topic(
                        title=topic.title,
                        description=topic.description,
                        order_index=topic.order_index,
                    )
                )
                order_index = self.controller._get_next_order_index("discipline_topics", "discipline_id", target_discipline.id)
                self.controller.add_topic_to_discipline(target_discipline.id, target_topic.id, order_index)
                self._sync_materials_for_entity(
                    "topic",
                    topic.id,
                    "topic",
                    target_topic.id,
                    target_program_id,
                    target_discipline.id,
                )
                for lesson in topic.lessons:
                    lesson_type_id = None
                    if lesson.lesson_type_name:
                        lesson_types = {t.name: t for t in self.controller.get_lesson_types()}
                        lesson_type = lesson_types.get(lesson.lesson_type_name)
                        if not lesson_type:
                            lesson_type = self.controller.add_lesson_type(LessonType(name=lesson.lesson_type_name))
                        lesson_type_id = lesson_type.id
                    target_lesson = self.controller.add_lesson(
                        Lesson(
                            title=lesson.title,
                            description=lesson.description,
                            duration_hours=lesson.duration_hours,
                            lesson_type_id=lesson_type_id,
                            classroom_hours=lesson.classroom_hours,
                            self_study_hours=lesson.self_study_hours,
                            order_index=lesson.order_index,
                        )
                    )
                    order_index = self.controller._get_next_order_index("topic_lessons", "topic_id", target_topic.id)
                    self.controller.add_lesson_to_topic(target_topic.id, target_lesson.id, order_index)
                    self._sync_materials_for_entity(
                        "lesson",
                        lesson.id,
                        "lesson",
                        target_lesson.id,
                        target_program_id,
                        target_discipline.id,
                    )
                    for question in lesson.questions:
                        target_question = self.controller.add_question(
                            Question(
                                content=question.content,
                                answer=question.answer,
                                order_index=question.order_index,
                            )
                        )
                        order_index = self.controller._get_next_order_index(
                            "lesson_questions",
                            "lesson_id",
                            target_lesson.id,
                        )
                        self.controller.add_question_to_lesson(target_lesson.id, target_question.id, order_index)

    def _resolve_sync_files_root(self, sync_root: Path) -> Path:
        settings_path = sync_root / "settings" / "storage.json"
        if settings_path.exists():
            try:
                data = json.loads(settings_path.read_text(encoding="utf-8"))
                root = data.get("materials_root")
                if root:
                    root_path = Path(root)
                    if root_path.exists():
                        return root_path
            except Exception:
                pass
        files_root = sync_root / "files"
        return files_root

    def _populate_sync_tree(
        self,
        tree: QTreeWidget,
        controller,
        checkable: bool,
        check_children: bool = True,
        compare_index: dict | None = None,
        hide_identical: bool = False,
        programs: list | None = None,
    ) -> None:  # noqa: ANN001
        tree.clear()
        program_list = programs if programs is not None else controller.get_programs()
        for program in program_list:
            if program is None:
                continue
            target_program = None
            if compare_index:
                target_program = compare_index["programs"].get(program.name) or compare_index.get("selected_program")
                if hide_identical and target_program:
                    if self._is_identical_entity(
                        "program",
                        program,
                        target_program,
                        controller,
                        self.sync_source_files_root,
                        self.sync_target_main,
                        self.file_storage.files_root,
                    ):
                        continue
            program_item = QTreeWidgetItem([program.name])
            program_item.setData(0, Qt.UserRole, ("program", program))
            if checkable:
                program_item.setFlags(program_item.flags() | Qt.ItemIsUserCheckable)
                program_item.setCheckState(0, Qt.Unchecked)
                if compare_index:
                    missing = self._materials_diff("program", program.id, target_program.id if target_program else None)
                    if missing:
                        self._mark_materials_diff(program_item, missing)
            disciplines = controller.get_program_structure(program.id)
            for discipline in disciplines:
                target_discipline = None
                if compare_index and target_program:
                    target_discipline = compare_index["disciplines"].get(target_program.id, {}).get(discipline.name)
                    if hide_identical and target_discipline:
                        if self._is_identical_entity(
                            "discipline",
                            discipline,
                            target_discipline,
                            controller,
                            self.sync_source_files_root,
                            self.sync_target_main,
                            self.file_storage.files_root,
                        ):
                            continue
                discipline_item = QTreeWidgetItem([discipline.name])
                discipline_item.setData(0, Qt.UserRole, ("discipline", discipline))
                if checkable and check_children:
                    discipline_item.setFlags(discipline_item.flags() | Qt.ItemIsUserCheckable)
                    discipline_item.setCheckState(0, Qt.Unchecked)
                    if compare_index:
                        missing = self._materials_diff(
                            "discipline",
                            discipline.id,
                            target_discipline.id if target_discipline else None,
                        )
                        if missing:
                            self._mark_materials_diff(discipline_item, missing)
                for topic in discipline.topics:
                    target_topic = None
                    if compare_index and target_discipline:
                        target_topic = compare_index["topics"].get(target_discipline.id, {}).get(topic.title)
                        if hide_identical and target_topic:
                            if self._is_identical_entity(
                                "topic",
                                topic,
                                target_topic,
                                controller,
                                self.sync_source_files_root,
                                self.sync_target_main,
                                self.file_storage.files_root,
                            ):
                                continue
                    topic_item = QTreeWidgetItem([topic.title])
                    topic_item.setData(0, Qt.UserRole, ("topic", topic))
                    if checkable and check_children:
                        topic_item.setFlags(topic_item.flags() | Qt.ItemIsUserCheckable)
                        topic_item.setCheckState(0, Qt.Unchecked)
                        if compare_index:
                            missing = self._materials_diff(
                                "topic",
                                topic.id,
                                target_topic.id if target_topic else None,
                            )
                            if missing:
                                self._mark_materials_diff(topic_item, missing)
                    for lesson in topic.lessons:
                        target_lesson = None
                        target_question_contents = None
                        if compare_index and target_topic:
                            target_lesson = compare_index["lessons"].get(target_topic.id, {}).get(lesson.title)
                            if target_lesson:
                                target_question_contents = {
                                    q.content
                                    for q in self.sync_target_main.lesson_repo.get_lesson_questions(
                                        target_lesson.id
                                    )
                                }
                            if hide_identical and target_lesson:
                                if self._is_identical_entity(
                                    "lesson",
                                    lesson,
                                    target_lesson,
                                    controller,
                                    self.sync_source_files_root,
                                    self.sync_target_main,
                                    self.file_storage.files_root,
                                ):
                                    continue
                        lesson_item = QTreeWidgetItem([lesson.title])
                        lesson_item.setData(0, Qt.UserRole, ("lesson", lesson))
                        if checkable and check_children:
                            lesson_item.setFlags(lesson_item.flags() | Qt.ItemIsUserCheckable)
                            lesson_item.setCheckState(0, Qt.Unchecked)
                            if compare_index:
                                missing = self._materials_diff(
                                    "lesson",
                                    lesson.id,
                                    target_lesson.id if target_lesson else None,
                                )
                                if missing:
                                    self._mark_materials_diff(lesson_item, missing)
                        for question in lesson.questions:
                            if hide_identical and target_question_contents is not None:
                                if question.content in target_question_contents:
                                    continue
                            question_item = QTreeWidgetItem([question.content])
                            question_item.setData(0, Qt.UserRole, ("question", question))
                            if checkable and check_children:
                                question_item.setFlags(question_item.flags() | Qt.ItemIsUserCheckable)
                                question_item.setCheckState(0, Qt.Unchecked)
                            lesson_item.addChild(question_item)
                        self._append_material_children(controller, "lesson", lesson.id, lesson_item)
                        topic_item.addChild(lesson_item)
                    self._append_material_children(controller, "topic", topic.id, topic_item)
                    discipline_item.addChild(topic_item)
                self._append_material_children(controller, "discipline", discipline.id, discipline_item)
                program_item.addChild(discipline_item)
            tree.addTopLevelItem(program_item)
            self._append_material_children(controller, "program", program.id, program_item)
        tree.expandAll()

    def _apply_sync(self) -> None:
        if not hasattr(self, "sync_source_main"):
            return
        target_program = self._get_selected_sync_target_program()
        if target_program is False:
            return
        type_flags = {
            "program": self.sync_type_program.isChecked(),
            "discipline": self.sync_type_discipline.isChecked(),
            "topic": self.sync_type_topic.isChecked(),
            "lesson": self.sync_type_lesson.isChecked(),
            "question": self.sync_type_question.isChecked(),
            "materials": self.sync_type_materials.isChecked(),
        }
        materials_only = type_flags["materials"] and not any(
            type_flags[t] for t in ["program", "discipline", "topic", "lesson", "question"]
        )

        def is_checked(item: QTreeWidgetItem) -> bool:
            return item.checkState(0) == Qt.Checked

        def any_child_checked(item: QTreeWidgetItem) -> bool:
            for i in range(item.childCount()):
                child = item.child(i)
                if is_checked(child) or any_child_checked(child):
                    return True
            return False

        program_map = {}
        discipline_map = {}
        topic_map = {}
        lesson_map = {}

        target_programs = {p.name: p for p in self.controller.get_programs()}

        def sync_program(item: QTreeWidgetItem, program):
            selected = is_checked(item)
            if not selected and not any_child_checked(item):
                return
            target = target_program or target_programs.get(program.name)
            if target is None and (type_flags["program"] or materials_only):
                target = self.controller.add_program(
                    EducationalProgram(
                        name=program.name,
                        description=program.description,
                        level=program.level,
                        year=program.year,
                        duration_hours=program.duration_hours,
                    )
                )
                target_programs[target.name] = target
            if target is None:
                return
            program_map[program.id] = target
            if type_flags["materials"] and (selected or materials_only):
                self._sync_materials_for_entity(
                    "program",
                    program.id,
                    "program",
                    target.id,
                    target.id,
                    self._ensure_program_discipline(target.id),
                )
            for i in range(item.childCount()):
                child_item = item.child(i)
                child_type, child_obj = child_item.data(0, Qt.UserRole)
                if child_type == "discipline":
                    sync_discipline(child_item, child_obj, target, force_materials=materials_only and selected)

        def sync_discipline(item: QTreeWidgetItem, discipline, target_program, force_materials: bool = False):
            selected = is_checked(item)
            if not selected and not any_child_checked(item) and not force_materials:
                return
            target_discipline = self._find_or_create_discipline(
                discipline,
                target_program,
                create=type_flags["discipline"] or materials_only,
            )
            if not target_discipline:
                return
            discipline_map[discipline.id] = target_discipline
            if type_flags["materials"] and (selected or materials_only or force_materials):
                self._sync_materials_for_entity(
                    "discipline",
                    discipline.id,
                    "discipline",
                    target_discipline.id,
                    target_program.id,
                    target_discipline.id,
                )
            for i in range(item.childCount()):
                child_item = item.child(i)
                child_type, child_obj = child_item.data(0, Qt.UserRole)
                if child_type == "topic":
                    sync_topic(
                        child_item,
                        child_obj,
                        target_program,
                        target_discipline,
                        force_materials=force_materials,
                    )

        def sync_topic(
            item: QTreeWidgetItem,
            topic,
            target_program,
            target_discipline,
            force_materials: bool = False,
        ):
            selected = is_checked(item)
            if not selected and not any_child_checked(item) and not force_materials:
                return
            target_topic = self._find_or_create_topic(
                topic,
                target_discipline,
                create=type_flags["topic"] or materials_only,
            )
            if not target_topic:
                return
            topic_map[topic.id] = target_topic
            if type_flags["materials"] and (selected or materials_only or force_materials):
                self._sync_materials_for_entity(
                    "topic",
                    topic.id,
                    "topic",
                    target_topic.id,
                    target_program.id,
                    target_discipline.id,
                )
            for i in range(item.childCount()):
                child_item = item.child(i)
                child_type, child_obj = child_item.data(0, Qt.UserRole)
                if child_type == "lesson":
                    sync_lesson(
                        child_item,
                        child_obj,
                        target_program,
                        target_discipline,
                        target_topic,
                        force_materials=force_materials,
                    )

        def sync_lesson(
            item: QTreeWidgetItem,
            lesson,
            target_program,
            target_discipline,
            target_topic,
            force_materials: bool = False,
        ):
            selected = is_checked(item)
            if not selected and not any_child_checked(item) and not force_materials:
                return
            target_lesson = self._find_or_create_lesson(
                lesson,
                target_topic,
                create=type_flags["lesson"] or materials_only,
            )
            if not target_lesson:
                return
            lesson_map[lesson.id] = target_lesson
            if type_flags["materials"] and (selected or materials_only or force_materials):
                self._sync_materials_for_entity(
                    "lesson",
                    lesson.id,
                    "lesson",
                    target_lesson.id,
                    target_program.id,
                    target_discipline.id,
                )
            for i in range(item.childCount()):
                child_item = item.child(i)
                child_type, child_obj = child_item.data(0, Qt.UserRole)
                if child_type == "question":
                    sync_question(child_item, child_obj, target_lesson, target_program, target_discipline)

        def sync_question(item: QTreeWidgetItem, question, target_lesson, target_program, target_discipline):
            selected = is_checked(item)
            if not selected and not any_child_checked(item):
                return
            target_question = self._find_or_create_question(
                question,
                target_lesson,
                create=type_flags["question"] or materials_only,
            )

        for i in range(self.sync_right_tree.topLevelItemCount()):
            item = self.sync_right_tree.topLevelItem(i)
            entity_type, entity = item.data(0, Qt.UserRole)
            if entity_type == "program":
                sync_program(item, entity)

        self._refresh_structure_tree()
        self.sync_status.setText(self.tr("Synchronization completed."))

    def _get_selected_sync_target_program(self):
        if hasattr(self, "sync_target_program_combo"):
            index = self.sync_target_program_combo.currentIndex()
            if index >= 0:
                return self.sync_target_program_combo.itemData(index)
            return None
        if not hasattr(self, "sync_left_tree"):
            return None
        selected = []
        for i in range(self.sync_left_tree.topLevelItemCount()):
            item = self.sync_left_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                entity_type, entity = item.data(0, Qt.UserRole)
                if entity_type == "program":
                    selected.append(entity)
        if len(selected) > 1:
            QMessageBox.warning(self, self.tr("Validation"), self.tr("Select only one target program."))
            return False
        return selected[0] if selected else None

    def _on_sync_target_changed(self, item: QTreeWidgetItem) -> None:
        if item is None:
            return
        if getattr(self, "_sync_updating_checks", False):
            return
        self._sync_updating_checks = True
        try:
            state = item.checkState(0)
            self._set_check_state_recursive(item, state)
        finally:
            self._sync_updating_checks = False

    def _on_sync_hide_identical_changed(self, _state: int) -> None:
        if not hasattr(self, "sync_source_main"):
            return
        self._on_sync_program_mapping_changed()

    def _on_sync_source_changed(self, item: QTreeWidgetItem) -> None:
        if item is None:
            return
        if getattr(self, "_sync_updating_checks", False):
            return
        self._sync_updating_checks = True
        try:
            state = item.checkState(0)
            self._set_check_state_recursive(item, state)
        finally:
            self._sync_updating_checks = False

    def _set_check_state_recursive(self, item: QTreeWidgetItem, state: Qt.CheckState) -> None:
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self._set_check_state_recursive(child, state)

    def _is_identical_entity(
        self,
        entity_type: str,
        source_entity,
        target_entity,
        source_controller,
        source_files_root: Path,
        target_controller,
        target_files_root: Path,
    ) -> bool:  # noqa: ANN001
        source_sig = self._entity_signature(
            source_controller, entity_type, source_entity, source_files_root, {}
        )
        target_sig = self._entity_signature(
            target_controller, entity_type, target_entity, target_files_root, {}
        )
        return source_sig == target_sig

    def _entity_signature(
        self,
        controller,
        entity_type: str,
        entity,
        files_root: Path,
        cache: dict,
    ) -> tuple:  # noqa: ANN001
        cache_key = (entity_type, getattr(entity, "id", None), str(files_root))
        if cache_key in cache:
            return cache[cache_key]
        if entity_type == "lesson":
            questions = controller.lesson_repo.get_lesson_questions(entity.id)
            q_sig = tuple(sorted(q.content for q in questions))
            m_sig = tuple(self._materials_signature(controller, "lesson", entity.id, files_root))
            sig = ("lesson", q_sig, m_sig)
        elif entity_type == "topic":
            lessons = controller.topic_repo.get_topic_lessons(entity.id)
            l_sig = tuple(
                sorted(
                    (
                        lesson.title,
                        self._entity_signature(controller, "lesson", lesson, files_root, cache),
                    )
                    for lesson in lessons
                )
            )
            m_sig = tuple(self._materials_signature(controller, "topic", entity.id, files_root))
            sig = ("topic", l_sig, m_sig)
        elif entity_type == "discipline":
            topics = controller.discipline_repo.get_discipline_topics(entity.id)
            t_sig = tuple(
                sorted(
                    (
                        topic.title,
                        self._entity_signature(controller, "topic", topic, files_root, cache),
                    )
                    for topic in topics
                )
            )
            m_sig = tuple(self._materials_signature(controller, "discipline", entity.id, files_root))
            sig = ("discipline", t_sig, m_sig)
        elif entity_type == "program":
            disciplines = controller.program_repo.get_program_disciplines(entity.id)
            d_sig = tuple(
                sorted(
                    (
                        disc.name,
                        self._entity_signature(controller, "discipline", disc, files_root, cache),
                    )
                    for disc in disciplines
                )
            )
            m_sig = tuple(self._materials_signature(controller, "program", entity.id, files_root))
            sig = ("program", d_sig, m_sig)
        else:
            sig = (entity_type, getattr(entity, "id", None))
        cache[cache_key] = sig
        return sig

    def _materials_signature(
        self,
        controller,
        entity_type: str,
        entity_id: int,
        files_root: Path,
    ) -> list[tuple]:  # noqa: ANN001
        materials = controller.get_materials_for_entity(entity_type, entity_id)
        sig = []
        for material in materials:
            crc = self._material_crc(material, files_root)
            sig.append((material.title, material.material_type, crc))
        return sorted(sig)

    def _material_crc(self, material: MethodicalMaterial, files_root: Path) -> int:
        path = None
        if material.relative_path:
            path = files_root / material.relative_path
        elif material.file_path:
            path = Path(material.file_path)
            if not path.is_absolute():
                path = files_root / material.file_path
        if not path or not path.exists():
            return 0
        checksum = 0
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                checksum = zlib.crc32(chunk, checksum)
        return checksum & 0xFFFFFFFF

    def _build_sync_compare_index_for_program(self, controller, program: EducationalProgram) -> dict:  # noqa: ANN001
        programs = {program.name: program}
        disciplines = {program.id: {d.name: d for d in controller.get_program_disciplines(program.id)}}
        topics = {}
        lessons = {}
        for discipline in disciplines[program.id].values():
            topics[discipline.id] = {
                t.title: t for t in controller.discipline_repo.get_discipline_topics(discipline.id)
            }
            for topic in topics[discipline.id].values():
                lessons[topic.id] = {l.title: l for l in controller.topic_repo.get_topic_lessons(topic.id)}
        return {
            "programs": programs,
            "selected_program": program,
            "disciplines": disciplines,
            "topics": topics,
            "lessons": lessons,
        }

    def _build_sync_compare_index(self, controller) -> dict:  # noqa: ANN001
        programs = {p.name: p for p in controller.get_programs()}
        disciplines = {}
        topics = {}
        lessons = {}
        for program in programs.values():
            disciplines[program.id] = {d.name: d for d in controller.get_program_disciplines(program.id)}
            for discipline in disciplines[program.id].values():
                topics[discipline.id] = {
                    t.title: t for t in controller.discipline_repo.get_discipline_topics(discipline.id)
                }
                for topic in topics[discipline.id].values():
                    lessons[topic.id] = {l.title: l for l in controller.topic_repo.get_topic_lessons(topic.id)}
        return {
            "programs": programs,
            "disciplines": disciplines,
            "topics": topics,
            "lessons": lessons,
        }

    def _materials_diff(self, entity_type: str, source_id: int, target_id: int | None) -> list[str]:
        if entity_type not in {"program", "discipline", "topic", "lesson"}:
            return []
        source_materials = self.sync_source_admin.get_materials_for_entity(entity_type, source_id)
        if not source_materials:
            return []
        if target_id is None:
            return [m.title for m in source_materials if m.title]
        target_materials = self.controller.get_materials_for_entity(entity_type, target_id)
        target_titles = {m.title for m in target_materials}
        return [m.title for m in source_materials if m.title not in target_titles]

    def _mark_materials_diff(self, item: QTreeWidgetItem, _missing: list[str]) -> None:
        item.setBackground(0, QBrush(QColor(255, 242, 204)))
        item.setForeground(0, QBrush(QColor(0, 0, 0)))

    def _append_material_children(
        self,
        controller,
        entity_type: str,
        entity_id: int,
        parent_item: QTreeWidgetItem,
    ) -> None:  # noqa: ANN001
        if not hasattr(controller, "get_materials_for_entity"):
            return
        materials = controller.get_materials_for_entity(entity_type, entity_id)
        if not materials:
            return
        header = QTreeWidgetItem([self.tr("Materials")])
        header.setForeground(0, QBrush(QColor(0, 128, 0)))
        header.setBackground(0, QBrush(QColor(226, 239, 218)))
        header.setFlags(header.flags() & ~Qt.ItemIsUserCheckable)
        for material in materials:
            title = material.title or ""
            label = f"• {title}"
            teachers = ", ".join(t.full_name for t in material.teachers) if material.teachers else ""
            if teachers:
                label += f" | {self.tr('Teachers')}: {teachers}"
            item = QTreeWidgetItem([label])
            item.setForeground(0, QBrush(QColor(0, 128, 0)))
            item.setBackground(0, QBrush(QColor(240, 248, 235)))
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
            header.addChild(item)
        parent_item.addChild(header)

    def _find_or_create_discipline(self, discipline: Discipline, program: EducationalProgram, create: bool) -> Discipline:
        existing = {d.name: d for d in self.controller.get_program_disciplines(program.id)}
        if discipline.name in existing:
            return existing[discipline.name]
        if not create:
            return None
        all_disciplines = {d.name: d for d in self.controller.get_disciplines()}
        target = all_disciplines.get(discipline.name)
        if target is None:
            target = self.controller.add_discipline(
                Discipline(
                    name=discipline.name,
                    description=discipline.description,
                    order_index=discipline.order_index,
                )
            )
        order_index = self.controller._get_next_order_index("program_disciplines", "program_id", program.id)
        self.controller.add_discipline_to_program(program.id, target.id, order_index)
        return target

    def _find_or_create_topic(self, topic: Topic, discipline: Discipline, create: bool) -> Topic:
        existing = {t.title: t for t in self.controller.get_discipline_topics(discipline.id)}
        if topic.title in existing:
            return existing[topic.title]
        if not create:
            return None
        target = self.controller.add_topic(
            Topic(
                title=topic.title,
                description=topic.description,
                order_index=topic.order_index,
            )
        )
        order_index = self.controller._get_next_order_index("discipline_topics", "discipline_id", discipline.id)
        self.controller.add_topic_to_discipline(discipline.id, target.id, order_index)
        return target

    def _find_or_create_lesson(self, lesson: Lesson, topic: Topic, create: bool) -> Lesson:
        existing = {l.title: l for l in self.controller.get_topic_lessons(topic.id)}
        if lesson.title in existing:
            return existing[lesson.title]
        if not create:
            return None
        lesson_type_id = None
        if lesson.lesson_type_name:
            lesson_types = {t.name: t for t in self.controller.get_lesson_types()}
            lesson_type = lesson_types.get(lesson.lesson_type_name)
            if lesson_type:
                lesson_type_id = lesson_type.id
        target = self.controller.add_lesson(
            Lesson(
                title=lesson.title,
                description=lesson.description,
                duration_hours=lesson.duration_hours,
                lesson_type_id=lesson_type_id,
                classroom_hours=lesson.classroom_hours,
                self_study_hours=lesson.self_study_hours,
                order_index=lesson.order_index,
            )
        )
        order_index = self.controller._get_next_order_index("topic_lessons", "topic_id", topic.id)
        self.controller.add_lesson_to_topic(topic.id, target.id, order_index)
        return target

    def _find_or_create_question(self, question: Question, lesson: Lesson, create: bool) -> Question:
        existing = {q.content: q for q in self.controller.get_lesson_questions(lesson.id)}
        if question.content in existing:
            return existing[question.content]
        if not create:
            return None
        target = self.controller.add_question(
            Question(
                content=question.content,
                answer=question.answer,
                order_index=question.order_index,
            )
        )
        order_index = self.controller._get_next_order_index("lesson_questions", "lesson_id", lesson.id)
        self.controller.add_question_to_lesson(lesson.id, target.id, order_index)
        return target

    def _ensure_program_discipline(self, program_id: int) -> int:
        disciplines = self.controller.get_program_disciplines(program_id)
        if disciplines:
            return disciplines[0].id
        program = self.controller.program_repo.get_by_id(program_id)
        base = program.name if program else str(program_id)
        name = f"{self.tr('Discipline for')} {base}"
        discipline = self.controller.add_discipline(Discipline(name=name))
        order_index = self.controller._get_next_order_index("program_disciplines", "program_id", program_id)
        self.controller.add_discipline_to_program(program_id, discipline.id, order_index)
        return discipline.id

    def _sync_materials_for_entity(
        self,
        source_entity_type: str,
        source_entity_id: int,
        target_entity_type: str,
        target_entity_id: int,
        target_program_id: int,
        target_discipline_id: int,
    ) -> None:
        if source_entity_type not in {"program", "discipline", "topic", "lesson"}:
            return
        materials = self.sync_source_admin.get_materials_for_entity(source_entity_type, source_entity_id)
        existing_titles = {
            m.title
            for m in self.controller.get_materials_for_entity(target_entity_type, target_entity_id)
        }
        material_types = {t.name for t in self.controller.get_material_types()}
        for material in materials:
            if material.material_type and material.material_type not in material_types:
                self.controller.add_material_type(MaterialType(name=material.material_type))
                material_types.add(material.material_type)
            title = self._unique_material_title(material.title, existing_titles)
            existing_titles.add(title)
            new_material = self.controller.add_material(
                MethodicalMaterial(
                    title=title,
                    material_type=material.material_type,
                    description=material.description,
                )
            )
            self.controller.add_material_to_entity(new_material.id, target_entity_type, target_entity_id)
            source_path = self._resolve_source_material_path(material)
            if source_path and source_path.exists():
                try:
                    self.controller.attach_material_file_with_context(
                        new_material, str(source_path), target_program_id, target_discipline_id
                    )
                except Exception:
                    pass

    def _resolve_source_material_path(self, material: MethodicalMaterial) -> Path | None:
        if material.relative_path:
            return self.sync_source_files_root / material.relative_path
        if material.file_path:
            path = Path(material.file_path)
            if path.is_absolute():
                return path
            return self.sync_source_files_root / material.file_path
        return None

    def _unique_material_title(self, title: str, existing: set[str]) -> str:
        if title not in existing:
            return title
        index = 1
        while True:
            suffix = f"_{index:02d}"
            candidate = f"{title}{suffix}"
            if candidate not in existing:
                return candidate
            index += 1

    def _export_user_settings(self) -> None:
        default_path = get_settings_dir() / "user_settings.ini"
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export user settings"),
            str(default_path),
            self.tr("Settings (*.ini);;All files (*)"),
        )
        if not path:
            return
        try:
            export_settings = QSettings(path, QSettings.IniFormat)
            export_settings.clear()
            for key in self.settings.allKeys():
                export_settings.setValue(key, self.settings.value(key))
            export_settings.sync()
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(self, self.tr("Export user settings"), self.tr("User settings exported."))

    def _import_user_settings(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Import user settings"),
            "",
            self.tr("Settings (*.ini);;All files (*)"),
        )
        if not path:
            return
        if QMessageBox.question(
            self,
            self.tr("Confirm"),
            self.tr("Replace the current user settings with the selected file?"),
        ) != QMessageBox.Yes:
            return
        try:
            import_settings = QSettings(path, QSettings.IniFormat)
            self.settings.clear()
            for key in import_settings.allKeys():
                self.settings.setValue(key, import_settings.value(key))
            self.settings.sync()
            self.i18n.load_from_settings()
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(
            self,
            self.tr("Import user settings"),
            self.tr("User settings imported. Restart the app."),
        )

    def _save_user_settings(self) -> None:
        try:
            self.settings.sync()
        except Exception as exc:
            QMessageBox.warning(self, self.tr("Import error"), str(exc))
            return
        QMessageBox.information(self, self.tr("Save user settings"), self.tr("User settings saved."))

    def _serialize_settings(self, settings: QSettings) -> str:
        import base64
        import json

        data = {}
        for key in settings.allKeys():
            value = settings.value(key)
            if isinstance(value, QByteArray):
                data[key] = {
                    "__type__": "QByteArray",
                    "data": base64.b64encode(bytes(value)).decode("ascii"),
                }
            else:
                data[key] = value
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _deserialize_settings(self, settings: QSettings, content: str) -> None:
        import base64
        import json

        data = json.loads(content)
        settings.clear()
        for key, value in data.items():
            if isinstance(value, dict) and value.get("__type__") == "QByteArray":
                raw = base64.b64decode(value.get("data", ""))
                settings.setValue(key, QByteArray(raw))
            else:
                settings.setValue(key, value)

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

    def retranslate_ui(self, *_args) -> None:
        self.setWindowTitle(self.tr("Admin Panel"))
        for child in self.findChildren(QMenuBar):
            child.clear()
            app_menu = child.addMenu(self.tr("Application"))
            action_about = app_menu.addAction(self.tr("About"))
            action_restart = app_menu.addAction(self.tr("Restart application"))
            action_exit = app_menu.addAction(self.tr("Exit application"))
            action_about.triggered.connect(self._show_about)
            action_restart.triggered.connect(self._restart_application)
            action_exit.triggered.connect(self._close_application)
        self.tabs.setTabText(0, self.tr("Structure"))
        self.tabs.setTabText(1, self.tr("Materials"))
        self.tabs.setTabText(2, self.tr("Teachers"))
        self.tabs.setTabText(3, self.tr("Synchronization"))
        self.tabs.setTabText(4, self.tr("Settings"))
        if hasattr(self, "sync_target_label"):
            self.sync_target_label.setText(self.tr("Target program:"))
        if hasattr(self, "sync_source_label"):
            self.sync_source_label.setText(self.tr("Source program:"))
        if hasattr(self, "sync_mode_label"):
            self.sync_mode_label.setText(self.tr("Mode:"))
        if hasattr(self, "sync_mode_import"):
            self.sync_mode_import.setText(self.tr("Import program fully"))
        if hasattr(self, "sync_mode_sync"):
            self.sync_mode_sync.setText(self.tr("Synchronize with existing program"))
        if hasattr(self, "sync_import_label"):
            self.sync_import_label.setText(self.tr("Program to import:"))
        if hasattr(self, "sync_import_apply"):
            self.sync_import_apply.setText(self.tr("Import program"))
        if hasattr(self, "materials_group"):
            self.materials_group.setTitle(self.tr("Materials"))
        if hasattr(self, "lesson_types_group"):
            self.lesson_types_group.setTitle(self.tr("Lesson types"))
        self.structure_tree.setHeaderLabels([self.tr("Structure")])
        self.structure_add_program.setText(self.tr("Add program"))
        self.structure_add_discipline.setText(self.tr("Add discipline"))
        self.structure_add_topic.setText(self.tr("Add topic"))
        self.structure_add_lesson.setText(self.tr("Add lesson"))
        self.structure_add_question.setText(self.tr("Add question"))
        self.structure_import.setText(self.tr("Import curriculum structure"))
        self.structure_refresh.setText(self.tr("Refresh"))
        self.structure_edit.setText(self.tr("Edit"))
        self.structure_delete.setText(self.tr("Delete"))
        self.structure_duplicate.setText(self.tr("Duplicate"))
        self.structure_copy.setText(self.tr("Copy"))

        if hasattr(self, "database_path_label"):
            self.database_path_label.setText(self.tr("Database file"))
        if hasattr(self, "ui_settings_path_label"):
            self.ui_settings_path_label.setText(self.tr("UI settings file"))

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
        self.lesson_types_table.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Synonyms")])
        self.questions_table.setHorizontalHeaderLabels([self.tr("Question")])
        self.materials_table.setHorizontalHeaderLabels(
            [self.tr("Title"), self.tr("Type"), self.tr("File"), self.tr("Authors")]
        )

        self.teacher_add.setText(self.tr("Add"))
        self.teacher_edit.setText(self.tr("Edit"))
        self.teacher_delete.setText(self.tr("Delete"))
        self.teacher_import.setText(self.tr("Import teachers from DOCX"))
        if hasattr(self, "teacher_disciplines_label"):
            self.teacher_disciplines_label.setText(self.tr("Assigned disciplines"))
            self.teacher_discipline_add.setText(self.tr("Add ->"))
            self.teacher_discipline_remove.setText(self.tr("<- Remove"))
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
        self.material_open.setText(self.tr("Open file"))
        self.material_show.setText(self.tr("Show in folder"))
        self.material_copy.setText(self.tr("Copy file as..."))
        if hasattr(self, "material_types_table"):
            self.material_types_table.setHorizontalHeaderLabels([self.tr("Name")])
            self.material_type_add.setText(self.tr("Add"))
            self.material_type_edit.setText(self.tr("Edit"))
            self.material_type_delete.setText(self.tr("Delete"))

        self.materials_location_label.setText(self.tr("Materials location"))
        self.materials_location_browse.setText(self.tr("Change..."))
        if hasattr(self, "database_path_label"):
            self.database_path_label.setText(self.tr("Database file"))
        if hasattr(self, "database_path_browse"):
            self.database_path_browse.setText(self.tr("Change..."))
        if hasattr(self, "ui_settings_path_label"):
            self.ui_settings_path_label.setText(self.tr("UI settings file"))
        if hasattr(self, "ui_settings_path_browse"):
            self.ui_settings_path_browse.setText(self.tr("Change..."))
        if hasattr(self, "translations_path_label"):
            self.translations_path_label.setText(self.tr("Translations file"))
        if hasattr(self, "translations_path_browse"):
            self.translations_path_browse.setText(self.tr("Change..."))
        self.db_export.setText(self.tr("Export database"))
        self.db_import.setText(self.tr("Import database"))
        self.db_check.setText(self.tr("Check database"))
        self.db_cleanup.setText(self.tr("Cleanup unused data"))
        self.db_repair.setText(self.tr("Repair database"))
        self.user_settings_export.setText(self.tr("Export user settings"))
        self.user_settings_import.setText(self.tr("Import user settings"))
        self.user_settings_save.setText(self.tr("Save user settings"))
        if hasattr(self, "sync_start"):
            self.sync_start.setText(self.tr("Start synchronization"))
            self.sync_apply.setText(self.tr("Apply synchronization"))
            self.sync_left_tree.setHeaderLabels([self.tr("Current structure")])
            self.sync_right_tree.setHeaderLabels([self.tr("Source structure")])
            self.sync_type_program.setText(self.tr("Program"))
            self.sync_type_discipline.setText(self.tr("Discipline"))
            self.sync_type_topic.setText(self.tr("Topic"))
            self.sync_type_lesson.setText(self.tr("Lesson"))
            self.sync_type_question.setText(self.tr("Question"))
            self.sync_type_materials.setText(self.tr("Materials"))


class _WrapItemDelegate(QStyledItemDelegate):
    def __init__(self, view):
        super().__init__(view)
        self._view = view

    def initStyleOption(self, option, index):  # noqa: ANN001
        super().initStyleOption(option, index)
        option.textElideMode = Qt.ElideNone
        option.wrapText = True

    def sizeHint(self, option, index):  # noqa: ANN001
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        style = opt.widget.style() if opt.widget else self._view.style()
        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, opt, opt.widget)
        width = text_rect.width()
        if width <= 0 and self._view is not None:
            width = self._view.columnWidth(index.column())
        if width <= 0:
            return super().sizeHint(option, index)
        doc = QTextDocument()
        doc.setDefaultFont(opt.font)
        doc.setTextWidth(width)
        doc.setPlainText(opt.text)
        height = max(int(doc.size().height()) + opt.fontMetrics.leading() + 10, opt.fontMetrics.height() + 10)
        return QSize(int(opt.rect.width()), height)

    def paint(self, painter, option, index):  # noqa: ANN001
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        text = opt.text
        opt.text = ""
        style = opt.widget.style() if opt.widget else self._view.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)

        doc = QTextDocument()
        doc.setDefaultFont(opt.font)
        doc.setTextWidth(opt.rect.width())
        doc.setPlainText(text)

        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, opt, opt.widget)
        painter.save()
        painter.translate(text_rect.topLeft())
        doc.drawContents(painter, QRect(0, 0, text_rect.width(), text_rect.height()))
        painter.restore()
