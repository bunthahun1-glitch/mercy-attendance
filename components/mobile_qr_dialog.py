import qrcode
import io
import socket
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QApplication, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QFont

import database

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class MobileQrDialog(QDialog):
    def __init__(self, parent=None, port=5000):
        super().__init__(parent)
        self.port = port
        self.setWindowTitle("📱 ស្កេនវត្តមានតាមទូរស័ព្ទ (Mobile Web Check-in QR)")
        self.setFixedSize(500, 710)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.wifi_ssid = database.get_setting("wifi_ssid", "Mercy Dental Care")
        self.local_ip = get_local_ip()
        self.public_url = database.get_setting("mobile_public_url", "").strip()
        
        # Default to public subdomain if available, else local IP
        self.active_mode = "subdomain" if self.public_url else "wifi"
        self.url = self.public_url if (self.active_mode == "subdomain") else f"http://{self.local_ip}:{self.port}"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # 1. Header Title
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("📱 QR Code ស្កេនវត្តមានលើទូរស័ព្ទដៃ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E293B;")
        title_box.addWidget(title)

        subtitle = QLabel("Mercy Dental Care • Mobile Attendance System")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600;")
        title_box.addWidget(subtitle)
        main_layout.addLayout(title_box)

        # 2. Network Mode Toggle (Cloudflare Subdomain vs Local Wi-Fi)
        mode_frame = QFrame()
        mode_frame.setStyleSheet("""
            QFrame {
                background-color: #F1F5F9;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(4, 4, 4, 4)
        mode_layout.setSpacing(6)

        self.btn_mode_cf = QPushButton("🌐 Cloudflare Subdomain")
        self.btn_mode_cf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_cf.setFixedHeight(32)
        self.btn_mode_cf.clicked.connect(lambda: self.switch_mode("subdomain"))

        self.btn_mode_wifi = QPushButton("📶 Local Wi-Fi (IP)")
        self.btn_mode_wifi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_wifi.setFixedHeight(32)
        self.btn_mode_wifi.clicked.connect(lambda: self.switch_mode("wifi"))

        mode_layout.addWidget(self.btn_mode_cf)
        mode_layout.addWidget(self.btn_mode_wifi)
        main_layout.addWidget(mode_frame)
        self._update_mode_buttons()

        # 3. Clinic Wi-Fi Highlight Card
        wifi_card = QFrame()
        wifi_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EEEDFB, stop:1 #F3F0FF);
                border: 1.5px solid #C4B5FD;
                border-radius: 14px;
                padding: 10px 14px;
            }
        """)
        wifi_h = QHBoxLayout(wifi_card)
        wifi_h.setContentsMargins(8, 6, 8, 6)
        wifi_h.setSpacing(12)

        icon_lbl = QLabel("📶")
        icon_lbl.setStyleSheet("font-size: 24px;")
        wifi_h.addWidget(icon_lbl)

        wifi_text_v = QVBoxLayout()
        wifi_text_v.setSpacing(2)
        lbl_w_title = QLabel("Wi-Fi គ្លីនិកដែលត្រូវភ្ជាប់ (Required Clinic Wi-Fi):")
        lbl_w_title.setStyleSheet("font-size: 11.5px; color: #5B21B6; font-weight: 600;")
        wifi_text_v.addWidget(lbl_w_title)

        self.lbl_w_name = QLabel(f"🦷 {self.wifi_ssid}")
        self.lbl_w_name.setStyleSheet("font-size: 15px; color: #433688; font-weight: 800;")
        wifi_text_v.addWidget(self.lbl_w_name)
        wifi_h.addLayout(wifi_text_v)
        wifi_h.addStretch()

        badge_lock = QLabel("🔒 ប្រើ Wi-Fi តែមួយ")
        badge_lock.setStyleSheet("""
            background-color: #5648A6;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 12px;
        """)
        wifi_h.addWidget(badge_lock)

        main_layout.addWidget(wifi_card)

        # 4. QR Code Card
        qr_card = QFrame()
        qr_card.setStyleSheet("""
            background-color: #FFFFFF;
            border: 2px solid #E2E8F0;
            border-radius: 18px;
            padding: 12px;
        """)
        qr_v = QVBoxLayout(qr_card)
        qr_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_v.setContentsMargins(10, 10, 10, 10)

        self.lbl_qr = QLabel()
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.generate_qr_pixmap()
        qr_v.addWidget(self.lbl_qr)

        main_layout.addWidget(qr_card)

        # 5. URL Box with Copy & Refresh
        url_box = QFrame()
        url_box.setStyleSheet("""
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 10px;
            padding: 6px 10px;
        """)
        url_h = QHBoxLayout(url_box)
        url_h.setContentsMargins(6, 4, 6, 4)
        url_h.setSpacing(8)

        self.lbl_url = QLabel(self.url)
        self.lbl_url.setStyleSheet("font-size: 12px; font-weight: 700; color: #5648A6;")
        url_h.addWidget(self.lbl_url)
        url_h.addStretch()

        btn_copy = QPushButton("📋 ចម្លង (Copy)")
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #EEEDFB;
                color: #5648A6;
                border: 1px solid #D0CCF7;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5648A6;
                color: white;
            }
        """)
        btn_copy.clicked.connect(self.copy_url)
        url_h.addWidget(btn_copy)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setToolTip("ធ្វើបច្ចុប្បន្នភាព IP Address ពេលប្តូរ Wi-Fi")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_refresh.clicked.connect(self.refresh_ip)
        url_h.addWidget(btn_refresh)

        main_layout.addWidget(url_box)

        # 5. Security Guidance Information Box
        sec_info = QFrame()
        sec_info.setStyleSheet("""
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 10px 12px;
        """)
        sec_v = QVBoxLayout(sec_info)
        sec_v.setContentsMargins(8, 6, 8, 6)
        sec_v.setSpacing(6)

        rule1 = QLabel("👥 <b>បុគ្គលិកស្កេនវត្តមាន៖</b> ត្រូវតែភ្ជាប់ Wi-Fi «<b>Mercy Dental Care</b>» នៅគ្លីនិកប៉ុណ្ណោះ ទើបស្កេនបាន។ បុគ្គលិកប្រើ 4G/5G ឬនៅក្រៅគ្លីនិក មិនអាចបើកស្កេនបានឡើយ។")
        rule1.setWordWrap(True)
        rule1.setStyleSheet("font-size: 11px; color: #334155; line-height: 1.4;")
        sec_v.addWidget(rule1)

        rule2 = QLabel("🛡️ <b>គណនី Admin៖</b> Admin អាចបើកមើលទិន្នន័យ របាយការណ៍ និងវត្តមានបុគ្គលិកបានពីគ្រប់ទីកន្លែងនៅក្នុងកម្មវិធីនេះ។")
        rule2.setWordWrap(True)
        rule2.setStyleSheet("font-size: 11px; color: #166534; line-height: 1.4;")
        sec_v.addWidget(rule2)

        main_layout.addWidget(sec_info)

        # 6. Close Button
        btn_close = QPushButton("បិទ (Close)")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: white;
                font-size: 13px;
                font-weight: 700;
                border-radius: 9px;
                border: none;
            }
            QPushButton:hover {
                background-color: #493D90;
            }
        """)
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close)

    def _update_mode_buttons(self):
        style_active = """
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11.5px;
                border-radius: 7px;
                border: none;
                padding: 4px 12px;
            }
        """
        style_inactive = """
            QPushButton {
                background-color: transparent;
                color: #64748B;
                font-weight: 600;
                font-size: 11.5px;
                border-radius: 7px;
                border: none;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
        """
        if self.active_mode == "subdomain":
            self.btn_mode_cf.setStyleSheet(style_active)
            self.btn_mode_wifi.setStyleSheet(style_inactive)
        else:
            self.btn_mode_cf.setStyleSheet(style_inactive)
            self.btn_mode_wifi.setStyleSheet(style_active)

    def switch_mode(self, mode):
        self.public_url = database.get_setting("mobile_public_url", "").strip()
        if mode == "subdomain" and not self.public_url:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "កំណត់ Cloudflare Subdomain", 
                "លោកអ្នកមិនទាន់បានកំណត់ Cloudflare Subdomain នៅក្នុងទំព័រ Settings នៅឡើយទេ។\n\nសូមចូលទៅកាន់ Settings -> Mobile Attendance រួចបញ្ចូល Subdomain (ឧ. https://attendance.yourdomain.com)។"
            )
            return

        self.active_mode = mode
        if mode == "subdomain":
            self.url = self.public_url
        else:
            self.local_ip = get_local_ip()
            self.url = f"http://{self.local_ip}:{self.port}"

        self._update_mode_buttons()
        self.lbl_url.setText(self.url)
        self.generate_qr_pixmap()

    def generate_qr_pixmap(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#5648A6", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qimg = QImage.fromData(buf.getvalue())
        pix = QPixmap.fromImage(qimg).scaled(210, 210, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_qr.setPixmap(pix)

    def refresh_ip(self):
        if self.active_mode == "subdomain":
            self.public_url = database.get_setting("mobile_public_url", "").strip()
            self.url = self.public_url or f"http://{get_local_ip()}:{self.port}"
        else:
            self.local_ip = get_local_ip()
            self.url = f"http://{self.local_ip}:{self.port}"
        self.lbl_url.setText(self.url)
        self.generate_qr_pixmap()

    def copy_url(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.url)
