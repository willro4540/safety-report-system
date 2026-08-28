from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt
from styles import (
    WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE,
    BTN_DANGER, PRIMARY
)

class CitizenMainWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("시민 메인")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 헤더 ──
        header = QLabel("🛡 시설 안전 민원 신고")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY};
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 18px;
            }}
        """)

        # ── 상단바 (유저명 + 로그아웃) ──
        topbar = QHBoxLayout()
        topbar.setContentsMargins(30, 12, 30, 12)
        lbl_user = QLabel(f"👤 {self.user_id} 님")
        lbl_user.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 13px;")

        # DB 연결 상태
        self.lbl_status = QLabel()
        self.check_db()
        self.lbl_status.setStyleSheet("font-size: 12px;")

        btn_logout = QPushButton("로그아웃")
        btn_logout.setFixedWidth(80)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: white; color: #5a8a92;
                border: 1px solid #b2dce4; border-radius: 5px;
                padding: 5px; font-size: 11px;
            }}
        """)
        btn_logout.clicked.connect(self.handle_logout)

        topbar.addWidget(lbl_user)
        topbar.addStretch()
        topbar.addWidget(self.lbl_status)
        topbar.addSpacing(12)
        topbar.addWidget(btn_logout)

        # ── 큰 버튼 2개 ──
        btn_area = QHBoxLayout()
        btn_area.setContentsMargins(80, 30, 80, 20)
        btn_area.setSpacing(20)

        self.big_btn_report = self._make_big_btn("📋", "신고하기")
        self.big_btn_history = self._make_big_btn("📂", "내 신고 내역")
        self.big_btn_report.clicked.connect(self.open_report)
        self.big_btn_history.clicked.connect(self.open_history)

        btn_area.addWidget(self.big_btn_report)
        btn_area.addWidget(self.big_btn_history)

        # ── 경고 박스 ──
        warn = QLabel("⚠️  긴급 상황은 119 또는 112로 신고하세요")
        warn.setAlignment(Qt.AlignCenter)
        warn.setStyleSheet("""
            QLabel {
                background: #fff8e1;
                border-left: 4px solid #ffc107;
                color: #7a5c00;
                font-size: 12px;
                padding: 12px 20px;
                margin: 0 80px;
                border-radius: 6px;
            }
        """)

        root.addWidget(header)
        root.addLayout(topbar)
        root.addLayout(btn_area)
        root.addWidget(warn)
        root.addStretch()
        self.setLayout(root)

    def _make_big_btn(self, icon, label):
        btn = QPushButton(f"{icon}\n{label}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #f0fbfd;
                border: 2px solid {PRIMARY};
                border-radius: 12px;
                color: #0e7c8f;
                font-size: 15px;
                font-weight: bold;
                padding: 40px 20px;
            }}
            QPushButton:hover {{
                background: #d6f3f8;
            }}
        """)
        return btn

    def check_db(self):
        try:
            from db.connection import get_connection
            conn = get_connection()
            conn.close()
            self.db_connected = True
            self.lbl_status.setText("🟢 서버 연결됨")
        except:
            self.db_connected = False
            self.lbl_status.setText("🔴 로컬 모드")

    def open_report(self):
        from ui.report import ReportWindow
        self.report_window = ReportWindow(self.user_id)
        self.report_window.show()

    def open_history(self):
        from ui.history import HistoryWindow
        self.history_window = HistoryWindow(self.user_id)
        self.history_window.show()

    def handle_logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()