"""
Leave Management View matching Click HR screenshot IMG_7446.
Features fully interactive sub-navigation:
1. Dashboard (Leave overview, KPI cards, upcoming leaves)
2. Calendar (Interactive leave calendar and date inspection)
3. Management (Staff leave requests, approval workflow)
4. Reporting (Staff annual leave balance report, CSV export)
5. Configuration (Leave types setup matching IMG_7446)
"""

import csv
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QMessageBox, QStackedWidget, QFrame, QCalendarWidget,
    QComboBox, QFileDialog, QButtonGroup, QGridLayout, QScrollArea,
    QAbstractItemView, QListView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QFont

import database
from components.leave_dialog import LeaveRequestDialog
from components.stat_card import StatCard
from theme import tr, PRIMARY, SUCCESS, DANGER, WARNING, INFO, BORDER

class LeaveView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # 1. Top Sub-navigation Bar matching IMG_7446
        sub_nav_frame = QFrame()
        sub_nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 4px 10px;
            }}
        """)
        sub_nav = QHBoxLayout(sub_nav_frame)
        sub_nav.setContentsMargins(8, 6, 8, 6)
        sub_nav.setSpacing(10)

        sub_title = QLabel("Leave / ច្បាប់")
        sub_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #1E293B; margin-right: 12px;")
        sub_nav.addWidget(sub_title)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.sub_menus = [
            ("Dashboard", "ផ្ទាំងទូទៅ", 0),
            ("Calendar", "ប្រតិទិន", 1),
            ("Management", "ការគ្រប់គ្រង", 2),
            ("Reporting", "របាយការណ៍", 3),
            ("Configuration", "ការកំណត់", 4)
        ]

        self.nav_buttons = []
        for en_name, kh_name, idx in self.sub_menus:
            btn = QPushButton(en_name)
            btn.setToolTip(f"{en_name} ({kh_name})")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: #64748B;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 6px 14px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    color: #5648A6;
                    background-color: #EEEDFB;
                }
                QPushButton:checked {
                    color: #5648A6;
                    background-color: #EEEDFB;
                    font-weight: 700;
                    border-bottom: 2px solid #5648A6;
                }
            """)
            self.btn_group.addButton(btn, idx)
            sub_nav.addWidget(btn)
            self.nav_buttons.append(btn)
            btn.clicked.connect(lambda checked, i=idx: self.switch_sub_page(i))

        sub_nav.addStretch()

        # Quick Request button in header
        btn_quick_req = QPushButton("+ Request Leave")
        btn_quick_req.setStyleSheet("""
            background-color: #5648A6;
            color: #FFFFFF;
            font-weight: 700;
            padding: 6px 16px;
            border-radius: 6px;
            border: none;
        """)
        btn_quick_req.clicked.connect(self.request_leave)
        sub_nav.addWidget(btn_quick_req)

        main_layout.addWidget(sub_nav_frame)

        # 2. Stacked Pages for the 5 Sub-views
        self.stack = QStackedWidget()

        self.page_dashboard = self._build_dashboard_page()
        self.page_calendar = self._build_calendar_page()
        self.page_management = self._build_management_page()
        self.page_reporting = self._build_reporting_page()
        self.page_config = self._build_config_page()

        self.stack.addWidget(self.page_dashboard)   # 0
        self.stack.addWidget(self.page_calendar)    # 1
        self.stack.addWidget(self.page_management)  # 2
        self.stack.addWidget(self.page_reporting)   # 3
        self.stack.addWidget(self.page_config)      # 4

        main_layout.addWidget(self.stack)

        # Set default to Management or Configuration matching screenshot
        self.nav_buttons[4].setChecked(True)
        self.switch_sub_page(4)

    def switch_sub_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.refresh_calendar()
        elif index == 2:
            self.load_leave_requests()
        elif index == 3:
            self.load_leave_report()
        elif index == 4:
            self.load_leave_types()

    # --- SUB-PAGE 0: DASHBOARD ---
    def _build_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(14)

        # KPI Row
        kpi_h = QHBoxLayout()
        kpi_h.setSpacing(12)

        self.kpi_annual = StatCard("Annual Leave Taken", "4 Days", "🌴", "#584BA2")
        kpi_h.addWidget(self.kpi_annual)

        self.kpi_sick = StatCard("Sick Leave Taken", "2 Days", "🤒", "#514397")
        kpi_h.addWidget(self.kpi_sick)

        self.kpi_pending = StatCard("Pending Approvals", "2 Requests", "⏳", "#4A3D8B")
        kpi_h.addWidget(self.kpi_pending)

        self.kpi_today = StatCard("On Leave Today", "0 Staff", "👥", "#3E327A")
        kpi_h.addWidget(self.kpi_today)

        layout.addLayout(kpi_h)

        # Upcoming Leaves Table
        sec = QFrame()
        sec.setStyleSheet(f"background-color: #FFFFFF; border: 1px solid {BORDER}; border-radius: 12px; padding: 14px;")
        s_v = QVBoxLayout(sec)
        s_v.setSpacing(10)

        s_head = QHBoxLayout()
        t = QLabel("Upcoming & Active Leaves / ច្បាប់ឈប់សម្រាកខាងមុខ")
        t.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        s_head.addWidget(t)
        s_head.addStretch()
        s_v.addLayout(s_head)

        self.table_dash_leaves = QTableWidget()
        self.table_dash_leaves.setColumnCount(6)
        self.table_dash_leaves.setHorizontalHeaderLabels(["Employee", "Department", "Leave Type", "Start Date", "End Date", "Status"])
        self.table_dash_leaves.setShowGrid(True)
        self.table_dash_leaves.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_dash_leaves.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_dash_leaves.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_dash_leaves.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_dash_leaves.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_dash_leaves.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_dash_leaves.setColumnWidth(5, 120)
        self.table_dash_leaves.verticalHeader().setVisible(False)
        self.table_dash_leaves.verticalHeader().setDefaultSectionSize(48)
        self.table_dash_leaves.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_dash_leaves.setAlternatingRowColors(True)
        s_v.addWidget(self.table_dash_leaves)

        layout.addWidget(sec)
        return page

    def refresh_dashboard(self):
        reqs = database.get_leave_requests()
        pending_count = sum(1 for r in reqs if r["status"] == "Pending")
        self.kpi_pending.update_value(f"{pending_count} Requests")

        self.table_dash_leaves.setRowCount(len(reqs))
        for r, req in enumerate(reqs):
            self.table_dash_leaves.setItem(r, 0, QTableWidgetItem(f"{req['name']} ({req['khmer_name']})"))
            self.table_dash_leaves.setItem(r, 1, QTableWidgetItem(req["department"]))
            self.table_dash_leaves.setItem(r, 2, QTableWidgetItem(req["leave_type"]))
            self.table_dash_leaves.setItem(r, 3, QTableWidgetItem(req["start_date"]))
            self.table_dash_leaves.setItem(r, 4, QTableWidgetItem(req["end_date"]))

            badge = QLabel(req["status"])
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if req["status"] == "Approved":
                badge.setStyleSheet("background-color: #ECFDF5; color: #065F46; border-radius: 6px; font-weight: 700;")
            elif req["status"] == "Rejected":
                badge.setStyleSheet("background-color: #FEE2E2; color: #991B1B; border-radius: 6px; font-weight: 700;")
            else:
                badge.setStyleSheet("background-color: #FEF3C7; color: #92400E; border-radius: 6px; font-weight: 700;")
            self.table_dash_leaves.setCellWidget(r, 5, badge)

    # --- SUB-PAGE 1: CALENDAR ---
    def _build_calendar_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(14)

        # Left Calendar
        cal_frame = QFrame()
        cal_frame.setStyleSheet(f"background-color: #FFFFFF; border: 1px solid {BORDER}; border-radius: 12px; padding: 14px;")
        c_v = QVBoxLayout(cal_frame)
        c_v.setSpacing(10)

        c_title = QLabel("Leave Calendar / ប្រតិទិនច្បាប់សម្រាក")
        c_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        c_v.addWidget(c_title)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget {
                alternate-background-color: #F8FAFC;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 13px;
                color: #1E293B;
                selection-background-color: #5648A6;
                selection-color: white;
            }
        """)
        self.calendar.selectionChanged.connect(self.on_calendar_date_clicked)
        c_v.addWidget(self.calendar)

        layout.addWidget(cal_frame, stretch=3)

        # Right Date Detail Card
        side_frame = QFrame()
        side_frame.setStyleSheet(f"background-color: #FFFFFF; border: 1px solid {BORDER}; border-radius: 12px; padding: 14px;")
        s_v = QVBoxLayout(side_frame)
        s_v.setSpacing(10)

        self.lbl_selected_date = QLabel("Selected Date: " + QDate.currentDate().toString("yyyy-MM-dd"))
        self.lbl_selected_date.setStyleSheet("font-size: 14px; font-weight: 700; color: #5648A6;")
        s_v.addWidget(self.lbl_selected_date)

        s_v.addWidget(QLabel("Staff on leave on this date / បុគ្គលិកឈប់សម្រាកក្នុងថ្ងៃនេះ:"))

        self.list_date_leaves = QTableWidget()
        self.list_date_leaves.setColumnCount(3)
        self.list_date_leaves.setHorizontalHeaderLabels(["Employee", "Type", "Status"])
        self.list_date_leaves.setShowGrid(True)
        self.list_date_leaves.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.list_date_leaves.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.list_date_leaves.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.list_date_leaves.verticalHeader().setVisible(False)
        self.list_date_leaves.verticalHeader().setDefaultSectionSize(40)
        s_v.addWidget(self.list_date_leaves)

        # Daily Notes & Memos section
        note_head = QHBoxLayout()
        n_lbl = QLabel("Daily Notes & Memos / កំណត់សម្គាល់ប្រចាំថ្ងៃ:")
        n_lbl.setStyleSheet("font-weight: 700; color: #1E293B; margin-top: 6px;")
        note_head.addWidget(n_lbl)

        btn_add_note = QPushButton("✏️ សរសេរអក្សរ / Add Note")
        btn_add_note.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_note.setStyleSheet("background-color: #EEEDFB; color: #4338CA; font-weight: 700; padding: 4px 10px; border-radius: 6px; border: 1px solid #818CF8;")
        btn_add_note.clicked.connect(lambda: self.open_calendar_note_dialog())
        note_head.addWidget(btn_add_note)
        s_v.addLayout(note_head)

        self.list_date_notes = QTableWidget()
        self.list_date_notes.setColumnCount(3)
        self.list_date_notes.setHorizontalHeaderLabels(["Type", "Note Content", "Action"])
        self.list_date_notes.setShowGrid(True)
        self.list_date_notes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.list_date_notes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.list_date_notes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.list_date_notes.setColumnWidth(2, 80)
        self.list_date_notes.verticalHeader().setVisible(False)
        self.list_date_notes.verticalHeader().setDefaultSectionSize(40)
        s_v.addWidget(self.list_date_notes)

        layout.addWidget(side_frame, stretch=2)
        return page

    def refresh_calendar(self):
        self.on_calendar_date_clicked()

    def on_calendar_date_clicked(self):
        sel_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.lbl_selected_date.setText(f"Selected Date: {sel_date}")

        # 1. Leaves
        reqs = database.get_leave_requests()
        matching = []
        for r in reqs:
            if r["start_date"] <= sel_date <= r["end_date"]:
                matching.append(r)

        self.list_date_leaves.setRowCount(len(matching))
        for i, m in enumerate(matching):
            self.list_date_leaves.setItem(i, 0, QTableWidgetItem(f"{m['name']} ({m['khmer_name']})"))
            self.list_date_leaves.setItem(i, 1, QTableWidgetItem(m["leave_type"]))
            self.list_date_leaves.setItem(i, 2, QTableWidgetItem(m["status"]))

        # 2. Notes
        notes = database.get_calendar_notes(date=sel_date)
        self.list_date_notes.setRowCount(len(notes))
        for i, n in enumerate(notes):
            self.list_date_notes.setItem(i, 0, QTableWidgetItem(n.get("note_type", "Note")))
            it_title = QTableWidgetItem(n.get("title", ""))
            it_title.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            self.list_date_notes.setItem(i, 1, it_title)

            btn_box = QWidget()
            b_lay = QHBoxLayout(btn_box)
            b_lay.setContentsMargins(4, 2, 4, 2)
            btn_ed = QPushButton("✏️ Edit")
            btn_ed.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ed.setStyleSheet("background-color: #EEEDFB; color: #4338CA; font-weight: 700; border-radius: 4px; padding: 2px 6px;")
            btn_ed.clicked.connect(lambda checked, nd=n: self.open_calendar_note_dialog(nd))
            b_lay.addWidget(btn_ed)
            self.list_date_notes.setCellWidget(i, 2, btn_box)

    def open_calendar_note_dialog(self, note_data=None):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit, QDialogButtonBox
        sel_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        dlg = QDialog(self)
        dlg.setWindowTitle("សរសេរ/កែប្រែកំណត់សម្គាល់ប្រតិទិន - " + sel_date)
        dlg.resize(400, 260)
        dlg.setStyleSheet("background-color: #FFFFFF;")

        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)

        lbl = QLabel(f"<b>📅 កាលបរិច្ឆេទ: {sel_date}</b>")
        lbl.setStyleSheet("font-size: 13px; color: #1E293B;")
        lay.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(10)

        cb_type = QComboBox()
        cb_type.addItems(["Note (កំណត់ចំណាំ)", "Holiday (ថ្ងៃបុណ្យ/ឈប់)", "Meeting (ប្រជុំ)", "Notice (ការជូនដំណឹង)", "Event (កម្មវិធី)"])
        if note_data:
            cur_t = note_data.get("note_type", "Note")
            for idx in range(cb_type.count()):
                if cur_t in cb_type.itemText(idx):
                    cb_type.setCurrentIndex(idx)
                    break
        form.addRow("ប្រភេទ (Type):", cb_type)

        txt_content = QTextEdit()
        txt_content.setPlaceholderText("សរសេរអក្សរ ឬកំណត់សម្គាល់នៅទីនេះ...")
        txt_content.setFixedHeight(80)
        if note_data:
            txt_content.setPlainText(note_data.get("title", ""))
        form.addRow("ខ្លឹមសារ (Note):", txt_content)

        lay.addLayout(form)

        btn_box = QHBoxLayout()
        if note_data and note_data.get("id"):
            btn_del = QPushButton("🗑️ លុប (Delete)")
            btn_del.setStyleSheet("background-color: #FEE2E2; color: #DC2626; font-weight: 700; padding: 6px 12px; border-radius: 6px; border: 1px solid #FCA5A5;")
            def do_delete():
                if QMessageBox.question(dlg, "Confirm", "តើចង់លុបកំណត់សម្គាល់នេះ?") == QMessageBox.StandardButton.Yes:
                    database.delete_calendar_note(note_data["id"])
                    dlg.accept()
                    self.on_calendar_date_clicked()
            btn_del.clicked.connect(do_delete)
            btn_box.addWidget(btn_del)

        btn_box.addStretch()
        btn_cancel = QPushButton("បោះបង់")
        btn_cancel.clicked.connect(dlg.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("💾 រក្សាទុក")
        btn_save.setStyleSheet("background-color: #5648A6; color: white; font-weight: 700; padding: 6px 16px; border-radius: 6px;")
        def do_save():
            text = txt_content.toPlainText().strip()
            if not text:
                QMessageBox.warning(dlg, "Warning", "សូមបញ្ចូលខ្លឹមសារកំណត់សម្គាល់!")
                return
            raw_type = cb_type.currentText().split(" ")[0]
            nid = note_data["id"] if note_data else None
            database.save_calendar_note(date=sel_date, title=text, note_type=raw_type, note_id=nid)
            dlg.accept()
            self.on_calendar_date_clicked()
        btn_save.clicked.connect(do_save)
        btn_box.addWidget(btn_save)

        lay.addLayout(btn_box)
        dlg.exec()

    # --- SUB-PAGE 2: MANAGEMENT (REQUESTS & APPROVALS) ---
    def _build_management_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        r_head = QHBoxLayout()
        r_title = QLabel("Staff Leave Requests & Approvals / សំណើសុំច្បាប់ & ការអនុម័ត")
        r_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        r_head.addWidget(r_title)
        r_head.addStretch()

        r_head.addWidget(QLabel("Filter Status:"))
        self.combo_req_filter = QComboBox()
        self.combo_req_filter.setView(QListView())
        self.combo_req_filter.addItems(["All", "Pending", "Approved", "Rejected"])
        self.combo_req_filter.currentTextChanged.connect(self.load_leave_requests)
        r_head.addWidget(self.combo_req_filter)

        btn_new_req = QPushButton("+ Request Leave / ស្នើសុំច្បាប់")
        btn_new_req.setStyleSheet("background-color: #5648A6; color: white; padding: 7px 18px; border-radius: 6px; font-weight: 700;")
        btn_new_req.clicked.connect(self.request_leave)
        r_head.addWidget(btn_new_req)

        layout.addLayout(r_head)

        self.table_reqs = QTableWidget()
        self.table_reqs.setColumnCount(8)
        self.table_reqs.setHorizontalHeaderLabels([
            "Employee ID", "Employee", "Leave Type", "Start Date", "End Date", "Days", "Status", "Actions"
        ])
        self.table_reqs.setShowGrid(True)
        self.table_reqs.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_reqs.setColumnWidth(0, 110)
        self.table_reqs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_reqs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_reqs.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_reqs.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_reqs.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_reqs.setColumnWidth(5, 70)
        self.table_reqs.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table_reqs.setColumnWidth(6, 120)
        self.table_reqs.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table_reqs.setColumnWidth(7, 180)
        self.table_reqs.verticalHeader().setVisible(False)
        self.table_reqs.verticalHeader().setDefaultSectionSize(48)
        self.table_reqs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_reqs.setAlternatingRowColors(True)
        layout.addWidget(self.table_reqs)
        return page

    def load_leave_requests(self):
        filt = getattr(self, "combo_req_filter", None)
        status_val = filt.currentText() if filt else "All"

        reqs = database.get_leave_requests()
        if status_val != "All":
            reqs = [r for r in reqs if r["status"] == status_val]

        self.table_reqs.setRowCount(len(reqs))

        for r, req in enumerate(reqs):
            it_id = QTableWidgetItem(req["emp_code"])
            it_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_reqs.setItem(r, 0, it_id)

            it_name = QTableWidgetItem(f"{req['name']} ({req['khmer_name']})")
            self.table_reqs.setItem(r, 1, it_name)

            it_type = QTableWidgetItem(req["leave_type"])
            self.table_reqs.setItem(r, 2, it_type)

            it_start = QTableWidgetItem(req["start_date"])
            self.table_reqs.setItem(r, 3, it_start)

            it_end = QTableWidgetItem(req["end_date"])
            self.table_reqs.setItem(r, 4, it_end)

            it_days = QTableWidgetItem(f"{req['days']} d")
            it_days.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_reqs.setItem(r, 5, it_days)

            status = req["status"]
            badge_lbl = QLabel(status)
            badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if status == "Approved":
                badge_lbl.setStyleSheet("background-color: #ECFDF5; color: #065F46; border-radius: 8px; font-weight: 700; padding: 2px 8px;")
            elif status == "Rejected":
                badge_lbl.setStyleSheet("background-color: #FEE2E2; color: #991B1B; border-radius: 8px; font-weight: 700; padding: 2px 8px;")
            else:
                badge_lbl.setStyleSheet("background-color: #FEF3C7; color: #92400E; border-radius: 8px; font-weight: 700; padding: 2px 8px;")
            self.table_reqs.setCellWidget(r, 6, badge_lbl)

            act_w = QWidget()
            act_h = QHBoxLayout(act_w)
            act_h.setContentsMargins(2, 2, 2, 2)
            act_h.setSpacing(4)

            req_id = req["id"]
            if status == "Pending":
                btn_app = QPushButton("✓ Approve")
                btn_app.setStyleSheet("background-color: #10B981; color: white; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 700;")
                btn_app.clicked.connect(lambda checked, rid=req_id: self.update_status(rid, "Approved"))
                act_h.addWidget(btn_app)

                btn_rej = QPushButton("✕ Reject")
                btn_rej.setStyleSheet("background-color: #EF4444; color: white; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: 700;")
                btn_rej.clicked.connect(lambda checked, rid=req_id: self.update_status(rid, "Rejected"))
                act_h.addWidget(btn_rej)

            btn_del_req = QPushButton("🗑️")
            btn_del_req.setToolTip("លុបសំណើសុំច្បាប់នេះ (Delete)")
            btn_del_req.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 4px;
                    padding: 3px 6px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover { background-color: #DC2626; color: white; }
            """)
            btn_del_req.clicked.connect(lambda checked, rid=req_id: self.delete_leave_request(rid))
            act_h.addWidget(btn_del_req)

            self.table_reqs.setCellWidget(r, 7, act_w)

    # --- SUB-PAGE 3: REPORTING ---
    def _build_reporting_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        head = QHBoxLayout()
        t = QLabel("Staff Leave Balance Summary Report / របាយការណ៍សង្ខេបច្បាប់បុគ្គលិក")
        t.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        head.addWidget(t)
        head.addStretch()

        btn_exp = QPushButton("📤 Export Report CSV")
        btn_exp.setStyleSheet("background-color: #F1F5F9; color: #334155; padding: 7px 16px; border-radius: 6px; border: 1px solid #CBD5E1; font-weight: 600;")
        btn_exp.clicked.connect(self.export_report_csv)
        btn_exp.setVisible(False)
        head.addWidget(btn_exp)

        layout.addLayout(head)

        self.table_report = QTableWidget()
        self.table_report.setColumnCount(7)
        self.table_report.setHorizontalHeaderLabels([
            "Employee ID", "Employee", "Department", "Days Taken", "Remaining Balance", "Sick Days Taken", "Action"
        ])
        self.table_report.setShowGrid(True)
        self.table_report.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_report.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_report.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_report.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_report.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_report.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table_report.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table_report.setColumnWidth(6, 100)
        self.table_report.verticalHeader().setVisible(False)
        self.table_report.verticalHeader().setDefaultSectionSize(48)
        self.table_report.setAlternatingRowColors(True)
        layout.addWidget(self.table_report)
        return page

    def load_leave_report(self):
        balances = database.get_employee_leave_balances()
        self.table_report.setRowCount(len(balances))

        for r, b in enumerate(balances):
            self.table_report.setItem(r, 0, QTableWidgetItem(b["emp_code"]))
            self.table_report.setItem(r, 1, QTableWidgetItem(f"{b['name']} ({b['khmer_name']})"))
            self.table_report.setItem(r, 2, QTableWidgetItem(b["department"]))

            self.table_report.setItem(r, 3, QTableWidgetItem(f"{b['used']} Days"))

            it_bal = QTableWidgetItem(f"{b['balance']} Days")
            it_bal.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            if b['balance'] < 0:
                it_bal.setForeground(QColor("#DC2626"))
            else:
                it_bal.setForeground(QColor("#16A34A"))
            self.table_report.setItem(r, 4, it_bal)

            self.table_report.setItem(r, 5, QTableWidgetItem(f"{b['sick']} Days"))

            btn_box = QWidget()
            btn_box.setStyleSheet("background: transparent;")
            b_layout = QHBoxLayout(btn_box)
            b_layout.setContentsMargins(6, 4, 6, 4)
            b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_edit = QPushButton("✏️ Edit")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setFixedHeight(28)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #4338CA;
                    font-weight: 700;
                    font-size: 11.5px;
                    padding: 3px 10px;
                    border-radius: 6px;
                    border: 1.2px solid #818CF8;
                }
                QPushButton:hover {
                    background-color: #4338CA;
                    color: #FFFFFF;
                }
            """)
            btn_edit.clicked.connect(lambda checked, bd=b: self.open_edit_leave_balance_dialog(bd))
            b_layout.addWidget(btn_edit)
            self.table_report.setCellWidget(r, 6, btn_box)

    def open_edit_leave_balance_dialog(self, b_data):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Edit Leave Balance - {b_data['name']} ({b_data['khmer_name']})")
        dlg.resize(380, 240)
        dlg.setStyleSheet("background-color: #FFFFFF;")

        lay = QVBoxLayout(dlg)
        lay.setSpacing(14)

        title = QLabel(f"<b>{b_data['emp_code']} - {b_data['name']} ({b_data['khmer_name']})</b><br><span style='color:#64748B;'>{b_data['department']} • {b_data['job_position']}</span>")
        title.setStyleSheet("font-size: 13px; color: #1E293B;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        spin_ent = QDoubleSpinBox()
        spin_ent.setRange(0, 365)
        spin_ent.setValue(float(b_data["entitled"]))
        spin_ent.setSuffix(" ថ្ងៃ (Days)")
        form.addRow("សិទ្ធិច្បាប់ប្រចាំឆ្នាំ (Entitled):", spin_ent)

        spin_used = QDoubleSpinBox()
        spin_used.setRange(0, 365)
        spin_used.setValue(float(b_data["used"]))
        spin_used.setSuffix(" ថ្ងៃ (Days)")
        form.addRow("បានឈប់ (Days Taken):", spin_used)

        spin_sick = QDoubleSpinBox()
        spin_sick.setRange(0, 365)
        spin_sick.setValue(float(b_data["sick"]))
        spin_sick.setSuffix(" ថ្ងៃ (Days)")
        form.addRow("ច្បាប់ឈឺ (Sick Days):", spin_sick)

        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)

        if dlg.exec():
            database.save_employee_leave_balance(
                b_data["emp_id"],
                spin_ent.value(),
                spin_used.value(),
                spin_sick.value()
            )
            self.load_leave_report()

    def export_report_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Leave Report", "mercy_dental_leave_report.csv", "CSV Files (*.csv)")
        if not path:
            return
        balances = database.get_employee_leave_balances()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Employee ID", "Employee", "Department", "Days Taken", "Remaining Balance", "Sick Days Taken"])
            for b in balances:
                w.writerow([b["emp_code"], f"{b['name']} ({b['khmer_name']})", b["department"], b["used"], b["balance"], b["sick"]])
        QMessageBox.information(self, "Success", f"Saved leave report to:\n{path}")

    # --- SUB-PAGE 4: CONFIGURATION (LEAVE TYPES MATCHING IMG_7446) ---
    def _build_config_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        t_action_h = QHBoxLayout()
        t_title = QLabel("Leave Types / ប្រភេទច្បាប់ឈប់សម្រាក")
        t_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        t_action_h.addWidget(t_title)

        btn_create = QPushButton("+ Create")
        btn_create.setStyleSheet("background-color: #5648A6; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600;")
        btn_create.clicked.connect(self.create_leave_type)
        t_action_h.addWidget(btn_create)

        btn_import = QPushButton("📥 Import")
        btn_import.setStyleSheet("background-color: #F1F5F9; color: #334155; padding: 6px 12px; border-radius: 6px; border: 1px solid #CBD5E1;")
        btn_import.clicked.connect(lambda: QMessageBox.information(self, "Import", "Leave types batch importer ready."))
        t_action_h.addWidget(btn_import)

        btn_export = QPushButton("📤 Export")
        btn_export.setStyleSheet("background-color: #F1F5F9; color: #334155; padding: 6px 12px; border-radius: 6px; border: 1px solid #CBD5E1;")
        btn_export.clicked.connect(self.export_types_csv)
        t_action_h.addWidget(btn_export)

        t_action_h.addStretch()
        layout.addLayout(t_action_h)

        self.table_types = QTableWidget()
        self.table_types.setColumnCount(6)
        self.table_types.setHorizontalHeaderLabels(["Select", "Display Name", "Code", "Mode", "Validation", "Actions / សកម្មភាព"])
        self.table_types.setShowGrid(True)
        self.table_types.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_types.setColumnWidth(0, 60)
        self.table_types.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_types.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_types.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_types.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_types.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_types.setColumnWidth(5, 140)
        self.table_types.verticalHeader().setVisible(False)
        self.table_types.verticalHeader().setDefaultSectionSize(48)
        self.table_types.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_types.setAlternatingRowColors(True)
        self.table_types.cellDoubleClicked.connect(self.on_table_types_double_clicked)
        layout.addWidget(self.table_types)
        return page

    def load_leave_types(self):
        types = database.get_leave_types()
        self._loaded_types = types
        self.table_types.setRowCount(len(types))
        for r, t in enumerate(types):
            chk_it = QTableWidgetItem()
            chk_it.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_it.setCheckState(Qt.CheckState.Unchecked)
            chk_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_types.setItem(r, 0, chk_it)

            name_str = f"{t['name']}  ({t['name_kh']})"
            it_name = QTableWidgetItem(name_str)
            self.table_types.setItem(r, 1, it_name)

            it_code = QTableWidgetItem(t["code"])
            it_code.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_types.setItem(r, 2, it_code)

            it_mode = QTableWidgetItem(t["mode"])
            self.table_types.setItem(r, 3, it_mode)

            it_val = QTableWidgetItem(t["validation"])
            self.table_types.setItem(r, 4, it_val)

            # Action buttons: Edit and Delete
            w_act = QWidget()
            h_act = QHBoxLayout(w_act)
            h_act.setContentsMargins(4, 4, 4, 4)
            h_act.setSpacing(6)
            h_act.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("✏️ កែ")
            btn_edit.setToolTip("កែប្រែប្រភេទច្បាប់ (Edit)")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #5648A6;
                    border: 1px solid #D6D3F7;
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #5648A6;
                    color: #FFFFFF;
                }
            """)
            btn_edit.clicked.connect(lambda ch, item_data=t: self.edit_leave_type(item_data))
            h_act.addWidget(btn_edit)

            btn_del = QPushButton("🗑️")
            btn_del.setToolTip("លុបប្រភេទច្បាប់ (Delete)")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    border: 1px solid #FECACA;
                    border-radius: 6px;
                    padding: 4px 6px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                    color: #FFFFFF;
                }
            """)
            btn_del.clicked.connect(lambda ch, tid=t['id'], tname=t['name']: self.delete_leave_type(tid, tname))
            h_act.addWidget(btn_del)

            self.table_types.setCellWidget(r, 5, w_act)

    def on_table_types_double_clicked(self, row, col):
        if hasattr(self, '_loaded_types') and 0 <= row < len(self._loaded_types):
            self.edit_leave_type(self._loaded_types[row])

    def create_leave_type(self):
        from components.leave_type_dialog import LeaveTypeDialog
        dlg = LeaveTypeDialog(parent=self)
        if dlg.exec():
            self.load_leave_types()

    def edit_leave_type(self, leave_type_data):
        from components.leave_type_dialog import LeaveTypeDialog
        dlg = LeaveTypeDialog(leave_type_data=leave_type_data, parent=self)
        if dlg.exec():
            self.load_leave_types()

    def delete_leave_type(self, type_id, name):
        reply = QMessageBox.question(
            self,
            "បញ្ជាក់ការលុប (Confirm Delete)",
            f"តើអ្នកពិតជាចង់លុបប្រភេទច្បាប់ '{name}' នេះមែនទេ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_leave_type(type_id)
            self.load_leave_types()
            QMessageBox.information(self, "ជោគជ័យ", "បានលុបប្រភេទច្បាប់ដោយជោគជ័យ!")

    def export_types_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Leave Types", "mercy_dental_leave_types.csv", "CSV Files (*.csv)")
        if not path:
            return
        types = database.get_leave_types()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Display Name", "Khmer Name", "Code", "Mode", "Validation"])
            for t in types:
                w.writerow([t["name"], t["name_kh"], t["code"], t["mode"], t["validation"]])
        QMessageBox.information(self, "Success", f"Saved leave types to:\n{path}")

    # --- COMMON ACTIONS ---
    def request_leave(self):
        dlg = LeaveRequestDialog(parent=self)
        if dlg.exec():
            self.load_leave_requests()
            if hasattr(self, 'refresh_dashboard'):
                self.refresh_dashboard()

    def update_status(self, req_id, status):
        database.update_leave_status(req_id, status)
        self.load_leave_requests()
        if hasattr(self, 'refresh_dashboard'):
            self.refresh_dashboard()

    def delete_leave_request(self, req_id):
        reply = QMessageBox.question(
            self, "បញ្ជាក់ការលុប (Confirm Delete)",
            "តើលោកអ្នកពិតជាចង់លុបសំណើសុំច្បាប់នេះមែនទេ?\nAre you sure you want to delete this leave request?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_leave_request(req_id)
            QMessageBox.information(self, "ជោគជ័យ", "បានលុបសំណើសុំច្បាប់ដោយជោគជ័យ!")
            self.load_leave_requests()
            if hasattr(self, 'refresh_dashboard'):
                self.refresh_dashboard()

