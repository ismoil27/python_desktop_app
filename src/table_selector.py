# # table_selector.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QHBoxLayout, QPushButton
)

from PySide6.QtCore import Qt
import pymysql


class TableSelector(QGroupBox):
    """Table selection panel."""

    def __init__(self, title="테이블 선택", parent=None):
        super().__init__(title, parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["선택", "테이블 이름", "행 개수"])

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(0, 60)
        self.table_widget.setColumnWidth(2, 100)
        layout.addWidget(self.table_widget)

        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("전체 선택")
        self.select_all_btn.clicked.connect(self.select_all)

        self.deselect_all_btn = QPushButton("선택 해제")
        self.deselect_all_btn.clicked.connect(self.deselect_all)

        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.deselect_all_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_tables(self, conn_info: dict):
        """
        Load real tables using connection info:
        conn_info = {
            'host': str,
            'port': int,
            'user': str,
            'password': str,
            'database': str
        }
        """
        try:
            connection = pymysql.connect(
                host=conn_info["host"],
                port=conn_info["port"],
                user=conn_info["user"],
                password=conn_info["password"],
                database=conn_info["database"]
            )
            cursor = connection.cursor()

            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            self.table_widget.setRowCount(len(tables))
            for i, (table_name,) in enumerate(tables):
                # Get row count for each table
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    row_count = cursor.fetchone()[0]
                except Exception:
                    row_count = "?"

                checkbox = QCheckBox()
                self.table_widget.setCellWidget(i, 0, checkbox)
                table_item = QTableWidgetItem(table_name)
                table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)

                count_item = QTableWidgetItem(str(row_count))
                count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)

                self.table_widget.setItem(i, 1, table_item)
                self.table_widget.setItem(i, 2, count_item)


            cursor.close()
            connection.close()

        except Exception as e:
            self.table_widget.setRowCount(0)
            self.table_widget.setItem(0, 1, QTableWidgetItem("불러오기 실패"))
            print("Failed to load tables:", e)

    def select_all(self):
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(True)

    def deselect_all(self):
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(False)

