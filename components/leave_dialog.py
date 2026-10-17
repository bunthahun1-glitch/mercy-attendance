"""
Leave Request Modal Dialog for Mercy Dental Care.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateEdit, QTextEdit, QMessageBox, QSpinBox, QListView
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

import database
from theme import tr, PRIMARY, setup_styled_combobox

class LeaveRequestDialog(QDialog):
    def __init__(self, emp_id=None, parent=None):
        super().__init__(parent)
        self.preselect_emp_id = emp_id
        self.setWindowTitle("Request Leave - Mercy Dental Care")
        self.resize(460, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QComboBox, QDateEdit, QSpinBox, QTextEdit {
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                background-color: #FFFFFF;
                color: #1E293B;
            }
            QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border: 1.5px solid #5648A6;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 26px;
                border-left: 1px solid #CBD5E1;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
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
                padding: 4px;
                outline: none;
                selection-background-color: #EDE9FE;
                selection-color: #5648A6;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("New Leave Request / ស្នើសុំច្បាប់ឈប់សម្រាក")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        layout.addWidget(title)

        # Employee selection
        layout.addWidget(QLabel("Employee / បុគ្គលិក:"))
        self.combo_emp = QComboBox()
        setup_styled_combobox(self.combo_emp)
        emps = database.get_all_employees()
        select_idx = 0
        for i, e in enumerate(emps):
            self.combo_emp.addItem(f"{e['emp_code']} - {e['name']} ({e['khmer_name']})", e['id'])
            if self.preselect_emp_id and e['id'] == self.preselect_emp_id:
                select_idx = i
        self.combo_emp.setCurrentIndex(select_idx)
        layout.addWidget(self.combo_emp)

        # Leave Type
        layout.addWidget(QLabel("Leave Type / ប្រភេទច្បាប់:"))
        self.combo_type = QComboBox()
        setup_styled_combobox(self.combo_type)
        types = database.get_leave_types()
        for t in types:
            self.combo_type.addItem(f"{t['name']} - {t['name_kh']}", t['name'])
        layout.addWidget(self.combo_type)

        # Dates
        d_layout = QHBoxLayout()
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Start Date / ថ្ងៃចាប់ផ្តើម:"))
        self.dt_start = QDateEdit()
        self.dt_start.setCalendarPopup(True)
        self.dt_start.setDate(QDate.currentDate())
        v1.addWidget(self.dt_start)
        d_layout.addLayout(v1)

        v2 = QVBoxLayout()
        v2.addWidget(QLabel("End Date / ថ្ងៃបញ្ចប់:"))
        self.dt_end = QDateEdit()
        self.dt_end.setCalendarPopup(True)
        self.dt_end.setDate(QDate.currentDate())
        v2.addWidget(self.dt_end)
        d_layout.addLayout(v2)
        layout.addLayout(d_layout)

        # Number of days
        layout.addWidget(QLabel("Total Days / ចំនួនថ្ងៃ:"))
        self.spin_days = QSpinBox()
        self.spin_days.setRange(1, 90)
        self.spin_days.setValue(1)
        layout.addWidget(self.spin_days)

        # Reason
        layout.addWidget(QLabel("Reason / មូលហេតុ:"))
        self.text_reason = QTextEdit()
        self.text_reason.setPlaceholderText("Enter detailed reason for leave request...")
        layout.addWidget(self.text_reason)

        # Buttons
        btn_h = QHBoxLayout()
        btn_h.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: #F1F5F9; color: #475569; padding: 8px 16px; border-radius: 8px;")
        btn_cancel.clicked.connect(self.reject)
        btn_h.addWidget(btn_cancel)

        btn_submit = QPushButton("Submit Request")
        btn_submit.setStyleSheet("background-color: #5648A6; color: white; padding: 8px 20px; border-radius: 8px; font-weight: 700;")
        btn_submit.clicked.connect(self.submit_request)
        btn_h.addWidget(btn_submit)

        layout.addLayout(btn_h)

    def submit_request(self):
        emp_id = self.combo_emp.currentData()
        leave_type = self.combo_type.currentData()
        start_str = self.dt_start.date().toString("yyyy-MM-dd")
        end_str = self.dt_end.date().toString("yyyy-MM-dd")
        days = self.spin_days.value()
        reason = self.text_reason.toPlainText().strip() or "Standard leave request"

        database.add_leave_request(emp_id, leave_type, start_str, end_str, days, reason)
        QMessageBox.information(self, "Success", "Leave request submitted to Clinic HR Manager for approval!")
        self.accept()
