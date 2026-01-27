"""Main application window."""
from typing import Dict, Tuple
from PySide6.QtCore import Qt
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
)
from ..controllers.main_controller import MainController
from ..ui.admin_dialog import AdminDialog


class MainWindow(QMainWindow):
    """Main window for user mode."""

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.program_items: Dict[int, QListWidgetItem] = {}
        self.tree_items: Dict[Tuple[str, int], QTreeWidgetItem] = {}
        self.setWindowTitle("Educational Program Manager")
        self.resize(1200, 720)
        self._build_ui()
        self._load_programs()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.admin_button = QPushButton("Admin Mode")
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.search_button)
        top_bar.addStretch(1)
        top_bar.addWidget(self.admin_button)
        layout.addLayout(top_bar)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)

        self.program_list = QListWidget()
        self.program_list.setMinimumWidth(220)
        splitter.addWidget(self._wrap_with_label(self.program_list, "Programs"))

        center_splitter = QSplitter()
        center_splitter.setOrientation(Qt.Vertical)

        self.content_tree = QTreeWidget()
        self.content_tree.setHeaderLabels(["Title", "Type"])
        self.content_tree.setColumnWidth(0, 350)
        center_splitter.addWidget(self._wrap_with_label(self.content_tree, "Program Structure"))

        self.search_results = QTableWidget(0, 3)
        self.search_results.setHorizontalHeaderLabels(["Type", "Title", "Description"])
        self.search_results.horizontalHeader().setStretchLastSection(True)
        center_splitter.addWidget(self._wrap_with_label(self.search_results, "Search Results"))

        splitter.addWidget(center_splitter)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        right_layout.addWidget(self._wrap_with_label(self.details, "Details"))

        self.materials_list = QListWidget()
        right_layout.addWidget(self._wrap_with_label(self.materials_list, "Methodical Materials"))

        self.open_material_button = QPushButton("Open Selected File")
        right_layout.addWidget(self.open_material_button)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)

        layout.addWidget(splitter)
        self.setCentralWidget(central)

        self.search_button.clicked.connect(self._on_search)
        self.search_input.returnPressed.connect(self._on_search)
        self.program_list.itemSelectionChanged.connect(self._on_program_selected)
        self.content_tree.itemSelectionChanged.connect(self._on_tree_selected)
        self.search_results.cellDoubleClicked.connect(self._on_search_result_activated)
        self.admin_button.clicked.connect(self._on_open_admin)
        self.open_material_button.clicked.connect(self._on_open_material)

    def _wrap_with_label(self, widget: QWidget, label: str) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(QLabel(label))
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
        self._load_program_structure(program_id)
        details = self.controller.get_entity_details("program", program_id)
        self._show_details(details)
        self._load_materials("program", program_id)

    def _load_program_structure(self, program_id: int) -> None:
        self.content_tree.clear()
        self.tree_items.clear()
        topics = self.controller.get_program_structure(program_id)
        for topic in topics:
            topic_item = QTreeWidgetItem([topic.title, "Topic"])
            topic_item.setData(0, Qt.UserRole, ("topic", topic.id))
            self.tree_items[("topic", topic.id)] = topic_item
            for lesson in topic.lessons:
                lesson_item = QTreeWidgetItem([lesson.title, "Lesson"])
                lesson_item.setData(0, Qt.UserRole, ("lesson", lesson.id))
                self.tree_items[("lesson", lesson.id)] = lesson_item
                for question in lesson.questions:
                    title = question.content if len(question.content) <= 60 else f"{question.content[:60]}..."
                    question_item = QTreeWidgetItem([title, "Question"])
                    question_item.setData(0, Qt.UserRole, ("question", question.id))
                    self.tree_items[("question", question.id)] = question_item
                    lesson_item.addChild(question_item)
                topic_item.addChild(lesson_item)
            self.content_tree.addTopLevelItem(topic_item)
        self.content_tree.expandAll()

    def _on_tree_selected(self) -> None:
        item = self.content_tree.currentItem()
        if not item:
            return
        entity_type, entity_id = item.data(0, Qt.UserRole)
        details = self.controller.get_entity_details(entity_type, entity_id)
        self._show_details(details)
        self._load_materials(entity_type, entity_id)

    def _show_details(self, details: Dict[str, str]) -> None:
        if not details:
            self.details.setPlainText("")
            return
        text = f"{details.get('title', '')}\n\n{details.get('description', '')}\n\n{details.get('meta', '')}"
        self.details.setPlainText(text.strip())

    def _load_materials(self, entity_type: str, entity_id: int) -> None:
        self.materials_list.clear()
        for material in self.controller.get_materials_for_entity(entity_type, entity_id):
            label = f"{material.title} ({material.material_type})"
            if material.file_name:
                label += f" | {material.file_name}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, material)
            self.materials_list.addItem(item)

    def _on_search(self) -> None:
        keyword = self.search_input.text().strip()
        results = self.controller.search(keyword)
        self.search_results.setRowCount(0)
        for result in results:
            row = self.search_results.rowCount()
            self.search_results.insertRow(row)
            self.search_results.setItem(row, 0, QTableWidgetItem(result.entity_type))
            self.search_results.setItem(row, 1, QTableWidgetItem(result.title))
            self.search_results.setItem(row, 2, QTableWidgetItem(result.description))
            self.search_results.item(row, 0).setData(Qt.UserRole, result)

    def _on_search_result_activated(self, row: int, _column: int) -> None:
        result_item = self.search_results.item(row, 0)
        if not result_item:
            return
        result = result_item.data(Qt.UserRole)
        navigation = self.controller.resolve_search_navigation(result)
        program_id = navigation.get("program_id")
        if program_id and program_id in self.program_items:
            self.program_list.setCurrentItem(self.program_items[program_id])
        if navigation.get("topic_id"):
            item = self.tree_items.get(("topic", navigation["topic_id"]))
            if item:
                self.content_tree.setCurrentItem(item)
                return
        if navigation.get("lesson_id"):
            item = self.tree_items.get(("lesson", navigation["lesson_id"]))
            if item:
                self.content_tree.setCurrentItem(item)
                return
        if navigation.get("question_id"):
            item = self.tree_items.get(("question", navigation["question_id"]))
            if item:
                self.content_tree.setCurrentItem(item)
                return
        if result.entity_type in {"teacher", "material"}:
            details = self.controller.get_entity_details(result.entity_type, result.entity_id)
            self._show_details(details)

    def _on_open_admin(self) -> None:
        dialog = AdminDialog(self.controller.db, self)
        if dialog.exec():
            self._load_programs()

    def _on_open_material(self) -> None:
        item = self.materials_list.currentItem()
        if not item:
            return
        material = item.data(Qt.UserRole)
        if not material.file_path:
            QMessageBox.information(self, "No File", "This material has no attached file.")
            return
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl

        QDesktopServices.openUrl(QUrl.fromLocalFile(material.file_path))
