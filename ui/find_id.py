import json
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from styles import WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE, LABEL_FIELD, PRIMARY

LOCAL_USERS = "local_users.json"


class FindIdWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("아이디 찾기")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("③ 아이디 찾기")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY};
                color: white; font-size: 16px;
                font-weight: bold; padding: 16px;
            }}
        """)

        body = QVBoxLayout()
        body.setContentsMargins(200, 20, 200, 40)
        body.setSpacing(8)

        notice = QLabel("이름과 휴대폰 번호로 아이디를 찾습니다.")
        notice.setStyleSheet("""
            QLabel {
                background: #e8f7fa;
                border-left: 4px solid #0e9db5;
                padding: 10px 12px;
                border-radius: 6px;
                font-size: 12px;
                color: #0a6f80;
            }
        """)

        lbl_name = QLabel("이름 *")
        lbl_name.setStyleSheet(LABEL_FIELD)
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("이름 입력")

        lbl_phone = QLabel("휴대폰 번호 *")
        lbl_phone.setStyleSheet(LABEL_FIELD)
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("010-0000-0000")

        self.btn_find = QPushButton("아이디 찾기")
        self.btn_find.setStyleSheet(BTN_PRIMARY)
        self.btn_find.clicked.connect(self.handle_find)

        self.result_box = QLabel("")
        self.result_box.setAlignment(Qt.AlignCenter)
        self.result_box.setStyleSheet("""
            QLabel {
                background: #f0fbfd;
                border: 1.5px solid #0e9db5;
                border-radius: 8px;
                padding: 16px;
                font-size: 16px;
                font-weight: bold;
                color: #0e7c8f;
            }
        """)
        self.result_box.hide()

        btn_back = QPushButton("로그인으로 돌아가기")
        btn_back.setStyleSheet(BTN_OUTLINE)
        btn_back.clicked.connect(self.close)

        body.addWidget(notice)
        body.addSpacing(8)
        body.addWidget(lbl_name)
        body.addWidget(self.input_name)
        body.addWidget(lbl_phone)
        body.addWidget(self.input_phone)
        body.addSpacing(6)
        body.addWidget(self.btn_find)
        body.addWidget(self.result_box)
        body.addWidget(btn_back)

        root.addWidget(header)
        root.addLayout(body)
        root.addStretch()
        self.setLayout(root)

    def handle_find(self):
        name  = self.input_name.text().strip()
        phone = self.input_phone.text().strip()
        if not name or not phone:
            QMessageBox.warning(self, "입력 오류", "이름과 휴대폰 번호를 입력하세요.")
            return

        # DB 시도
        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM users WHERE name = %s AND phone = %s",
                (name, phone)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                self.show_result(row[0])
                return
        except:
            pass

        # 로컬
        if not os.path.exists(LOCAL_USERS):
            QMessageBox.warning(self, "찾기 실패", "일치하는 정보가 없습니다.")
            return
        with open(LOCAL_USERS, "r", encoding="utf-8") as f:
            users = json.load(f)
        user = next((u for u in users if u["name"] == name and u["phone"] == phone), None)
        if user:
            self.show_result(user["user_id"])
        else:
            QMessageBox.warning(self, "찾기 실패", "일치하는 정보가 없습니다.")

    def show_result(self, user_id):
        masked = user_id[:2] + "*" * (len(user_id) - 2)
        self.result_box.setText(f"찾은 아이디: {masked}")
        self.result_box.show()