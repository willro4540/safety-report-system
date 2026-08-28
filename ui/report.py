import cv2
import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QMessageBox,
    QFileDialog, QComboBox, QProgressDialog,
    QApplication
)
from PySide6.QtCore import Qt
from styles import (
    WINDOW_STYLE, BTN_PRIMARY, BTN_OUTLINE,
    LABEL_FIELD, PRIMARY
)

load_dotenv()

SEND_EMAIL    = os.getenv("SEND_EMAIL")
SEND_PASSWORD = os.getenv("SEND_APP_PASSWORD")
RECV_EMAIL    = os.getenv("RECV_EMAIL")
LOCAL_REPORTS = "local_reports.json"

REPORT_TYPES = [
    "유형 선택",
    "도로 파손",
    "가로등 고장",
    "시설물 파손",
    "보도블럭 파손",
    "하수구 막힘",
    "불법 주정차",
    "기타"
]


class ReportWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.image_path = None
        self.setWindowTitle("민원 신고")
        self.resize(900, 650)
        self.setStyleSheet(WINDOW_STYLE)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("⑥ 신고 접수")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY};
                color: white; font-size: 16px;
                font-weight: bold; padding: 16px;
            }}
        """)

        body = QVBoxLayout()
        body.setContentsMargins(120, 20, 120, 40)
        body.setSpacing(8)

        # 신고 유형
        lbl_type = QLabel("신고 유형 *")
        lbl_type.setStyleSheet(LABEL_FIELD)
        self.combo_type = QComboBox()
        self.combo_type.addItems(REPORT_TYPES)
        self.combo_type.setStyleSheet(f"""
            QComboBox {{
                background: white;
                border: 1.5px solid #b2dce4;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 13px;
            }}
        """)

        # 사진 첨부
        lbl_photo = QLabel("사진 첨부")
        lbl_photo.setStyleSheet(LABEL_FIELD)
        photo_row = QHBoxLayout()
        self.lbl_photo_name = QLabel("선택된 사진 없음")
        self.lbl_photo_name.setStyleSheet(f"""
            QLabel {{
                background: white;
                border: 1.5px solid #b2dce4;
                border-radius: 7px;
                padding: 8px 12px;
                color: #7a9ea5;
                font-size: 12px;
            }}
        """)
        btn_photo = QPushButton("📁 사진 선택")
        btn_photo.setFixedWidth(110)
        btn_photo.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY}; color: white;
                border: none; border-radius: 7px;
                padding: 8px; font-size: 12px; font-weight: bold;
            }}
        """)
        btn_photo.clicked.connect(self.select_photo)

        btn_camera = QPushButton("📸 현장 촬영")
        btn_camera.setFixedWidth(110)
        btn_camera.setStyleSheet(f"""
            QPushButton {{
                background: #0a7a8f; color: white;
                border: none; border-radius: 7px;
                padding: 8px; font-size: 12px; font-weight: bold;
            }}
        """)
        btn_camera.clicked.connect(self.take_photo)
        photo_row.addWidget(self.lbl_photo_name)
        photo_row.addWidget(btn_photo)
        photo_row.addWidget(btn_camera)

        # GPS
        lbl_gps = QLabel("📍 GPS 위치 (사진에서 자동 추출)")
        lbl_gps.setStyleSheet(LABEL_FIELD)
        self.lbl_gps_value = QLabel("사진을 선택하면 자동으로 추출됩니다")
        self.lbl_gps_value.setStyleSheet(f"""
            QLabel {{
                background: #e8f7fa;
                border: 1.5px solid #0e9db5;
                border-radius: 7px;
                padding: 8px 12px;
                color: #0a6f80;
                font-size: 12px;
            }}
        """)

        # 발생 위치
        lbl_loc = QLabel("발생 위치 * (GPS 없을 때 직접 입력)")
        lbl_loc.setStyleSheet(LABEL_FIELD)
        self.input_location = QLineEdit()
        self.input_location.setPlaceholderText("예: 광주광역시 광산구 소촌로 152")

        # 신고 내용
        lbl_content = QLabel("신고 내용 *")
        lbl_content.setStyleSheet(LABEL_FIELD)
        self.input_content = QTextEdit()
        self.input_content.setPlaceholderText("내용을 입력하세요 (5~900자)")
        self.input_content.setFixedHeight(100)

        self.btn_submit = QPushButton("신고 접수")
        self.btn_submit.setStyleSheet(BTN_PRIMARY)
        self.btn_submit.clicked.connect(self.handle_submit)

        btn_back = QPushButton("취소")
        btn_back.setStyleSheet(BTN_OUTLINE)
        btn_back.clicked.connect(self.close)

        body.addWidget(lbl_type)
        body.addWidget(self.combo_type)
        body.addWidget(lbl_photo)
        body.addLayout(photo_row)
        body.addWidget(lbl_gps)
        body.addWidget(self.lbl_gps_value)
        body.addWidget(lbl_loc)
        body.addWidget(self.input_location)
        body.addWidget(lbl_content)
        body.addWidget(self.input_content)
        body.addSpacing(6)
        body.addWidget(self.btn_submit)
        body.addWidget(btn_back)

        root.addWidget(header)
        root.addLayout(body)
        root.addStretch()
        self.setLayout(root)

    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "사진 선택", "",
            "이미지 파일 (*.jpg *.jpeg *.png *.bmp)"
        )
        if not file_path:
            return
        self.image_path = file_path
        self.lbl_photo_name.setText(os.path.basename(file_path))
        self.extract_gps(file_path)

    def take_photo(self):
        from ui.camera import CameraWindow
        self.camera_window = CameraWindow(self.on_photo_taken)
        self.camera_window.show()

    def on_photo_taken(self, save_path):
        self.image_path = save_path
        self.lbl_photo_name.setText(save_path)
        self.extract_gps(save_path)

    def extract_gps(self, file_path):
        try:
            img = Image.open(file_path)
            exif_data = img._getexif()
            if not exif_data:
                self.lbl_gps_value.setText("EXIF 정보 없음 — 위치를 직접 입력하세요")
                return
            gps_info = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = gps_value
            if not gps_info:
                self.lbl_gps_value.setText("GPS 정보 없음 — 위치를 직접 입력하세요")
                return
            lat = self._convert_dms(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
            lon = self._convert_dms(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
            text = f"위도: {lat:.6f}, 경도: {lon:.6f}"
            self.lbl_gps_value.setText(text)
            self.input_location.setText(text)
        except:
            self.lbl_gps_value.setText("GPS 추출 실패 — 위치를 직접 입력하세요")

    def _convert_dms(self, dms, ref):
        d, m, s = dms
        result = float(d) + float(m) / 60 + float(s) / 3600
        if ref in ["S", "W"]:
            result = -result
        return result

    def handle_submit(self):
        report_type = self.combo_type.currentText()
        location    = self.input_location.text().strip()
        content     = self.input_content.toPlainText().strip()

        if report_type == "유형 선택":
            QMessageBox.warning(self, "입력 오류", "신고 유형을 선택하세요.")
            return
        if not location or not content:
            QMessageBox.warning(self, "입력 오류", "위치와 내용을 입력하세요.")
            return

        progress = QProgressDialog("민원을 접수하고 있습니다...", None, 0, 0, self)
        progress.setWindowTitle("전송 중")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()

        self.save_local(report_type, location, content)
        pdf_path = self.create_pdf(report_type, location, content)
        self.send_email(report_type, location, content, pdf_path)

        progress.close()
        QMessageBox.information(self, "접수 완료", "민원이 접수되었습니다.")
        self.close()

    def save_local(self, report_type, location, content):
        data = {
            "user_id": self.user_id,
            "type": report_type,
            "location": location,
            "content": content,
            "status": "접수",
            "image_path": self.image_path or "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        reports = []
        if os.path.exists(LOCAL_REPORTS):
            with open(LOCAL_REPORTS, "r", encoding="utf-8") as f:
                reports = json.load(f)
        reports.append(data)
        with open(LOCAL_REPORTS, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    def create_pdf(self, report_type, location, content):
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtWidgets import QDialog, QTextEdit

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

        pdf_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        printer.setOutputFileName(pdf_path)

        text_edit = QTextEdit()
        text_edit.setPlainText(
            f"시설 안전 민원 신고서\n\n"
            f"신고자: {self.user_id}\n"
            f"신고 유형: {report_type}\n"
            f"위치: {location}\n"
            f"일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"신고 내용:\n{content}"
        )
        text_edit.print_(printer)

        return pdf_path

    def send_email(self, report_type, location, content, pdf_path=None):
        try:
            msg = MIMEMultipart()
            msg["From"]    = SEND_EMAIL
            msg["To"]      = RECV_EMAIL
            msg["Subject"] = f"[민원 신고 - {report_type}] {location}"
            body = f"신고자: {self.user_id}\n유형: {report_type}\n위치: {location}\n내용:\n{content}"
            msg.attach(MIMEText(body, "plain"))

            if self.image_path and os.path.exists(self.image_path):
                with open(self.image_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(self.image_path)}"
                )
                msg.attach(part)

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(pdf_path)}"
                )
                msg.attach(part)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SEND_EMAIL, SEND_PASSWORD)
            server.sendmail(SEND_EMAIL, RECV_EMAIL, msg.as_string())
            server.quit()

        except Exception as e:
            QMessageBox.warning(self, "이메일 오류", str(e))
