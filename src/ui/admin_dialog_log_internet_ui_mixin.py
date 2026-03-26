"""Log tab and internet tab UI building for AdminDialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


class AdminDialogLogInternetUiMixin:
    """Build/refresh methods for log tab and internet tab."""

    def _build_log_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.log_table = QTableWidget(0, 5)
        self.log_table.setHorizontalHeaderLabels(
            [
                self.tr("Time"),
                self.tr("User"),
                self.tr("Mode"),
                self.tr("Action"),
                self.tr("Details"),
            ]
        )
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.log_table)

        btn_row = QHBoxLayout()
        self.log_refresh_btn = QPushButton(self.tr("Refresh"))
        self.log_clear_btn = QPushButton(self.tr("Clear log"))
        self.log_scope_toggle = QPushButton(self.tr("Show full log"))
        self._log_show_full = False
        self.log_limit_hint = QLabel(self.tr("Showing up to last 1000 records."))
        btn_row.addWidget(self.log_refresh_btn)
        btn_row.addWidget(self.log_clear_btn)
        btn_row.addWidget(self.log_scope_toggle)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)
        layout.addWidget(self.log_limit_hint)

        self.log_refresh_btn.clicked.connect(self._refresh_log_tab)
        self.log_clear_btn.clicked.connect(self._clear_log_tab)
        self.log_scope_toggle.clicked.connect(self._toggle_log_scope)
        self._refresh_log_tab()
        return tab

    def _build_internet_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.internet_db_group = QGroupBox(self.tr("Internet database connection"))
        form_layout = QFormLayout(self.internet_db_group)

        self.internet_db_host = QLineEdit()
        self.internet_db_port = QLineEdit()
        self.internet_db_name = QLineEdit()
        self.internet_db_user = QLineEdit()
        self.internet_db_password = QLineEdit()
        self.internet_db_password.setEchoMode(QLineEdit.Password)

        self.internet_db_host_label = QLabel(self.tr("Host"))
        self.internet_db_port_label = QLabel(self.tr("Port"))
        self.internet_db_name_label = QLabel(self.tr("Database"))
        self.internet_db_user_label = QLabel(self.tr("Login"))
        self.internet_db_password_label = QLabel(self.tr("Password"))

        form_layout.addRow(self.internet_db_host_label, self.internet_db_host)
        form_layout.addRow(self.internet_db_port_label, self.internet_db_port)
        form_layout.addRow(self.internet_db_name_label, self.internet_db_name)
        form_layout.addRow(self.internet_db_user_label, self.internet_db_user)
        form_layout.addRow(self.internet_db_password_label, self.internet_db_password)
        layout.addWidget(self.internet_db_group)

        actions_layout = QHBoxLayout()
        self.internet_db_indicator = QLabel()
        self.internet_db_indicator.setFixedSize(10, 10)
        self.internet_db_save = QPushButton(self.tr("Save"))
        self.internet_db_connect = QPushButton(self.tr("Connect"))
        self.internet_db_status = QLabel(self.tr("Not connected"))
        actions_layout.addWidget(self.internet_db_indicator)
        actions_layout.addWidget(self.internet_db_save)
        actions_layout.addWidget(self.internet_db_connect)
        actions_layout.addWidget(self.internet_db_status, 1)
        layout.addLayout(actions_layout)

        sync_layout = QHBoxLayout()
        self.internet_sync_direction = QComboBox()
        self.internet_sync_direction.addItem(self.tr("Local -> Internet"), "push")
        self.internet_sync_direction.addItem(self.tr("Internet -> Local"), "pull")
        self.internet_db_sync = QPushButton(self.tr("Synchronize"))
        sync_layout.addWidget(self.internet_sync_direction)
        sync_layout.addWidget(self.internet_db_sync)
        sync_layout.addStretch(1)
        layout.addLayout(sync_layout)
        layout.addStretch(1)

        self.internet_db_save.clicked.connect(self._save_internet_db_settings)
        self.internet_db_connect.clicked.connect(self._connect_internet_database)
        self.internet_db_sync.clicked.connect(self._synchronize_internet_database)
        self._load_internet_db_settings()
        return tab

    def _refresh_log_tab(self) -> None:
        limit = None if self._log_show_full else 1000
        rows = list(self.activity_log.read_all(limit=limit))
        rows.reverse()
        self.log_table.setRowCount(0)
        for row_data in rows:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)
            self.log_table.setItem(row, 0, QTableWidgetItem(str(row_data.get("timestamp", ""))))
            self.log_table.setItem(row, 1, QTableWidgetItem(str(row_data.get("user", ""))))
            self.log_table.setItem(row, 2, QTableWidgetItem(str(row_data.get("mode", ""))))
            self.log_table.setItem(row, 3, QTableWidgetItem(str(row_data.get("action", ""))))
            self.log_table.setItem(row, 4, QTableWidgetItem(str(row_data.get("details", ""))))
        self.log_table.resizeRowsToContents()
        if self._log_show_full:
            self.log_limit_hint.setText(self.tr("Showing all records."))
        else:
            self.log_limit_hint.setText(self.tr("Showing up to last 1000 records."))

    def _clear_log_tab(self) -> None:
        if QMessageBox.question(
            self,
            self.tr("Confirm"),
            self.tr("Clear all log records?"),
        ) != QMessageBox.Yes:
            return
        self.activity_log.clear()
        self._refresh_log_tab()
        self._log_action("clear_log", "Activity log was cleared")

    def _toggle_log_scope(self) -> None:
        self._log_show_full = not self._log_show_full
        if self._log_show_full:
            self.log_scope_toggle.setText(self.tr("Show recent log"))
        else:
            self.log_scope_toggle.setText(self.tr("Show full log"))
        self._refresh_log_tab()
