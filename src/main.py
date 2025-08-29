# main.py

import sys
import traceback
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from connection_panel import ConnectionPanel
from table_selector import TableSelector
from progress_panel import ProgressPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left_connection_panel = None
        self.table_selector = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("데이터베이스 테이블 내보내기 / 가져오기")
        self.setGeometry(100, 100, 1400, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        self.create_header(main_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.create_left_panel())
        splitter.addWidget(self.create_right_panel())
        splitter.setSizes([700, 700])
        main_layout.addWidget(splitter)

        central_widget.setLayout(main_layout)

        # Optional: Load QSS if exists
        try:
            with open("style.qss", "r") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except FileNotFoundError:
            print("style.qss not found — skipping stylesheet.")

    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #343a40;
                color: white;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QLabel { color: white; }
        """)
        header_layout = QVBoxLayout()
        title_label = QLabel("데이터베이스 테이블 내보내기 / 가져오기")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        version_label = QLabel("버전 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(version_label)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

    def create_left_panel(self):
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: #fff5f5; border-radius: 10px; }")
        layout = QVBoxLayout()

        title_label = QLabel("📤 내보내기 (원본)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #dc3545; margin: 10px;")
        layout.addWidget(title_label)

        # Store references
        self.left_connection_panel = ConnectionPanel("데이터베이스 연결")
        self.table_selector = TableSelector("내보낼 테이블 선택")

        layout.addWidget(self.left_connection_panel)
        layout.addWidget(self.table_selector)
        panel.setLayout(layout)

        # Connect button click to handler
        self.left_connection_panel.test_btn.clicked.connect(self.handle_left_connection)

        return panel

    def create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: #f0fff4; border-radius: 10px; }")
        layout = QVBoxLayout()
        title_label = QLabel("📥 가져오기 (대상)")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #28a745; margin: 10px;")
        layout.addWidget(title_label)
        layout.addWidget(ConnectionPanel("데이터베이스 연결"))
        layout.addWidget(ProgressPanel("가져오기 옵션 및 진행 상태"))
        panel.setLayout(layout)
        return panel

    def handle_left_connection(self):
        """Called when test connection button is clicked."""
        if "연결됨" in self.left_connection_panel.status_label.text():
            conn_info = {
                "host": self.left_connection_panel.host.text().strip(),
                "port": int(self.left_connection_panel.port.text().strip()),
                "user": self.left_connection_panel.username.text().strip(),
                "password": self.left_connection_panel.password.text().strip(),
                "database": self.left_connection_panel.database.text().strip()
            }
            self.table_selector.load_tables(conn_info)


def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()

