import cv2
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap


class CameraWindow(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback  # 촬영 완료 후 report.py 로 경로 전달
        self.cap = None
        self.last_frame = None
        self.preview_mode = False  # False=라이브, True=촬영후 미리보기
        self.setWindowTitle("현장 촬영")
        self.resize(700, 550)
        self.init_ui()
        self.start_camera()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # 카메라 화면
        self.lbl_camera = QLabel()
        self.lbl_camera.setAlignment(Qt.AlignCenter)
        self.lbl_camera.setStyleSheet("""
            QLabel {
                background: #1a2a3a;
                border-radius: 8px;
                min-height: 400px;
            }
        """)
        self.lbl_camera.setText("카메라 시작 중...")
        self.lbl_camera.setStyleSheet(
            "background:#1a2a3a; color:white; font-size:14px;"
            "border-radius:8px; min-height:400px;"
        )

        # 버튼 행
        btn_row = QHBoxLayout()

        self.btn_shoot = QPushButton("📸 촬영")
        self.btn_shoot.setStyleSheet("""
            QPushButton {
                background: #0e9db5; color: white;
                border: none; border-radius: 7px;
                padding: 10px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #0a7a8f; }
        """)
        self.btn_shoot.clicked.connect(self.shoot)

        self.btn_retake = QPushButton("🔄 다시 촬영")
        self.btn_retake.setStyleSheet("""
            QPushButton {
                background: #e67e22; color: white;
                border: none; border-radius: 7px;
                padding: 10px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #d35400; }
        """)
        self.btn_retake.clicked.connect(self.retake)
        self.btn_retake.hide()  # 처음엔 숨김

        self.btn_use = QPushButton("✅ 이 사진 사용")
        self.btn_use.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white;
                border: none; border-radius: 7px;
                padding: 10px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #1e8449; }
        """)
        self.btn_use.clicked.connect(self.use_photo)
        self.btn_use.hide()  # 처음엔 숨김

        self.btn_cancel = QPushButton("취소")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: white; color: #5a8a92;
                border: 1.5px solid #b2dce4; border-radius: 7px;
                padding: 10px 24px; font-size: 13px;
            }
        """)
        self.btn_cancel.clicked.connect(self.cancel)

        btn_row.addWidget(self.btn_shoot)
        btn_row.addWidget(self.btn_retake)
        btn_row.addWidget(self.btn_use)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)

        root.addWidget(self.lbl_camera)
        root.addLayout(btn_row)
        self.setLayout(root)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "카메라 오류", "카메라를 열 수 없습니다.")
            self.close()
            return
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms 마다 갱신 (약 33fps)

    def update_frame(self):
        if self.preview_mode:
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        self.last_frame = frame
        self.show_frame(frame)

    def show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.lbl_camera.setPixmap(
            QPixmap.fromImage(img).scaled(
                self.lbl_camera.width(), self.lbl_camera.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def shoot(self):
        if self.last_frame is None:
            return
        self.preview_mode = True
        self.show_frame(self.last_frame)

        # 버튼 전환
        self.btn_shoot.hide()
        self.btn_retake.show()
        self.btn_use.show()

    def retake(self):
        self.preview_mode = False
        self.btn_shoot.show()
        self.btn_retake.hide()
        self.btn_use.hide()

    def use_photo(self):
        save_path = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(save_path, self.last_frame)
        self.stop_camera()
        self.callback(save_path)  # report.py 로 경로 전달
        self.close()

    def cancel(self):
        self.stop_camera()
        self.close()

    def stop_camera(self):
        if hasattr(self, "timer"):
            self.timer.stop()
        if self.cap:
            self.cap.release()

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()