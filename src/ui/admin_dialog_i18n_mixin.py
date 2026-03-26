"""UI translation updates for AdminDialog."""

from __future__ import annotations

from PySide6.QtWidgets import QMenuBar


class AdminDialogI18nMixin:
    """Retranslation logic for controls inside AdminDialog."""

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
        self.tabs.setTabText(4, self.tr("Internet"))
        self.tabs.setTabText(5, self.tr("Log"))
        self.tabs.setTabText(6, self.tr("Settings"))
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
        if hasattr(self, "internet_db_group"):
            self.internet_db_group.setTitle(self.tr("Internet database connection"))
            self.internet_db_host_label.setText(self.tr("Host"))
            self.internet_db_port_label.setText(self.tr("Port"))
            self.internet_db_name_label.setText(self.tr("Database"))
            self.internet_db_user_label.setText(self.tr("Login"))
            self.internet_db_password_label.setText(self.tr("Password"))
            self.internet_db_save.setText(self.tr("Save"))
            self.internet_db_connect.setText(self.tr("Connect"))
            self.internet_db_sync.setText(self.tr("Synchronize"))
            if self.internet_sync_direction.count() >= 2:
                self.internet_sync_direction.setItemText(0, self.tr("Local -> Internet"))
                self.internet_sync_direction.setItemText(1, self.tr("Internet -> Local"))
        if hasattr(self, "internet_db_status") and not self.internet_db_status.text().strip():
            self.internet_db_status.setText(self.tr("Not connected"))
        if hasattr(self, "log_table"):
            self.log_table.setHorizontalHeaderLabels(
                [
                    self.tr("Time"),
                    self.tr("User"),
                    self.tr("Mode"),
                    self.tr("Action"),
                    self.tr("Details"),
                ]
            )
            self.log_refresh_btn.setText(self.tr("Refresh"))
            self.log_clear_btn.setText(self.tr("Clear log"))
            if hasattr(self, "log_scope_toggle"):
                if getattr(self, "_log_show_full", False):
                    self.log_scope_toggle.setText(self.tr("Show recent log"))
                else:
                    self.log_scope_toggle.setText(self.tr("Show full log"))
            if hasattr(self, "log_limit_hint"):
                if getattr(self, "_log_show_full", False):
                    self.log_limit_hint.setText(self.tr("Showing all records."))
                else:
                    self.log_limit_hint.setText(self.tr("Showing up to last 1000 records."))

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
        if hasattr(self, "passwords_label"):
            self.passwords_label.setText(self.tr("Access passwords"))
        if hasattr(self, "change_admin_password_btn"):
            self.change_admin_password_btn.setText(self.tr("Change admin password"))
        if hasattr(self, "change_editor_password_btn"):
            self.change_editor_password_btn.setText(self.tr("Change editor password"))
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
