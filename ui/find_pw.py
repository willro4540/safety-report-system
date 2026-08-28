import json
import os
import bcrypt
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from styles import WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE, LABEL_FIELD, PRIMARY

LOCAL_USERS = "local_users.json"


class FindPwWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("비밀번호 찾기")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("④ 비밀번호 찾기")
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

        notice = QLabel("본인 확인 후 새 비밀번호를 설정합니다.")
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

        lbl_id = QLabel("아이디 *")
        lbl_id.setStyleSheet(LABEL_FIELD)
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("아이디 입력")

        lbl_name = QLabel("이름 *")
        lbl_name.setStyleSheet(LABEL_FIELD)
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("이름 입력")

        lbl_phone = QLabel("휴대폰 번호 *")
        lbl_phone.setStyleSheet(LABEL_FIELD)
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("010-0000-0000")

        divider = QLabel()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #b2dce4;")

        lbl_pw = QLabel("새 비밀번호 *")
        lbl_pw.setStyleSheet(LABEL_FIELD)
        self.input_pw = QLineEdit()
        self.input_pw.setPlaceholderText("새 비밀번호 입력")
        self.input_pw.setEchoMode(QLineEdit.EchoMode.Password)

        lbl_pw2 = QLabel("새 비밀번호 확인 *")
        lbl_pw2.setStyleSheet(LABEL_FIELD)
        self.input_pw2 = QLineEdit()
        self.input_pw2.setPlaceholderText("새 비밀번호 재입력")
        self.input_pw2.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_reset = QPushButton("비밀번호 재설정")
        self.btn_reset.setStyleSheet(BTN_PRIMARY)
        self.btn_reset.clicked.connect(self.handle_reset)

        btn_back = QPushButton("로그인으로 돌아가기")
        btn_back.setStyleSheet(BTN_OUTLINE)
        btn_back.clicked.connect(self.close)

        body.addWidget(notice)
        body.addSpacing(8)
        body.addWidget(lbl_id)
        body.addWidget(self.input_id)
        body.addWidget(lbl_name)
        body.addWidget(self.input_name)
        body.addWidget(lbl_phone)
        body.addWidget(self.input_phone)
        body.addSpacing(6)
        body.addWidget(divider)
        body.addSpacing(6)
        body.addWidget(lbl_pw)
        body.addWidget(self.input_pw)
        body.addWidget(lbl_pw2)
        body.addWidget(self.input_pw2)
        body.addSpacing(6)
        body.addWidget(self.btn_reset)
        body.addWidget(btn_back)

        root.addWidget(header)
        root.addLayout(body)
        root.addStretch()
        self.setLayout(root)

    def handle_reset(self):
        user_id = self.input_id.text().strip()
        name    = self.input_name.text().strip()
        phone   = self.input_phone.text().strip()
        new_pw  = self.input_pw.text().strip()
        new_pw2 = self.input_pw2.text().strip()

        if not all([user_id, name, phone, new_pw, new_pw2]):
            QMessageBox.warning(self, "입력 오류", "모든 항목을 입력하세요.")
            return
        if new_pw != new_pw2:
            QMessageBox.warning(self, "입력 오류", "비밀번호가 일치하지 않습니다.")
            return

        hashed_pw = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # DB 시도
        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = %s AND name = %s AND phone = %s",
                (user_id, name, phone)
            )
            if not cursor.fetchone():
                QMessageBox.warning(self, "인증 실패", "일치하는 정보가 없습니다.")
                conn.close()
                return
            cursor.execute(
                "UPDATE users SET password = %s WHERE user_id = %s",
                (hashed_pw, user_id)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "완료", "비밀번호가 재설정되었습니다.")
            self.close()
            return
        except:
            pass

        # 로컬
        if not os.path.exists(LOCAL_USERS):
            QMessageBox.warning(self, "인증 실패", "일치하는 정보가 없습니다.")
            return
        with open(LOCAL_USERS, "r", encoding="utf-8") as f:
            users = json.load(f)
        found = False
        for u in users:
            if u["user_id"] == user_id and u["name"] == name and u["phone"] == phone:
                u["password"] = hashed_pw
                found = True
                break
        if not found:
            QMessageBox.warning(self, "인증 실패", "일치하는 정보가 없습니다.")
            return
        with open(LOCAL_USERS, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "완료", "비밀번호가 재설정되었습니다.")
        self.close()