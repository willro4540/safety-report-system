import json
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt
from styles import WINDOW_STYLE, BTN_OUTLINE, PRIMARY

LOCAL_REPORTS = "local_reports.json"


class HistoryWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("신고 내역")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("⑦ 내 신고 내역")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY};
                color: white; font-size: 16px;
                font-weight: bold; padding: 16px;
            }}
        """)

        body = QVBoxLayout()
        body.setContentsMargins(60, 20, 60, 40)
        body.setSpacing(10)

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
                background: #e0f5f8;
                color: #0e7c8f;
            }
        """)

        btn_back = QPushButton("뒤로가기")
        btn_back.setStyleSheet(BTN_OUTLINE)
        btn_back.clicked.connect(self.close)

        body.addWidget(self.list_widget)
        body.addWidget(btn_back)

        root.addWidget(header)
        root.addLayout(body)
        self.setLayout(root)

        self.load_history()

    def load_history(self):
        loaded = False

        try:
            from db.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, location, content, status, created_at FROM complaints WHERE user_id = %s ORDER BY created_at DESC",
                (self.user_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            if rows:
                self.list_widget.clear()
                for row in rows:
                    status = row[3]
                    icon = self.status_icon(status)
                    self.list_widget.addItem(
                        f"{icon} [{row[4]}] {row[1]} — {row[2][:30]} ({status})"
                    )
                loaded = True
        except:
            pass

        if not loaded:
            if not os.path.exists(LOCAL_REPORTS):
                self.list_widget.addItem("신고 내역이 없습니다.")
                return
            with open(LOCAL_REPORTS, "r", encoding="utf-8") as f:
                reports = json.load(f)
            my = [r for r in reports if str(r["user_id"]) == str(self.user_id)]
            self.list_widget.clear()
            if not my:
                self.list_widget.addItem("신고 내역이 없습니다.")
                return
            for r in my:
                status = r.get("status", "접수")
                rtype  = r.get("type", "")
                icon   = self.status_icon(status)
                reason = f" | 사유: {r['reject_reason']}" if status == "기각" and "reject_reason" in r else ""
                self.list_widget.addItem(
                    f"{icon} [{r['created_at']}] {rtype} | {r['location']} — {r['content'][:20]} ({status}){reason}"
                )

    def status_icon(self, status):
        icons = {
            "접수":  "🔵",
            "처리중": "🟡",
            "완료":  "🟢",
            "기각":  "🔴"
        }
        return icons.get(status, "⚪")