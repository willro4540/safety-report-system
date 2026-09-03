import json
import os
import bcrypt
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from styles import (
    WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE,
    LABEL_TITLE, LABEL_FIELD, PRIMARY, BORDER
)

LOCAL_USERS = "local_users.json"

# ───────────────────────────────────────────
# ✏️ 수정 포인트
# LOCAL_USERS = "local_users.json"  ← 로컬 저장 파일명 변경 시
# ───────────────────────────────────────────

def load_users():
    if not os.path.exists(LOCAL_USERS):
        return []
    with open(LOCAL_USERS, "r", encoding="utf-8") as f:
        return json.load(f)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("시설 안전 민원 신고")
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

        # ── 부제목 ──
        sub = QLabel("안전한 환경을 함께 만들어요")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: #5a8a92; font-size: 12px; padding: 6px 0 16px 0;")

        # ── 본문 컨테이너 ──
        body = QVBoxLayout()
        body.setContentsMargins(200, 10, 200, 40)
        body.setSpacing(10)

        # 아이디
        lbl_id = QLabel("아이디")
        lbl_id.setStyleSheet(LABEL_FIELD)
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("아이디를 입력하세요")

        # 비밀번호
        lbl_pw = QLabel("비밀번호")
        lbl_pw.setStyleSheet(LABEL_FIELD)
        self.input_pw = QLineEdit()
        self.input_pw.setPlaceholderText("비밀번호를 입력하세요")
        self.input_pw.setEchoMode(QLineEdit.EchoMode.Password)

        # 로그인 버튼
        self.btn_login = QPushButton("로그인")
        self.btn_login.setStyleSheet(BTN_PRIMARY)
        self.btn_login.clicked.connect(self.handle_login)

        # 회원가입 버튼
        self.btn_signup = QPushButton("회원가입")
        self.btn_signup.setStyleSheet(BTN_OUTLINE)
        self.btn_signup.clicked.connect(self.open_signup)

        # 아이디/비번 찾기 버튼 행
        btn_row = QHBoxLayout()
        self.btn_find_id = QPushButton("아이디 찾기")
        self.btn_find_id.setStyleSheet(BTN_OUTLINE)
        self.btn_find_pw = QPushButton("비밀번호 찾기")
        self.btn_find_pw.setStyleSheet(BTN_OUTLINE)
        btn_row.addWidget(self.btn_find_id)
        btn_row.addWidget(self.btn_find_pw)
        self.btn_find_id.clicked.connect(self.open_find_id)
        self.btn_find_pw.clicked.connect(self.open_find_pw)

        body.addWidget(lbl_id)
        body.addWidget(self.input_id)
        body.addWidget(lbl_pw)
        body.addWidget(self.input_pw)
        body.addSpacing(6)
        body.addWidget(self.btn_login)
        body.addWidget(self.btn_signup)
        body.addLayout(btn_row)

        root.addWidget(header)
        root.addWidget(sub)
        root.addLayout(body)
        root.addStretch()
        self.setLayout(root)

    def handle_login(self):
        user_id = self.input_id.text().strip()
        user_pw = self.input_pw.text().strip()
        if not user_id or not user_pw:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 입력하세요.")
            return

        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password, role FROM users WHERE user_id = %s", (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            if row is None:
                QMessageBox.warning(self, "로그인 실패", "아이디가 존재하지 않습니다.")
                return
            if bcrypt.checkpw(user_pw.encode("utf-8"), row[0].encode("utf-8")):
                self.go_main(user_id, row[1])
            else:
                QMessageBox.warning(self, "로그인 실패", "비밀번호가 틀렸습니다.")
        except:
            # DB 실패 → 로컬
            users = load_users()
            user = next((u for u in users if u["user_id"] == user_id), None)
            if user is None:
                QMessageBox.warning(self, "로그인 실패", "아이디가 존재하지 않습니다.")
                return
            if bcrypt.checkpw(user_pw.encode("utf-8"), user["password"].encode("utf-8")):
                self.go_main(user_id, user.get("role", "user"))
            else:
                QMessageBox.warning(self, "로그인 실패", "비밀번호가 틀렸습니다.")

    def go_main(self, user_id, role):
        if role == "admin":
            from ui.admin import AdminWindow
            self.main_window = AdminWindow(user_id)
        else:
            from ui.citizen_main import CitizenMainWindow
            self.main_window = CitizenMainWindow(user_id)
        self.main_window.show()
        self.close()

    def open_signup(self):
        from ui.signup import SignupWindow
        self.signup_window = SignupWindow()
        self.signup_window.show()

    def open_find_id(self):
        from ui.find_id import FindIdWindow
        self.find_id_window = FindIdWindow()
        self.find_id_window.show()

    def open_find_pw(self):
        from ui.find_pw import FindPwWindow
        self.find_pw_window = FindPwWindow()
        self.find_pw_window.show()