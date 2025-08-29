# progress_panel.py

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QProgressBar, QTextEdit, QPushButton
)


class ProgressPanel(QGroupBox):
    """Progress and import mode panel."""

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
