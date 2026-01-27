"""Main application window."""
from typing import Dict, Tuple
from PySide6.QtCore import Qt, QSettings
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
)
from ..controllers.main_controller import MainController
from ..ui.admin_dialog import AdminDialog
from ..services.i18n import I18nManager


class MainWindow(QMainWindow):
    """Main window for user mode."""

    def __init__(self, controller: MainController, i18n: I18nManager, settings: QSettings):
        super().__init__()
        self.controller = controller
        self.i18n = i18n
        self.settings = settings
        self.program_items: Dict[int, QListWidgetItem] = {}
        self.tree_items: Dict[Tuple[str, int], QTreeWidgetItem] = {}
        self.last_program_id = None
        self.last_discipline_id = None
        self.setWindowTitle(self.tr("Educational Program Manager"))
        self.resize(1200, 720)
        self._build_ui()
        self._load_programs()
        self._load_settings()
        self.i18n.language_changed.connect(self._on_language_changed)

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        self.search_label = QLabel(self.tr("Search:"))
        top_bar.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_button = QPushButton(self.tr("Search"))
        self.language_combo = QComboBox()
        self.language_combo.addItem(self.tr("Ukrainian"), "uk")
        self.language_combo.addItem(self.tr("English"), "en")
        self.admin_button = QPushButton(self.tr("Admin Mode"))
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.search_button)
        top_bar.addWidget(self.language_combo)
        top_bar.addStretch(1)
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
        self.structure_label = QLabel(self.tr("Program Structure"))
        self.center_splitter.addWidget(self._wrap_with_label(self.content_tree, self.structure_label))

        self.search_results = QTableWidget(0, 3)
        self.search_results.setHorizontalHeaderLabels([self.tr("Type"), self.tr("Title"), self.tr("Description")])
        self.language_combo.setItemText(0, self.tr("Ukrainian"))
        self.language_combo.setItemText(1, self.tr("English"))
        self.search_results.horizontalHeader().setStretchLastSection(True)
        self.search_results_label = QLabel(self.tr("Search Results"))
        self.center_splitter.addWidget(self._wrap_with_label(self.search_results, self.search_results_label))

        self.main_splitter.addWidget(self.center_splitter)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details_label = QLabel(self.tr("Details"))
        right_layout.addWidget(self._wrap_with_label(self.details, self.details_label))

        self.materials_list = QListWidget()
        self.materials_label = QLabel(self.tr("Methodical Materials"))
        right_layout.addWidget(self._wrap_with_label(self.materials_list, self.materials_label))

        self.open_material_button = QPushButton(self.tr("Open Selected File"))
        right_layout.addWidget(self.open_material_button)

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
        self.admin_button.clicked.connect(self._on_open_admin)
        self.open_material_button.clicked.connect(self._on_open_material)
        self.language_combo.currentIndexChanged.connect(self._on_language_combo_changed)

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
        self._load_program_structure(program_id)
        details = self.controller.get_entity_details("program", program_id)
        self._show_details(details)
        self._load_materials("program", program_id)
        self.last_program_id = program_id

    def _load_program_structure(self, program_id: int) -> None:
        self.content_tree.clear()
        self.tree_items.clear()
        disciplines = self.controller.get_program_structure(program_id)
        for discipline in disciplines:
            discipline_item = QTreeWidgetItem([discipline.name, self.tr("Discipline")])
            discipline_item.setData(0, Qt.UserRole, ("discipline", discipline.id))
            self.tree_items[("discipline", discipline.id)] = discipline_item
            for topic in discipline.topics:
                topic_item = QTreeWidgetItem([topic.title, self.tr("Topic")])
                topic_item.setData(0, Qt.UserRole, ("topic", topic.id))
                self.tree_items[("topic", topic.id)] = topic_item
                for lesson in topic.lessons:
                    lesson_item = QTreeWidgetItem([lesson.title, self.tr("Lesson")])
                    lesson_item.setData(0, Qt.UserRole, ("lesson", lesson.id))
                    self.tree_items[("lesson", lesson.id)] = lesson_item
                    for question in lesson.questions:
                        title = question.content if len(question.content) <= 60 else f"{question.content[:60]}..."
                        question_item = QTreeWidgetItem([title, self.tr("Question")])
                        question_item.setData(0, Qt.UserRole, ("question", question.id))
                        self.tree_items[("question", question.id)] = question_item
                        lesson_item.addChild(question_item)
                    topic_item.addChild(lesson_item)
                discipline_item.addChild(topic_item)
            self.content_tree.addTopLevelItem(discipline_item)
        self.content_tree.expandAll()
        if self.last_discipline_id:
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
            if "difficulty_level" in meta:
                meta_lines.append(f"{self.tr('Difficulty')}: {meta.get('difficulty_level')}")
            if "answer" in meta:
                answer = meta.get("answer") or self.tr("Not provided")
                meta_lines.append(f"{self.tr('Answer')}: {answer}")
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
            if meta_lines:
                lines.extend(["", " | ".join(meta_lines)])
        else:
            lines.extend(["", str(meta)])
        text = "\n".join(line for line in lines if line is not None)
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
            context = self._build_search_context(result)
            description = result.description
            if context:
                description = f"{description} | {context}" if description else context
            self.search_results.setItem(row, 0, QTableWidgetItem(self._translate_entity_type(result.entity_type)))
            self.search_results.setItem(row, 1, QTableWidgetItem(result.title))
            self.search_results.setItem(row, 2, QTableWidgetItem(description))
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
        if navigation.get("discipline_id"):
            item = self.tree_items.get(("discipline", navigation["discipline_id"]))
            if item:
                self.content_tree.setCurrentItem(item)
                return
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
        dialog = AdminDialog(self.controller.db, self.i18n, self)
        if dialog.exec():
            self._load_programs()

    def _on_open_material(self) -> None:
        item = self.materials_list.currentItem()
        if not item:
            return
        material = item.data(Qt.UserRole)
        if not material.file_path:
            QMessageBox.information(self, self.tr("No File"), self.tr("This material has no attached file."))
            return
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl

        QDesktopServices.openUrl(QUrl.fromLocalFile(material.file_path))

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

    def closeEvent(self, event) -> None:
        self.settings.setValue("ui/main_geometry", self.saveGeometry())
        self.settings.setValue("ui/main_splitter", self.main_splitter.saveState())
        self.settings.setValue("ui/center_splitter", self.center_splitter.saveState())
        if self.last_program_id:
            self.settings.setValue("ui/last_program_id", int(self.last_program_id))
        if self.last_discipline_id:
            self.settings.setValue("ui/last_discipline_id", int(self.last_discipline_id))
        super().closeEvent(event)

    def _on_language_combo_changed(self) -> None:
        language = self.language_combo.currentData()
        if language:
            self.i18n.set_language(language)

    def _on_language_changed(self, _language: str) -> None:
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(self.tr("Educational Program Manager"))
        self.search_label.setText(self.tr("Search:"))
        self.search_button.setText(self.tr("Search"))
        self.admin_button.setText(self.tr("Admin Mode"))
        self.program_label.setText(self.tr("Programs"))
        self.structure_label.setText(self.tr("Program Structure"))
        self.search_results_label.setText(self.tr("Search Results"))
        self.details_label.setText(self.tr("Details"))
        self.materials_label.setText(self.tr("Methodical Materials"))
        self.open_material_button.setText(self.tr("Open Selected File"))
        self.content_tree.setHeaderLabels([self.tr("Title"), self.tr("Type")])
        self.search_results.setHorizontalHeaderLabels([self.tr("Type"), self.tr("Title"), self.tr("Description")])
        self._load_program_structure(self.last_program_id) if self.last_program_id else None
        if self.content_tree.currentItem():
            self._on_tree_selected()

    def _build_search_context(self, result) -> str:
        navigation = self.controller.resolve_search_navigation(result)
        parts = []
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
