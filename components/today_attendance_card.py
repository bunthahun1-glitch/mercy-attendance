"""
Today's Clinic Attendance & Leave Widget
Displays live employee check-in, check-out, overtime (OT), and staff leave details for the current working day.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from datetime import datetime, date
import database

class TodayAttendanceCard(QFrame):
    open_attendance_clicked = pyqtSignal()
    open_leave_dialog_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("todayAttCard")
        self.setStyleSheet("""
            QFrame#todayAttCard {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
                padding: 10px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 11.5px;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #475569;
                font-weight: 700;
                font-size: 11.5px;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
            }
            QTabBar::tab {
                background: #F1F5F9;
                color: #64748B;
                padding: 5px 12px;
                font-size: 11.5px;
                font-weight: 700;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #EEEDFB;
                color: #5648A6;
                border-bottom: 2px solid #5648A6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 1. Header Row
        head_h = QHBoxLayout()
        head_h.setSpacing(8)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        self.lbl_title = QLabel("📋 វត្តមាន និងការសុំច្បាប់ប្រចាំថ្ងៃ (Today's Attendance & Leave)")
        self.lbl_title.setStyleSheet("font-size: 13.5px; font-weight: 800; color: #1E293B;")
        title_v.addWidget(self.lbl_title)

        today_kh = date.today().strftime("%d-%b-%Y")
        shift_start = database.get_setting("shift_start", "07:30")
        shift_end = database.get_setting("shift_end", "18:00")
        self.lbl_sub = QLabel(f"កាលបរិច្ឆេទ៖ {today_kh} | ម៉ោងការងារ {shift_start} - {shift_end} | ម៉ោងថែម (OT): សម្រាប់តែពេលមានអ្នកជំងឺ (30 នាទី = $0.75 • 1 ម៉ោង = $1.50 • គិតចាប់ពី 15 នាទីឡើង)")
        self.lbl_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        title_v.addWidget(self.lbl_sub)
        head_h.addLayout(title_v, stretch=1)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setToolTip("ផ្ទុកទិន្នន័យឡើងវិញ (Refresh)")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_refresh.clicked.connect(self.refresh_data)
        head_h.addWidget(btn_refresh)

        layout.addLayout(head_h)

        # 2. Summary Mini-Pills
        pill_h = QHBoxLayout()
        pill_h.setSpacing(6)

        self.pill_present = QLabel("✅ វត្តមាន: 0/0")
        self.pill_present.setStyleSheet("background-color: #ECFDF5; color: #059669; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #A7F3D0;")
        pill_h.addWidget(self.pill_present)

        self.pill_late = QLabel("⏰ យឺត: 0")
        self.pill_late.setStyleSheet("background-color: #FFFBEB; color: #D97706; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #FDE68A;")
        pill_h.addWidget(self.pill_late)

        self.pill_ot = QLabel("⚡ ម៉ោងថែម (អ្នកជំងឺ): 0 នាក់")
        self.pill_ot.setToolTip("ម៉ោងថែម (OT) គិតជូនសម្រាប់តែករណីមានអ្នកជំងឺប៉ុណ្ណោះ ($1.50/ម៉ោង គិតតាមនាទីជាក់ស្តែងចាប់ពី 10 នាទីឡើង)")
        self.pill_ot.setStyleSheet("background-color: #EEEDFB; color: #5648A6; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #D6D3F7;")
        pill_h.addWidget(self.pill_ot)

        self.pill_leave = QLabel("🏖️ សុំច្បាប់: 0")
        self.pill_leave.setStyleSheet("background-color: #EFF6FF; color: #2563EB; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #BFDBFE;")
        pill_h.addWidget(self.pill_leave)

        pill_h.addStretch()
        layout.addLayout(pill_h)

        # 3. Tabs: 1. Attendance & Overtime, 2. Staff on Leave
        self.tabs = QTabWidget()

        # Tab 1: Attendance Table
        tab_att = QWidget()
        att_v = QVBoxLayout(tab_att)
        att_v.setContentsMargins(0, 4, 0, 0)
        att_v.setSpacing(0)

        self.table_att = QTableWidget()
        self.table_att.setColumnCount(6)
        self.table_att.setHorizontalHeaderLabels([
            "បុគ្គលិក (Staff)", "ចូល (In)", "ចេញ (Out)", "OT (ម៉ោង)", "ស្ថានភាព (Status)", "សកម្មភាព"
        ])
        self.table_att.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_att.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_att.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_att.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_att.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_att.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_att.setColumnWidth(5, 110)
        self.table_att.verticalHeader().setVisible(False)
        self.table_att.verticalHeader().setDefaultSectionSize(32)
        self.table_att.setFixedHeight(210)
        self.table_att.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_att.setAlternatingRowColors(True)
        self.table_att.itemDoubleClicked.connect(self._on_att_row_double_clicked)
        att_v.addWidget(self.table_att)
        self.tabs.addTab(tab_att, "⏱️ វត្តមាន & OT (អ្នកជំងឺ)")

        # Tab 2: Leave Table
        tab_leave = QWidget()
        leave_v = QVBoxLayout(tab_leave)
        leave_v.setContentsMargins(0, 4, 0, 0)
        leave_v.setSpacing(0)

        self.table_leave = QTableWidget()
        self.table_leave.setColumnCount(6)
        self.table_leave.setHorizontalHeaderLabels([
            "បុគ្គលិក (Staff)", "ប្រភេទច្បាប់ (Leave Type)", "កាលបរិច្ឆេទ (Duration)", "មូលហេតុ (Reason)", "ស្ថានភាព (Status)", "សកម្មភាព"
        ])
        self.table_leave.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_leave.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_leave.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_leave.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_leave.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_leave.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_leave.setColumnWidth(5, 80)
        self.table_leave.verticalHeader().setVisible(False)
        self.table_leave.verticalHeader().setDefaultSectionSize(32)
        self.table_leave.setFixedHeight(200)
        self.table_leave.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_leave.setAlternatingRowColors(True)
        leave_v.addWidget(self.table_leave)

        self.lbl_no_leave = QLabel("✅ ថ្ងៃនេះគ្មានបុគ្គលិកសុំច្បាប់សម្រាកទេ (No Staff on Leave Today)")
        self.lbl_no_leave.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_no_leave.setStyleSheet("font-size: 12px; color: #64748B; padding: 20px; font-weight: 600;")
        self.lbl_no_leave.setVisible(False)
        leave_v.addWidget(self.lbl_no_leave)

        self.tabs.addTab(tab_leave, "🏖️ សុំច្បាប់ថ្ងៃនេះ")

        layout.addWidget(self.tabs, stretch=1)

        # 4. Bottom Action Row
        btm_h = QHBoxLayout()
        btm_h.setContentsMargins(0, 2, 0, 0)

        btn_view_all = QPushButton("➔ បើកមើលបញ្ជីវត្តមានលម្អិត (Open Attendance Log)")
        btn_view_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view_all.setStyleSheet("""
            QPushButton {
                background-color: #EEEDFB;
                color: #5648A6;
                font-weight: 700;
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 11.5px;
                border: 1px solid #D6D3F7;
            }
            QPushButton:hover {
                background-color: #5648A6;
                color: #FFFFFF;
            }
        """)
        btn_view_all.clicked.connect(self.open_attendance_clicked.emit)
        btm_h.addWidget(btn_view_all)

        btm_h.addStretch()

        btn_req_leave = QPushButton("+ សុំច្បាប់ (Request Leave)")
        btn_req_leave.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_req_leave.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                font-weight: 700;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 11.5px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)
        btn_req_leave.clicked.connect(self.open_leave_dialog_clicked.emit)
        btm_h.addWidget(btn_req_leave)

        layout.addLayout(btm_h)

        self.refresh_data()

    def refresh_data(self):
        data = database.get_today_dashboard_attendance_and_leave()
        total = data.get("total_staff", 0)
        expected = data.get("expected_staff", total)
        present = data.get("present_count", 0)
        late = data.get("late_count", 0)
        ot_cnt = data.get("ot_count", 0)
        leave_cnt = data.get("leave_count", 0)

        today_kh = date.today().strftime("%d-%b-%Y")
        shift_start = database.get_setting("shift_start", "07:30")
        shift_end = database.get_setting("shift_end", "18:00")
        self.lbl_sub.setText(f"កាលបរិច្ឆេទ៖ {today_kh} | ម៉ោងការងារ {shift_start} - {shift_end} | ម៉ោងថែម (OT): សម្រាប់តែពេលមានអ្នកជំងឺ (30 នាទី = $0.75 • 1 ម៉ោង = $1.50 • គិតចាប់ពី 15 នាទីឡើង)")

        self.pill_present.setText(f"✅ វត្តមាន: {present}/{expected}")
        self.pill_late.setText(f"⏰ យឺត: {late}")
        self.pill_ot.setText(f"⚡ ម៉ោងថែម (អ្នកជំងឺ): {ot_cnt} នាក់")
        self.pill_leave.setText(f"🏖️ សុំច្បាប់: {leave_cnt} នាក់")
        self.tabs.setTabText(1, f"🏖️ សុំច្បាប់ថ្ងៃនេះ ({leave_cnt})")

        # Populate Attendance Table
        att_list = data.get("attendance_list", [])
        self.table_att.setRowCount(len(att_list))
        for row, emp in enumerate(att_list):
            name_text = emp['khmer_name'] if emp.get('khmer_name') else emp.get('name', '')
            it_name = QTableWidgetItem(name_text)
            it_name.setToolTip(f"{emp.get('name', '')} ({emp.get('khmer_name', '')})\nID: {emp.get('emp_code', '')}\nតួនាទី: {emp.get('job_position', '')}\nប្រភេទ: {emp.get('employment_type', '')}")
            self.table_att.setItem(row, 0, it_name)

            cin = emp.get("check_in")
            cin_text = cin[:5] if cin and len(cin) >= 5 else "--:--"
            it_in = QTableWidgetItem(cin_text)
            it_in.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if cin:
                it_in.setForeground(QColor("#059669"))
            else:
                it_in.setForeground(QColor("#94A3B8"))
            self.table_att.setItem(row, 1, it_in)

            cout = emp.get("check_out")
            cout_text = cout[:5] if cout and len(cout) >= 5 else "--:--"
            it_out = QTableWidgetItem(cout_text)
            it_out.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if cout:
                it_out.setForeground(QColor("#4F46E5"))
            else:
                it_out.setForeground(QColor("#94A3B8"))
            self.table_att.setItem(row, 2, it_out)

            ot_h = emp.get("ot_hours", 0.0)
            if ot_h > 0:
                ot_text = f"+{ot_h:.1f}h (${emp.get('ot_pay', 0.0):.2f})"
                it_ot = QTableWidgetItem(ot_text)
                it_ot.setForeground(QColor("#7C3AED"))
                it_ot.setToolTip(f"ម៉ោងថែមព្យាបាលអ្នកជំងឺ: {ot_h:.1f} ម៉ោង (${emp.get('ot_pay', 0.0):.2f})")
            else:
                it_ot = QTableWidgetItem("0")
                it_ot.setForeground(QColor("#94A3B8"))
                it_ot.setToolTip("គ្មានម៉ោងថែម (គិតជូនសម្រាប់តែពេលមានអ្នកជំងឺប៉ុណ្ណោះ)")
            it_ot.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_att.setItem(row, 3, it_ot)

            # Status badge item
            st = emp.get("status")
            if st == "On Time":
                st_display = "✅ ទៀងទាត់"
                st_color = "#059669"
            elif st == "Late":
                st_display = "⏰ យឺត"
                st_color = "#D97706"
            elif st == "On Leave":
                st_display = "🏖️ ច្បាប់"
                st_color = "#2563EB"
            elif st == "Present":
                st_display = "✅ វត្តមាន"
                st_color = "#059669"
            elif st == "Remote":
                st_display = "🌐 ពីចម្ងាយ (Remote)"
                st_color = "#0284C7"
            elif st == "Part-Time Off":
                st_display = "🎓 ក្រៅម៉ោង (ទំនេរទើបមក)"
                st_color = "#7C3AED"
            elif st == "Overtime":
                st_display = "⭐ ថែមម៉ោង"
                st_color = "#7C3AED"
            else:
                st_display = "⏳ មិនទាន់ស្កេន"
                st_color = "#64748B"

            it_st = QTableWidgetItem(st_display)
            it_st.setForeground(QColor(st_color))
            it_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_att.setItem(row, 4, it_st)

            # Actions cell for attendance
            act_w = QWidget()
            act_w.setStyleSheet("background: transparent;")
            act_l = QHBoxLayout(act_w)
            act_l.setContentsMargins(2, 2, 2, 2)
            act_l.setSpacing(4)

            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("កែប្រែកំណត់ត្រាវត្តមាន (Edit)")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #5648A6;
                    border: 1px solid #C7D2FE;
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover { background-color: #5648A6; color: white; }
            """)
            btn_edit.clicked.connect(lambda ch, e=emp: self._edit_attendance(e))
            act_l.addWidget(btn_edit)

            if emp.get("att_id"):
                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("លុបកំណត់ត្រាវត្តមាន (Delete)")
                btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_del.setStyleSheet("""
                    QPushButton {
                        background-color: #FEE2E2;
                        color: #DC2626;
                        border: 1px solid #FECACA;
                        border-radius: 4px;
                        padding: 2px 6px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover { background-color: #DC2626; color: white; }
                """)
                btn_del.clicked.connect(lambda ch, aid=emp["att_id"]: self._delete_attendance(aid))
                act_l.addWidget(btn_del)

            self.table_att.setCellWidget(row, 5, act_w)

        # Populate Leave Table
        leave_list = data.get("leave_list", [])
        if leave_list:
            self.table_leave.setVisible(True)
            self.lbl_no_leave.setVisible(False)
            self.table_leave.setRowCount(len(leave_list))
            for row, lr in enumerate(leave_list):
                name_text = f"{lr.get('khmer_name') or lr.get('name')} ({lr.get('emp_code', '')})"
                it_name = QTableWidgetItem(name_text)
                self.table_leave.setItem(row, 0, it_name)

                it_type = QTableWidgetItem(lr.get("leave_type", ""))
                self.table_leave.setItem(row, 1, it_type)

                period_text = f"{lr.get('start_date', '')} ➔ {lr.get('end_date', '')} ({lr.get('days', 1)} ថ្ងៃ)"
                it_period = QTableWidgetItem(period_text)
                self.table_leave.setItem(row, 2, it_period)

                it_reason = QTableWidgetItem(lr.get("reason", "") or "-")
                self.table_leave.setItem(row, 3, it_reason)

                st = lr.get("status", "Approved")
                st_badge = "✅ អនុម័ត" if st == "Approved" else ("⏳ កំពុងរង់ចាំ" if st == "Pending" else "❌ បដិសេធ")
                it_st = QTableWidgetItem(st_badge)
                it_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_leave.setItem(row, 4, it_st)

                # Delete Leave Action button
                act_lw = QWidget()
                act_lw.setStyleSheet("background: transparent;")
                act_ll = QHBoxLayout(act_lw)
                act_ll.setContentsMargins(2, 2, 2, 2)
                act_ll.setAlignment(Qt.AlignmentFlag.AlignCenter)

                lid = lr.get("id")
                btn_del_l = QPushButton("🗑️")
                btn_del_l.setToolTip("លុបការសុំច្បាប់នេះ (Delete)")
                btn_del_l.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_del_l.setStyleSheet("""
                    QPushButton {
                        background-color: #FEE2E2;
                        color: #DC2626;
                        border: 1px solid #FECACA;
                        border-radius: 4px;
                        padding: 2px 6px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover { background-color: #DC2626; color: white; }
                """)
                btn_del_l.clicked.connect(lambda ch, i=lid: self._delete_leave(i))
                act_ll.addWidget(btn_del_l)
                self.table_leave.setCellWidget(row, 5, act_lw)
        else:
            self.table_leave.setRowCount(0)
            self.table_leave.setVisible(False)
            self.lbl_no_leave.setVisible(True)

    def _on_att_row_double_clicked(self, item):
        row = item.row()
        data = database.get_today_dashboard_attendance_and_leave()
        att_list = data.get("attendance_list", [])
        if 0 <= row < len(att_list):
            self._edit_attendance(att_list[row])

    def _edit_attendance(self, emp):
        from components.attendance_edit_dialog import AttendanceEditDialog
        from PyQt6.QtWidgets import QMessageBox
        # Fetch today's record if present
        today_str = date.today().strftime("%Y-%m-%d")
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM attendance WHERE emp_id = ? AND date = ?", (emp["id"], today_str))
        row = c.fetchone()
        conn.close()

        record = dict(row) if row else {"emp_id": emp["id"], "date": today_str}
        dlg = AttendanceEditDialog(record=record, emp_id=emp["id"], parent=self)
        if dlg.exec():
            self.refresh_data()

    def _delete_attendance(self, att_id):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "បញ្ជាក់ការលុប (Confirm Delete)",
            "តើលោកអ្នកពិតជាចង់លុបកំណត់ត្រាវត្តមាននេះមែនទេ?\nAre you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_attendance_record(att_id)
            self.refresh_data()

    def _delete_leave(self, leave_id):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "បញ្ជាក់ការលុប (Confirm Delete)",
            "តើលោកអ្នកពិតជាចង់លុបការសុំច្បាប់នេះមែនទេ?\nAre you sure you want to delete this leave request?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_leave_request(leave_id)
            self.refresh_data()

