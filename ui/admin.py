import json
import os
import time
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QListWidget, QMessageBox,
    QDialog, QTextEdit, QComboBox,
    QProgressDialog, QApplication
)
from PySide6.QtCore import Qt
from styles import WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE, BTN_DANGER, PRIMARY
from sms_notifier import send_sms_notification

ADMIN_COLOR   = "#0a6f80"
LOCAL_REPORTS = "local_reports.json"
LOCAL_USERS   = "local_users.json"


def get_user_phone(user_id):
    try:
        from db.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        pass

    if not os.path.exists(LOCAL_USERS):
        return None
    with open(LOCAL_USERS, "r", encoding="utf-8") as f:
        users = json.load(f)
    for u in users:
        if u.get("user_id") == user_id:
            return u.get("phone")
    return None


class AdminWindow(QWidget):
    def __init__(self, admin_id):
        super().__init__()
        self.admin_id = admin_id
        self.data_source = None     # load_complaints가 "db" 또는 "local"로 채움
        self.current_rows = []      # 화면에 표시된 순서 그대로 — 상태변경/기각 처리에서 재사용
        self.setWindowTitle("관리자 패널")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("🛡 관리자 패널")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {ADMIN_COLOR};
                color: white; font-size: 16px;
                font-weight: bold; padding: 16px;
            }}
        """)

        topbar = QHBoxLayout()
        topbar.setContentsMargins(30, 12, 30, 12)
        lbl_admin = QLabel("🛡 관리자")
        lbl_admin.setStyleSheet(f"color: {ADMIN_COLOR}; font-weight: bold; font-size: 13px;")
        btn_logout = QPushButton("로그아웃")
        btn_logout.setFixedWidth(80)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: white; color: #5a8a92;
                border: 1px solid #b2dce4; border-radius: 5px;
                padding: 5px; font-size: 11px;
            }
        """)
        btn_logout.clicked.connect(self.handle_logout)
        topbar.addWidget(lbl_admin)
        topbar.addStretch()
        topbar.addWidget(btn_logout)

        body = QVBoxLayout()
        body.setContentsMargins(60, 10, 60, 20)
        body.setSpacing(10)

        lbl_title = QLabel("전체 신고 목록")
        lbl_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {ADMIN_COLOR};")

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1.5px solid #b2dce4;
                border-radius: 8px;
                background: white;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #e0f0f4;
                font-size: 13px;
            }
            QListWidget::item:selected {
                background: #d6f0f4;
                color: #0a6f80;
            }
        """)

        # 버튼 행
        btn_row = QHBoxLayout()

        btn_refresh = QPushButton("새로고침")
        btn_refresh.setStyleSheet(BTN_OUTLINE)
        btn_refresh.clicked.connect(self.load_complaints)

        btn_status = QPushButton("상태 변경")
        btn_status.setStyleSheet(BTN_PRIMARY)
        btn_status.clicked.connect(self.change_status)

        btn_reject = QPushButton("기각/취소")
        btn_reject.setStyleSheet(f"""
            QPushButton {{
                background: white; color: #e74c3c;
                border: 1.5px solid #e74c3c;
                border-radius: 7px; padding: 9px 0;
                font-size: 13px; font-weight: bold;
            }}
            QPushButton:hover {{ background: #fdecea; }}
        """)
        btn_reject.clicked.connect(self.reject_complaint)

        btn_row.addWidget(btn_refresh)
        btn_row.addWidget(btn_status)
        btn_row.addWidget(btn_reject)

        body.addWidget(lbl_title)
        body.addWidget(self.list_widget)
        body.addLayout(btn_row)

        root.addWidget(header)
        root.addLayout(topbar)
        root.addLayout(body)
        self.setLayout(root)

        self.load_complaints()

    def load_complaints(self):
        progress = QProgressDialog("신고 내역을 불러오는 중...", None, 0, 0, self)
        progress.setWindowTitle("로딩 중")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()
        time.sleep(1)

        self.list_widget.clear()
        self.current_rows = []

        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, type, location, content, status, reject_reason, created_at "
                "FROM reports ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            conn.close()
            self.data_source = "db"
            for row in rows:
                self.current_rows.append({
                    "id": row[0], "user_id": row[1], "type": row[2],
                    "location": row[3], "content": row[4], "status": row[5],
                    "reject_reason": row[6], "created_at": row[7]
                })
        except Exception:
            self.data_source = "local"
            if os.path.exists(LOCAL_REPORTS):
                with open(LOCAL_REPORTS, "r", encoding="utf-8") as f:
                    reports = json.load(f)
                for i, r in enumerate(reports):
                    self.current_rows.append({
                        "id": i, "user_id": r["user_id"], "type": r.get("type", ""),
                        "location": r["location"], "content": r["content"],
                        "status": r.get("status", "접수"),
                        "reject_reason": r.get("reject_reason"),
                        "created_at": r["created_at"]
                    })

        if not self.current_rows:
            self.list_widget.addItem("신고 내역이 없습니다.")
        else:
            for r in self.current_rows:
                self.list_widget.addItem(
                    f"[{r['created_at']}] {r['user_id']} | {r['type']} | "
                    f"{r['location']} — {r['content'][:20]} ({r['status']})"
                )

        progress.close()

    def get_selected_row(self):
        idx = self.list_widget.currentRow()
        if idx < 0 or idx >= len(self.current_rows):
            QMessageBox.warning(self, "선택 오류", "신고 항목을 선택하세요.")
            return None
        return self.current_rows[idx]

    def change_status(self):
        row = self.get_selected_row()
        if row is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("상태 변경")
        dialog.resize(300, 150)
        layout = QVBoxLayout()
        lbl = QLabel("상태를 선택하세요:")
        combo = QComboBox()
        combo.addItems(["접수", "처리중", "완료"])
        combo.setCurrentText(row["status"])
        btn_ok = QPushButton("확인")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(lbl)
        layout.addWidget(combo)
        layout.addWidget(btn_ok)
        dialog.setLayout(layout)

        if dialog.exec():
            new_status = combo.currentText()
            self._update_status(row, new_status)

            # 접수 완료 안내는 이메일로 이미 나갔으므로(ui/report.py),
            # 여기서는 "답변 이후" 단계(처리 완료)에만 SMS로 알린다.
            if new_status == "완료":
                phone = get_user_phone(row["user_id"])
                send_sms_notification(
                    phone,
                    f"[안전신고] 접수하신 민원이 처리 완료되었습니다. ({row['location']})"
                )

            QMessageBox.information(self, "완료", "상태가 변경되었습니다.")
            self.load_complaints()

    def reject_complaint(self):
        row = self.get_selected_row()
        if row is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("기각/취소 사유")
        dialog.resize(400, 200)
        layout = QVBoxLayout()
        lbl = QLabel("기각/취소 사유를 입력하세요:")
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("사유를 입력하세요")
        btn_ok = QPushButton("기각/취소 처리")
        btn_ok.setStyleSheet("QPushButton { background: #e74c3c; color: white; border-radius: 6px; padding: 8px; font-weight: bold; }")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(lbl)
        layout.addWidget(text_edit)
        layout.addWidget(btn_ok)
        dialog.setLayout(layout)

        if dialog.exec():
            reason = text_edit.toPlainText().strip()
            if not reason:
                QMessageBox.warning(self, "입력 오류", "사유를 입력하세요.")
                return

            self._update_status(row, "기각", reason=reason)

            phone = get_user_phone(row["user_id"])
            send_sms_notification(
                phone,
                f"[안전신고] 접수하신 민원이 기각되었습니다. 사유: {reason}"
            )

            QMessageBox.information(self, "완료", "기각/취소 처리되었습니다.")
            self.load_complaints()

    def _update_status(self, row, new_status, reason=None):
        """선택된 신고 1건의 상태를 바꾸고, DB 모드일 때만 admin_actions 감사 이력을 남긴다.
        어느 저장소를 쓸지는 load_complaints가 정한 self.data_source를 그대로 따른다
        (조회 때 DB를 썼으면 갱신도 DB로, 로컬 JSON을 썼으면 갱신도 로컬로 — 둘이 어긋나면
        읽은 목록과 실제로 바뀌는 데이터가 달라지는 문제가 있었음)."""
        action = "완료처리" if new_status == "완료" else ("기각" if new_status == "기각" else None)

        if self.data_source == "db":
            try:
                from db.connection import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                if reason is not None:
                    cursor.execute(
                        "UPDATE reports SET status = %s, reject_reason = %s WHERE id = %s",
                        (new_status, reason, row["id"])
                    )
                else:
                    cursor.execute(
                        "UPDATE reports SET status = %s WHERE id = %s",
                        (new_status, row["id"])
                    )
                if action:
                    cursor.execute(
                        "INSERT INTO admin_actions (report_id, admin_id, action, reason) VALUES (%s,%s,%s,%s)",
                        (row["id"], self.admin_id, action, reason)
                    )
                conn.commit()
                conn.close()
                return
            except Exception:
                pass  # DB 갱신 실패 시 로컬로 폴백

        if not os.path.exists(LOCAL_REPORTS):
            return
        with open(LOCAL_REPORTS, "r", encoding="utf-8") as f:
            reports = json.load(f)
        reports[row["id"]]["status"] = new_status
        if reason is not None:
            reports[row["id"]]["reject_reason"] = reason
        with open(LOCAL_REPORTS, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    def handle_logout(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
