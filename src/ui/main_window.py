"""Main application window."""
import os
import re
import sys
from typing import Dict, Tuple
from PySide6.QtCore import Qt, QSettings, QSize, QRect
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QPushButton,
    QSplitter,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QFileDialog,
    QHeaderView,
    QAbstractScrollArea,
    QTabWidget,
    QDialog,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from PySide6.QtGui import QFont, QColor, QBrush, QTextDocument, QFontMetrics
from PySide6.QtCore import QProcess
from ..controllers.main_controller import MainController
from ..ui.admin_dialog import AdminDialog
from ..ui.editor_wizard import EditorWizardDialog
from ..services.auth_service import AuthService
from ..services.i18n import I18nManager
from ..services.file_storage import FileStorageManager


class MainWindow(QMainWindow):
    """Main window for user mode."""

    def __init__(self, controller: MainController, i18n: I18nManager, settings: QSettings):
        super().__init__()
        self.controller = controller
        self.i18n = i18n
        self.settings = settings
        self.file_storage = FileStorageManager()
        self.auth_service = AuthService()
        self.program_items: Dict[int, QListWidgetItem] = {}
        self.tree_items: Dict[Tuple[str, int], QTreeWidgetItem] = {}
        self._tree_syncing_columns = False
        self.last_program_id = None
        self.last_discipline_id = None
        self.setWindowTitle(self.tr("Educational Program Manager"))
        self.resize(1200, 720)
        self._build_ui()
        self._apply_word_wrap()
        self._load_programs()
        self._load_settings()
        self.i18n.language_changed.connect(self._on_language_changed)

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        app_menu = self.menuBar().addMenu(self.tr("Application"))
        self.action_restart = app_menu.addAction(self.tr("Restart application"))
        self.action_exit = app_menu.addAction(self.tr("Exit application"))
        self.action_restart.triggered.connect(self._restart_application)
        self.action_exit.triggered.connect(self._close_application)

        top_bar = QHBoxLayout()
        self.search_label = QLabel(self.tr("Search:"))
        top_bar.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_button = QPushButton(self.tr("Search"))
        self.language_combo = QComboBox()
        self.language_combo.addItem(self.tr("Ukrainian"), "uk")
        self.language_combo.addItem(self.tr("English"), "en")
        self.font_combo = QComboBox()
        self.font_combo.addItems(["10", "11", "12", "13", "14", "15", "16", "18"])
        self.editor_button = QPushButton(self.tr("Editor Mode"))
        self.admin_button = QPushButton(self.tr("Admin Mode"))
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.search_button)
        top_bar.addWidget(self.language_combo)
        top_bar.addWidget(self.font_combo)
        top_bar.addStretch(1)
        top_bar.addWidget(self.editor_button)
        top_bar.addWidget(self.admin_button)
        layout.addLayout(top_bar)

        self.main_splitter = QSplitter()
        self.main_splitter.setOrientation(Qt.Horizontal)

        self.program_list = QListWidget()
        self.program_list.setMinimumWidth(220)
        self.program_label = QLabel(self.tr("Programs"))
        splitter_left = self._wrap_with_label(self.program_list, self.program_label)
        self.main_splitter.addWidget(splitter_left)

        self.center_splitter = QSplitter()
        self.center_splitter.setOrientation(Qt.Vertical)

        self.content_tree = QTreeWidget()
        self.content_tree.setHeaderLabels([self.tr("Title"), self.tr("Type")])
        self.content_tree.setColumnWidth(0, 350)
        header = self.content_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.content_tree.setColumnWidth(1, 120)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(40)
        header.sectionResized.connect(self._on_tree_header_resized)
        self.content_tree.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.structure_label = QLabel(self.tr("Program Structure"))
        self.report_table = QTableWidget(0, 0)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.verticalHeader().setVisible(False)
        self.report_label = QLabel(self.tr("Report"))

        self.structure_tabs = QTabWidget()
        structure_tab = QWidget()
        structure_layout = QVBoxLayout(structure_tab)
        structure_layout.addWidget(self._wrap_with_label(self.content_tree, self.structure_label))
        report_tab = QWidget()
        report_layout = QVBoxLayout(report_tab)
        report_layout.addWidget(self._wrap_with_label(self.report_table, self.report_label))
        self.structure_tabs.addTab(structure_tab, self.tr("Structure"))
        self.structure_tabs.addTab(report_tab, self.tr("Report"))

        self.center_splitter.addWidget(self.structure_tabs)

        self.search_results = QTableWidget(0, 3)
        self.search_results.setHorizontalHeaderLabels([self.tr("Type"), self.tr("Title"), self.tr("Description")])
        self.language_combo.setItemText(0, self.tr("Ukrainian"))
        self.language_combo.setItemText(1, self.tr("English"))
        self.search_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.search_results.horizontalHeader().setStretchLastSection(True)
        self.search_results_label = QLabel(self.tr("Search Results"))
        self.center_splitter.addWidget(self._wrap_with_label(self.search_results, self.search_results_label))

        self.main_splitter.addWidget(self.center_splitter)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.details_label = QLabel(self.tr("Details"))
        right_layout.addWidget(self._wrap_with_label(self.details, self.details_label))

        self.materials_list = QListWidget()
        self.materials_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.materials_list.setAlternatingRowColors(True)
        self.materials_list.setStyleSheet(
            "QListWidget::item {"
            "  background: #ffffff;"
            "  border-bottom: 1px solid #000000;"
            "  padding: 4px;"
            "}"
            "QListWidget::item:alternate {"
            "  background: #f2f2f2;"
            "}"
            "QListWidget::item:selected {"
            "  background: #cfe8ff;"
            "  color: #000000;"
            "}"
        )
        self.materials_label = QLabel(self.tr("Methodical Materials"))
        right_layout.addWidget(self._wrap_with_label(self.materials_list, self.materials_label))

        self.open_material_button = QPushButton(self.tr("Open Selected File"))
        self.show_material_button = QPushButton(self.tr("Show in folder"))
        self.copy_material_button = QPushButton(self.tr("Copy file as..."))
        right_layout.addWidget(self.open_material_button)
        right_layout.addWidget(self.show_material_button)
        right_layout.addWidget(self.copy_material_button)

        self.main_splitter.addWidget(right_panel)
        self.main_splitter.setStretchFactor(1, 2)
        self.main_splitter.setStretchFactor(2, 1)

        layout.addWidget(self.main_splitter)
        self.setCentralWidget(central)

        self.search_button.clicked.connect(self._on_search)
        self.search_input.returnPressed.connect(self._on_search)
        self.program_list.itemSelectionChanged.connect(self._on_program_selected)
        self.content_tree.itemSelectionChanged.connect(self._on_tree_selected)
        self.search_results.cellDoubleClicked.connect(self._on_search_result_activated)
        self.search_results.itemSelectionChanged.connect(self._on_search_result_selected)
        self.admin_button.clicked.connect(self._on_open_admin)
        self.editor_button.clicked.connect(self._on_open_editor)
        self.materials_list.itemDoubleClicked.connect(self._on_open_material_item)
        self.report_table.itemSelectionChanged.connect(self._on_report_selection_changed)
        self.open_material_button.clicked.connect(self._on_open_material)
        self.show_material_button.clicked.connect(self._on_show_material)
        self.copy_material_button.clicked.connect(self._on_copy_material)
        self.language_combo.currentIndexChanged.connect(self._on_language_combo_changed)
        self.font_combo.currentTextChanged.connect(self._on_font_size_changed)

    def _apply_word_wrap(self) -> None:
        self.program_list.setWordWrap(True)
        self.program_list.setTextElideMode(Qt.ElideNone)
        self.program_list.setUniformItemSizes(False)
        self.materials_list.setWordWrap(True)
        self.materials_list.setTextElideMode(Qt.ElideNone)
        self.materials_list.setUniformItemSizes(False)
        self.content_tree.setWordWrap(True)
        self.content_tree.setUniformRowHeights(False)
        self.content_tree.setTextElideMode(Qt.ElideNone)
        self.search_results.setWordWrap(True)
        self.search_results.setTextElideMode(Qt.ElideNone)
        self.search_results.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.report_table.setWordWrap(True)
        self.report_table.setTextElideMode(Qt.ElideNone)
        self.report_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.search_results.resizeRowsToContents()
        self.search_results.resizeColumnsToContents()
        self._sync_tree_columns()
        self._rewrap_tree_texts()
        self._update_tree_item_sizes()
        self.content_tree.doItemsLayout()
        self.content_tree.viewport().update()
        self.program_list.doItemsLayout()
        self.materials_list.doItemsLayout()
        self.report_table.resizeRowsToContents()
        self.report_table.resizeColumnsToContents()

    def _restart_application(self) -> None:
        QProcess.startDetached(sys.executable, sys.argv)
        QApplication.quit()

    def _close_application(self) -> None:
        QApplication.quit()

    def _wrap_with_label(self, widget: QWidget, label: QLabel) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(label)
        layout.addWidget(widget)
        return wrapper

    def _load_programs(self) -> None:
        self.program_list.clear()
        self.program_items.clear()
        for program in self.controller.get_programs():
            item = QListWidgetItem(program.name)
            item.setData(Qt.UserRole, program.id)
            self.program_list.addItem(item)
            self.program_items[program.id] = item

    def _on_program_selected(self) -> None:
        selected = self.program_list.currentItem()
        if not selected:
            return
        program_id = selected.data(Qt.UserRole)
        self._load_program_structure(program_id, select_last_discipline=False)
        details = self.controller.get_entity_details("program", program_id)
        self._show_details(details)
        self._load_materials("program", program_id)
        self._refresh_report(program_id)
        self.last_program_id = program_id

    def _load_program_structure(self, program_id: int, select_last_discipline: bool = True) -> None:
        self.content_tree.clear()
        self.tree_items.clear()
        disciplines = self.controller.get_program_structure(program_id)
        for discipline in disciplines:
            discipline_item = QTreeWidgetItem([discipline.name, self.tr("Discipline")])
            discipline_item.setData(0, Qt.UserRole + 10, discipline.name)
            discipline_item.setData(0, Qt.UserRole, ("discipline", discipline.id))
            self.tree_items[("discipline", discipline.id)] = discipline_item
            for topic in discipline.topics:
                topic_item = QTreeWidgetItem([topic.title, self.tr("Topic")])
                topic_item.setData(0, Qt.UserRole + 10, topic.title)
                topic_item.setData(0, Qt.UserRole, ("topic", topic.id))
                self.tree_items[("topic", topic.id)] = topic_item
                for lesson in topic.lessons:
                    lesson_item = QTreeWidgetItem([lesson.title, self.tr("Lesson")])
                    lesson_item.setData(0, Qt.UserRole + 10, lesson.title)
                    lesson_item.setData(0, Qt.UserRole, ("lesson", lesson.id))
                    self.tree_items[("lesson", lesson.id)] = lesson_item
                    for question in lesson.questions:
                        question_item = QTreeWidgetItem([question.content, self.tr("Question")])
                        question_item.setData(0, Qt.UserRole + 10, question.content)
                        question_item.setData(0, Qt.UserRole, ("question", question.id))
                        self.tree_items[("question", question.id)] = question_item
                        lesson_item.addChild(question_item)
                    topic_item.addChild(lesson_item)
                discipline_item.addChild(topic_item)
            self.content_tree.addTopLevelItem(discipline_item)
        self.content_tree.expandAll()
        self._sync_tree_columns()
        self._rewrap_tree_texts()
        self._update_tree_item_sizes()
        self.content_tree.doItemsLayout()
        self.content_tree.viewport().update()
        if select_last_discipline and self.last_discipline_id:
            item = self.tree_items.get(("discipline", self.last_discipline_id))
            if item:
                self.content_tree.setCurrentItem(item)

    def _on_tree_selected(self) -> None:
        item = self.content_tree.currentItem()
        if not item:
            return
        entity_type, entity_id = item.data(0, Qt.UserRole)
        details = self.controller.get_entity_details(entity_type, entity_id)
        self._show_details(details)
        self._load_materials(entity_type, entity_id)
        if entity_type == "discipline":
            self.last_discipline_id = entity_id
        elif entity_type == "topic":
            disciplines = self.controller.discipline_repo.get_disciplines_for_topic(entity_id)
            if disciplines:
                self.last_discipline_id = disciplines[0].id
        elif entity_type == "lesson":
            disciplines = self.controller.discipline_repo.get_disciplines_for_lesson(entity_id)
            if disciplines:
                self.last_discipline_id = disciplines[0].id
        elif entity_type == "question":
            disciplines = self.controller.discipline_repo.get_disciplines_for_question(entity_id)
            if disciplines:
                self.last_discipline_id = disciplines[0].id

    def _show_details(self, details: Dict[str, object]) -> None:
        if not details:
            self.details.setPlainText("")
            return
        meta = details.get("meta", {})
        lines = [details.get("title", ""), "", details.get("description", "")]
        if isinstance(meta, dict):
            meta_lines = []
            if "level" in meta:
                meta_lines.append(f"{self.tr('Level')}: {meta.get('level') or self.tr('N/A')}")
            if "year" in meta:
                meta_lines.append(f"{self.tr('Year')}: {meta.get('year') or self.tr('N/A')}")
            if "duration_hours" in meta:
                meta_lines.append(f"{self.tr('Total hours')}: {meta.get('duration_hours')} {self.tr('hours')}")
            if "classroom_hours" in meta:
                classroom = meta.get("classroom_hours")
                if classroom is not None:
                    meta_lines.append(f"{self.tr('Classroom hours')}: {classroom} {self.tr('hours')}")
            if "self_study_hours" in meta:
                self_study = meta.get("self_study_hours")
                if self_study is not None:
                    meta_lines.append(f"{self.tr('Self-study hours')}: {self_study} {self.tr('hours')}")
            if "order_index" in meta:
                meta_lines.append(f"{self.tr('Order')}: {meta.get('order_index')}")
            if "lesson_type" in meta:
                lesson_type = meta.get("lesson_type") or self.tr("N/A")
                meta_lines.append(f"{self.tr('Lesson type')}: {lesson_type}")
            if "material_type" in meta:
                material_type = meta.get("material_type")
                material_type_label = self._translate_material_type(material_type)
                meta_lines.append(f"{self.tr('Type')}: {material_type_label}")
            if "file_name" in meta:
                file_name = meta.get("file_name") or self.tr("No file")
                meta_lines.append(f"{self.tr('File')}: {file_name}")
            if "teachers" in meta:
                teachers = meta.get("teachers") or self.tr("Not assigned")
                meta_lines.append(f"{self.tr('Teachers')}: {teachers}")
            if "email" in meta:
                meta_lines.append(f"{self.tr('Email')}: {meta.get('email') or self.tr('N/A')}")
            if "phone" in meta:
                meta_lines.append(f"{self.tr('Phone')}: {meta.get('phone') or self.tr('N/A')}")
            if "rank" in meta:
                rank = meta.get("rank") or self.tr("N/A")
                meta_lines.append(f"{self.tr('Military rank')}: {rank}")
            if meta_lines:
                lines.append("")
                lines.extend(meta_lines)
        else:
            lines.extend(["", str(meta)])
        text = "\n".join(line for line in lines if line is not None)
        self.details.setPlainText(text.strip())

    def _load_materials(self, entity_type: str, entity_id: int) -> None:
        self.materials_list.clear()
        materials = self.controller.get_materials_for_entity(entity_type, entity_id)
        if entity_type == "program":
            for discipline in self.controller.get_program_disciplines(entity_id):
                materials.extend(self.controller.get_materials_for_entity("discipline", discipline.id))
        elif entity_type == "discipline":
            # keep only discipline-level materials
            pass
        unique = {material.id: material for material in materials if material.id is not None}
        for material in unique.values():
            material_type_label = self._translate_material_type(material.material_type)
            label = f"{material.title} ({material_type_label})"
            filename = material.original_filename or material.file_name
            if filename:
                label += f" | {filename}"
            teachers = ", ".join(t.full_name for t in material.teachers) if material.teachers else ""
            if teachers:
                label += f" | {self.tr('Teachers')}: {teachers}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, material)
            self.materials_list.addItem(item)

    def _update_tree_item_sizes(self) -> None:
        fm = self.content_tree.fontMetrics()
        line_height = fm.lineSpacing()
        padding = 6

        def update_item(item):
            if not item:
                return
            text = item.text(0) or ""
            lines = text.count("\n") + 1
            height = max(line_height * lines + padding, line_height + padding)
            item.setSizeHint(0, QSize(self.content_tree.columnWidth(0), height))
            item.setSizeHint(1, QSize(self.content_tree.columnWidth(1), height))
            for i in range(item.childCount()):
                update_item(item.child(i))

        for i in range(self.content_tree.topLevelItemCount()):
            update_item(self.content_tree.topLevelItem(i))

    def _rewrap_tree_texts(self) -> None:
        base_width = self.content_tree.columnWidth(0) - 8
        if base_width <= 0:
            return
        font = self.content_tree.font()
        indent_step = self.content_tree.indentation() or 0

        def depth(item):
            d = 0
            parent = item.parent()
            while parent is not None:
                d += 1
                parent = parent.parent()
            return d

        def wrap_item(item):
            if not item:
                return
            d = depth(item)
            width = max(120, base_width - (indent_step * d) - 8)
            full_text = item.data(0, Qt.UserRole + 10) or item.text(0)
            wrapped = self._wrap_text(full_text, width, font)
            item.setText(0, wrapped)
            for i in range(item.childCount()):
                wrap_item(item.child(i))

        for i in range(self.content_tree.topLevelItemCount()):
            wrap_item(self.content_tree.topLevelItem(i))

    def _sync_tree_columns(self) -> None:
        header = self.content_tree.header()
        if header is None:
            return
        viewport_width = self.content_tree.viewport().width()
        if viewport_width <= 0:
            return
        type_width = self.content_tree.columnWidth(1)
        min_title_width = 200
        min_type_width = 60
        if type_width < min_type_width:
            type_width = min_type_width
            self._tree_syncing_columns = True
            try:
                self.content_tree.setColumnWidth(1, type_width)
            finally:
                self._tree_syncing_columns = False
        title_width = max(min_title_width, viewport_width - type_width - 12)
        self._tree_syncing_columns = True
        try:
            self.content_tree.setColumnWidth(0, title_width)
        finally:
            self._tree_syncing_columns = False

    def _on_tree_header_resized(self, logical_index: int, old_size: int, new_size: int) -> None:
        if self._tree_syncing_columns:
            return
        if logical_index == 1:
            self._sync_tree_columns()
        self._rewrap_tree_texts()
        self._update_tree_item_sizes()
        self.content_tree.doItemsLayout()
        self.content_tree.viewport().update()

    def _wrap_text(self, text: str, width: int, font: QFont) -> str:
        if not text:
            return ""
        fm = QFontMetrics(font)
        if fm.horizontalAdvance(text) <= width:
            return text
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if fm.horizontalAdvance(candidate) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                if fm.horizontalAdvance(word) > width:
                    chunk = ""
                    for ch in word:
                        if fm.horizontalAdvance(chunk + ch) <= width:
                            chunk += ch
                        else:
                            if chunk:
                                lines.append(chunk)
                            chunk = ch
                    current = chunk
                else:
                    current = word
        if current:
            lines.append(current)
        return "\n".join(lines)

    def _on_search(self) -> None:
        keyword = self.search_input.text().strip()
        results = self.controller.search(keyword)
        self.search_results.setRowCount(0)
        for result in results:
            row = self.search_results.rowCount()
            self.search_results.insertRow(row)
            context = self._build_search_context(result)
            description = result.description
            if context:
                description = f"{description} | {context}" if description else context
            self.search_results.setItem(row, 0, QTableWidgetItem(self._translate_entity_type(result.entity_type)))
            self.search_results.setItem(row, 1, QTableWidgetItem(result.title))
            self.search_results.setItem(row, 2, QTableWidgetItem(description))
            self.search_results.item(row, 0).setData(Qt.UserRole, result)
        self.search_results.resizeRowsToContents()

    def _on_search_result_selected(self) -> None:
        row = self.search_results.currentRow()
        if row < 0:
            return
        result_item = self.search_results.item(row, 0)
        if not result_item:
            return
        result = result_item.data(Qt.UserRole)
        if result:
            self._navigate_to_search_result(result, open_material=False)

    def _on_search_result_activated(self, row: int, _column: int) -> None:
        result_item = self.search_results.item(row, 0)
        if not result_item:
            return
        result = result_item.data(Qt.UserRole)
        if result:
            self._navigate_to_search_result(result, open_material=True)

    def _navigate_to_search_result(self, result, open_material: bool) -> None:
        if result.entity_type == "material" and open_material:
            material = self.controller.material_repo.get_by_id(result.entity_id)
            if not material or not material.relative_path:
                QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
                return
            if not self.file_storage.open_file(material.relative_path):
                QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))
            return

        navigation = self.controller.resolve_search_navigation(result)
        program_id = navigation.get("program_id")
        if program_id and program_id in self.program_items:
            if program_id != self.last_program_id:
                self.program_list.blockSignals(True)
                self.program_list.setCurrentItem(self.program_items[program_id])
                self.program_list.blockSignals(False)
                self._load_program_structure(program_id, select_last_discipline=False)
                self._load_materials("program", program_id)
                self.last_program_id = program_id
            else:
                self.program_list.setCurrentItem(self.program_items[program_id])

        if result.entity_type == "program":
            details = self.controller.get_entity_details("program", result.entity_id)
            self._show_details(details)
            self._load_materials("program", result.entity_id)
            return

        target = None
        if navigation.get("question_id"):
            target = ("question", navigation["question_id"])
        elif navigation.get("lesson_id"):
            target = ("lesson", navigation["lesson_id"])
        elif navigation.get("topic_id"):
            target = ("topic", navigation["topic_id"])
        elif navigation.get("discipline_id"):
            target = ("discipline", navigation["discipline_id"])

        if target:
            item = self.tree_items.get(target)
            if item:
                self._select_tree_item(item)
                return

        details = self.controller.get_entity_details(result.entity_type, result.entity_id)
        self._show_details(details)

    def _select_tree_item(self, item: QTreeWidgetItem) -> None:
        current = item.parent()
        while current:
            current.setExpanded(True)
            current = current.parent()
        self.content_tree.setCurrentItem(item)
        self.content_tree.scrollToItem(item)

    def _on_open_admin(self) -> None:
        dialog = AdminDialog(self.controller.db, self.i18n, self.settings, self)
        dialog.exec()
        # Always refresh after admin dialog closes to sync UI state.
        self._load_programs()
        if self.last_program_id and self.last_program_id in self.program_items:
            self.program_list.setCurrentItem(self.program_items[self.last_program_id])
        else:
            self._load_program_structure(self.last_program_id) if self.last_program_id else None
        if self.last_program_id:
            self._refresh_report(self.last_program_id)

    def _on_open_editor(self) -> None:
        from ..ui.dialogs import PasswordDialog

        while True:
            dialog = PasswordDialog(
                self,
                title=self.tr("Editor Access"),
                label=self.tr("Enter editor password:"),
            )
            if dialog.exec() != QDialog.Accepted:
                return
            if self.auth_service.verify_editor_password(dialog.get_password()):
                break
            QMessageBox.warning(self, self.tr("Access denied"), self.tr("Invalid editor password."))
        wizard = EditorWizardDialog(self.controller.db, self.i18n, self)
        wizard.exec()
        self._load_programs()
        if self.last_program_id and self.last_program_id in self.program_items:
            self.program_list.setCurrentItem(self.program_items[self.last_program_id])
        else:
            self._load_program_structure(self.last_program_id) if self.last_program_id else None
        if self.last_program_id:
            self._refresh_report(self.last_program_id)

    def _on_open_material(self) -> None:
        items = self.materials_list.selectedItems()
        if not items:
            return
        for item in items:
            material = item.data(Qt.UserRole)
            if not material.relative_path:
                QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
                continue
            if not self.file_storage.open_file(material.relative_path):
                QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

    def _on_open_material_item(self, item: QListWidgetItem) -> None:
        material = item.data(Qt.UserRole)
        if not material:
            return
        if not material.relative_path:
            QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
            return
        if not self.file_storage.open_file(material.relative_path):
            QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

    def _on_show_material(self) -> None:
        items = self.materials_list.selectedItems()
        if not items:
            return
        for item in items:
            material = item.data(Qt.UserRole)
            if not material.relative_path:
                QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
                continue
            if not self.file_storage.show_in_folder(material.relative_path):
                QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

    def _on_copy_material(self) -> None:
        items = self.materials_list.selectedItems()
        if not items:
            return
        if len(items) == 1:
            material = items[0].data(Qt.UserRole)
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
            return

        dest_dir = QFileDialog.getExistingDirectory(self, self.tr("Copy file as..."), "")
        if not dest_dir:
            return
        used_names = set()
        for item in items:
            material = item.data(Qt.UserRole)
            if not material.relative_path:
                continue
            base_name, ext = self._material_copy_name_parts(material)
            author_suffix = self._material_copy_author_suffix(material)
            filename = f"{base_name}{author_suffix}{ext}"
            filename = self._sanitize_filename(filename)
            filename = self._ensure_unique_filename(dest_dir, filename, used_names)
            target = os.path.join(dest_dir, filename)
            if not self.file_storage.copy_file_as(material.relative_path, target):
                QMessageBox.warning(self, self.tr("No File"), self.tr("File is missing in storage."))

    def _refresh_report(self, program_id: int) -> None:
        self.report_table.clear()
        self._report_rows = []
        disciplines = self.controller.get_program_disciplines(program_id)
        discipline_ids = [d.id for d in disciplines if d and d.id is not None]
        teachers = self.controller.get_teachers_for_disciplines(discipline_ids)

        lessons = []
        program_structure = self.controller.get_program_structure(program_id)
        for discipline in program_structure:
            topic_index = 1
            for topic in discipline.topics:
                lesson_index = 1
                for lesson in topic.lessons:
                    lesson_type = (lesson.lesson_type_name or "").strip().lower()
                    is_self_study = "самостійна" in lesson_type or "self-study" in lesson_type or "self study" in lesson_type
                    if is_self_study:
                        code = f"т.{topic_index}.ср"
                    else:
                        code = f"т.{topic_index}.з.{lesson_index}"
                    lessons.append(
                        {
                            "code": code,
                            "lesson": lesson,
                            "discipline": discipline,
                            "topic": topic,
                            "is_self_study": is_self_study,
                        }
                    )
                    self._report_rows.append(lesson)
                    if not is_self_study:
                        lesson_index += 1
                topic_index += 1

        if not teachers or not lessons:
            self.report_table.setRowCount(0)
            self.report_table.setColumnCount(0)
            return

        cell_map = {}
        cell_types = {}
        teachers_with_materials = set()
        for lesson_row, info in enumerate(lessons):
            lesson = info["lesson"]
            materials = self.controller.get_materials_for_entity("lesson", lesson.id)
            for material in materials:
                for teacher in material.teachers:
                    if teacher.id is None:
                        continue
                    teachers_with_materials.add(teacher.id)
                    key = (lesson_row, teacher.id)
                    cell_map.setdefault(key, []).append(material.title)
                    raw_type = (material.material_type or "").strip().lower()
                    normalized = "guide" if raw_type == "metod" else raw_type
                    cell_types.setdefault(key, set()).add(normalized)

        teachers = sorted(
            teachers,
            key=lambda t: (t.id not in teachers_with_materials, t.full_name.lower()),
        )

        self.report_table.setRowCount(len(lessons))
        self.report_table.setColumnCount(len(teachers) + 1)
        headers = [self.tr("Lesson")] + [
            (f"{t.military_rank}\n{t.full_name}" if t.military_rank else t.full_name) for t in teachers
        ]
        self.report_table.setHorizontalHeaderLabels(headers)

        for row_index, info in enumerate(lessons):
            self.report_table.setItem(row_index, 0, QTableWidgetItem(info["code"]))
            for col_offset, teacher in enumerate(teachers, start=1):
                titles = cell_map.get((row_index, teacher.id), [])
                item = QTableWidgetItem("\n".join(titles) if titles else "")
                types = cell_types.get((row_index, teacher.id), set())
                if info.get("is_self_study"):
                    normalized = [title.lower() for title in titles]
                    has_cadets = any(("курсант" in t) or ("слухач" in t) for t in normalized)
                    has_teachers = any("викладач" in t for t in normalized)
                    if len(titles) >= 2 and has_cadets and has_teachers:
                        item.setBackground(QBrush(QColor(198, 239, 206)))
                    elif titles:
                        item.setBackground(QBrush(QColor(255, 242, 204)))
                    else:
                        item.setBackground(QBrush(QColor(255, 199, 206)))
                else:
                    has_plan = "plan" in types
                    has_guide = "guide" in types
                    has_presentation = "presentation" in types
                    if has_plan and has_guide and has_presentation:
                        item.setBackground(QBrush(QColor(198, 239, 206)))
                    elif types:
                        item.setBackground(QBrush(QColor(255, 242, 204)))
                    else:
                        item.setBackground(QBrush(QColor(255, 199, 206)))
                self.report_table.setItem(row_index, col_offset, item)

        for idx, info in enumerate(lessons):
            tooltip = f"{info['discipline'].name} | {info['topic'].title} | {info['lesson'].title}"
            row_item = self.report_table.item(idx, 0)
            if row_item:
                row_item.setToolTip(tooltip)
        self.report_table.resizeRowsToContents()
        self.report_table.resizeColumnsToContents()

    def _on_report_selection_changed(self) -> None:
        item = self.report_table.currentItem()
        if not item:
            return
        row = item.row()
        col = item.column()
        if not hasattr(self, "_report_rows"):
            return
        if row < 0 or row >= len(self._report_rows):
            return
        # Column 0 is the lesson code; other columns are per-teacher materials.
        if col > 0 and not item.text().strip():
            self._show_details({})
            self.materials_list.clear()
            return
        lesson = self._report_rows[row]
        details = self.controller.get_entity_details("lesson", lesson.id)
        self._show_details(details)
        self._load_materials("lesson", lesson.id)

    def _material_copy_name_parts(self, material) -> Tuple[str, str]:
        original = material.original_filename or ""
        if original:
            name, ext = os.path.splitext(original)
            if ext:
                return name, ext
        ext = f".{material.file_type}" if material.file_type else ""
        return material.title, ext

    def _material_copy_author_suffix(self, material) -> str:
        if not material.teachers:
            return ""
        full_name = material.teachers[0].full_name or ""
        parts = [p for p in full_name.split() if p]
        if not parts:
            return ""
        surname = parts[0]
        return f" - {surname}"

    def _sanitize_filename(self, name: str) -> str:
        cleaned = re.sub(r'[<>:"/\\\\|?*]+', "_", name)
        return cleaned.strip().strip(".")

    def _ensure_unique_filename(self, dest_dir: str, filename: str, used_names: set) -> str:
        base, ext = os.path.splitext(filename)
        candidate = filename
        counter = 1
        while candidate in used_names or os.path.exists(os.path.join(dest_dir, candidate)):
            candidate = f"{base} ({counter}){ext}"
            counter += 1
        used_names.add(candidate)
        return candidate

    def _load_settings(self) -> None:
        geometry = self.settings.value("ui/main_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        splitter_state = self.settings.value("ui/main_splitter")
        if splitter_state:
            self.main_splitter.restoreState(splitter_state)
        center_state = self.settings.value("ui/center_splitter")
        if center_state:
            self.center_splitter.restoreState(center_state)

        last_discipline = self.settings.value("ui/last_discipline_id")
        if last_discipline:
            self.last_discipline_id = int(last_discipline)
        last_program = self.settings.value("ui/last_program_id")
        if last_program and int(last_program) in self.program_items:
            self.program_list.setCurrentItem(self.program_items[int(last_program)])

        current_language = self.i18n.current_language()
        index = self.language_combo.findData(current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        font_size = self.settings.value("ui/font_size")
        if font_size:
            idx = self.font_combo.findText(str(font_size))
            if idx >= 0:
                self.font_combo.setCurrentIndex(idx)

    def closeEvent(self, event) -> None:
        self.settings.setValue("ui/main_geometry", self.saveGeometry())
        self.settings.setValue("ui/main_splitter", self.main_splitter.saveState())
        self.settings.setValue("ui/center_splitter", self.center_splitter.saveState())
        if self.last_program_id:
            self.settings.setValue("ui/last_program_id", int(self.last_program_id))
        if self.last_discipline_id:
            self.settings.setValue("ui/last_discipline_id", int(self.last_discipline_id))
        self.settings.sync()
        super().closeEvent(event)

    def _on_language_combo_changed(self) -> None:
        language = self.language_combo.currentData()
        if language:
            self.i18n.set_language(language)

    def _on_font_size_changed(self, value: str) -> None:
        if not value:
            return
        try:
            size = int(value)
        except ValueError:
            return
        font = QFont(self.font())
        font.setPointSize(size)
        self.setFont(font)
        self.settings.setValue("ui/font_size", size)

    def _on_language_changed(self, _language: str) -> None:
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(self.tr("Educational Program Manager"))
        self.search_label.setText(self.tr("Search:"))
        self.search_button.setText(self.tr("Search"))
        self.editor_button.setText(self.tr("Editor Mode"))
        self.admin_button.setText(self.tr("Admin Mode"))
        self.menuBar().clear()
        app_menu = self.menuBar().addMenu(self.tr("Application"))
        self.action_restart = app_menu.addAction(self.tr("Restart application"))
        self.action_exit = app_menu.addAction(self.tr("Exit application"))
        self.action_restart.triggered.connect(self._restart_application)
        self.action_exit.triggered.connect(self._close_application)
        self.program_label.setText(self.tr("Programs"))
        self.structure_label.setText(self.tr("Program Structure"))
        self.search_results_label.setText(self.tr("Search Results"))
        self.details_label.setText(self.tr("Details"))
        self.materials_label.setText(self.tr("Methodical Materials"))
        self.open_material_button.setText(self.tr("Open Selected File"))
        self.show_material_button.setText(self.tr("Show in folder"))
        self.copy_material_button.setText(self.tr("Copy file as..."))
        self.content_tree.setHeaderLabels([self.tr("Title"), self.tr("Type")])
        self.search_results.setHorizontalHeaderLabels([self.tr("Type"), self.tr("Title"), self.tr("Description")])
        self._load_program_structure(self.last_program_id) if self.last_program_id else None
        if self.content_tree.currentItem():
            self._on_tree_selected()

    def _build_search_context(self, result) -> str:
        navigation = self.controller.resolve_search_navigation(result)
        parts = []
        if navigation.get("program_id"):
            program = self.controller.program_repo.get_by_id(navigation["program_id"])
            if program:
                parts.append(f"{self.tr('Program')}: {program.name}")
        if navigation.get("discipline_id"):
            discipline = self.controller.discipline_repo.get_by_id(navigation["discipline_id"])
            if discipline:
                parts.append(f"{self.tr('Discipline')}: {discipline.name}")
        if navigation.get("topic_id"):
            topic = self.controller.topic_repo.get_by_id(navigation["topic_id"])
            if topic:
                parts.append(f"{self.tr('Topic')}: {topic.title}")
        if navigation.get("lesson_id"):
            lesson = self.controller.lesson_repo.get_by_id(navigation["lesson_id"])
            if lesson:
                parts.append(f"{self.tr('Lesson')}: {lesson.title}")
        return " | ".join(parts)

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


class _WrapItemDelegate(QStyledItemDelegate):
    def __init__(self, view):
        super().__init__(view)
        self._view = view

    def initStyleOption(self, option, index):  # noqa: ANN001
        super().initStyleOption(option, index)
        if index.column() == 0:
            option.textElideMode = Qt.ElideNone
            option.wrapText = True

    def sizeHint(self, option, index):  # noqa: ANN001
        if index.column() != 0:
            return super().sizeHint(option, index)
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
        if index.column() != 0:
            return super().paint(painter, option, index)
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
