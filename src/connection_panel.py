# connection_panel.py

import traceback
import pymysql
from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt


class ConnectionPanel(QGroupBox):
    """Database connection panel."""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Status label
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("상태:"))
        self.status_label = QLabel("● 연결 끊김")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Connection fields
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

        # Buttons
        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("연결 테스트")
        self.test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(self.test_btn)

        self.disconnect_btn = QPushButton("연결 해제")
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.disconnect_btn.setEnabled(False)
        btn_layout.addWidget(self.disconnect_btn)

        layout.addLayout(btn_layout)

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


    
    def translate_error_code(self, code, detail="") -> str:
        """Maps MySQL error codes to friendly messages."""
        if code == 1045:
            return "접속 실패: 사용자 이름 또는 비밀번호가 잘못되었습니다."
        elif code == 1049:
            return "접속 실패: 존재하지 않는 데이터베이스입니다."
        elif code == 2003:
            return "접속 실패: 호스트에 연결할 수 없습니다. 서버 주소 또는 포트를 확인하세요."
        elif code == 2005:
            return "접속 실패: 잘못된 호스트명입니다."
        elif code == 2006:
            return "접속 실패: 서버에 연결이 끊어졌습니다."
        elif code == 1130:
            return "접속 실패: 이 호스트는 DB 서버에 접근할 권한이 없습니다."
        else:
            # fallback for unknown codes
            return f"접속 실패: {detail}"


    def test_connection(self):
        db_type = self.db_type.currentText()

        if db_type not in ["MySQL", "MariaDB"]:
            QMessageBox.information(self, "지원 안함", f"{db_type} 연결은 아직 지원하지 않습니다.")
            return

        host = self.host.text().strip()
        port = self.port.text().strip()
        user = self.username.text().strip()
        password = self.password.text().strip()
        database = self.database.text().strip()

        try:
            # If DB is provided, connect to it directly
            if database:
                conn = pymysql.connect(
                    host=host,
                    port=int(port),
                    user=user,
                    password=password,
                    database=database,
                    connect_timeout=3
                )
                conn.close()
                self.status_label.setText("● 연결됨")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                QMessageBox.information(self, "연결 성공", f"{database} DB에 연결 성공 ✅")
                self.disconnect_btn.setEnabled(True)
            else:
                # Connect to server without database
                conn = pymysql.connect(
                    host=host,
                    port=int(port),
                    user=user,
                    password=password,
                    connect_timeout=3
                )
                cursor = conn.cursor()
                cursor.execute("SHOW DATABASES")
                databases = [row[0] for row in cursor.fetchall()]
                conn.close()

                self.status_label.setText("● 연결됨 (DB 없음)")
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.disconnect_btn.setEnabled(True)

                if databases:
                    db_list = "\n".join(databases)
                    QMessageBox.warning(
                        self,
                        "DB 없음",
                        f"데이터베이스가 선택되지 않았습니다.\n\n서버에 존재하는 DB 목록:\n{db_list}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "DB 없음",
                        "서버에 연결되었지만, 생성된 데이터베이스가 없습니다."
                    )

        except pymysql.err.OperationalError as e:
            code = e.args[0]
            msg = self.translate_error_code(code, e.args[1])
            self.status_label.setText("● 연결 실패")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "연결 실패", msg)
            self.disconnect_btn.setEnabled(False)

        except Exception as e:
            print("Unhandled error:", traceback.format_exc())
            self.status_label.setText("● 연결 실패")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "연결 실패", "예상치 못한 오류가 발생했습니다. 입력 정보를 다시 확인해 주세요.")
            self.disconnect_btn.setEnabled(False)


    def disconnect(self):
        self.host.setText("localhost")
        self.port.setText("3306")
        self.username.setText("root")
        self.password.clear()
        self.database.clear()
        self.status_label.setText("● 연결 끊김")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.disconnect_btn.setEnabled(False)



