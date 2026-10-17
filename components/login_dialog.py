"""
Modern Login Dialog for Mercy Dental Care Attendance & HR System (QT6).
Provides secure login for Administrator and Clinic Staff with Password/PIN verification.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTabWidget, QWidget, QComboBox,
    QMessageBox, QGraphicsDropShadowEffect, QListView
)
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt

import database
from theme import PRIMARY, PRIMARY_HOVER, PRIMARY_LIGHT, BORDER, BG_MAIN, setup_styled_combobox

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_data = None

        self.setWindowTitle("Mercy Dental Care - Sign In / ចូលប្រើប្រព័ន្ធ")
        self.setFixedSize(480, 580)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_MAIN};
            }}
        """)

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Center Card Container
        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            QFrame#loginCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                padding: 16px;
            }
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(14)

        # 1. Logo & Clinic Branding Header
        header_box = QVBoxLayout()
        header_box.setSpacing(6)
        header_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.jpg")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaledToHeight(68, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("🦷")
            logo_lbl.setStyleSheet("font-size: 36px;")
        header_box.addWidget(logo_lbl)

        title_lbl = QLabel("Mercy Dental Care")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {PRIMARY};")
        header_box.addWidget(title_lbl)

        sub_lbl = QLabel(f"{database.get_setting('clinic_name_kh', 'គ្លីនិកទន្តសាស្រ្ត មើស៊ី')} • HR & Attendance System")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 500;")
        header_box.addWidget(sub_lbl)

        c_layout.addLayout(header_box)

        # 2. Tabs for Admin & Staff Sign In
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                top: 6px;
            }}
            QTabBar::tab {{
                background-color: #F8FAFC;
                color: #64748B;
                font-weight: 600;
                font-size: 13px;
                padding: 10px 24px;
                border-radius: 8px;
                margin-right: 6px;
                border: 1px solid #E2E8F0;
            }}
            QTabBar::tab:selected {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border: none;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {PRIMARY_LIGHT};
                color: {PRIMARY};
            }}
        """)

        # Tab 1: Administrator
        admin_tab = QWidget()
        a_layout = QVBoxLayout(admin_tab)
        a_layout.setContentsMargins(6, 14, 6, 6)
        a_layout.setSpacing(10)

        a_layout.addWidget(QLabel("<b>Admin Username:</b>"))
        self.admin_user = QLineEdit("admin")
        self.admin_user.setPlaceholderText("Enter admin username")
        self.admin_user.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #5648A6;
            }
        """)
        a_layout.addWidget(self.admin_user)

        a_layout.addWidget(QLabel("<b>Admin Password:</b>"))
        pwd_box = QHBoxLayout()
        pwd_box.setSpacing(4)
        self.admin_pwd = QLineEdit()
        self.admin_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_pwd.setPlaceholderText("Enter admin password")
        self.admin_pwd.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #5648A6;
            }
        """)
        self.admin_pwd.returnPressed.connect(self.login_admin)

        btn_eye_a = QPushButton("👁️")
        btn_eye_a.setFixedSize(38, 38)
        btn_eye_a.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_a.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 8px; background: #F8FAFC;")
        btn_eye_a.clicked.connect(lambda: self._toggle_echo(self.admin_pwd, btn_eye_a))
        pwd_box.addWidget(self.admin_pwd)
        pwd_box.addWidget(btn_eye_a)
        a_layout.addLayout(pwd_box)

        btn_login_admin = QPushButton("🔓 Sign In as Administrator")
        btn_login_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login_admin.setFixedHeight(42)
        btn_login_admin.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                font-weight: 700;
                font-size: 13px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)
        btn_login_admin.clicked.connect(self.login_admin)
        a_layout.addWidget(btn_login_admin)

        self.tabs.addTab(admin_tab, "🔑 Administrator")

        # Tab 2: Staff Login
        staff_tab = QWidget()
        s_layout = QVBoxLayout(staff_tab)
        s_layout.setContentsMargins(6, 14, 6, 6)
        s_layout.setSpacing(10)

        s_layout.addWidget(QLabel("<b>Select Staff Member (ជ្រើសរើសបុគ្គលិក):</b>"))
        self.staff_combo = QComboBox()
        setup_styled_combobox(self.staff_combo)
        self.staff_combo.setFixedHeight(38)
        self.staff_combo.setStyleSheet("""
            QComboBox {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: #F8FAFC;
                color: #1E293B;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: 1px solid #CBD5E1;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                background-color: #F8FAFC;
            }
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748B;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1E293B;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 4px;
                outline: none;
                selection-background-color: #EDE9FE;
                selection-color: #5648A6;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 6px 10px;
                border-radius: 6px;
                color: #1E293B;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F1F5F9;
                color: #5648A6;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #EDE9FE;
                color: #5648A6;
                font-weight: 600;
            }
        """)
        self._load_staff_combo()
        s_layout.addWidget(self.staff_combo)

        s_layout.addWidget(QLabel("<b>Password / PIN Code (ពាក្យសម្ងាត់):</b>"))
        s_pwd_box = QHBoxLayout()
        s_pwd_box.setSpacing(4)
        self.staff_pwd = QLineEdit()
        self.staff_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.staff_pwd.setPlaceholderText("Password or PIN Code")
        self.staff_pwd.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #5648A6;
            }
        """)
        self.staff_pwd.returnPressed.connect(self.login_staff)

        btn_eye_s = QPushButton("👁️")
        btn_eye_s.setFixedSize(38, 38)
        btn_eye_s.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_s.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 8px; background: #F8FAFC;")
        btn_eye_s.clicked.connect(lambda: self._toggle_echo(self.staff_pwd, btn_eye_s))
        s_pwd_box.addWidget(self.staff_pwd)
        s_pwd_box.addWidget(btn_eye_s)
        s_layout.addLayout(s_pwd_box)

        btn_login_staff = QPushButton("👤 Sign In as Staff")
        btn_login_staff.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login_staff.setFixedHeight(42)
        btn_login_staff.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                font-weight: 700;
                font-size: 13px;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)
        btn_login_staff.clicked.connect(self.login_staff)
        s_layout.addWidget(btn_login_staff)

        self.tabs.addTab(staff_tab, "👥 Staff / បុគ្គលិក")

        c_layout.addWidget(self.tabs)
        layout.addWidget(card)

        # Error label
        self.err_lbl = QLabel()
        self.err_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.err_lbl.setStyleSheet("color: #DC2626; font-size: 12px; font-weight: 600;")
        self.err_lbl.setVisible(False)
        layout.addWidget(self.err_lbl)

    def _toggle_echo(self, line_edit, btn):
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setText("🔒")
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setText("👁️")

    def _load_staff_combo(self):
        self.staff_combo.clear()
        emps = database.get_all_employees()
        for e in emps:
            self.staff_combo.addItem(f"{e['emp_code']} - {e['name']} ({e['khmer_name']})", e["id"])

    def login_admin(self):
        user = self.admin_user.text().strip()
        pwd = self.admin_pwd.text().strip()

        if user != "admin" and user != "Administrator":
            self.err_lbl.setText("❌ Username មិនត្រឹមត្រូវទេ!")
            self.err_lbl.setVisible(True)
            return

        if database.verify_admin_password(pwd):
            self.user_data = {
                "role": "admin",
                "username": "admin",
                "display_name": "Administrator",
                "sub_text": "Mercy Dental Care"
            }
            self.accept()
        else:
            self.err_lbl.setText("❌ Password មិនត្រឹមត្រូវទេ!")
            self.err_lbl.setVisible(True)
            self.admin_pwd.selectAll()
            self.admin_pwd.setFocus()

    def login_staff(self):
        emp_id = self.staff_combo.currentData()
        pwd = self.staff_pwd.text().strip()

        if not emp_id:
            self.err_lbl.setText("❌ សូមជ្រើសរើសបុគ្គលិក!")
            self.err_lbl.setVisible(True)
            return

        if database.verify_employee_credentials(emp_id, pwd):
            emp = database.get_employee_by_id(emp_id)
            self.user_data = {
                "role": "staff",
                "emp_id": emp["id"],
                "emp_code": emp["emp_code"],
                "display_name": f"{emp['name']} ({emp['khmer_name']})",
                "sub_text": f"{emp['job_position']} • {emp['department']}"
            }
            self.accept()
        else:
            self.err_lbl.setText("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
            self.err_lbl.setVisible(True)
            self.staff_pwd.selectAll()
            self.staff_pwd.setFocus()
