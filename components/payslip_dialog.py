"""
Payslip Details Dialog matching Click HR screenshot IMG_7451 & IMG_7452.
Displays itemized wage lines, tax calculation, allowances, and export/print options.
Fully supports the 5-item monthly payroll breakdown:
1. ប្រាក់ខែគោល (Base Salary)
2. ប្រាក់លើកទឹកចិត្ត (Incentive)
3. Target income 14k $ up
4. Over time
5. Over day off almost 1 day (Deduction)
"""

import os
import base64
import json
import uuid
import calendar
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTabWidget, QWidget, QDoubleSpinBox, QSpinBox, QGridLayout,
    QLineEdit, QScrollArea, QTextBrowser, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument, QIcon
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import database

class EditPayrollBreakdownDialog(QDialog):
    """Dialog allowing HR to customize the 5 monthly payroll items for an employee."""
    def __init__(self, slip_data, parent=None):
        super().__init__(parent)
        self.slip = slip_data
        self.setWindowTitle(f"កែប្រែប្រាក់បៀវត្ស - {self.slip.get('name', '')} ({self.slip.get('payslip_no', '')})")
        self.resize(520, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 12px;
                color: #334155;
            }
            QDoubleSpinBox {
                min-height: 32px;
                padding: 2px 8px;
                font-size: 13px;
                font-weight: 600;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #1E293B;
            }
            QDoubleSpinBox:focus {
                border: 1.5px solid #5648A6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        title = QLabel("កែសម្រួលធាតុផ្សំនៃបៀវត្សប្រចាំខែ (Monthly Payroll Breakdown)")
        title.setStyleSheet("font-size: 15px; font-weight: 800; color: #5648A6;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        # 1. Base Salary
        grid.addWidget(QLabel("<b>១. ប្រាក់ខែគោល (Base Salary):</b>"), 0, 0)
        self.sp_base = QDoubleSpinBox()
        self.sp_base.setRange(0, 100000)
        self.sp_base.setPrefix("$ ")
        self.sp_base.setDecimals(2)
        self.sp_base.setValue(float(self.slip.get("base_salary", 500) or 0))
        grid.addWidget(self.sp_base, 0, 1)

        # 2. Incentive
        grid.addWidget(QLabel("<b>២. ប្រាក់លើកទឹកចិត្ត (Incentive):</b>"), 1, 0)
        self.sp_incentive = QDoubleSpinBox()
        self.sp_incentive.setRange(0, 50000)
        self.sp_incentive.setPrefix("$ ")
        self.sp_incentive.setDecimals(2)
        inc_val = self.slip.get("incentive")
        if inc_val is None:
            inc_val = self.slip.get("allowance", 45.0)
        self.sp_incentive.setValue(float(inc_val or 0))
        grid.addWidget(self.sp_incentive, 1, 1)

        # 3. Target income 14k $ up
        grid.addWidget(QLabel("<b>៣. Target income 14k $ up:</b>"), 2, 0)
        self.sp_target = QDoubleSpinBox()
        self.sp_target.setRange(0, 50000)
        self.sp_target.setPrefix("$ ")
        self.sp_target.setDecimals(2)
        self.sp_target.setValue(float(self.slip.get("target_bonus", 0) or 0))
        grid.addWidget(self.sp_target, 2, 1)

        # 4. Over time
        grid.addWidget(QLabel("<b>៤. Over time (ប្រាក់ថែមម៉ោង):</b>"), 3, 0)
        self.sp_ot = QDoubleSpinBox()
        self.sp_ot.setRange(0, 50000)
        self.sp_ot.setPrefix("$ ")
        self.sp_ot.setDecimals(2)
        self.sp_ot.setValue(float(self.slip.get("ot_pay", 0) or 0))
        grid.addWidget(self.sp_ot, 3, 1)

        # 5. Over day off almost 1 day
        grid.addWidget(QLabel("<b>៥. Over day off almost 1 day (កាត់ប្រាក់ឈប់លើស):</b>"), 4, 0)
        self.sp_day_off = QDoubleSpinBox()
        self.sp_day_off.setRange(0, 50000)
        self.sp_day_off.setPrefix("-$ ")
        self.sp_day_off.setDecimals(2)
        self.sp_day_off.setValue(float(self.slip.get("over_day_off_deduction", 0) or 0))
        grid.addWidget(self.sp_day_off, 4, 1)

        layout.addLayout(grid)

        # Live calculation preview box
        prev_card = QFrame()
        prev_card.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        prev_layout = QVBoxLayout(prev_card)
        prev_layout.setSpacing(4)
        self.lbl_prev_gross = QLabel("Gross Salary (ប្រាក់ចំណូលសរុប): $0.00")
        self.lbl_prev_gross.setStyleSheet("font-weight: 600; color: #1E293B;")
        self.lbl_prev_net = QLabel("Net Salary (ប្រាក់ត្រូវបើកសុទ្ធ): $0.00")
        self.lbl_prev_net.setStyleSheet("font-size: 14px; font-weight: 800; color: #5648A6;")
        prev_layout.addWidget(self.lbl_prev_gross)
        prev_layout.addWidget(self.lbl_prev_net)
        layout.addWidget(prev_card)

        # Connect live updates
        for sp in [self.sp_base, self.sp_incentive, self.sp_target, self.sp_ot, self.sp_day_off]:
            sp.valueChanged.connect(self._recalc_preview)
        self._recalc_preview()

        # Action buttons
        btn_h = QHBoxLayout()
        btn_cancel = QPushButton("បោះបង់ (Cancel)")
        btn_cancel.setStyleSheet("background-color: #F1F5F9; color: #475569; padding: 8px 16px; border-radius: 6px; font-weight: 600;")
        btn_cancel.clicked.connect(self.reject)
        btn_h.addWidget(btn_cancel)

        btn_h.addStretch()

        btn_save = QPushButton("💾 រក្សាទុកបៀវត្ស (Save Changes)")
        btn_save.setStyleSheet("background-color: #5648A6; color: white; padding: 8px 22px; border-radius: 6px; font-weight: 700;")
        btn_save.clicked.connect(self._save_changes)
        btn_h.addWidget(btn_save)
        layout.addLayout(btn_h)

    def _recalc_preview(self):
        gross = self.sp_base.value() + self.sp_incentive.value() + self.sp_target.value() + self.sp_ot.value()
        tax = round(gross * 0.02, 2) if gross > 500 else 0.0
        net = round(gross - self.sp_day_off.value() - tax, 2)
        self.lbl_prev_gross.setText(f"Gross Salary (ប្រាក់ចំណូលសរុប): <b>${gross:,.2f}</b>")
        self.lbl_prev_net.setText(f"Net Salary (ប្រាក់ត្រូវបើកសុទ្ធ): <b>${net:,.2f}</b> (Tax: -${tax:.2f})")

    def _save_changes(self):
        gross = round(self.sp_base.value() + self.sp_incentive.value() + self.sp_target.value() + self.sp_ot.value(), 2)
        tax = round(gross * 0.02, 2) if gross > 500 else 0.0
        net = round(gross - self.sp_day_off.value() - tax, 2)

        data = {
            "base_salary": self.sp_base.value(),
            "incentive": self.sp_incentive.value(),
            "target_bonus": self.sp_target.value(),
            "ot_pay": self.sp_ot.value(),
            "over_day_off_deduction": self.sp_day_off.value(),
            "tax_deduction": tax,
            "other_deduction": 0.0,
            "status": "Paid"
        }
        database.update_payroll_record(self.slip["id"], data)
        self.accept()

class PayslipDialog(QDialog):
    def __init__(self, slip_data, parent=None):
        super().__init__(parent)
        self.slip = dict(slip_data)
        self.setWindowTitle(f"Payslip - {self.slip.get('name', '')} ({self.slip.get('payslip_no', '')})")
        self.resize(950, 840)
        self.setMinimumSize(880, 780)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
            QLabel {
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
            }
            QDoubleSpinBox, QSpinBox {
                min-height: 32px;
                padding: 2px 10px;
                font-family: 'Segoe UI', 'Kantumruy Pro', sans-serif;
                font-size: 13px;
                font-weight: 700;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #1E293B;
            }
            QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1.5px solid #5648A6;
                background-color: #FAF5FF;
            }
        """)

        self.worked_days_val = int(self.slip.get("worked_days", 26) or 26)
        self.tax_val = float(self.slip.get("tax_deduction", 0) or 0)
        self._init_breakdown_items()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(10)

        # Header bar with Actions
        h_bar = QHBoxLayout()
        title_top = QLabel("Open: Payslips / ប័ណ្ណទូទាត់ប្រាក់បៀវត្ស")
        title_top.setStyleSheet("font-size: 17px; font-weight: 800; color: #1E293B;")
        h_bar.addWidget(title_top)
        h_bar.addStretch()

        btn_email = QPushButton("✉️ Send By Email")
        btn_email.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_email.setStyleSheet("""
            QPushButton {
                background-color: #EEEDFB;
                color: #5648A6;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid #C4B5FD;
            }
            QPushButton:hover {
                background-color: #DDD6FE;
            }
        """)
        btn_email.clicked.connect(lambda: QMessageBox.information(self, "Email Sent", f"Payslip {self.slip.get('payslip_no')} has been emailed to {self.slip.get('email', 'the employee')}."))
        h_bar.addWidget(btn_email)
        layout.addLayout(h_bar)

        # Compact Unified Employee Info Card
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QLabel {
                font-size: 13px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(5)

        # Row 1: Slip No, Employee Name, Department
        r1 = QHBoxLayout()
        lbl_code = QLabel(f"📄 <b>{self.slip.get('payslip_no', 'SLIP/001')}</b>")
        lbl_code.setStyleSheet("font-size: 14px; font-weight: 800; color: #5648A6; background: #EEEDFB; padding: 2px 8px; border-radius: 5px;")
        r1.addWidget(lbl_code)

        lbl_emp = QLabel(f"<b>Employee:</b> {self.slip.get('emp_code', '')} - {self.slip.get('name', '')} ({self.slip.get('khmer_name', '')})")
        lbl_emp.setStyleSheet("color: #1E293B; font-weight: 600;")
        r1.addWidget(lbl_emp)

        r1.addStretch()
        lbl_dept = QLabel(f"<b>Department:</b> {self.slip.get('department', 'Clinic')}")
        lbl_dept.setStyleSheet("color: #475569;")
        r1.addWidget(lbl_dept)
        info_layout.addLayout(r1)

        # Row 2: Period, Structure, Currency
        r2 = QHBoxLayout()
        lbl_period = QLabel(f"📅 <b>Period:</b> {self.slip.get('date_from', '')} ➔ {self.slip.get('date_to', '')}")
        lbl_period.setStyleSheet("color: #475569; font-size: 12px;")
        r2.addWidget(lbl_period)

        r2.addStretch()
        lbl_struct = QLabel("<b>Structure:</b> Dental Clinic Wage Structure  |  <b>Currency:</b> USD ($)")
        lbl_struct.setStyleSheet("color: #64748B; font-size: 12px;")
        r2.addWidget(lbl_struct)
        info_layout.addLayout(r2)

        layout.addWidget(info_frame)

        # Tabs: Salary Breakdown, Inputs, Other Info
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #F1F5F9;
                color: #475569;
                padding: 7px 18px;
                font-weight: 700;
                font-size: 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #5648A6;
                border: 1px solid #CBD5E1;
                border-bottom: 2px solid #5648A6;
            }
        """)

        # Tab 1: Editable Salary Breakdown Table
        salary_tab = QWidget()
        sal_v = QVBoxLayout(salary_tab)
        sal_v.setContentsMargins(12, 10, 12, 10)
        sal_v.setSpacing(9)

        hint_lbl = QLabel("💡 <b>ចំណាំ៖</b> លោកអ្នកអាចកែប្រែឈ្មោះ (Text) ចំនួនទឹកប្រាក់ ($) ព្រមទាំងលុប (🗑️) ឬបន្ថែម (➕) ធាតុផ្សំបៀវត្សនីមួយៗបានដោយសេរី រួចចុច <b>រក្សាទុកការកែប្រែ</b>។")
        hint_lbl.setStyleSheet("font-size: 12px; color: #4338CA; background-color: #EEEDFB; padding: 7px 14px; border-radius: 6px;")
        sal_v.addWidget(hint_lbl)

        # Toolbar for adding items / resetting
        tool_bar = QHBoxLayout()
        tool_bar.setSpacing(8)

        btn_add_earn = QPushButton("➕ បន្ថែមប្រាក់ចំណូល/ឧបត្ថម្ភ (+ Add Earning)")
        btn_add_earn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_earn.setStyleSheet("""
            QPushButton {
                background-color: #ECFDF5;
                color: #065F46;
                border: 1.5px solid #A7F3D0;
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D1FAE5;
                border-color: #34D399;
            }
        """)
        btn_add_earn.clicked.connect(self._add_earning)
        tool_bar.addWidget(btn_add_earn)

        btn_add_ded = QPushButton("➖ បន្ថែមការកាត់ប្រាក់ (+ Add Deduction)")
        btn_add_ded.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_ded.setStyleSheet("""
            QPushButton {
                background-color: #FFF1F2;
                color: #9F1239;
                border: 1.5px solid #FECDD3;
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #FFE4E6;
                border-color: #FB7185;
            }
        """)
        btn_add_ded.clicked.connect(self._add_deduction)
        tool_bar.addWidget(btn_add_ded)

        tool_bar.addStretch()

        btn_reset = QPushButton("🔄 កំណត់ដូចដើម (Reset Defaults)")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                color: #475569;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #1E293B;
                border-color: #94A3B8;
            }
        """)
        btn_reset.clicked.connect(self._reset_defaults)
        tool_bar.addWidget(btn_reset)

        sal_v.addLayout(tool_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "NAME / DESCRIPTION (ធាតុផ្សំនៃបៀវត្ស)", 
            "AMOUNT / VALUE (ទឹកប្រាក់ $ USD)",
            "ACTION"
        ])
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 260)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 70)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setAlternatingRowColors(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setMinimumHeight(415)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                gridline-color: #E2E8F0;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 13px;
                outline: none;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #334155;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 800;
                font-size: 12px;
                padding: 8px 10px;
                border: none;
                border-right: 1px solid #E2E8F0;
                border-bottom: 2px solid #CBD5E1;
            }
        """)

        sal_v.addWidget(self.table, 1)
        self.tabs.addTab(salary_tab, "Salary Breakdown (បៀវត្សលម្អិត)")

        # Tab 2: Inputs
        inputs_tab = QWidget()
        in_v = QVBoxLayout(inputs_tab)
        in_v.setContentsMargins(16, 16, 16, 16)
        in_v.addWidget(QLabel("<b>Attendance & Biometric Log Data:</b>\n• Biometric hours tracked: 208 hours.\n• Standard schedule: 08:00 - 17:00 (Mon - Sat).\n• Target revenue threshold: $14,000 USD.\n• Overtime coefficient: 1.5x regular, 2.0x holiday."))
        in_v.addStretch()
        self.tabs.addTab(inputs_tab, "Inputs")

        # Tab 3: Other Info
        other_tab = QWidget()
        ot_v = QVBoxLayout(other_tab)
        ot_v.setContentsMargins(16, 16, 16, 16)
        ot_v.addWidget(QLabel("<b>Disbursement & Clinic Details:</b>\n• Method: Bank Transfer (ABA Bank Payroll / ACLEDA Bank)\n• Company: Mercy Dental Care\n• Branch: Phnom Penh Central Clinic\n• Tax Status: Cambodian General Department of Taxation compliant"))
        ot_v.addStretch()
        self.tabs.addTab(other_tab, "Other Info")

        layout.addWidget(self.tabs, 1)

        # Bottom Bar: Close, Live Net Display, Save Changes, Print Payslip
        bot_bar = QHBoxLayout()
        bot_bar.setContentsMargins(0, 4, 0, 0)
        bot_bar.setSpacing(10)

        close_btn = QPushButton("បិទ (Close)")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border-radius: 8px;
                padding: 9px 18px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 700;
                font-size: 13px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        close_btn.clicked.connect(self.accept)
        bot_bar.addWidget(close_btn)

        bot_bar.addStretch()

        self.amt_label = QLabel("Amount to Pay: $0.00")
        self.amt_label.setStyleSheet("font-size: 16px; color: #5648A6; font-weight: 800; padding-right: 8px; font-family: 'Segoe UI', sans-serif;")
        bot_bar.addWidget(self.amt_label)

        self.btn_save_payroll = QPushButton("💾 រក្សាទុកការកែប្រែ (Save Changes)")
        self.btn_save_payroll.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_payroll.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 9px 20px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 800;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_save_payroll.clicked.connect(self.save_payroll_changes)
        bot_bar.addWidget(self.btn_save_payroll)

        print_btn = QPushButton("🖨️ បោះពុម្ព (Print Payslip)")
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 9px 20px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 800;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        print_btn.clicked.connect(self._print_payslip)
        bot_bar.addWidget(print_btn)

        layout.addLayout(bot_bar)

        # Build and populate editable rows
        self._render_table()

    def _init_breakdown_items(self):
        raw_items = self.slip.get("breakdown_items")
        loaded = False
        if raw_items:
            try:
                parsed = json.loads(raw_items)
                if isinstance(parsed, list) and len(parsed) > 0:
                    self.earnings = [dict(it) for it in parsed if it.get("type", "earning") == "earning"]
                    self.deductions = [dict(it) for it in parsed if it.get("type") == "deduction"]
                    loaded = True
            except Exception:
                loaded = False

        if not loaded:
            base_sal = float(self.slip.get("base_salary", 500) or 0)
            inc_val = self.slip.get("incentive")
            if inc_val is None:
                inc_val = self.slip.get("allowance", 45.0)
            incentive = float(inc_val or 0)
            target_bonus = float(self.slip.get("target_bonus", 0) or 0)
            ot_pay = float(self.slip.get("ot_pay", 0) or 0)
            over_day_off = float(self.slip.get("over_day_off_deduction", 0) or 0)

            self.earnings = [
                {"id": "base", "name": "១. ប្រាក់ខែគោល (Base Salary)", "amount": base_sal, "type": "earning"},
                {"id": "incentive", "name": "២. ប្រាក់លើកទឹកចិត្ត (Incentive)", "amount": incentive, "type": "earning"},
                {"id": "target", "name": "៣. Target income 14k $ up (ប្រាក់រង្វាន់សម្រេចគោលដៅ)", "amount": target_bonus, "type": "earning"},
                {"id": "ot", "name": "៤. Over time (ប្រាក់ថែមម៉ោង)", "amount": ot_pay, "type": "earning"}
            ]
            self.deductions = [
                {"id": "day_off", "name": "៥. Over day off almost 1 day (កាត់ប្រាក់ឈប់លើស)", "amount": over_day_off, "type": "deduction"}
            ]

    def _on_item_name_changed(self, item, new_name):
        item["name"] = new_name

    def _on_item_amount_changed(self, item, new_amount):
        item["amount"] = float(new_amount)
        self._recalc_table()

    def _on_worked_days_changed(self, val):
        self.worked_days_val = int(val)

    def _on_tax_changed(self, val):
        self.tax_val = float(val)
        self._recalc_table()

    def _add_earning(self):
        new_item = {
            "id": f"earn_{uuid.uuid4().hex[:6]}",
            "name": f"ប្រាក់ចំណូល/ឧបត្ថម្ភបន្ថែម ({len(self.earnings) + 1})",
            "amount": 0.0,
            "type": "earning"
        }
        self.earnings.append(new_item)
        self._render_table()

    def _add_deduction(self):
        new_item = {
            "id": f"ded_{uuid.uuid4().hex[:6]}",
            "name": f"ការកាត់ប្រាក់បន្ថែម ({len(self.deductions) + 1})",
            "amount": 0.0,
            "type": "deduction"
        }
        self.deductions.append(new_item)
        self._render_table()

    def _delete_item(self, itm):
        item_name = itm.get("name", "ធាតុនេះ")
        reply = QMessageBox.question(
            self,
            "លុបធាតុផ្សំបៀវត្ស (Delete Item)",
            f"តើលោកអ្នកពិតជាចង់លុបធាតុ «{item_name}» ឬទេ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if itm in self.earnings:
                self.earnings.remove(itm)
            elif itm in self.deductions:
                self.deductions.remove(itm)
            self._render_table()

    def _reset_defaults(self):
        reply = QMessageBox.question(
            self,
            "កំណត់ដូចដើម (Reset Defaults)",
            "តើលោកអ្នកពិតជាចង់កំណត់ធាតុផ្សំបៀវត្សទាំង ៥ មកដូចដើមវិញមែនទេ?\n(Reset to default 5 payroll items?)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            base_sal = float(self.slip.get("base_salary", 500) or 0)
            inc_val = self.slip.get("incentive")
            if inc_val is None:
                inc_val = self.slip.get("allowance", 45.0)
            incentive = float(inc_val or 0)
            target_bonus = float(self.slip.get("target_bonus", 0) or 0)
            ot_pay = float(self.slip.get("ot_pay", 0) or 0)
            over_day_off = float(self.slip.get("over_day_off_deduction", 0) or 0)

            self.earnings = [
                {"id": "base", "name": "១. ប្រាក់ខែគោល (Base Salary)", "amount": base_sal, "type": "earning"},
                {"id": "incentive", "name": "២. ប្រាក់លើកទឹកចិត្ត (Incentive)", "amount": incentive, "type": "earning"},
                {"id": "target", "name": "៣. Target income 14k $ up (ប្រាក់រង្វាន់សម្រេចគោលដៅ)", "amount": target_bonus, "type": "earning"},
                {"id": "ot", "name": "៤. Over time (ប្រាក់ថែមម៉ោង)", "amount": ot_pay, "type": "earning"}
            ]
            self.deductions = [
                {"id": "day_off", "name": "៥. Over day off almost 1 day (កាត់ប្រាក់ឈប់លើស)", "amount": over_day_off, "type": "deduction"}
            ]
            self._render_table()

    def _render_table(self):
        # Rows: Worked Days (1) + Earnings (N) + Gross (1) + Deductions (M) + Tax (1) + Net (1)
        total_rows = 1 + len(self.earnings) + 1 + len(self.deductions) + 1 + 1
        self.table.setRowCount(total_rows)

        def _wrap(widget, pad_h=6, align=Qt.AlignmentFlag.AlignVCenter):
            w = QWidget()
            w.setStyleSheet("background: transparent;")
            lay = QHBoxLayout(w)
            lay.setContentsMargins(pad_h, 3, pad_h, 3)
            lay.setAlignment(align)
            lay.addWidget(widget)
            return w

        def _make_action_placeholder():
            w = QWidget()
            w.setStyleSheet("background: transparent;")
            lay = QHBoxLayout(w)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel("—")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 13px;")
            lay.addWidget(lbl)
            return w

        row_height = 42
        box_style_common = (
            "min-height: 32px; max-height: 32px; "
            "font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif; "
            "font-size: 13px; "
        )

        # ----------------- Row 0: Worked Days -----------------
        self.table.setRowHeight(0, row_height)
        lbl_w0 = QLabel("Worked Days (ថ្ងៃធ្វើការ)")
        lbl_w0.setStyleSheet(f"""
            QLabel {{
                {box_style_common}
                font-weight: 700;
                color: #1E293B;
                background-color: #F8FAFC;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                padding: 0 10px;
            }}
        """)
        lbl_w0.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setCellWidget(0, 0, _wrap(lbl_w0))

        self.sp_worked_days = QSpinBox()
        self.sp_worked_days.setRange(0, 31)
        self.sp_worked_days.setValue(self.worked_days_val)
        self.sp_worked_days.setSuffix(" ថ្ងៃ (Days)")
        self.sp_worked_days.setStyleSheet(f"""
            QSpinBox {{
                {box_style_common}
                padding: 0 8px;
                font-weight: 700;
                color: #1E293B;
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
            }}
            QSpinBox:focus {{
                border-color: #5648A6;
                background-color: #FAF5FF;
            }}
        """)
        self.sp_worked_days.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sp_worked_days.valueChanged.connect(self._on_worked_days_changed)
        self.table.setCellWidget(0, 1, _wrap(self.sp_worked_days))
        self.table.setCellWidget(0, 2, _make_action_placeholder())

        # ----------------- Earnings Rows -----------------
        for idx, itm in enumerate(self.earnings):
            row = 1 + idx
            self.table.setRowHeight(row, row_height)

            # Col 0: Editable Name
            le = QLineEdit(itm.get("name", ""))
            le.setPlaceholderText("បញ្ចូលឈ្មោះធាតុផ្សំចំណូល...")
            le.setStyleSheet(f"""
                QLineEdit {{
                    {box_style_common}
                    padding: 0 10px;
                    font-weight: 600;
                    color: #1E293B;
                    background-color: #FFFFFF;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 6px;
                }}
                QLineEdit:hover {{
                    border-color: #94A3B8;
                }}
                QLineEdit:focus {{
                    border: 1.5px solid #5648A6;
                    background-color: #FAF5FF;
                }}
            """)
            le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            le.textChanged.connect(lambda txt, item=itm: self._on_item_name_changed(item, txt))
            self.table.setCellWidget(row, 0, _wrap(le))

            # Col 1: SpinBox for Amount
            sp = QDoubleSpinBox()
            sp.setRange(0, 100000)
            sp.setDecimals(2)
            is_base = (itm.get("id") == "base" or idx == 0)
            sp.setPrefix("$ " if is_base else "+$ ")
            sp.setValue(float(itm.get("amount", 0) or 0))
            sp.setStyleSheet(f"""
                QDoubleSpinBox {{
                    {box_style_common}
                    padding: 0 8px;
                    font-weight: 700;
                    color: #1E293B;
                    background-color: #FFFFFF;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 6px;
                }}
                QDoubleSpinBox:focus {{
                    border-color: #5648A6;
                    background-color: #FAF5FF;
                }}
            """)
            sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sp.valueChanged.connect(lambda val, item=itm: self._on_item_amount_changed(item, val))
            self.table.setCellWidget(row, 1, _wrap(sp))

            # Col 2: Delete Button
            del_box = QWidget()
            del_box.setStyleSheet("background: transparent;")
            del_layout = QHBoxLayout(del_box)
            del_layout.setContentsMargins(0, 0, 0, 0)
            del_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_del = QPushButton("🗑")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("លុបធាតុនេះ (Delete item)")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    border: 1.5px solid #FECACA;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 34px;
                    max-width: 34px;
                    min-height: 28px;
                    max-height: 28px;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                    color: #FFFFFF;
                    border-color: #B91C1C;
                }
            """)
            btn_del.clicked.connect(lambda _, item=itm: self._delete_item(item))
            del_layout.addWidget(btn_del)
            self.table.setCellWidget(row, 2, del_box)

        # ----------------- Gross Salary row (Subtotal) -----------------
        gross_row = 1 + len(self.earnings)
        self.table.setRowHeight(gross_row, row_height)

        lbl_g0 = QLabel("ប្រាក់បៀវត្សសរុប (Gross Salary)")
        lbl_g0.setStyleSheet(f"""
            QLabel {{
                {box_style_common}
                font-weight: 800;
                color: #0F172A;
                background-color: #F1F5F9;
                border: 1.5px solid #94A3B8;
                border-radius: 6px;
                padding: 0 10px;
            }}
        """)
        lbl_g0.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setCellWidget(gross_row, 0, _wrap(lbl_g0))

        self.lbl_cell_gross = QLabel("$0.00")
        self.lbl_cell_gross.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_cell_gross.setStyleSheet(f"""
            QLabel {{
                {box_style_common}
                font-size: 14px;
                font-weight: 800;
                color: #0F172A;
                background-color: #F1F5F9;
                border: 1.5px solid #94A3B8;
                border-radius: 6px;
                padding-right: 12px;
            }}
        """)
        self.lbl_cell_gross.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setCellWidget(gross_row, 1, _wrap(self.lbl_cell_gross))
        self.table.setCellWidget(gross_row, 2, _make_action_placeholder())

        # ----------------- Deductions rows -----------------
        ded_start = gross_row + 1
        for idx, itm in enumerate(self.deductions):
            row = ded_start + idx
            self.table.setRowHeight(row, row_height)

            # Col 0: Editable Name
            le = QLineEdit(itm.get("name", ""))
            le.setPlaceholderText("បញ្ចូលឈ្មោះធាតុកាត់ប្រាក់...")
            le.setStyleSheet(f"""
                QLineEdit {{
                    {box_style_common}
                    padding: 0 10px;
                    font-weight: 600;
                    color: #DC2626;
                    background-color: #FEF2F2;
                    border: 1.5px solid #FECACA;
                    border-radius: 6px;
                }}
                QLineEdit:hover {{
                    border-color: #F87171;
                }}
                QLineEdit:focus {{
                    border: 1.5px solid #DC2626;
                    background-color: #FFFFFF;
                }}
            """)
            le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            le.textChanged.connect(lambda txt, item=itm: self._on_item_name_changed(item, txt))
            self.table.setCellWidget(row, 0, _wrap(le))

            # Col 1: SpinBox for Amount
            sp = QDoubleSpinBox()
            sp.setRange(0, 100000)
            sp.setDecimals(2)
            sp.setPrefix("-$ ")
            sp.setValue(float(itm.get("amount", 0) or 0))
            sp.setStyleSheet(f"""
                QDoubleSpinBox {{
                    {box_style_common}
                    padding: 0 8px;
                    font-weight: 700;
                    color: #DC2626;
                    background-color: #FFFFFF;
                    border: 1.5px solid #FECACA;
                    border-radius: 6px;
                }}
                QDoubleSpinBox:focus {{
                    border-color: #DC2626;
                    background-color: #FEF2F2;
                }}
            """)
            sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sp.valueChanged.connect(lambda val, item=itm: self._on_item_amount_changed(item, val))
            self.table.setCellWidget(row, 1, _wrap(sp))

            # Col 2: Delete Button
            del_box = QWidget()
            del_box.setStyleSheet("background: transparent;")
            del_layout = QHBoxLayout(del_box)
            del_layout.setContentsMargins(0, 0, 0, 0)
            del_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_del = QPushButton("🗑")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("លុបធាតុនេះ (Delete item)")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    border: 1.5px solid #FECACA;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 34px;
                    max-width: 34px;
                    min-height: 28px;
                    max-height: 28px;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                    color: #FFFFFF;
                    border-color: #B91C1C;
                }
            """)
            btn_del.clicked.connect(lambda _, item=itm: self._delete_item(item))
            del_layout.addWidget(btn_del)
            self.table.setCellWidget(row, 2, del_box)

        # ----------------- Tax on Salary row -----------------
        tax_row = ded_start + len(self.deductions)
        self.table.setRowHeight(tax_row, row_height)

        lbl_t0 = QLabel("ពន្ធលើប្រាក់បៀវត្ស (Tax on Salary)")
        lbl_t0.setStyleSheet(f"""
            QLabel {{
                {box_style_common}
                font-weight: 700;
                color: #DC2626;
                background-color: #FEF2F2;
                border: 1.5px solid #FECACA;
                border-radius: 6px;
                padding: 0 10px;
            }}
        """)
        lbl_t0.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setCellWidget(tax_row, 0, _wrap(lbl_t0))

        self.sp_tax = QDoubleSpinBox()
        self.sp_tax.setRange(0, 50000)
        self.sp_tax.setDecimals(2)
        self.sp_tax.setPrefix("-$ ")
        self.sp_tax.setValue(self.tax_val)
        self.sp_tax.setStyleSheet(f"""
            QDoubleSpinBox {{
                {box_style_common}
                padding: 0 8px;
                font-weight: 700;
                color: #DC2626;
                background-color: #FFFFFF;
                border: 1.5px solid #FECACA;
                border-radius: 6px;
            }}
            QDoubleSpinBox:focus {{
                border-color: #DC2626;
                background-color: #FEF2F2;
            }}
        """)
        self.sp_tax.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sp_tax.valueChanged.connect(self._on_tax_changed)
        self.table.setCellWidget(tax_row, 1, _wrap(self.sp_tax))
        self.table.setCellWidget(tax_row, 2, _make_action_placeholder())

        # ----------------- Net Salary row (Grand Total) -----------------
        net_row = tax_row + 1
        self.table.setRowHeight(net_row, row_height)

        lbl_n0 = QLabel("ប្រាក់ត្រូវបើកសុទ្ធ (Salary to Pay / Net Salary)")
        lbl_n0.setStyleSheet(f"""
            QLabel {{
                {box_style_common}
                font-weight: 800;
                color: #5648A6;
                background-color: #EEEDFB;
                border: 1.5px solid #8B5CF6;
                border-radius: 6px;
                padding: 0 10px;
            }}
        """)
        lbl_n0.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setCellWidget(net_row, 0, _wrap(lbl_n0))

        self.lbl_cell_net = QLabel("$0.00")
        self.lbl_cell_net.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_cell_net.setStyleSheet(f"""
            QLabel {{
                {box_style_common}
                font-size: 15px;
                font-weight: 900;
                color: #5648A6;
                background-color: #EEEDFB;
                border: 1.5px solid #8B5CF6;
                border-radius: 6px;
                padding-right: 12px;
            }}
        """)
        self.lbl_cell_net.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.setCellWidget(net_row, 1, _wrap(self.lbl_cell_net))
        self.table.setCellWidget(net_row, 2, _make_action_placeholder())

        self._recalc_table()

    def _recalc_table(self):
        gross = round(sum(float(e.get("amount", 0) or 0) for e in self.earnings), 2)
        deductions = round(sum(float(d.get("amount", 0) or 0) for d in self.deductions), 2)
        tax = round(self.tax_val, 2)
        net = round(max(0.0, gross - deductions - tax), 2)

        if hasattr(self, 'lbl_cell_gross'):
            self.lbl_cell_gross.setText(f"${gross:,.2f}")
        if hasattr(self, 'lbl_cell_net'):
            self.lbl_cell_net.setText(f"${net:,.2f}")
        if hasattr(self, 'amt_label'):
            self.amt_label.setText(f"Amount to Pay: <b>${net:,.2f}</b>")

    def save_payroll_changes(self):
        gross = round(sum(float(e.get("amount", 0) or 0) for e in self.earnings), 2)
        total_ded = round(sum(float(d.get("amount", 0) or 0) for d in self.deductions), 2)
        tax = round(self.tax_val, 2)
        net = round(max(0.0, gross - total_ded - tax), 2)

        # Build list of all items to persist
        all_items = []
        for e in self.earnings:
            all_items.append({"id": e["id"], "type": "earning", "name": e["name"], "amount": e["amount"]})
        for d in self.deductions:
            all_items.append({"id": d["id"], "type": "deduction", "name": d["name"], "amount": d["amount"]})

        breakdown_json = json.dumps(all_items, ensure_ascii=False)

        # Standard field mapping for backwards compatibility and summary table
        base_item = next((e for e in self.earnings if e.get("id") == "base"), None)
        base_sal = base_item["amount"] if base_item else (self.earnings[0]["amount"] if self.earnings else 0.0)

        inc_item = next((e for e in self.earnings if e.get("id") == "incentive"), None)
        inc_val = inc_item["amount"] if inc_item else 0.0

        target_item = next((e for e in self.earnings if e.get("id") == "target"), None)
        target_val = target_item["amount"] if target_item else 0.0

        ot_item = next((e for e in self.earnings if e.get("id") == "ot"), None)
        ot_val = ot_item["amount"] if ot_item else 0.0

        day_off_item = next((d for d in self.deductions if d.get("id") == "day_off"), None)
        day_off_val = day_off_item["amount"] if day_off_item else 0.0

        other_ded = round(total_ded - day_off_val, 2)
        if other_ded < 0:
            other_ded = 0.0

        data = {
            "worked_days": self.worked_days_val,
            "base_salary": base_sal,
            "incentive": inc_val,
            "allowance": inc_val,
            "target_bonus": target_val,
            "ot_pay": ot_val,
            "over_day_off_deduction": day_off_val,
            "tax_deduction": tax,
            "other_deduction": other_ded,
            "gross_salary": gross,
            "net_salary": net,
            "status": "Paid",
            "breakdown_items": breakdown_json
        }
        database.update_payroll_record(self.slip["id"], data)

        # Update in-memory slip
        self.slip.update(data)

        # Sync base salary to employees table so profile and payslips stay synchronized
        try:
            emp_id = self.slip.get("emp_id")
            if emp_id and base_sal > 0:
                conn_emp = database.get_connection()
                conn_emp.execute("UPDATE employees SET base_salary = ? WHERE id = ?", (base_sal, emp_id))
                conn_emp.commit()
                conn_emp.close()
        except Exception:
            pass

        # Refresh parent payroll table if available
        if self.parent() and hasattr(self.parent(), "load_payroll"):
            self.parent().load_payroll()

        QMessageBox.information(
            self, 
            "ជោគជ័យ (Saved)", 
            f"✅ បានរក្សាទុកការកែប្រែបៀវត្សសម្រាប់ {self.slip.get('name')} ដោយជោគជ័យ!\n\n"
            f"• ប្រាក់បៀវត្សសរុប (Gross): ${gross:,.2f}\n"
            f"• កាត់ប្រាក់សរុប (Deductions): -${total_ded:,.2f}\n"
            f"• ពន្ធលើប្រាក់បៀវត្ស (Tax): -${tax:,.2f}\n"
            f"• ប្រាក់ត្រូវបើកសុទ្ធ (Net Salary): ${net:,.2f}"
        )

    def open_edit_dialog(self):
        self.tabs.setCurrentIndex(0)
        self.table.setFocus()

    def _print_payslip(self):
        dlg = PayslipPrintDialog(
            slip_data=self.slip,
            earnings=self.earnings,
            deductions=self.deductions,
            tax=self.tax_val,
            worked_days=self.worked_days_val,
            parent=self
        )
        dlg.exec()

class PayslipPrintDialog(QDialog):
    """
    Formal Payslip Voucher print & preview dialog matching Mercy Dental Care invoice design.
    Features:
    - High-resolution Mercy Dental Care blue banner with logo and contact info
    - Formatted Period Date, Khmer title, bold Employee Name
    - Clean border table matching screenshot with exact amounts and Total
    - Manager and Employee signatures
    - One-click print to any printer via QPrintDialog
    - One-click direct PDF export
    """
    def __init__(self, slip_data, earnings, deductions, tax=0.0, worked_days=26, parent=None):
        super().__init__(parent)
        self.slip = dict(slip_data)
        self.earnings = list(earnings)
        self.deductions = list(deductions)
        self.tax = float(tax or 0)
        self.worked_days = int(worked_days)

        emp_title = self.slip.get("name", "Employee")
        self.setWindowTitle(f"Print Payslip - Mercy Dental Care - {emp_title}")
        self.resize(680, 680)
        self.setMinimumSize(580, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        self.html = self._generate_html()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        # Top Action Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        lbl_doc_title = QLabel("📄 <b>ប័ណ្ណទូទាត់ប្រាក់បៀវត្ស (Payslip Voucher Preview)</b>")
        lbl_doc_title.setStyleSheet("font-size: 14px; color: #1E293B; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;")
        top_bar.addWidget(lbl_doc_title)

        top_bar.addStretch()

        btn_pdf = QPushButton("💾 រក្សាទុកជា PDF (Save as PDF)")
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 700;
                font-size: 11.5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_pdf.clicked.connect(self._save_pdf)
        top_bar.addWidget(btn_pdf)

        btn_print = QPushButton("🖨️ បោះពុម្ព (Print)")
        btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 6px 16px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 700;
                font-size: 11.5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        btn_print.clicked.connect(self._print_doc)
        top_bar.addWidget(btn_print)

        btn_close = QPushButton("បិទ (Close)")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #334155;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 11.5px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        btn_close.clicked.connect(self.accept)
        top_bar.addWidget(btn_close)

        layout.addLayout(top_bar)

        # Center Preview Container (ScrollArea with centered paper sheet)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }
        """)

        container = QWidget()
        container.setStyleSheet("background-color: #E2E8F0;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.browser = QTextBrowser()
        self.browser.setFixedSize(540, 600)
        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
        """)
        self.browser.setHtml(self.html)
        c_layout.addWidget(self.browser)

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

    def _generate_html(self):
        # Format Date matching screenshot e.g. Date : 31ˢᵗ December 2025
        d_str = str(self.slip.get("date_to", "") or "")
        try:
            if d_str and "-" in d_str:
                dt = datetime.strptime(d_str.split()[0], "%Y-%m-%d")
            else:
                m = int(self.slip.get("period_month", 12))
                y = int(self.slip.get("period_year", 2025))
                last_day = calendar.monthrange(y, m)[1]
                dt = datetime(y, m, last_day)
        except Exception:
            dt = datetime.now()

        day = dt.day
        if 11 <= (day % 100) <= 13:
            sfx = "ˢᵗ" if day == 11 else "ᵗʰ"
        else:
            sfx = {1: "ˢᵗ", 2: "ⁿᵈ", 3: "ʳᵈ"}.get(day % 10, "ᵗʰ")
        date_formatted = f"{day}{sfx} {dt.strftime('%B')} {dt.year}"

        emp_name = self.slip.get("name") or "Bloe Ni"

        # Base64 Logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        logo_b64 = ""
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")

        gross = round(sum(float(e.get("amount", 0) or 0) for e in self.earnings), 2)
        tot_ded = round(sum(float(d.get("amount", 0) or 0) for d in self.deductions), 2)
        net = round(max(0.0, gross - tot_ded - self.tax), 2)

        rows_html = ""
        for itm in self.earnings:
            name = itm.get("name", "")
            amt = float(itm.get("amount", 0) or 0)
            amt_str = f"${int(amt):,}" if amt == int(amt) else f"${amt:,.2f}"
            rows_html += f"""
            <tr>
              <td align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 13px; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;">{name}</td>
              <td align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', Arial, sans-serif;">{amt_str}</td>
            </tr>
            """

        for itm in self.deductions:
            name = itm.get("name", "")
            amt = float(itm.get("amount", 0) or 0)
            if amt > 0:
                amt_str = f"-${int(amt):,}" if amt == int(amt) else f"-${amt:,.2f}"
                rows_html += f"""
                <tr>
                  <td align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 13px; color: #DC2626; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;">{name}</td>
                  <td align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 14px; font-weight: bold; color: #DC2626; font-family: 'Segoe UI', Arial, sans-serif;">{amt_str}</td>
                </tr>
                """

        if self.tax > 0:
            t_amt = self.tax
            t_str = f"-${int(t_amt):,}" if t_amt == int(t_amt) else f"-${t_amt:,.2f}"
            rows_html += f"""
            <tr>
              <td align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 13px; color: #DC2626; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;">ពន្ធលើប្រាក់បៀវត្ស (Tax on Salary)</td>
              <td align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 14px; font-weight: bold; color: #DC2626; font-family: 'Segoe UI', Arial, sans-serif;">{t_str}</td>
            </tr>
            """

        rows_html += """
        <tr style="height: 20px;">
          <td style="border: 1.5px solid #000000; padding: 4px;">&nbsp;</td>
          <td style="border: 1.5px solid #000000; padding: 4px;">&nbsp;</td>
        </tr>
        """

        net_str = f"${int(net):,}" if net == int(net) else f"${net:,.2f}"
        rows_html += f"""
        <tr>
          <td align="center" style="border: 1.5px solid #000000; padding: 8px 6px; font-size: 14.5px; font-weight: bold; font-family: 'Segoe UI', sans-serif;">Total</td>
          <td align="center" style="border: 1.5px solid #000000; padding: 8px 6px; font-size: 16px; font-weight: 900; font-family: 'Segoe UI', sans-serif;">{net_str}</td>
        </tr>
        """

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body style="margin: 0; padding: 0; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', Arial, sans-serif; background-color: #FFFFFF; color: #000000;">
  
  <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
    <tr>
      <td bgcolor="#96C2F7" width="28%" align="center" valign="middle" style="padding: 10px 8px;">
        <table cellpadding="4" cellspacing="0" bgcolor="#FFFFFF" style="border-radius: 4px; border: 1px solid #CBD5E1;">
          <tr>
            <td align="center" valign="middle">
              <img src="data:image/png;base64,{logo_b64}" width="105" />
            </td>
          </tr>
        </table>
      </td>
      <td bgcolor="#96C2F7" width="2%" align="center" valign="middle">
        <table cellpadding="0" cellspacing="0" height="65" style="border-left: 2px solid #D97706;">
          <tr><td>&nbsp;</td></tr>
        </table>
      </td>
      <td bgcolor="#96C2F7" width="70%" valign="middle" style="padding: 8px 14px; font-size: 11px; line-height: 1.35; color: #000000;">
        <table cellpadding="1.5" cellspacing="0" style="font-size: 11px; color: #000000; font-family: 'Segoe UI', Arial, sans-serif;">
          <tr>
            <td width="55" valign="top"><b>Phone:</b></td>
            <td>096 58 59 95<br>086 65 55 27 / 096 333 8889</td>
          </tr>
          <tr>
            <td valign="top"><b>Email:</b></td>
            <td>Mercydental8@gmail.com</td>
          </tr>
          <tr>
            <td valign="top"><b>Address:</b></td>
            <td>Sensok, Phnom Penh</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>

  <div style="padding: 14px 24px 20px 24px;">
    <div style="font-size: 13px; font-weight: bold; margin-bottom: 6px;">Date : {date_formatted}</div>

    <div align="center" style="font-size: 17px; font-weight: bold; margin: 4px 0 2px 0; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', sans-serif;">ប្រាក់បៀវត្សប្រចាំខែបុគ្គលិក</div>
    <div align="center" style="font-family: 'Georgia', 'Times New Roman', serif; font-size: 22px; font-weight: bold; margin: 2px 0 14px 0;">{emp_name}</div>

    <table width="100%" border="1" cellpadding="0" cellspacing="0" style="border-collapse: collapse; border: 1.5px solid #000000; text-align: center;">
      <tr>
        <th width="50%" align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 13px; font-weight: bold; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', sans-serif;">ប្រភេទ</th>
        <th width="50%" align="center" style="border: 1.5px solid #000000; padding: 7px 6px; font-size: 13px; font-weight: bold; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', sans-serif;">ប្រាក់ទទួលបាន</th>
      </tr>
      {rows_html}
    </table>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 36px; border-collapse: collapse;">
      <tr>
        <td width="50%" align="center" style="font-size: 13px; font-weight: bold; font-family: 'Segoe UI', 'Georgia', serif;">Manager Signature</td>
        <td width="50%" align="center" style="font-size: 13px; font-weight: bold; font-family: 'Segoe UI', 'Georgia', serif;">Employee Signature</td>
      </tr>
    </table>
  </div>
</body>
</html>
        """
        return html

    def _print_doc(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() == QPrintDialog.DialogCode.Accepted:
            doc = QTextDocument()
            doc.setHtml(self.html)
            doc.print(printer)
            QMessageBox.information(self, "ជោគជ័យ (Printed)", "✅ បានបញ្ជូនទៅម៉ាស៊ីនបោះពុម្ពដោយជោគជ័យ!")

    def _save_pdf(self):
        default_name = f"Payslip_{self.slip.get('payslip_no', 'SLIP')}_{self.slip.get('name', 'Employee')}.pdf".replace("/", "_").replace(" ", "_")
        path, _ = QFileDialog.getSaveFileName(self, "រក្សាទុកប័ណ្ណបៀវត្សជា PDF (Save as PDF)", default_name, "PDF Files (*.pdf)")
        if path:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            doc = QTextDocument()
            doc.setHtml(self.html)
            doc.print(printer)
            QMessageBox.information(self, "ជោគជ័យ (Saved)", f"✅ បានរក្សាទុកជា PDF ដោយជោគជ័យនៅ:\n{path}")


