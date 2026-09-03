import json
import os
import bcrypt
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox
)
from PySide6.QtCore import Qt
from styles import (
    WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE,
    LABEL_FIELD, PRIMARY
)

LOCAL_USERS = "local_users.json"

def load_users():
    if not os.path.exists(LOCAL_USERS):
        return []
    with open(LOCAL_USERS, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(LOCAL_USERS, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 헤더
        header = QLabel("② 회원가입")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY};
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 16px;
            }}
        """)

        body = QVBoxLayout()
        body.setContentsMargins(180, 20, 180, 40)
        body.setSpacing(8)

        # 아이디 + 중복확인
        lbl_id = QLabel("아이디 *")
        lbl_id.setStyleSheet(LABEL_FIELD)
        id_row = QHBoxLayout()
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("아이디 입력 (4~20자)")
        btn_check = QPushButton("중복확인")
        btn_check.setFixedWidth(80)
        btn_check.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY}; color: white;
                border: none; border-radius: 7px;
                padding: 8px; font-size: 12px; font-weight: bold;
            }}
        """)
        btn_check.clicked.connect(self.check_duplicate)
        id_row.addWidget(self.input_id)
        id_row.addWidget(btn_check)

        lbl_pw = QLabel("비밀번호 *")
        lbl_pw.setStyleSheet(LABEL_FIELD)
        self.input_pw = QLineEdit()
        self.input_pw.setPlaceholderText("비밀번호 입력 (8자 이상)")
        self.input_pw.setEchoMode(QLineEdit.EchoMode.Password)

        lbl_pw2 = QLabel("비밀번호 확인 *")
        lbl_pw2.setStyleSheet(LABEL_FIELD)
        self.input_pw2 = QLineEdit()
        self.input_pw2.setPlaceholderText("비밀번호 재입력")
        self.input_pw2.setEchoMode(QLineEdit.EchoMode.Password)

        lbl_name = QLabel("이름 *")
        lbl_name.setStyleSheet(LABEL_FIELD)
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("이름 입력")

        lbl_phone = QLabel("휴대폰 번호 *")
        lbl_phone.setStyleSheet(LABEL_FIELD)
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("010-0000-0000")

        self.btn_signup = QPushButton("회원가입")
        self.btn_signup.setStyleSheet(BTN_PRIMARY)
        self.btn_signup.clicked.connect(self.handle_signup)

        btn_back = QPushButton("로그인으로 돌아가기")
        btn_back.setStyleSheet(BTN_OUTLINE)
        btn_back.clicked.connect(self.close)

        body.addWidget(lbl_id)
        body.addLayout(id_row)
        body.addWidget(lbl_pw)
        body.addWidget(self.input_pw)
        body.addWidget(lbl_pw2)
        body.addWidget(self.input_pw2)
        body.addWidget(lbl_name)
        body.addWidget(self.input_name)
        body.addWidget(lbl_phone)
        body.addWidget(self.input_phone)
        body.addSpacing(6)
        body.addWidget(self.btn_signup)
        body.addWidget(btn_back)

        root.addWidget(header)
        root.addLayout(body)
        root.addStretch()
        self.setLayout(root)

    def check_duplicate(self):
        user_id = self.input_id.text().strip()
        if not user_id:
            QMessageBox.warning(self, "입력 오류", "아이디를 입력하세요.")
            return
        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            exists = cursor.fetchone()
            conn.close()
        except:
            users = load_users()
            exists = any(u["user_id"] == user_id for u in users)

        if exists:
            QMessageBox.warning(self, "중복", "이미 사용 중인 아이디입니다.")
        else:
            QMessageBox.information(self, "확인", "사용 가능한 아이디입니다.")

    def handle_signup(self):
        user_id   = self.input_id.text().strip()
        user_pw   = self.input_pw.text().strip()
        user_pw2  = self.input_pw2.text().strip()
        user_name = self.input_name.text().strip()
        user_phone = self.input_phone.text().strip()

        if not all([user_id, user_pw, user_pw2, user_name, user_phone]):
            QMessageBox.warning(self, "입력 오류", "모든 항목을 입력하세요.")
            return
        if user_pw != user_pw2:
            QMessageBox.warning(self, "입력 오류", "비밀번호가 일치하지 않습니다.")
            return

        hashed_pw = bcrypt.hashpw(user_pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                QMessageBox.warning(self, "가입 실패", "이미 존재하는 아이디입니다.")
                conn.close()
                return
            cursor.execute(
                "INSERT INTO users (user_id, password, name, phone, role) VALUES (%s,%s,%s,%s,%s)",
                (user_id, hashed_pw, user_name, user_phone, "user")
            )
            conn.commit()
            conn.close()
        except:
            users = load_users()
            if any(u["user_id"] == user_id for u in users):
                QMessageBox.warning(self, "가입 실패", "이미 존재하는 아이디입니다.")
                return
            users.append({
                "user_id": user_id, "password": hashed_pw,
                "name": user_name, "phone": user_phone, "role": "user"
            })
            save_users(users)

        QMessageBox.information(self, "가입 완료", "회원가입이 완료되었습니다.")
        self.close()