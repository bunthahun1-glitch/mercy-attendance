"""
Attendance Record Edit & Add Dialog for Desktop App.
Allows Administrator to modify check-in, check-out, status, OT hours, and notes,
or manually add a missing attendance record.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox,
    QMessageBox, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, QTime
import database
from theme import PRIMARY, BORDER, setup_styled_combobox

class AttendanceEditDialog(QDialog):
    def __init__(self, record=None, emp_id=None, parent=None):
        super().__init__(parent)
        self.record = record
        self.emp_id = emp_id if emp_id else (record["emp_id"] if record else None)
        
        is_edit = record is not None
        title_text = "✏️ កែប្រែកំណត់ត្រាវត្តមាន (Edit Attendance)" if is_edit else "➕ បន្ថែមកំណត់ត្រាវត្តមាន (Add Attendance)"
        self.setWindowTitle(title_text)
        self.setFixedWidth(460)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 12px;
                color: #334155;
                font-weight: 600;
            }
            QLineEdit, QDateEdit, QTimeEdit, QDoubleSpinBox {
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QDoubleSpinBox:focus {
                border-color: #5648A6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        head = QLabel(title_text)
        head.setStyleSheet("font-size: 16px; font-weight: 800; color: #1E293B; margin-bottom: 4px;")
        layout.addWidget(head)

        # Employee Selector / Info
        emp_box = QFrame()
        emp_box.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px;")
        emp_l = QVBoxLayout(emp_box)
        emp_l.setContentsMargins(4, 4, 4, 4)
        emp_l.setSpacing(4)

        emp_l.addWidget(QLabel("បុគ្គលិក (Employee):"))
        self.combo_emp = QComboBox()
        setup_styled_combobox(self.combo_emp)
        emps = database.get_all_employees()
        sel_idx = 0
        for i, e in enumerate(emps):
            self.combo_emp.addItem(f"{e['emp_code']} - {e['khmer_name']} ({e['name']})", e["id"])
            if self.emp_id and e["id"] == self.emp_id:
                sel_idx = i
        self.combo_emp.setCurrentIndex(sel_idx)
        if is_edit:
            self.combo_emp.setEnabled(False) # lock employee on edit
        emp_l.addWidget(self.combo_emp)
        layout.addWidget(emp_box)

        # Date Row
        date_row = QHBoxLayout()
        date_lbl = QLabel("កាលបរិច្ឆេទ (Date):")
        date_row.addWidget(date_lbl)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        if record and record.get("date"):
            d = QDate.fromString(record["date"], "yyyy-MM-dd")
            self.date_edit.setDate(d if d.isValid() else QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())
        date_row.addWidget(self.date_edit)
        layout.addLayout(date_row)

        # Check In Row
        in_row = QHBoxLayout()
        self.chk_has_in = QCheckBox("ម៉ោងចូល (Check In):")
        self.chk_has_in.setChecked(bool(record and record.get("check_in")))
        self.chk_has_in.toggled.connect(self._toggle_in)
        in_row.addWidget(self.chk_has_in)

        self.time_in = QTimeEdit()
        self.time_in.setDisplayFormat("HH:mm:ss")
        if record and record.get("check_in"):
            t = QTime.fromString(record["check_in"][:8], "HH:mm:ss")
            self.time_in.setTime(t if t.isValid() else QTime(7, 30))
        else:
            self.time_in.setTime(QTime(7, 30))
        self.time_in.setEnabled(self.chk_has_in.isChecked())
        in_row.addWidget(self.time_in)
        layout.addLayout(in_row)

        # Check Out Row
        out_row = QHBoxLayout()
        self.chk_has_out = QCheckBox("ម៉ោងចេញ (Check Out):")
        self.chk_has_out.setChecked(bool(record and record.get("check_out")))
        self.chk_has_out.toggled.connect(self._toggle_out)
        out_row.addWidget(self.chk_has_out)

        self.time_out = QTimeEdit()
        self.time_out.setDisplayFormat("HH:mm:ss")
        if record and record.get("check_out"):
            t = QTime.fromString(record["check_out"][:8], "HH:mm:ss")
            self.time_out.setTime(t if t.isValid() else QTime(18, 0))
        else:
            self.time_out.setTime(QTime(18, 0))
        self.time_out.setEnabled(self.chk_has_out.isChecked())
        out_row.addWidget(self.time_out)
        layout.addLayout(out_row)

        # Status & OT Row
        stat_ot_row = QHBoxLayout()
        stat_v = QVBoxLayout()
        stat_v.addWidget(QLabel("ស្ថានភាព (Status):"))
        self.combo_status = QComboBox()
        setup_styled_combobox(self.combo_status)
        self.combo_status.addItems(["On Time", "Late", "Early Out", "Absent", "Overtime"])
        if record and record.get("status"):
            idx = self.combo_status.findText(record["status"])
            if idx >= 0:
                self.combo_status.setCurrentIndex(idx)
        stat_v.addWidget(self.combo_status)
        stat_ot_row.addLayout(stat_v)

        ot_v = QVBoxLayout()
        ot_v.addWidget(QLabel("ម៉ោងថែម OT (Hours):"))
        self.spin_ot = QDoubleSpinBox()
        self.spin_ot.setRange(0.0, 24.0)
        self.spin_ot.setSingleStep(0.5)
        self.spin_ot.setDecimals(2)
        if record and record.get("ot_hours"):
            self.spin_ot.setValue(float(record["ot_hours"]))
        ot_v.addWidget(self.spin_ot)
        stat_ot_row.addLayout(ot_v)
        layout.addLayout(stat_ot_row)

        # Notes
        layout.addWidget(QLabel("កំណត់សម្គាល់ (Notes):"))
        self.txt_notes = QLineEdit()
        self.txt_notes.setPlaceholderText("ឧ. មកទាន់ពេល, OT ជួយអ្នកជំងឺវះកាត់...")
        if record and record.get("notes"):
            self.txt_notes.setText(str(record["notes"]))
        layout.addWidget(self.txt_notes)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("បោះបង់ (Cancel)")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                font-weight: 700;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("💾 រក្សាទុក (Save)")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                font-weight: 700;
                padding: 8px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #4338CA; }
        """)
        btn_save.clicked.connect(self.save)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _toggle_in(self, checked):
        self.time_in.setEnabled(checked)

    def _toggle_out(self, checked):
        self.time_out.setEnabled(checked)

    def save(self):
        emp_id = self.combo_emp.currentData()
        att_date = self.date_edit.date().toString("yyyy-MM-dd")
        check_in = self.time_in.time().toString("HH:mm:ss") if self.chk_has_in.isChecked() else None
        check_out = self.time_out.time().toString("HH:mm:ss") if self.chk_has_out.isChecked() else None
        status = self.combo_status.currentText()
        ot_hours = float(self.spin_ot.value())
        notes = self.txt_notes.text().strip()

        if self.record and self.record.get("id"):
            # Update existing
            database.update_attendance_record(
                self.record["id"], check_in, check_out, status, ot_hours, notes
            )
            QMessageBox.information(self, "ជោគជ័យ", "បានកែប្រែកំណត់ត្រាវត្តមានដោយជោគជ័យ! (Updated successfully)")
        else:
            # Insert new
            database.add_attendance_record(
                emp_id, att_date, check_in, check_out, status, ot_hours, notes
            )
            QMessageBox.information(self, "ជោគជ័យ", "បានបន្ថែមកំណត់ត្រាវត្តមានថ្មីដោយជោគជ័យ! (Added successfully)")

        self.accept()
