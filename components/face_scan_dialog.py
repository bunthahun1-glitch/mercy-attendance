"""
Face Scan Verification Dialog for Mercy Dental Care Kiosk.
Uses the desktop camera/webcam to verify staff face during Check-In & Check-Out,
with graceful fallback to Password/PIN.
"""

import os
import cv2
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor

import database
from theme import PRIMARY, BORDER

class FaceScanDialog(QDialog):
    def __init__(self, emp_id, action_name="Check In / ចូលធ្វើការ", parent=None):
        super().__init__(parent)
        self.emp_id = emp_id
        self.action_name = action_name
        self.emp = database.get_employee_by_id(emp_id) or {}
        self.use_password_fallback = False
        self.captured_photo_path = None

        self.setWindowTitle("📸 ស្កេនផ្ទៃមុខបុគ្គលិក (Face Scan Verification)")
        self.setFixedSize(460, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # 1. Staff Header Info
        header_card = QFrame()
        header_card.setStyleSheet(f"""
            background-color: #F8FAFC;
            border: 1.5px solid {BORDER};
            border-radius: 12px;
            padding: 8px 12px;
        """)
        h_box = QHBoxLayout(header_card)
        h_box.setContentsMargins(6, 4, 6, 4)
        h_box.setSpacing(10)

        avatar_lbl = QLabel("👤")
        avatar_lbl.setStyleSheet("font-size: 26px;")
        h_box.addWidget(avatar_lbl)

        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        name_txt = f"{self.emp.get('emp_code', '')} - {self.emp.get('khmer_name', '')} ({self.emp.get('name', '')})"
        lbl_name = QLabel(name_txt)
        lbl_name.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #1E293B;")
        info_v.addWidget(lbl_name)

        lbl_sub = QLabel(f"សកម្មភាព៖ <b style='color:#5648A6;'>{action_name}</b>")
        lbl_sub.setStyleSheet("font-size: 11.5px; color: #64748B;")
        info_v.addWidget(lbl_sub)
        h_box.addLayout(info_v)
        h_box.addStretch()

        badge_kiosk = QLabel("🦷 Kiosk Cam")
        badge_kiosk.setStyleSheet("""
            background-color: #EEEDFB;
            color: #5648A6;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
        """)
        h_box.addWidget(badge_kiosk)
        layout.addWidget(header_card)

        # 2. Camera Frame Container
        self.cam_frame = QFrame()
        self.cam_frame.setStyleSheet("""
            background-color: #0F172A;
            border: 2px solid #5648A6;
            border-radius: 16px;
        """)
        cam_v = QVBoxLayout(self.cam_frame)
        cam_v.setContentsMargins(6, 6, 6, 6)
        cam_v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.video_label = QLabel()
        self.video_label.setFixedSize(360, 290)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("border-radius: 12px; background-color: #1E293B;")
        self.video_label.setText("🎥 កំពុងបើកកាមេរ៉ាស្កេនមុខ...")
        cam_v.addWidget(self.video_label)

        layout.addWidget(self.cam_frame)

        # 3. Status text & Guide
        self.status_lbl = QLabel("👀 សូមសម្លឹងមើលកាមេរ៉ា ដើម្បីស្កេនផ្ទៃមុខផ្ទៀងផ្ទាត់")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #475569;")
        layout.addWidget(self.status_lbl)

        # 4. Action Buttons
        self.btn_capture = QPushButton("📸 ស្កេនមុខ & បញ្ជាក់ (Scan & Verify Face)")
        self.btn_capture.setFixedHeight(44)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5648A6, stop:1 #433688);
                color: white;
                font-size: 13.5px;
                font-weight: 700;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background: #433688;
            }
        """)
        self.btn_capture.clicked.connect(self.capture_and_confirm)
        layout.addWidget(self.btn_capture)

        # Secondary row: Password fallback & Cancel
        sub_row = QHBoxLayout()
        sub_row.setSpacing(10)

        self.btn_pwd = QPushButton("🔑 ប្រើ Password / PIN ជំនួស")
        self.btn_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pwd.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                color: #475569;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 11.5px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #EEEDFB;
                color: #5648A6;
                border-color: #5648A6;
            }
        """)
        self.btn_pwd.clicked.connect(self.switch_to_password)
        sub_row.addWidget(self.btn_pwd)

        btn_cancel = QPushButton("បោះបង់ (Cancel)")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #64748B;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 7px 14px;
                font-size: 11.5px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        sub_row.addWidget(btn_cancel)

        layout.addLayout(sub_row)

        # Initialize Webcam
        self.cap = None
        self.current_frame = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.init_camera()

    def init_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap or not self.cap.isOpened():
                self.video_label.setText("⚠️ រកមិនឃើញកាមេរ៉ា Webcam ទេ\n(សូមប្រើ Password ជំនួស)")
                self.btn_capture.setEnabled(False)
                return
            self.timer.start(30)
        except Exception as e:
            self.video_label.setText(f"⚠️ កំហុសកាមេរ៉ា: {e}")
            self.btn_capture.setEnabled(False)

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        self.current_frame = frame.copy()

        # Flip horizontally for natural selfie view
        frame = cv2.flip(frame, 1)

        # Overlay face scanning frame graphics
        h, w, c = frame.shape
        center_x, center_y = w // 2, h // 2
        radius_x, radius_y = int(w * 0.22), int(h * 0.32)

        # Draw biometric target oval
        cv2.ellipse(frame, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, (166, 72, 86), 2)
        # Corner brackets
        cv2.putText(frame, "MERCY DENTAL FACE ID", (center_x - 90, center_y + radius_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (166, 72, 86), 1, cv2.LINE_AA)

        # Convert to Qt QImage
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb_frame.data, w, h, 3 * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(360, 290, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(pix)

    def capture_and_confirm(self):
        if self.current_frame is None:
            QMessageBox.warning(self, "កាមេរ៉ា", "មិនទាន់អាចថតរូបបានទេ សូមរង់ចាំបន្តិច!")
            return

        # Biometric Face Verification
        try:
            import face_service
            face_ok, score, msg = face_service.verify_face(self.emp_id, self.current_frame)
            if not face_ok:
                QMessageBox.warning(self, "ផ្ទៀងផ្ទាត់ផ្ទៃមុខមិនជោគជ័យ", msg)
                return
        except Exception as e:
            print("Face service verification error in kiosk:", e)

        # Save photo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        selfies_dir = os.path.join(base_dir, "uploads", "selfies")
        os.makedirs(selfies_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kiosk_face_{self.emp_id}_{ts}.jpg"
        self.captured_photo_path = os.path.join(selfies_dir, filename)

        try:
            cv2.imwrite(self.captured_photo_path, self.current_frame)
        except Exception as e:
            print("Failed to save face image:", e)

        self.cleanup_camera()
        self.accept()

    def switch_to_password(self):
        self.use_password_fallback = True
        self.cleanup_camera()
        self.reject()

    def cleanup_camera(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def closeEvent(self, event):
        self.cleanup_camera()
        super().closeEvent(event)
