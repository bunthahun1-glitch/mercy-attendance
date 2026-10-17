"""
Employee Details & Profile Editor Dialog
Faithful recreation of Click HR profile view from IMG_7447 & IMG_7449.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QWidget, QLineEdit, QComboBox,
    QDateEdit, QMessageBox, QGridLayout, QListView
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

import database
from theme import tr, PRIMARY, BORDER, setup_styled_combobox

class EmployeeDialog(QDialog):
    def __init__(self, emp_id=None, parent=None):
        super().__init__(parent)
        self.emp_id = emp_id
        self.is_edit = bool(emp_id)
        self.emp_data = database.get_employee_by_id(emp_id) if emp_id else {}

        self.setWindowTitle("Employee Profile - Mercy Dental Care")
        self.resize(740, 520)
        self.setMinimumSize(640, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #334155;
            }
            QLineEdit, QComboBox {
                min-height: 27px;
                max-height: 29px;
                padding: 1px 7px;
                font-size: 11px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                border: 1.2px solid #CBD5E1;
                border-radius: 5px;
                background-color: #FFFFFF;
                color: #1E293B;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1.5px solid #5648A6;
            }
            QComboBox:editable {
                background: #FFFFFF;
            }
            QComboBox:editable QLineEdit {
                background: transparent;
                border: none;
                padding: 1px 4px;
                color: #1E293B;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 11px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border-left: 1px solid #CBD5E1;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
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
                border: 1.2px solid #CBD5E1;
                border-radius: 6px;
                padding: 3px;
                outline: none;
                selection-background-color: #EDE9FE;
                selection-color: #5648A6;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF;
                min-height: 26px;
                padding: 4px 8px;
                color: #1E293B;
                border-radius: 4px;
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
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                background: #FFFFFF;
                top: -1px;
            }
            QTabBar::tab {
                background: #F8FAFC;
                color: #64748B;
                border: 1px solid #E2E8F0;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 5px 12px;
                font-weight: 600;
                font-size: 11px;
                margin-right: 3px;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #5648A6;
                border-color: #CBD5E1;
                border-bottom: 2px solid #5648A6;
                font-weight: 700;
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 6px;
                margin: 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        from PyQt6.QtWidgets import QScrollArea

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(6)

        # 1. Top Breadcrumb
        code = self.emp_data.get("emp_code", "New Employee")
        name = self.emp_data.get("name", "New Employee")
        breadcrumb = QLabel(f"Dashboard Action  /  Total Employees  /  {code} - {name}")
        breadcrumb.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 500;")
        main_layout.addWidget(breadcrumb)

        # 2. Top Action Buttons (Print Badge on right)
        action_bar = QHBoxLayout()
        action_bar.addStretch()

        btn_print = QPushButton("🖨️ Print Badge")
        btn_print.setStyleSheet("""
            background-color: #F1F5F9;
            color: #334155;
            font-weight: 600;
            border-radius: 5px;
            padding: 4px 10px;
            border: 1px solid #CBD5E1;
            font-size: 11px;
        """)
        btn_print.clicked.connect(self.open_badge)
        action_bar.addWidget(btn_print)

        main_layout.addLayout(action_bar)

        # 3. Middle Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #FFFFFF;")
        c_layout = QVBoxLayout(content_widget)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(6)

        # Employee Title Block (Sleek Horizontal banner)
        title_block = QFrame()
        title_block.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px;")
        t_layout = QHBoxLayout(title_block)
        t_layout.setContentsMargins(10, 6, 10, 6)

        v_name_box = QVBoxLayout()
        v_name_box.setSpacing(1)
        self.name_heading = QLabel(f"{self.emp_data.get('name', 'New Staff')}  ({self.emp_data.get('khmer_name', '')})")
        self.name_heading.setStyleSheet("font-size: 14px; font-weight: 800; color: #1E293B;")
        v_name_box.addWidget(self.name_heading)

        sub_txt = f"Clinic Staff Profile • Mercy Dental Care"
        lbl_sub = QLabel(sub_txt)
        lbl_sub.setStyleSheet("font-size: 10px; color: #64748B;")
        v_name_box.addWidget(lbl_sub)
        t_layout.addLayout(v_name_box)

        t_layout.addStretch()

        id_box = QWidget()
        id_box.setStyleSheet("background: transparent;")
        id_layout = QHBoxLayout(id_box)
        id_layout.setContentsMargins(0, 0, 0, 0)
        id_layout.setSpacing(4)

        lbl_id = QLabel("ID:")
        lbl_id.setStyleSheet("color: #5648A6; font-size: 11.5px; font-weight: 800;")
        id_layout.addWidget(lbl_id)

        self.input_code = QLineEdit(self.emp_data.get("emp_code", ""))
        self.input_code.setPlaceholderText("Auto")
        self.input_code.setFixedWidth(84)
        self.input_code.setFixedHeight(27)
        self.input_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_code.setToolTip("Employee ID (អត្តលេខបុគ្គលិក) - លោកអ្នកអាចកែសម្រួលបាន")
        self.input_code.setStyleSheet("""
            QLineEdit {
                background-color: #EDE9FE;
                color: #5648A6;
                font-size: 11.5px;
                font-weight: 800;
                padding: 1px 6px;
                border-radius: 5px;
                border: 1.5px solid #8B5CF6;
            }
            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 2px solid #5648A6;
            }
        """)
        id_layout.addWidget(self.input_code)
        t_layout.addWidget(id_box)

        c_layout.addWidget(title_block)

        # Core Details (Compact 2x2 grid)
        core_grid = QGridLayout()
        core_grid.setHorizontalSpacing(10)
        core_grid.setVerticalSpacing(4)

        core_grid.addWidget(QLabel("<b>Company:</b>"), 0, 0)
        self.input_company = QLabel("Mercy Dental Care")
        self.input_company.setStyleSheet("color: #5648A6; font-weight: 700; font-size: 11px;")
        core_grid.addWidget(self.input_company, 0, 1)

        core_grid.addWidget(QLabel("<b>Department:</b>"), 0, 2)
        self.input_dept = QComboBox()
        self.input_dept.setEditable(True)
        setup_styled_combobox(self.input_dept)
        if self.input_dept.lineEdit():
            self.input_dept.lineEdit().setPlaceholderText("ជ្រើសរើស ឬវាយបញ្ចូលឈ្មោះផ្នែក...")

        # Load all departments dynamically
        depts = database.get_all_departments()
        for d in depts:
            self.input_dept.addItem(d)

        cur_dept = self.emp_data.get("department", "Dental Surgery")
        if cur_dept:
            if cur_dept not in depts:
                self.input_dept.addItem(cur_dept)
            self.input_dept.setCurrentText(cur_dept)
        core_grid.addWidget(self.input_dept, 0, 3)

        core_grid.addWidget(QLabel("<b>Job Position:</b>"), 1, 0)
        self.input_pos = QLineEdit(self.emp_data.get("job_position", "Dental Assistant"))
        core_grid.addWidget(self.input_pos, 1, 1)

        core_grid.addWidget(QLabel("<b>Manager:</b>"), 1, 2)
        cur_mgr = self.emp_data.get("manager")
        if not cur_mgr or cur_mgr in ("Dr. Bunheng LY", ""):
            cur_mgr = "Dr. Buntha"
        self.input_manager = QLineEdit(cur_mgr)
        core_grid.addWidget(self.input_manager, 1, 3)

        c_layout.addLayout(core_grid)

        # Tabs: Work Information, Personal, Contract & Salary, Compliance
        self.tabs = QTabWidget()

        # Tab 1: Work Information
        work_tab = QWidget()
        w_grid = QGridLayout(work_tab)
        w_grid.setContentsMargins(8, 6, 8, 6)
        w_grid.setVerticalSpacing(5)
        w_grid.setHorizontalSpacing(8)

        w_grid.addWidget(QLabel("English Name:"), 0, 0)
        self.input_name = QLineEdit(self.emp_data.get("name", ""))
        w_grid.addWidget(self.input_name, 0, 1)

        w_grid.addWidget(QLabel("Khmer Name (ឈ្មោះខ្មែរ):"), 0, 2)
        self.input_kh_name = QLineEdit(self.emp_data.get("khmer_name", ""))
        w_grid.addWidget(self.input_kh_name, 0, 3)

        w_grid.addWidget(QLabel("Employee ID (អត្តលេខ):"), 1, 0)
        self.input_code_work = QLineEdit(self.emp_data.get("emp_code", ""))
        self.input_code_work.setPlaceholderText("Auto (ឧ. 001)")
        w_grid.addWidget(self.input_code_work, 1, 1)

        w_grid.addWidget(QLabel("Joining Date:"), 1, 2)
        self.input_join = QLineEdit(self.emp_data.get("join_date", "2024-01-15"))
        w_grid.addWidget(self.input_join, 1, 3)

        w_grid.addWidget(QLabel("Login Users:"), 2, 0)
        self.input_login = QLineEdit(self.emp_data.get("name", "").lower().replace(" ", "."))
        w_grid.addWidget(self.input_login, 2, 1)

        w_grid.addWidget(QLabel("Work Phone:"), 2, 2)
        self.input_phone = QLineEdit(self.emp_data.get("phone", ""))
        w_grid.addWidget(self.input_phone, 2, 3)

        w_grid.addWidget(QLabel("Work Email:"), 3, 0)
        self.input_email = QLineEdit(self.emp_data.get("email", ""))
        w_grid.addWidget(self.input_email, 3, 1)

        w_grid.addWidget(QLabel("Working Hours:"), 3, 2)
        self.input_hours = QLineEdit(self.emp_data.get("working_hours", "Monday-Saturday (07:30 to 18:00)"))
        w_grid.addWidget(self.input_hours, 3, 3)

        w_grid.addWidget(QLabel("PIN Code (កូដកាត):"), 4, 0)
        self.input_pin = QLineEdit(self.emp_data.get("pin_code", "1234"))
        w_grid.addWidget(self.input_pin, 4, 1)

        w_grid.addWidget(QLabel("Password (ពាក្យសម្ងាត់):"), 4, 2)
        pwd_box = QHBoxLayout()
        pwd_box.setSpacing(3)
        self.input_pwd = QLineEdit(self.emp_data.get("password", "123456"))
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_toggle_pwd = QPushButton("👁️")
        self.btn_toggle_pwd.setFixedWidth(28)
        self.btn_toggle_pwd.setFixedHeight(27)
        self.btn_toggle_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_pwd.setToolTip("Show/Hide Password")
        self.btn_toggle_pwd.clicked.connect(self._toggle_pwd_visibility)
        pwd_box.addWidget(self.input_pwd)
        pwd_box.addWidget(self.btn_toggle_pwd)
        w_grid.addLayout(pwd_box, 4, 3)

        w_grid.addWidget(QLabel("Coach:"), 5, 0)
        cur_coach = self.emp_data.get("coach")
        if not cur_coach or cur_coach in ("Dr. Chantra THY", ""):
            cur_coach = "Dr. Vuochlin"
        self.input_coach = QLineEdit(cur_coach)
        w_grid.addWidget(self.input_coach, 5, 1)

        w_grid.addWidget(QLabel("Employment Type:"), 5, 2)
        self.combo_emp_type = QComboBox()
        self.combo_emp_type.addItem("Full-Time (ពេញម៉ោង • ស្កេនធម្មតា)", "Full-Time")
        self.combo_emp_type.addItem("Remote (ពីចម្ងាយ • មិនបាច់ស្កេន)", "Remote")
        self.combo_emp_type.addItem("Part-Time (ក្រៅម៉ោង • ពេលទំនេរ/សៅរ៍)", "Part-Time")
        cur_type = self.emp_data.get("employment_type", "Full-Time")
        idx_type = self.combo_emp_type.findData(cur_type)
        if idx_type >= 0:
            self.combo_emp_type.setCurrentIndex(idx_type)
        w_grid.addWidget(self.combo_emp_type, 5, 3)

        # Sync input_code and input_code_work
        self.input_code.textChanged.connect(lambda t: self.input_code_work.setText(t) if self.input_code_work.text() != t else None)
        self.input_code_work.textChanged.connect(lambda t: self.input_code.setText(t) if self.input_code.text() != t else None)

        self.tabs.addTab(work_tab, "Work Information")

        # Tab 2: Personal Information
        pers_tab = QWidget()
        p_grid = QGridLayout(pers_tab)
        p_grid.setContentsMargins(8, 6, 8, 6)
        p_grid.setVerticalSpacing(5)
        p_grid.setHorizontalSpacing(8)

        p_grid.addWidget(QLabel("Gender:"), 0, 0)
        self.input_gender = QComboBox()
        setup_styled_combobox(self.input_gender)
        self.input_gender.addItems(["Female", "Male"])
        if self.emp_data.get("gender"):
            self.input_gender.setCurrentText(self.emp_data["gender"])
        p_grid.addWidget(self.input_gender, 0, 1)

        p_grid.addWidget(QLabel("Date of Birth:"), 0, 2)
        self.input_dob = QLineEdit(self.emp_data.get("dob", "1995-05-15"))
        p_grid.addWidget(self.input_dob, 0, 3)

        p_grid.addWidget(QLabel("Emergency Contact:"), 1, 0)
        self.input_emg = QLineEdit(self.emp_data.get("emergency_contact", "012 334 556"))
        p_grid.addWidget(self.input_emg, 1, 1)

        p_grid.addWidget(QLabel("Home Address:"), 1, 2)
        self.input_address = QLineEdit(self.emp_data.get("address", "Phnom Penh"))
        p_grid.addWidget(self.input_address, 1, 3)

        p_grid.addWidget(QLabel("Employment Status:"), 2, 0)
        self.input_status = QComboBox()
        setup_styled_combobox(self.input_status)
        self.input_status.addItems(["Active", "On Leave", "Resigned"])
        if self.emp_data.get("status"):
            self.input_status.setCurrentText(self.emp_data["status"])
        p_grid.addWidget(self.input_status, 2, 1)

        self.tabs.addTab(pers_tab, "Personal Information")

        # Tab 3: Contract & Salary
        sal_tab = QWidget()
        s_grid = QGridLayout(sal_tab)
        s_grid.setContentsMargins(8, 6, 8, 6)
        s_grid.setVerticalSpacing(5)
        s_grid.setHorizontalSpacing(8)

        s_grid.addWidget(QLabel("Base Salary (USD):"), 0, 0)
        self.input_salary = QLineEdit(str(self.emp_data.get("base_salary", "500.0")))
        s_grid.addWidget(self.input_salary, 0, 1)

        s_grid.addWidget(QLabel("Payment Structure:"), 0, 2)
        s_grid.addWidget(QLabel("Mercy Dental Clinic Base Structure"), 0, 3)

        self.tabs.addTab(sal_tab, "Contract & Salary")

        # Tab 4: Compliance
        comp_tab = QWidget()
        c_v = QVBoxLayout(comp_tab)
        c_v.setContentsMargins(8, 6, 8, 6)
        c_v.addWidget(QLabel("• Dental Council Medical License: Verified ✓\n• Sterilization & Infection Control Protocol: Certified ✓\n• Staff Ethics & Patient Privacy: Signed ✓"))
        self.tabs.addTab(comp_tab, "Compliance")

        c_layout.addWidget(self.tabs)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area, 1)

        # Pinned Bottom Buttons (Always visible at the bottom)
        bot_h = QHBoxLayout()
        bot_h.addStretch()

        btn_cancel = QPushButton("Close (បិទ)")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                padding: 6px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        bot_h.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Save Changes (រក្សាទុក)")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: white;
                padding: 6px 20px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #43368E;
            }
        """)
        btn_save.clicked.connect(self.save_employee_data)
        bot_h.addWidget(btn_save)

        main_layout.addLayout(bot_h)

    def _toggle_pwd_visibility(self):
        if self.input_pwd.echoMode() == QLineEdit.EchoMode.Password:
            self.input_pwd.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_pwd.setText("🔒")
        else:
            self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_pwd.setText("👁️")

    def save_employee_data(self):
        name = self.input_name.text().strip()
        kh_name = self.input_kh_name.text().strip() or name

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please provide Employee Name.")
            return

        data = {
            "emp_code": self.input_code.text().strip(),
            "name": name,
            "khmer_name": kh_name,
            "gender": self.input_gender.currentText(),
            "dob": self.input_dob.text().strip(),
            "phone": self.input_phone.text().strip(),
            "email": self.input_email.text().strip(),
            "address": self.input_address.text().strip(),
            "department": self.input_dept.currentText().strip() or "Dental Surgery",
            "job_position": self.input_pos.text().strip(),
            "manager": self.input_manager.text().strip() or "Dr. Buntha",
            "coach": self.input_coach.text().strip() or "Dr. Vuochlin",
            "join_date": self.input_join.text().strip(),
            "status": self.input_status.currentText(),
            "base_salary": float(self.input_salary.text().strip() or 500),
            "working_hours": self.input_hours.text().strip(),
            "pin_code": self.input_pin.text().strip(),
            "password": self.input_pwd.text().strip(),
            "emergency_contact": self.input_emg.text().strip(),
            "employment_type": self.combo_emp_type.currentData() or "Full-Time"
        }

        database.save_employee(data, self.emp_id)
        QMessageBox.information(self, "Success", f"Employee {name} information saved successfully!")
        self.accept()

    def open_badge(self):
        from components.badge_dialog import BadgeDialog
        dlg = BadgeDialog(self.emp_data, parent=self)
        dlg.exec()
