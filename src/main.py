import sys
import traceback
import pymysql
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QTextEdit, QGroupBox, QGridLayout, QHeaderView,
    QCheckBox, QSplitter, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


# -------------------- Connection Panel --------------------
class ConnectionPanel(QGroupBox):
    """연결 설정 패널"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("상태:"))
        self.status_label = QLabel("● 연결 끊김")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Connection form
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("데이터베이스 종류:"), 0, 0)
        self.db_type = QComboBox()
        self.db_type.addItems(["MySQL", "MariaDB", "PostgreSQL", "Oracle", "SQLite"])
        self.db_type.setCurrentText("MySQL")
        self.db_type.currentTextChanged.connect(self.update_form_fields)
        form_layout.addWidget(self.db_type, 0, 1)

        form_layout.addWidget(QLabel("호스트:"), 1, 0)
        self.host = QLineEdit("localhost")
        form_layout.addWidget(self.host, 1, 1)

        form_layout.addWidget(QLabel("포트:"), 2, 0)
        self.port = QLineEdit("3306")
        form_layout.addWidget(self.port, 2, 1)

        form_layout.addWidget(QLabel("사용자명:"), 3, 0)
        self.username = QLineEdit("root")
        form_layout.addWidget(self.username, 3, 1)

        form_layout.addWidget(QLabel("비밀번호:"), 4, 0)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password, 4, 1)

        form_layout.addWidget(QLabel("데이터베이스:"), 5, 0)
        self.database = QLineEdit()
        form_layout.addWidget(self.database, 5, 1)

        layout.addLayout(form_layout)

        # Test button
        self.test_btn = QPushButton("연결 테스트")
        self.test_btn.clicked.connect(self.test_connection)  # bind connection test
        layout.addWidget(self.test_btn)

        self.setLayout(layout)
        self.update_form_fields("MySQL")

    def update_form_fields(self, db_type):
        if db_type in ["MySQL", "MariaDB"]:
            self.port.setText("3306")
            self.host.setText("localhost")
            self.username.setText("root")
            self.database.setPlaceholderText("데이터베이스 이름")
            self._enable_standard_fields(True)
        elif db_type == "PostgreSQL":
            self.port.setText("5432")
            self._enable_standard_fields(False)
        elif db_type == "Oracle":
            self.port.setText("1521")
            self._enable_standard_fields(False)
        elif db_type == "SQLite":
            self.host.clear()
            self.port.clear()
            self.username.clear()
            self.password.clear()
            self.host.setEnabled(False)
            self.port.setEnabled(False)
            self.username.setEnabled(False)
            self.password.setEnabled(False)
            self.database.setPlaceholderText("데이터베이스 파일 경로")
            self.database.setEnabled(True)

    def _enable_standard_fields(self, enable=True):
        self.host.setEnabled(enable)
        self.port.setEnabled(enable)
        self.username.setEnabled(enable)
        self.password.setEnabled(enable)
        self.database.setEnabled(True)

    def test_connection(self):
        """MySQL / MariaDB 연결 테스트"""
        db_type = self.db_type.currentText()

        if db_type not in ["MySQL", "MariaDB"]:
            QMessageBox.information(
                self, "지원 안함", f"{db_type} 연결은 아직 지원하지 않습니다."
            )
            return

        host = self.host.text().strip()
        port = self.port.text().strip()
        user = self.username.text().strip()
        password = self.password.text().strip()
        database = self.database.text().strip()

        try:
            conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database
            )
            conn.close()
            self.status_label.setText("● 연결됨")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            QMessageBox.information(self, "연결 성공", "DB 연결 성공 ✅")
        except Exception as e:
            err_msg = f"연결 실패:\n\n{e}\n\n{traceback.format_exc()}"
            self.status_label.setText("● 연결 실패")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "연결 실패", err_msg)


# -------------------- Table Selector --------------------
class TableSelector(QGroupBox):
    """테이블 선택 패널"""

    def __init__(self, title="테이블 선택", parent=None):
        super().__init__(title, parent)
        self.setup_ui()
        self.load_sample_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.table_widget = QTableWidget()
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
        btn_layout.addWidget(QPushButton("전체 선택"))
        btn_layout.addWidget(QPushButton("선택 해제"))
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_sample_data(self):
        sample_tables = [
            ("사용자", "1,250"),
            ("주문", "5,430"),
            ("상품", "892"),
            ("카테고리", "25"),
            ("로그", "15,680"),
            ("고객", "2,180"),
            ("재고", "450")
        ]
        self.table_widget.setRowCount(len(sample_tables))
        for row, (table_name, row_count) in enumerate(sample_tables):
            checkbox = QCheckBox()
            self.table_widget.setCellWidget(row, 0, checkbox)
            self.table_widget.setItem(row, 1, QTableWidgetItem(table_name))
            self.table_widget.setItem(row, 2, QTableWidgetItem(row_count))


# -------------------- Progress Panel --------------------
class ProgressPanel(QGroupBox):
    """진행 상태 패널"""

    def __init__(self, title="전송 진행 상태", parent=None):
        super().__init__(title, parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("가져오기 모드:"))
        self.import_mode = QComboBox()
        self.import_mode.addItems([
            "새 테이블 생성",
            "기존 데이터 교체",
            "기존 데이터 추가",
            "기존 데이터 업데이트"
        ])
        mode_layout.addWidget(self.import_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_text = QLabel("전송 준비 완료...")
        self.status_text.setWordWrap(True)
        layout.addWidget(self.status_text)

        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(150)
        self.log_area.setReadOnly(True)
        self.log_area.setText("[정보] 전송을 시작할 준비가 되었습니다...")
        layout.addWidget(self.log_area)

        self.transfer_btn = QPushButton("전송 시작")
        self.transfer_btn.setMinimumHeight(40)
        layout.addWidget(self.transfer_btn)

        self.setLayout(layout)


# -------------------- Main Window --------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        with open("style.qss", "r") as f:
            qss = f.read()
            self.setStyleSheet(qss)

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
        layout.addWidget(ConnectionPanel("데이터베이스 연결"))
        layout.addWidget(TableSelector("내보낼 테이블 선택"))
        panel.setLayout(layout)
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


# -------------------- Entry Point --------------------
def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception:
        # For debugging unexpected crashes
        traceback.print_exc()


if __name__ == "__main__":
    main()
