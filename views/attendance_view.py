"""
Attendance Management & Biometric Logging View for Mercy Dental Care.
"""

import csv
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QFrame, QListView
)
from PyQt6.QtCore import Qt, QDate

import database
from theme import tr, PRIMARY, SUCCESS, WARNING, DANGER, INFO, setup_styled_combobox

class AttendanceView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Header & Live Clock
        h_row = QHBoxLayout()
        title = QLabel("Clinic Attendance Logs / បញ្ជីវត្តមានបុគ្គលិក")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1E293B;")
        h_row.addWidget(title)
        h_row.addStretch()

        btn_add = QPushButton("➕ បន្ថែមកំណត់ត្រា (+ Add)")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                font-weight: 700;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #4338CA; }
        """)
        btn_add.clicked.connect(self.add_attendance_dialog)
        h_row.addWidget(btn_add)

        self.btn_export = QPushButton("📤 Export Attendance CSV")
        self.btn_export.setStyleSheet("""
            background-color: #F1F5F9;
            color: #334155;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid #CBD5E1;
        """)
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setVisible(False)
        h_row.addWidget(self.btn_export)

        layout.addLayout(h_row)

        # 2. Quick Attendance Punch Bar
        punch_frame = QFrame()
        punch_frame.setStyleSheet("""
            QFrame {
                background-color: #EEEDFB;
                border: 1px solid #C7D2FE;
                border-radius: 12px;
                padding: 12px;
            }
        """)
        p_layout = QHBoxLayout(punch_frame)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(12)

        p_lbl = QLabel("<b>⚡ Quick Staff Check-In / Out:</b>")
        p_lbl.setStyleSheet("color: #4338CA; font-size: 13px;")
        p_layout.addWidget(p_lbl)

        self.combo_quick_emp = QComboBox()
        setup_styled_combobox(self.combo_quick_emp)
        self.combo_quick_emp.setFixedWidth(260)
        self.load_quick_emp_list()
        p_layout.addWidget(self.combo_quick_emp)

        btn_in = QPushButton("🟢 Clock In")
        btn_in.setStyleSheet("""
            background-color: #10B981;
            color: white;
            font-weight: 700;
            border-radius: 6px;
            padding: 6px 14px;
        """)
        btn_in.clicked.connect(self.quick_clock_in)
        p_layout.addWidget(btn_in)

        btn_out = QPushButton("🔴 Clock Out")
        btn_out.setStyleSheet("""
            background-color: #EF4444;
            color: white;
            font-weight: 700;
            border-radius: 6px;
            padding: 6px 14px;
        """)
        btn_out.clicked.connect(self.quick_clock_out)
        p_layout.addWidget(btn_out)

        btn_out_ot = QPushButton("⭐ ចេញថែមម៉ោង (OT អ្នកជំងឺ)")
        btn_out_ot.setToolTip("Clock Out with Overtime (គិតម៉ោងថែមជូនសម្រាប់តែពេលមានអ្នកជំងឺ $1.50/ម៉ោង គិតតាមនាទីជាក់ស្តែងចាប់ពី 10 នាទីឡើង)")
        btn_out_ot.setStyleSheet("""
            background-color: #D97706;
            color: white;
            font-weight: 700;
            border-radius: 6px;
            padding: 6px 14px;
        """)
        btn_out_ot.clicked.connect(self.quick_clock_out_ot)
        p_layout.addWidget(btn_out_ot)

        p_layout.addStretch()
        layout.addWidget(punch_frame)

        # 3. Filters: Date, Department, Status
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        filter_row.addWidget(QLabel("Date:"))
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setDisplayFormat("yyyy-MM-dd")
        self.date_filter.setMinimumWidth(135)
        self.date_filter.dateChanged.connect(self.load_attendance)
        filter_row.addWidget(self.date_filter)

        filter_row.addWidget(QLabel("Department:"))
        self.dept_filter = QComboBox()
        setup_styled_combobox(self.dept_filter)
        self.dept_filter.setMinimumWidth(160)
        self.dept_filter.addItem("All Departments")
        for d in database.get_all_departments():
            self.dept_filter.addItem(d)
        self.dept_filter.currentTextChanged.connect(self.load_attendance)
        filter_row.addWidget(self.dept_filter)

        filter_row.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        setup_styled_combobox(self.status_filter)
        self.status_filter.setMinimumWidth(130)
        self.status_filter.addItems(["All Status", "On Time", "Late", "Early Out", "Absent"])
        self.status_filter.currentTextChanged.connect(self.load_attendance)
        filter_row.addWidget(self.status_filter)

        filter_row.addStretch()

        btn_today = QPushButton("Today")
        btn_today.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_today.setStyleSheet("""
            QPushButton {
                background-color: #F8FAFC;
                color: #1E293B;
                border: 1.5px solid #CBD5E1;
                font-weight: 600;
                padding: 6px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_today.clicked.connect(lambda: self.date_filter.setDate(QDate.currentDate()))
        filter_row.addWidget(btn_today)

        layout.addLayout(filter_row)

        # 4. Table with Crisp, High-Visibility Gridlines
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Employee", "Department", "Date", "Check In", "Check Out", "Status", "ថែមម៉ោង (OT)", "Notes", "Actions"
        ])
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 105)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 95)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 95)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 115)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 130)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(8, 140)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)
        layout.addWidget(self.table)

        self.load_attendance()

    def load_quick_emp_list(self):
        self.combo_quick_emp.clear()
        emps = database.get_all_employees()
        for e in emps:
            self.combo_quick_emp.addItem(f"{e['emp_code']} - {e['name']}", e['id'])

    def load_attendance(self):
        selected_date = self.date_filter.date().toString("yyyy-MM-dd")
        dept_val = self.dept_filter.currentText()
        status_val = self.status_filter.currentText()

        conn = database.get_connection()
        c = conn.cursor()

        query = """
            SELECT a.*, e.emp_code, e.name, e.khmer_name, e.department, e.job_position
            FROM attendance a
            JOIN employees e ON e.id = a.emp_id
            WHERE a.date = ?
        """
        params = [selected_date]

        if dept_val != "All Departments":
            query += " AND e.department = ?"
            params.append(dept_val)

        if status_val != "All Status":
            query += " AND a.status = ?"
            params.append(status_val)

        query += " ORDER BY e.emp_code ASC"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            row_dict = dict(row)

            # Column 0: Employee
            code_prefix = f"{row.get('emp_code', '')} - " if row.get('emp_code') else ""
            it_name = QTableWidgetItem(f"{code_prefix}{row['khmer_name']} ({row['name']})")
            it_name.setData(Qt.ItemDataRole.UserRole, row_dict)
            self.table.setItem(r, 0, it_name)

            # Column 1: Department
            it_dept = QTableWidgetItem(row["department"])
            self.table.setItem(r, 1, it_dept)

            # Column 2: Date
            it_date = QTableWidgetItem(row["date"])
            it_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, it_date)

            # Column 3: Check In
            it_in = QTableWidgetItem(row["check_in"] or "--:--")
            it_in.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, it_in)

            # Column 4: Check Out
            it_out = QTableWidgetItem(row["check_out"] or "--:--")
            it_out.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 4, it_out)

            # Column 5: Status Badge widget
            status_text = row["status"]
            badge_w = QWidget()
            badge_w.setStyleSheet("background: transparent;")
            b_layout = QHBoxLayout(badge_w)
            b_layout.setContentsMargins(6, 4, 6, 4)
            b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            badge_lbl = QLabel(status_text)
            badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if status_text == "On Time":
                badge_lbl.setStyleSheet("background-color: #ECFDF5; color: #065F46; border: 1.5px solid #10B981; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 12px;")
            elif status_text == "Overtime":
                badge_lbl.setStyleSheet("background-color: #FEF3C7; color: #B45309; border: 1.5px solid #F59E0B; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 12px;")
            elif status_text == "Late":
                badge_lbl.setStyleSheet("background-color: #FEE2E2; color: #991B1B; border: 1.5px solid #EF4444; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 12px;")
            elif status_text == "Early Out":
                badge_lbl.setStyleSheet("background-color: #EFF6FF; color: #1E40AF; border: 1.5px solid #3B82F6; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 12px;")
            else:
                badge_lbl.setStyleSheet("background-color: #F1F5F9; color: #475569; border: 1.5px solid #94A3B8; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 12px;")
            b_layout.addWidget(badge_lbl)
            self.table.setCellWidget(r, 5, badge_w)

            # Column 6: ថែមម៉ោង (OT)
            ot_h = float(row_dict.get("ot_hours") or 0.0)
            if ot_h > 0:
                notes_str_raw = row_dict.get("notes") or ""
                import re
                m = re.search(r"\+\$(\d+\.\d{2})", notes_str_raw)
                ot_pay = float(m.group(1)) if m else round(ot_h * 1.50, 2)
                it_ot = QTableWidgetItem(f"+{ot_h:.1f}h (${ot_pay:.2f})")
                it_ot.setForeground(QColor("#7C3AED"))
                f_ot = it_ot.font()
                f_ot.setBold(True)
                it_ot.setFont(f_ot)
                it_ot.setToolTip(f"ម៉ោងថែម OT: +{ot_h:.1f}h (${ot_pay:.2f})")
            else:
                it_ot = QTableWidgetItem("0")
                it_ot.setForeground(QColor("#94A3B8"))
                it_ot.setToolTip("គ្មានម៉ោងថែម (0)")
            it_ot.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 6, it_ot)

            # Column 7: Notes (Show only Patient Name)
            notes_str = row_dict.get("notes") or ""
            pat_match = re.search(r"អ្នកជំងឺ[៖:]\s*([^•\)\(\|,]+)", notes_str)
            if pat_match:
                display_note = pat_match.group(1).strip()
            elif any(k in notes_str for k in ["Regular Checked Out", "Mobile QR Scan", "Checked out with Overtime"]):
                display_note = "--"
            else:
                display_note = notes_str or "--"

            it_notes = QTableWidgetItem(display_note)
            if display_note != "--":
                it_notes.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                it_notes.setForeground(QColor("#0F172A"))
            else:
                it_notes.setForeground(QColor("#94A3B8"))
                it_notes.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_notes.setToolTip(notes_str)
            self.table.setItem(r, 7, it_notes)

            # Column 8: Actions Widget: Edit (✏️) and Delete (🗑️)
            act_w = QWidget()
            act_w.setStyleSheet("background: transparent;")
            act_l = QHBoxLayout(act_w)
            act_l.setContentsMargins(4, 4, 4, 4)
            act_l.setSpacing(6)

            att_id = row["id"]
            btn_edit = QPushButton("✏️ Edit")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #5648A6;
                    font-weight: 700;
                    font-size: 11.5px;
                    padding: 4px 8px;
                    border-radius: 6px;
                    border: 1px solid #C7D2FE;
                }
                QPushButton:hover {
                    background-color: #5648A6;
                    color: #FFFFFF;
                }
            """)
            btn_edit.clicked.connect(lambda checked, d=row_dict: self.edit_attendance_dialog(d))
            act_l.addWidget(btn_edit)

            btn_del = QPushButton("🗑️")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("លុបកំណត់ត្រាវត្តមាន (Delete)")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    font-weight: 700;
                    font-size: 12px;
                    padding: 4px 8px;
                    border-radius: 6px;
                    border: 1px solid #FCA5A5;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                    color: #FFFFFF;
                }
            """)
            btn_del.clicked.connect(lambda checked, i=att_id: self.delete_attendance(i))
            act_l.addWidget(btn_del)

            self.table.setCellWidget(r, 8, act_w)

    def on_row_double_clicked(self, item):
        row = item.row()
        id_item = self.table.item(row, 0)
        if id_item:
            row_dict = id_item.data(Qt.ItemDataRole.UserRole)
            if row_dict:
                self.edit_attendance_dialog(row_dict)

    def add_attendance_dialog(self):
        from components.attendance_edit_dialog import AttendanceEditDialog
        dlg = AttendanceEditDialog(record=None, parent=self)
        if dlg.exec():
            self.load_attendance()

    def edit_attendance_dialog(self, row_data):
        from components.attendance_edit_dialog import AttendanceEditDialog
        dlg = AttendanceEditDialog(record=row_data, parent=self)
        if dlg.exec():
            self.load_attendance()

    def delete_attendance(self, att_id):
        reply = QMessageBox.question(
            self, "បញ្ជាក់ការលុប (Confirm Delete)",
            "តើលោកអ្នកពិតជាចង់លុបកំណត់ត្រាវត្តមាននេះមែនទេ?\n"
            "Are you sure you want to delete this attendance record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_attendance_record(att_id)
            QMessageBox.information(self, "ជោគជ័យ", "បានលុបកំណត់ត្រាវត្តមានដោយជោគជ័យ! (Deleted successfully)")
            self.load_attendance()

    def quick_clock_in(self):
        emp_id = self.combo_quick_emp.currentData()
        status, t = database.record_check_in(emp_id)
        QMessageBox.information(self, "Clock In", f"Logged Check In at {t} ({status}).")
        self.load_attendance()

    def quick_clock_out(self):
        emp_id = self.combo_quick_emp.currentData()
        t, ot_h, ot_p = database.record_check_out(emp_id, has_overtime=False)
        QMessageBox.information(self, "Clock Out", f"Logged Regular Check Out at {t} (No OT).")
        self.load_attendance()

    def quick_clock_out_ot(self):
        emp_id = self.combo_quick_emp.currentData()
        if not emp_id:
            QMessageBox.warning(self, "ជូនដំណឹង", "សូមជ្រើសរើសបុគ្គលិកជាមុនសិន!")
            return

        from datetime import datetime
        shift_end = database.get_setting("shift_end", "18:00")
        now_hm = datetime.now().strftime("%H:%M")
        if now_hm < shift_end[:5]:
            QMessageBox.warning(
                self, "មិនទាន់ដល់ម៉ោងថែម",
                f"⚠️ មិនទាន់ដល់ម៉ោងចេញធ្វើការ ({shift_end}) នៅឡើយទេ! (ម៉ោងបច្ចុប្បន្ន៖ {now_hm})\n\nការថែមម៉ោង (OT) គិតតែចាប់ពីម៉ោង {shift_end} ឡើងទៅប៉ុណ្ណោះ។\n\nប្រសិនបើលោកអ្នកចេញពេលនេះ សូមចុចប៊ូតុង 'Clock Out' ធម្មតា។"
            )
            return

        from PyQt6.QtWidgets import QInputDialog
        p_name, ok = QInputDialog.getText(
            self, "ឈ្មោះអ្នកជំងឺ (Patient Name)",
            "⭐ ថែមម៉ោង (OT) សម្រាប់តែមានអ្នកជំងឺ៖\n(អត្រា៖ 30 នាទី = $0.75 • 1 ម៉ោង = $1.50)\n\nសូមបញ្ចូលឈ្មោះអ្នកជំងឺ (Patient Name)៖"
        )
        if not ok or not p_name.strip():
            QMessageBox.warning(self, "មិនទាន់ជោគជ័យ", "❌ សូមបញ្ចូលឈ្មោះអ្នកជំងឺជាមុនសិន ទើបអាចស្កេនចេញថែមម៉ោង (OT) បាន!")
            return

        patient_name = p_name.strip()
        t, ot_h, ot_p = database.record_check_out(emp_id, has_overtime=True, patient_name=patient_name)
        if ot_h > 0:
            mins = int(round(ot_h * 60))
            QMessageBox.information(
                self, "ចេញថែមម៉ោង (OT អ្នកជំងឺ)", 
                f"បានកត់ត្រាចេញថែមម៉ោង (អ្នកជំងឺ) នៅម៉ោង {t}!\n\n👤 អ្នកជំងឺ៖ {patient_name}\n💰 ម៉ោងថែម: +{ot_h} ម៉ោង ({mins} នាទី) = +${ot_p:.2f} (30 នាទី=$0.75 • 1 ម៉ោង=$1.50)\nបានបញ្ចូលក្នុង Payroll រួចរាល់។"
            )
        else:
            QMessageBox.information(
                self, "ចេញពីធ្វើការ", 
                f"បានកត់ត្រាចេញពីធ្វើការនៅម៉ោង {t}។\n\n👤 អ្នកជំងឺ៖ {patient_name}\n⚠️ លើសតិចជាង ១៥ នាទី មិនទាន់គ្រប់លក្ខខណ្ឌគិតម៉ោងថែម (OT) ឡើយ។"
            )
        self.load_attendance()

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Attendance", "mercy_dental_attendance.csv", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        date_str = self.date_filter.date().toString("yyyy-MM-dd")
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT a.date, e.emp_code, e.name, e.khmer_name, e.department, a.check_in, a.check_out, a.status, a.ot_hours
            FROM attendance a
            JOIN employees e ON e.id = a.emp_id
            WHERE a.date = ?
            ORDER BY e.emp_code ASC
        """, (date_str,))
        rows = c.fetchall()
        conn.close()

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Employee ID", "English Name", "Khmer Name", "Department", "Check In", "Check Out", "Status", "OT Hours"])
            for r in rows:
                writer.writerow(list(r))

        QMessageBox.information(self, "Export Successful", f"Saved attendance log to:\n{file_path}")
