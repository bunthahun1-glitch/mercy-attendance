"""
Main Window for Mercy Dental Care - HR & Attendance Management System (QT6).
Implements sidebar navigation, top header, page switching, and bilingual localization.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QButtonGroup, QFrame, QLineEdit,
    QComboBox, QMessageBox, QListView
)
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

import database
import theme
from theme import tr, set_language, APP_STYLE, PRIMARY, BORDER, setup_styled_combobox

from views.dashboard_view import DashboardView
from views.employees_view import EmployeesView
from views.attendance_view import AttendanceView
from views.leave_view import LeaveView
from views.payroll_view import PayrollView
from views.requests_view import RequestsView
from views.settings_view import SettingsView
from components.kiosk_widget import KioskWidget

class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user or {
            "role": "admin",
            "username": "admin",
            "display_name": "Administrator",
            "sub_text": "Mercy Dental Care"
        }

        self.setWindowTitle("Mercy Dental Care - HR & Attendance Management System")
        self.resize(1340, 860)
        self.setMinimumSize(1080, 700)
        self.setStyleSheet(APP_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = self._create_sidebar()
        root_layout.addWidget(self.sidebar)

        # 2. Right Content Area (Top Header + Stacked Pages)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.top_header = self._create_top_header()
        content_layout.addWidget(self.top_header)

        # Stacked Pages
        self.stack = QStackedWidget()

        self.page_dashboard = DashboardView()
        self.page_employees = EmployeesView()
        self.page_attendance = AttendanceView()
        self.page_leave = LeaveView()
        self.page_payroll = PayrollView()
        self.page_requests = RequestsView()
        self.page_settings = SettingsView()

        # Page Kiosk container (centered)
        kiosk_page = QWidget()
        k_layout = QVBoxLayout(kiosk_page)
        k_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kiosk_widget = KioskWidget()
        k_layout.addWidget(self.kiosk_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.page_dashboard)    # Index 0
        self.stack.addWidget(self.page_employees)    # Index 1
        self.stack.addWidget(self.page_attendance)   # Index 2
        self.stack.addWidget(self.page_leave)        # Index 3
        self.stack.addWidget(self.page_payroll)      # Index 4
        self.stack.addWidget(self.page_requests)     # Index 5
        self.stack.addWidget(kiosk_page)             # Index 6
        self.stack.addWidget(self.page_settings)     # Index 7

        content_layout.addWidget(self.stack)
        root_layout.addWidget(content_container)

        # Wire cross-view signals
        self.page_dashboard.open_employee.connect(self.navigate_to_employee)
        self.page_dashboard.open_attendance.connect(lambda: self.switch_page(2))
        self.page_dashboard.request_leave_requested.connect(self.page_leave.request_leave)
        self.kiosk_widget.attendance_updated.connect(self.on_attendance_updated)
        self.page_settings.language_changed.connect(self.on_language_changed)
        self.page_settings.permissions_changed.connect(lambda p: self.apply_user_permissions())

        # Timer for header clock
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_header_clock)
        self.clock_timer.start(1000)
        self.update_header_clock()

        # Apply user profile and permissions, then land on appropriate page
        self.set_logged_in_user(self.current_user)
        if hasattr(self, 'sidebar_pie'):
            self.sidebar_pie.set_data(database.get_dept_distribution())

    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebarContainer")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Logo and Clinic Title (Click to return Home / Dashboard or Kiosk)
        brand_frame = QFrame()
        brand_frame.setObjectName("brandFrame")
        brand_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        brand_frame.setToolTip("ត្រឡប់ទៅទំព័រដើម (Go to Home / Dashboard)")
        brand_frame.mousePressEvent = lambda event: self.switch_page(0 if self.current_user.get("role") == "admin" else 6)

        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(6, 4, 6, 12)
        brand_layout.setSpacing(10)

        logo_lbl = QLabel()
        logo_lbl.setStyleSheet("background: transparent; border: none;")
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.jpg")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaledToHeight(52, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("🦷")
            logo_lbl.setStyleSheet("font-size: 26px;")
        brand_layout.addWidget(logo_lbl)

        brand_text_v = QVBoxLayout()
        brand_text_v.setSpacing(1)
        self.brand_title = QLabel("Mercy Dental Care")
        self.brand_title.setObjectName("brandTitle")
        self.brand_sub = QLabel("HR & Attendance")
        self.brand_sub.setObjectName("brandSubtitle")
        brand_text_v.addWidget(self.brand_title)
        brand_text_v.addWidget(self.brand_sub)
        brand_layout.addLayout(brand_text_v)

        layout.addWidget(brand_frame)

        # Navigation Buttons matching Click HR sidebar
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_items = [
            ("📊", "nav_dashboard", 0, "dashboard"),
            ("👥", "nav_employees", 1, "employees"),
            ("⏱️", "nav_attendances", 2, "attendance"),
            ("📅", "nav_leave", 3, "leave"),
            ("💵", "nav_payroll", 4, "payroll"),
            ("📋", "nav_requests", 5, "requests"),
            ("📱", "nav_kiosk", 6, "kiosk"),
            ("⚙️", "nav_settings", 7, "settings")
        ]

        self.nav_btns = []
        for icon, tr_key, idx, perm_key in self.nav_items:
            btn = QPushButton(f"{icon}  {tr(tr_key)}")
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav_group.addButton(btn, idx)
            layout.addWidget(btn)
            self.nav_btns.append(btn)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))

        # Mini By Departments Donut Card below Settings in Sidebar
        from components.pie_chart import DepartmentPieChartWidget
        self.sidebar_pie = DepartmentPieChartWidget()
        self.sidebar_pie.setObjectName("sidebarPieCard")
        self.sidebar_pie.setStyleSheet("""
            QFrame#sidebarPieCard {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
                padding: 6px 8px;
                margin-top: 4px;
            }
        """)
        self.sidebar_pie.title_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #1E293B;")
        self.sidebar_pie.canvas.setFixedHeight(75)
        self.sidebar_pie.canvas.setMinimumSize(60, 60)
        self.sidebar_pie.set_data(database.get_dept_distribution(), is_khmer=True)
        layout.addWidget(self.sidebar_pie)

        layout.addStretch()

        # Bottom Profile Card (Admin or Staff)
        user_card = QFrame()
        user_card.setStyleSheet(f"""
            QFrame {{
                background-color: #F8FAFC;
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: #5648A6;
                background-color: #EEEDFB;
            }}
        """)
        user_card.setCursor(Qt.CursorShape.PointingHandCursor)
        user_card.setToolTip("ព័ត៌មានគណនីបច្ចុប្បន្ន (Current Account Info)")
        user_card.mousePressEvent = self._on_user_card_clicked
        u_layout = QHBoxLayout(user_card)
        u_layout.setContentsMargins(6, 6, 6, 6)
        u_layout.setSpacing(8)

        u_avatar = QLabel("👤")
        u_avatar.setFixedSize(34, 34)
        u_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        u_avatar.setStyleSheet("background-color: #EEEDFB; border-radius: 17px; font-size: 16px;")
        u_layout.addWidget(u_avatar)

        u_text = QVBoxLayout()
        u_text.setSpacing(1)
        self.u_name = QLabel("Administrator")
        self.u_name.setStyleSheet("font-size: 12px; font-weight: 700; color: #1E293B;")
        self.u_role = QLabel("Mercy Dental Care")
        self.u_role.setStyleSheet("font-size: 10px; color: #64748B;")
        u_text.addWidget(self.u_name)
        u_text.addWidget(self.u_role)
        u_layout.addLayout(u_text)

        layout.addWidget(user_card)

        # Logout Button in Sidebar
        self.btn_logout_side = QPushButton("🚪  Log Out / ចាកចេញ")
        self.btn_logout_side.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout_side.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                color: #DC2626;
                font-weight: 700;
                font-size: 12px;
                padding: 8px 14px;
                border-radius: 8px;
                border: 1px solid #FECACA;
                margin-top: 4px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        self.btn_logout_side.clicked.connect(self.handle_logout)
        layout.addWidget(self.btn_logout_side)

        return sidebar

    def _create_top_header(self):
        header = QWidget()
        header.setObjectName("topHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(16)

        # Page Title / Breadcrumbs (Click to return Home / Dashboard)
        self.header_title = QLabel("Mercy Dental Care  /  Dashboard")
        self.header_title.setObjectName("headerTitle")
        self.header_title.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_title.setToolTip("ត្រឡប់ទៅទំព័រដើម (Go to Home / Dashboard)")
        self.header_title.mousePressEvent = lambda event: self.switch_page(0)
        layout.addWidget(self.header_title)

        layout.addStretch()

        # Live Clock Widget
        self.header_clock = QLabel()
        self.header_clock.setStyleSheet("font-size: 13px; font-weight: 700; color: #5648A6; background-color: #EEEDFB; border-radius: 6px; padding: 6px 12px;")
        layout.addWidget(self.header_clock)

        # Language Selector
        self.lang_combo = QComboBox()
        setup_styled_combobox(self.lang_combo)
        self.lang_combo.setFixedWidth(130)
        self.lang_combo.addItem("🇰🇭 ខ្មែរ", "kh")
        self.lang_combo.addItem("🇬🇧 English", "en")
        self.lang_combo.currentIndexChanged.connect(self.on_lang_dropdown_changed)
        layout.addWidget(self.lang_combo)

        # Mobile Web Check-in QR Button
        btn_mob_qr = QPushButton("📱 Mobile QR")
        btn_mob_qr.setToolTip("ស្កេនវត្តមានតាមទូរស័ព្ទដៃ (Scan with Phone)")
        btn_mob_qr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_mob_qr.setStyleSheet("""
            QPushButton {
                background-color: #EEEDFB;
                color: #5648A6;
                font-weight: 700;
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 8px;
                border: 1px solid #D0CCF7;
            }
            QPushButton:hover {
                background-color: #5648A6;
                color: #FFFFFF;
            }
        """)
        btn_mob_qr.clicked.connect(self.open_mobile_qr_dialog)
        layout.addWidget(btn_mob_qr)

        # Notifications Bell Button
        bell_btn = QPushButton("🔔")
        bell_btn.setFixedSize(36, 36)
        bell_btn.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #EEEDFB;
            }
        """)
        bell_btn.clicked.connect(lambda: QMessageBox.information(self, "Notifications", "• 18 staff members clocked in today.\n• 2 pending requests require review."))
        layout.addWidget(bell_btn)

        # Top Header Logout Button
        top_logout_btn = QPushButton("🚪 Log Out")
        top_logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        top_logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEE2E2;
                color: #DC2626;
                font-weight: 700;
                font-size: 12px;
                padding: 6px 14px;
                border-radius: 8px;
                border: 1px solid #FECACA;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        top_logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(top_logout_btn)

        return header

    def _on_user_card_clicked(self, event):
        if self.current_user.get("role") == "admin":
            self.switch_page(7)
        else:
            QMessageBox.information(
                self, "ព័ត៌មានគណនី (Staff Account)",
                f"👤 គណនីបុគ្គលិក:\n"
                f"ឈ្មោះ: {self.current_user.get('display_name', '')}\n"
                f"តួនាទី: {self.current_user.get('sub_text', '')}\n\n"
                f"🔒 សិទ្ធិមើល និងប្រើប្រាស់ទំព័រ ត្រូវបានកំណត់ដោយ Administrator។"
            )

    def apply_user_permissions(self):
        role = self.current_user.get("role", "admin")
        if role == "admin":
            for btn in self.nav_btns:
                btn.setVisible(True)
            return

        perms = database.get_staff_permissions()
        first_allowed = None
        for i, (icon, tr_key, idx, perm_key) in enumerate(self.nav_items):
            allowed = perms.get(perm_key, True)
            self.nav_btns[i].setVisible(allowed)
            if allowed and first_allowed is None:
                first_allowed = idx

        # If current page is restricted for this staff, switch to first allowed page
        current_idx = self.stack.currentIndex()
        if current_idx < len(self.nav_items):
            current_perm = self.nav_items[current_idx][3]
            if not perms.get(current_perm, True):
                target = first_allowed if first_allowed is not None else 6
                self.switch_page(target)

    def set_logged_in_user(self, user_data):
        self.current_user = user_data
        self.u_name.setText(user_data.get("display_name", "Administrator"))
        self.u_role.setText(user_data.get("sub_text", "Mercy Dental Care"))
        self.apply_user_permissions()

        if user_data.get("role") == "staff":
            if hasattr(self, "kiosk_widget"):
                idx = self.kiosk_widget.staff_combo.findData(user_data.get("emp_id"))
                if idx >= 0:
                    self.kiosk_widget.staff_combo.setCurrentIndex(idx)
            # Staff lands on Quick Attendance Kiosk (page 6) first
            self.switch_page(6)
        else:
            self.switch_page(0)

    def handle_logout(self):
        reply = QMessageBox.question(
            self, "Log Out / ចាកចេញ",
            "តើលោកអ្នកពិតជាចង់ចាកចេញ (Log Out) ពីប្រព័ន្ធមែនទេ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.hide()
            from components.login_dialog import LoginDialog
            dlg = LoginDialog()
            if dlg.exec():
                self.set_logged_in_user(dlg.user_data)
                self.show()
                self.raise_()
                self.activateWindow()
            else:
                from PyQt6.QtWidgets import QApplication
                QApplication.quit()

    def switch_page(self, index):
        role = self.current_user.get("role", "admin")
        if role == "staff" and index < len(self.nav_items):
            perms = database.get_staff_permissions()
            perm_key = self.nav_items[index][3]
            if not perms.get(perm_key, True):
                QMessageBox.warning(
                    self, "គ្មានសិទ្ធិចូលប្រើ (Access Restricted)",
                    "ផ្នែកនេះត្រូវបានកំណត់ដោយ Admin មិនអនុញ្ញាតឱ្យបុគ្គលិកចូលប្រើប្រាស់ឡើយ!\n"
                    "This section is restricted for staff accounts by Administrator."
                )
                return

        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == index)

        # Update header breadcrumbs
        titles = [
            "Mercy Dental Care  /  Dashboard",
            "Dashboard Action  /  Total Employees",
            "Mercy Dental Care  /  Attendances",
            "Mercy Dental Care  /  Leave Management",
            "Mercy Dental Care  /  Payroll",
            "Mercy Dental Care  /  Staff Requests",
            "Mercy Dental Care  /  Quick Attendance Kiosk",
            "Mercy Dental Care  /  Clinic Settings"
        ]
        if index < len(titles):
            self.header_title.setText(titles[index])

        # Refresh page data when switched
        if index == 0:
            self.page_dashboard.refresh_dashboard()
        elif index == 1:
            self.page_employees.load_employees()
        elif index == 2:
            self.page_attendance.load_attendance()
        elif index == 3:
            self.page_leave.load_leave_requests()
        elif index == 4:
            self.page_payroll.load_payroll()
        elif index == 5:
            self.page_requests.load_requests()

    def update_header_clock(self):
        now = datetime.now()
        self.header_clock.setText(now.strftime("📅 %d-%b-%Y  ⏰ %H:%M:%S"))

    def navigate_to_employee(self, emp_id):
        self.switch_page(1)
        self.page_employees.open_employee_profile(emp_id)

    def on_attendance_updated(self):
        self.page_dashboard.refresh_dashboard()
        self.page_attendance.load_attendance()

    def on_lang_dropdown_changed(self, idx):
        lang = self.lang_combo.currentData()
        set_language(lang)
        self.update_ui_texts()

    def on_language_changed(self, lang):
        idx = 0 if lang == "kh" else 1
        self.lang_combo.setCurrentIndex(idx)
        self.update_ui_texts()

    def update_ui_texts(self):
        # Refresh sidebar navigation button texts
        for i, (icon, tr_key, idx, perm_key) in enumerate(self.nav_items):
            self.nav_btns[i].setText(f"{icon}  {tr(tr_key)}")

        self.brand_title.setText(tr("company_name"))
        if hasattr(self, 'sidebar_pie'):
            self.sidebar_pie.set_data(database.get_dept_distribution(), is_khmer=True)
        self.page_dashboard.refresh_dashboard()

    def open_mobile_qr_dialog(self):
        from components.mobile_qr_dialog import MobileQrDialog
        dlg = MobileQrDialog(parent=self)
        dlg.exec()
