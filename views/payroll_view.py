"""
Payroll & Payslip Management View matching Click HR screenshots IMG_7448 & IMG_7450.
Features interactive sub-navigation:
1. Payrolls (Monthly payroll processing & payslips list)
2. Salary (Base salary structures & allowances)
3. Compliance (NSSF & Tax compliance rules)
4. Reporting (Monthly clinic payroll analytics & export)
5. Configuration (Overtime rates, shift allowances)
"""

import csv
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QGridLayout, QStackedWidget, QFrame,
    QButtonGroup, QFileDialog, QAbstractItemView, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

import database
from components.payslip_dialog import PayslipDialog
from theme import tr, PRIMARY, SUCCESS, BORDER

class PayrollView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Top Sub-navigation matching IMG_7448
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

        sub_title = QLabel("Payroll / បៀវត្ស")
        sub_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #1E293B; margin-right: 12px;")
        sub_nav.addWidget(sub_title)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.menus = [
            ("Payrolls", 0),
            ("Salary", 1),
            ("Compliance", 2),
            ("Reporting", 3),
            ("Configuration", 4)
        ]

        self.nav_btns = []
        for en, idx in self.menus:
            btn = QPushButton(en)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: #64748B;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 6px 16px;
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
            self.nav_btns.append(btn)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))

        sub_nav.addStretch()
        layout.addWidget(sub_nav_frame)

        # 2. Stacked Pages
        self.stack = QStackedWidget()

        self.page_payrolls = self._build_payrolls_page()
        self.page_salary = self._build_salary_page()
        self.page_compliance = self._build_compliance_page()
        self.page_reporting = self._build_reporting_page()
        self.page_config = self._build_config_page()

        self.stack.addWidget(self.page_payrolls)
        self.stack.addWidget(self.page_salary)
        self.stack.addWidget(self.page_compliance)
        self.stack.addWidget(self.page_reporting)
        self.stack.addWidget(self.page_config)

        layout.addWidget(self.stack)

        self.nav_btns[0].setChecked(True)
        self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == index)

        if index == 0:
            self.load_payroll()
        elif index == 1:
            self.load_salary_page()
        elif index == 3:
            self.load_reporting_page()
        elif index == 4:
            self.load_config_page()

    def _build_payrolls_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        tool_row = QHBoxLayout()
        title_sec = QLabel("Payrolls / ប័ណ្ណបើកប្រាក់")
        title_sec.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        tool_row.addWidget(title_sec)

        tool_row.addStretch()

        tool_row.addWidget(QLabel("Month:"))
        self.spin_month = QSpinBox()
        self.spin_month.setRange(1, 12)
        self.spin_month.setValue(date.today().month)
        tool_row.addWidget(self.spin_month)

        tool_row.addWidget(QLabel("Year:"))
        self.spin_year = QSpinBox()
        self.spin_year.setRange(2023, 2030)
        self.spin_year.setValue(date.today().year)
        tool_row.addWidget(self.spin_year)

        btn_generate = QPushButton("⚡ Generate Monthly Payroll")
        btn_generate.setStyleSheet("background-color: #10B981; color: white; padding: 7px 16px; border-radius: 6px; font-weight: 700;")
        btn_generate.clicked.connect(self.generate_payroll)
        tool_row.addWidget(btn_generate)

        layout.addLayout(tool_row)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Select", "កូដ (Code)", "Employee", "ប្រាក់ខែគោល", "លើកទឹកចិត្ត", "Target 14k+", "Over time", "Over day off", "ប្រាក់បើកសុទ្ធ", "Action"
        ])
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(9, 140)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        return page

    def _build_salary_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        t = QLabel("Staff Salary Structure & Base Wages / ប្រាក់ខែគោលបុគ្គលិក")
        t.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        layout.addWidget(t)

        self.table_salary = QTableWidget()
        self.table_salary.setColumnCount(6)
        self.table_salary.setHorizontalHeaderLabels(["Employee ID", "Employee", "Department", "Job Position", "Base Salary (USD)", "Action"])
        self.table_salary.setShowGrid(True)
        self.table_salary.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_salary.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_salary.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_salary.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_salary.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_salary.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_salary.setColumnWidth(5, 150)
        self.table_salary.verticalHeader().setVisible(False)
        self.table_salary.verticalHeader().setDefaultSectionSize(48)
        self.table_salary.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_salary.setAlternatingRowColors(True)
        self.table_salary.itemDoubleClicked.connect(self.on_salary_double_clicked)
        layout.addWidget(self.table_salary)
        return page

    def load_salary_page(self):
        emps = database.get_all_employees()
        self.table_salary.setRowCount(len(emps))
        for r, e in enumerate(emps):
            eid = e["id"]
            it_code = QTableWidgetItem(e["emp_code"])
            it_code.setData(Qt.ItemDataRole.UserRole, eid)
            it_code.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_salary.setItem(r, 0, it_code)

            it_emp = QTableWidgetItem(f"{e['name']} ({e['khmer_name']})")
            it_emp.setData(Qt.ItemDataRole.UserRole, eid)
            self.table_salary.setItem(r, 1, it_emp)

            self.table_salary.setItem(r, 2, QTableWidgetItem(e["department"]))
            self.table_salary.setItem(r, 3, QTableWidgetItem(e["job_position"]))

            sal_it = QTableWidgetItem(f"${e['base_salary']:,.2f}")
            sal_it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font = sal_it.font()
            font.setBold(True)
            sal_it.setFont(font)
            self.table_salary.setItem(r, 4, sal_it)

            btn_box = QWidget()
            btn_box.setStyleSheet("background: transparent;")
            b_layout = QHBoxLayout(btn_box)
            b_layout.setContentsMargins(6, 4, 6, 4)
            b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_edit = QPushButton("✏️ Edit Salary")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setFixedHeight(32)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #4338CA;
                    font-weight: 700;
                    font-size: 11.5px;
                    padding: 4px 12px;
                    border-radius: 6px;
                    border: 1.5px solid #818CF8;
                }
                QPushButton:hover {
                    background-color: #4338CA;
                    color: #FFFFFF;
                }
            """)
            btn_edit.clicked.connect(lambda checked, i=eid: self.open_salary_dialog(i))
            b_layout.addWidget(btn_edit)
            self.table_salary.setCellWidget(r, 5, btn_box)

    def on_salary_double_clicked(self, item):
        row = item.row()
        item0 = self.table_salary.item(row, 0)
        if item0:
            emp_id = item0.data(Qt.ItemDataRole.UserRole)
            self.open_salary_dialog(emp_id)

    def open_salary_dialog(self, emp_id):
        from components.employee_dialog import EmployeeDialog
        dlg = EmployeeDialog(emp_id=emp_id, parent=self)
        dlg.tabs.setCurrentIndex(2) # Focus Contract & Salary tab!
        if dlg.exec():
            self.load_salary_page()
            self.load_payroll()

    def _build_compliance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(14)

        t = QLabel("Labor & Tax Compliance (អនុលោមភាពច្បាប់ការងារ និងពន្ធដារ)")
        t.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        layout.addWidget(t)

        card = QFrame()
        card.setStyleSheet(f"background-color: #FFFFFF; border: 1px solid {BORDER}; border-radius: 12px; padding: 18px;")
        c_v = QVBoxLayout(card)
        c_v.setSpacing(12)
        c_v.addWidget(QLabel("<b>1. NSSF (ប.ស.ស) Health & Occupational Risk:</b> Registered & Active ✓"))
        c_v.addWidget(QLabel("<b>2. Cambodia Tax on Salary (ពន្ធលើប្រាក់បៀវត្ស):</b> Automated 0% - 20% progressive brackets ✓"))
        c_v.addWidget(QLabel("<b>3. Seniority Payment (ប្រាក់បំណាច់អតីតភាពការងារ):</b> Calculated bi-annually (June & December) ✓"))
        c_v.addWidget(QLabel("<b>4. Overtime Multpliers:</b> 1.5x Regular OT (17:00 - 22:00), 2.0x Sundays & Public Holidays ✓"))
        c_v.addStretch()
        layout.addWidget(card)
        return page

    def _create_metric_card(self, title_en, title_kh, val_label, accent_color):
        card = QFrame()
        card.setObjectName("metricCard")
        card.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-top: 3.5px solid {accent_color};
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame#metricCard QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(2)

        t_en = QLabel(title_en)
        t_en.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700; border: none; background: transparent;")
        v.addWidget(t_en)

        t_kh = QLabel(title_kh)
        t_kh.setStyleSheet("color: #64748B; font-size: 11px; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif; border: none; background: transparent;")
        v.addWidget(t_kh)

        val_label.setStyleSheet("color: #1E293B; font-size: 18px; font-weight: 800; margin-top: 6px; border: none; background: transparent;")
        v.addWidget(val_label)
        return card

    def _build_reporting_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        head = QHBoxLayout()
        t = QLabel("Monthly Payroll Expense Analytics / របាយការណ៍ចំណាយបៀវត្ស")
        t.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        head.addWidget(t)
        head.addStretch()

        self.btn_refresh_rep = QPushButton("🔄 Refresh (ផ្ទុកឡើងវិញ)")
        self.btn_refresh_rep.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh_rep.setStyleSheet("background-color: #F1F5F9; color: #334155; padding: 6px 14px; border-radius: 6px; border: 1px solid #CBD5E1; font-weight: 600; font-size: 11px;")
        self.btn_refresh_rep.clicked.connect(lambda: self.load_reporting_page(filter_dates=True))
        head.addWidget(self.btn_refresh_rep)

        btn_exp = QPushButton("📤 Export Payroll CSV")
        btn_exp.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exp.setStyleSheet("background-color: #5648A6; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 600; font-size: 11px;")
        btn_exp.clicked.connect(self.export_payroll_csv)
        btn_exp.setVisible(False)
        head.addWidget(btn_exp)
        layout.addLayout(head)

        # 4 Dynamic Metric Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)

        self.lbl_rep_base = QLabel("$0.00 USD")
        self.lbl_rep_allowance = QLabel("$0.00 USD")
        self.lbl_rep_tax = QLabel("$0.00 USD")
        self.lbl_rep_net = QLabel("$0.00 USD")

        stats_layout.addWidget(self._create_metric_card("Total Monthly Base Payroll", "ប្រាក់បៀវត្សគោលសរុប", self.lbl_rep_base, "#4338CA"))
        stats_layout.addWidget(self._create_metric_card("Total Monthly Allowances", "ប្រាក់ឧបត្ថម្ភសរុប", self.lbl_rep_allowance, "#0284C7"))
        stats_layout.addWidget(self._create_metric_card("Estimated Withholding Tax", "ពន្ធលើប្រាក់បៀវត្ស", self.lbl_rep_tax, "#D97706"))
        stats_layout.addWidget(self._create_metric_card("Net Monthly Disbursed", "ប្រាក់បើកជាក់ស្ដែងសរុប", self.lbl_rep_net, "#059669"))
        layout.addLayout(stats_layout)

        # Content Container (Filter Bar + Summary Header + Table + Empty Box)
        self.rep_content_frame = QFrame()
        self.rep_content_frame.setObjectName("repContentFrame")
        self.rep_content_frame.setStyleSheet(f"""
            QFrame#repContentFrame {{
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        rep_layout = QVBoxLayout(self.rep_content_frame)
        rep_layout.setContentsMargins(12, 12, 12, 12)
        rep_layout.setSpacing(10)

        # Filter & Summary Header Bar (Date filter placed in front of summary list)
        filter_bar = QFrame()
        filter_bar.setObjectName("repFilterBar")
        filter_bar.setStyleSheet("""
            QFrame#repFilterBar {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(8, 6, 8, 6)
        filter_layout.setSpacing(8)

        lbl_date_title = QLabel("📅 កំណត់កាលបរិច្ឆេទ ៖")
        lbl_date_title.setStyleSheet("font-weight: 700; color: #1E293B; font-size: 13px; border: none; background: transparent;")
        filter_layout.addWidget(lbl_date_title)

        lbl_from = QLabel("ពីថ្ងៃ (From):")
        lbl_from.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        filter_layout.addWidget(lbl_from)

        today = date.today()
        # Default start of current month
        init_start = QDate(today.year, today.month, 1)
        # Default end of current month
        if today.month == 12:
            last_day = 31
        else:
            last_day = (date(today.year, today.month + 1, 1) - timedelta(days=1)).day
        init_end = QDate(today.year, today.month, last_day)

        date_style = """
            QDateEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: 'Segoe UI', 'Kantumruy Pro', sans-serif;
                font-size: 12px;
                font-weight: 700;
                color: #1E293B;
                min-width: 110px;
            }
            QDateEdit:focus {
                border: 1.5px solid #5648A6;
                background-color: #FAF5FF;
            }
        """

        self.rep_date_from = QDateEdit()
        self.rep_date_from.setCalendarPopup(True)
        self.rep_date_from.setDisplayFormat("yyyy-MM-dd")
        self.rep_date_from.setDate(init_start)
        self.rep_date_from.setStyleSheet(date_style)
        filter_layout.addWidget(self.rep_date_from)

        lbl_to = QLabel("ដល់ថ្ងៃ (To):")
        lbl_to.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        filter_layout.addWidget(lbl_to)

        self.rep_date_to = QDateEdit()
        self.rep_date_to.setCalendarPopup(True)
        self.rep_date_to.setDisplayFormat("yyyy-MM-dd")
        self.rep_date_to.setDate(init_end)
        self.rep_date_to.setStyleSheet(date_style)
        filter_layout.addWidget(self.rep_date_to)

        self.btn_filter_rep = QPushButton("🔍 ចម្រាញ់ (Filter)")
        self.btn_filter_rep.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter_rep.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: white;
                font-weight: 700;
                font-size: 11.5px;
                padding: 5px 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        self.btn_filter_rep.clicked.connect(lambda: self.load_reporting_page(filter_dates=True))
        filter_layout.addWidget(self.btn_filter_rep)

        self.btn_all_rep = QPushButton("🔄 ទាំងអស់ (All)")
        self.btn_all_rep.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_all_rep.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #475569;
                font-weight: 600;
                font-size: 11.5px;
                padding: 5px 12px;
                border-radius: 6px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        self.btn_all_rep.clicked.connect(self.show_all_reporting)
        filter_layout.addWidget(self.btn_all_rep)

        filter_layout.addStretch()

        # Summary title on the right
        self.lbl_rep_title = QLabel("📋 បញ្ជីសង្ខេបបៀវត្សបុគ្គលិកសរុប (0 នាក់)")
        self.lbl_rep_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; border: none; background: transparent;")
        filter_layout.addWidget(self.lbl_rep_title)

        rep_layout.addWidget(filter_bar)

        # Summary Table
        self.table_rep = QTableWidget()
        self.table_rep.setColumnCount(6)
        self.table_rep.setHorizontalHeaderLabels([
            "កូដ (Code)", "បុគ្គលិក (Employee)", "ផ្នែក (Department)", "កាលបរិច្ឆេទ (Period)", "ប្រាក់បើកសុទ្ធ (Net Salary)", "សកម្មភាព (Action)"
        ])
        self.table_rep.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_rep.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_rep.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_rep.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_rep.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_rep.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_rep.setColumnWidth(5, 120)
        self.table_rep.verticalHeader().setVisible(False)
        self.table_rep.verticalHeader().setDefaultSectionSize(40)
        self.table_rep.setAlternatingRowColors(True)
        self.table_rep.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_rep.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 11.5px;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #334155;
                font-weight: 700;
                font-size: 11.5px;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
            }
        """)
        rep_layout.addWidget(self.table_rep)

        # Empty notice box (when no records match)
        self.empty_rep_box = QFrame()
        self.empty_rep_box.setObjectName("emptyRepBox")
        self.empty_rep_box.setStyleSheet("""
            QFrame#emptyRepBox {
                background-color: #F8FAFC;
                border: 1.5px dashed #CBD5E1;
                border-radius: 8px;
                padding: 24px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        e_v = QVBoxLayout(self.empty_rep_box)
        e_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_v.setSpacing(6)

        icon_lbl = QLabel("📊")
        icon_lbl.setStyleSheet("font-size: 32px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_v.addWidget(icon_lbl)

        self.lbl_empty_msg = QLabel("មិនទាន់មានទិន្នន័យរបាយការណ៍បៀវត្សក្នុងចន្លោះកាលបរិច្ឆេទនេះទេ")
        self.lbl_empty_msg.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B;")
        self.lbl_empty_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_v.addWidget(self.lbl_empty_msg)

        self.lbl_empty_sub = QLabel("សូមជ្រើសរើសចន្លោះកាលបរិច្ឆេទផ្សេង ឬចុច 'បង្ហាញទាំងអស់ (All)' ដើម្បីមើលទិន្នន័យ។")
        self.lbl_empty_sub.setStyleSheet("font-size: 12px; color: #64748B;")
        self.lbl_empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e_v.addWidget(self.lbl_empty_sub)

        rep_layout.addWidget(self.empty_rep_box)
        self.empty_rep_box.setVisible(False)

        layout.addWidget(self.rep_content_frame, 1)

        self.current_rep_records = []
        return page

    def show_all_reporting(self):
        records = database.get_payroll_records()
        if records:
            # find min date_from and max date_to
            dates_from = [r.get("date_from") for r in records if r.get("date_from")]
            dates_to = [r.get("date_to") for r in records if r.get("date_to")]
            if dates_from:
                min_d = min(dates_from)
                parts = [int(p) for p in min_d.split("-")]
                self.rep_date_from.setDate(QDate(parts[0], parts[1], parts[2]))
            if dates_to:
                max_d = max(dates_to)
                parts = [int(p) for p in max_d.split("-")]
                self.rep_date_to.setDate(QDate(parts[0], parts[1], parts[2]))
        self.load_reporting_page(filter_dates=False)

    def load_reporting_page(self, filter_dates=True):
        all_records = database.get_payroll_records()

        if filter_dates and all_records:
            d_from_str = self.rep_date_from.date().toString("yyyy-MM-dd")
            d_to_str = self.rep_date_to.date().toString("yyyy-MM-dd")
            # Filter where payroll period overlaps with selected range
            filtered = []
            for r in all_records:
                rf = r.get("date_from") or ""
                rt = r.get("date_to") or ""
                if not rf or not rt:
                    filtered.append(r)
                elif rt >= d_from_str and rf <= d_to_str:
                    filtered.append(r)
            records = filtered
        else:
            records = all_records

        self.current_rep_records = records

        if not records:
            self.lbl_rep_base.setText("$0.00 USD")
            self.lbl_rep_allowance.setText("$0.00 USD")
            self.lbl_rep_tax.setText("$0.00 USD")
            self.lbl_rep_net.setText("$0.00 USD")
            self.lbl_rep_title.setText("📋 បញ្ជីសង្ខេបបៀវត្សបុគ្គលិកសរុប (0 នាក់)")

            self.table_rep.setVisible(False)
            self.empty_rep_box.setVisible(True)
            if not all_records:
                self.lbl_empty_msg.setText("មិនទាន់មានទិន្នន័យរបាយការណ៍បៀវត្សនៅឡើយទេ (No Payroll Records Yet)")
                self.lbl_empty_sub.setText("សូមចូលទៅកាន់ 'Payrolls' ដើម្បីបង្កើតប័ណ្ណបើកប្រាក់ (Generate Monthly Payroll) ជាមុនសិន។")
            else:
                self.lbl_empty_msg.setText("មិនមានទិន្នន័យបៀវត្សក្នុងចន្លោះកាលបរិច្ឆេទនេះទេ (No Records in Range)")
                self.lbl_empty_sub.setText("សូមចុច '🔄 ទាំងអស់ (All)' ឬជ្រើសរើសចន្លោះកាលបរិច្ឆេទផ្សេងទៀត។")
        else:
            total_base = sum(float(r.get("base_salary", 0.0) or 0.0) for r in records)
            total_allow = sum(float(r.get("allowance", 0.0) or 0.0) for r in records)
            total_tax = sum(float(r.get("tax_deduction", 0.0) or 0.0) for r in records)
            total_net = sum(float(r.get("net_salary", 0.0) or 0.0) for r in records)

            self.lbl_rep_base.setText(f"${total_base:,.2f} USD")
            self.lbl_rep_allowance.setText(f"${total_allow:,.2f} USD")
            self.lbl_rep_tax.setText(f"${total_tax:,.2f} USD")
            self.lbl_rep_net.setText(f"${total_net:,.2f} USD")

            self.lbl_rep_title.setText(f"📋 បញ្ជីសង្ខេបបៀវត្សបុគ្គលិកសរុប ({len(records)} នាក់)")

            self.empty_rep_box.setVisible(False)
            self.table_rep.setVisible(True)
            self.table_rep.setRowCount(len(records))

            for r_idx, r_data in enumerate(records):
                # Col 0: Emp Code
                it_slip = QTableWidgetItem(r_data.get("emp_code", ""))
                it_slip.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_rep.setItem(r_idx, 0, it_slip)

                # Col 1: Employee
                emp_name = f"{r_data.get('name', '')}"
                if r_data.get("khmer_name"):
                    emp_name = f"{r_data.get('khmer_name')} ({r_data.get('name')})"
                it_name = QTableWidgetItem(emp_name)
                font_name = it_name.font()
                font_name.setBold(True)
                it_name.setFont(font_name)
                self.table_rep.setItem(r_idx, 1, it_name)

                # Col 2: Department
                it_dept = QTableWidgetItem(r_data.get("department", ""))
                it_dept.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_rep.setItem(r_idx, 2, it_dept)

                # Col 3: Period
                period_str = f"{r_data.get('date_from', '')} - {r_data.get('date_to', '')}"
                it_period = QTableWidgetItem(period_str)
                it_period.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_rep.setItem(r_idx, 3, it_period)

                # Col 4: Net Salary
                net_val = float(r_data.get("net_salary", 0.0) or 0.0)
                it_net = QTableWidgetItem(f"${net_val:,.2f}")
                it_net.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                font_net = it_net.font()
                font_net.setBold(True)
                it_net.setFont(font_net)
                it_net.setForeground(QColor("#5648A6"))
                self.table_rep.setItem(r_idx, 4, it_net)

                # Col 5: Action (Payslip button)
                btn_box = QWidget()
                btn_box.setStyleSheet("background: transparent;")
                b_lay = QHBoxLayout(btn_box)
                b_lay.setContentsMargins(4, 2, 4, 2)
                b_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

                btn_view = QPushButton("📄 Payslip")
                btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_view.setFixedHeight(28)
                btn_view.setStyleSheet("""
                    QPushButton {
                        background-color: #EEEDFB;
                        color: #5648A6;
                        font-weight: 700;
                        font-size: 11px;
                        padding: 2px 10px;
                        border-radius: 5px;
                        border: 1px solid #D6D3F7;
                    }
                    QPushButton:hover {
                        background-color: #5648A6;
                        color: #FFFFFF;
                    }
                """)
                rec_id = r_data.get("id")
                btn_view.clicked.connect(lambda checked, pid=rec_id: self.open_payslip(pid))
                b_lay.addWidget(btn_view)
                self.table_rep.setCellWidget(r_idx, 5, btn_box)

    def export_payroll_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Payroll", "mercy_dental_payroll_report.csv", "CSV Files (*.csv)")
        if not path:
            return
        records = getattr(self, "current_rep_records", None) or database.get_payroll_records()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Slip No", "Employee", "Department", "Period", "Base Salary", "Gross", "Net"])
            for r in records:
                w.writerow([r.get("payslip_no"), r.get("name"), r.get("department"), f"{r.get('date_from')} - {r.get('date_to')}", r.get("base_salary"), r.get("gross_salary"), r.get("net_salary")])
        QMessageBox.information(self, "Success", f"Saved payroll report ({len(records)} records) to:\n{path}")

    def _build_config_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(14)

        top_h = QHBoxLayout()
        t = QLabel("Payroll Configuration & Rates / កំណត់អត្រាបៀវត្ស និងគោលការណ៍គណនា")
        t.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        top_h.addWidget(t)
        top_h.addStretch()

        self.btn_save_config = QPushButton("💾 រក្សាទុកការកំណត់ (Save Configuration)")
        self.btn_save_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_config.setStyleSheet("background-color: #5648A6; color: white; padding: 8px 22px; border-radius: 6px; font-weight: 700; font-size: 13px; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;")
        self.btn_save_config.clicked.connect(self.save_config_page)
        top_h.addWidget(self.btn_save_config)
        layout.addLayout(top_h)

        card = QFrame()
        card.setObjectName("configCard")
        card.setStyleSheet(f"""
            QFrame#configCard {{
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame#configCard QLabel {{
                border: none;
                background: transparent;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                font-size: 13.5px;
                color: #334155;
            }}
            QSpinBox, QDoubleSpinBox, QLineEdit {{
                min-height: 34px;
                padding: 2px 10px;
                font-family: 'Segoe UI', 'Kantumruy Pro', sans-serif;
                font-size: 13px;
                font-weight: 700;
                border: 1.5px solid #CBD5E1;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #1E293B;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
                border: 1.5px solid #5648A6;
                background-color: #FAF5FF;
            }}
        """)
        grid = QGridLayout(card)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(14)

        # 1. Standard Working Days per Month
        lbl_days = QLabel("<b>• ចំនួនថ្ងៃធ្វើការក្នុង១ខែ (Standard Working Days / Month):</b>")
        self.cfg_work_days = QSpinBox()
        self.cfg_work_days.setRange(1, 31)
        self.cfg_work_days.setSuffix(" ថ្ងៃ (Days)")
        grid.addWidget(lbl_days, 0, 0)
        grid.addWidget(self.cfg_work_days, 0, 1)

        # 2. Daily Working Hours
        lbl_hrs = QLabel("<b>• ម៉ោងធ្វើការក្នុង១ថ្ងៃ (Daily Working Hours):</b>")
        self.cfg_work_hours = QSpinBox()
        self.cfg_work_hours.setRange(1, 24)
        self.cfg_work_hours.setSuffix(" ម៉ោង (Hours)")
        grid.addWidget(lbl_hrs, 1, 0)
        grid.addWidget(self.cfg_work_hours, 1, 1)

        # 3. Default Monthly Incentive
        lbl_inc = QLabel("<b>• ប្រាក់លើកទឹកចិត្តស្តង់ដារ (Default Incentive / Meal Allowance):</b>")
        self.cfg_incentive = QDoubleSpinBox()
        self.cfg_incentive.setRange(0, 10000)
        self.cfg_incentive.setDecimals(2)
        self.cfg_incentive.setPrefix("$ ")
        grid.addWidget(lbl_inc, 2, 0)
        grid.addWidget(self.cfg_incentive, 2, 1)

        # 4. Target Income Threshold
        lbl_tgt_inc = QLabel("<b>• គោលដៅចំណូលគ្លីនិក (Target Revenue Threshold):</b>")
        self.cfg_target_income = QDoubleSpinBox()
        self.cfg_target_income.setRange(0, 100000)
        self.cfg_target_income.setDecimals(2)
        self.cfg_target_income.setPrefix("$ ")
        grid.addWidget(lbl_tgt_inc, 3, 0)
        grid.addWidget(self.cfg_target_income, 3, 1)

        # 5. Target Bonus Amount
        lbl_tgt_bon = QLabel("<b>• ប្រាក់រង្វាន់សម្រេចគោលដៅ (Target 14k+ Bonus):</b>")
        self.cfg_target_bonus = QDoubleSpinBox()
        self.cfg_target_bonus.setRange(0, 10000)
        self.cfg_target_bonus.setDecimals(2)
        self.cfg_target_bonus.setPrefix("$ ")
        grid.addWidget(lbl_tgt_bon, 4, 0)
        grid.addWidget(self.cfg_target_bonus, 4, 1)

        # 6. Overtime Hourly Rate
        lbl_ot = QLabel("<b>• អត្រាប្រាក់ថែមម៉ោង (OT Hourly Rate / hr):</b>")
        self.cfg_ot_rate = QDoubleSpinBox()
        self.cfg_ot_rate.setRange(0, 500)
        self.cfg_ot_rate.setDecimals(2)
        self.cfg_ot_rate.setPrefix("$ ")
        grid.addWidget(lbl_ot, 5, 0)
        grid.addWidget(self.cfg_ot_rate, 5, 1)

        # 7. Payment Currency
        lbl_cur = QLabel("<b>• រូបិយប័ណ្ណទូទាត់ (Payment Currency):</b>")
        self.cfg_currency = QLineEdit("USD ($)")
        self.cfg_currency.setReadOnly(True)
        grid.addWidget(lbl_cur, 6, 0)
        grid.addWidget(self.cfg_currency, 6, 1)

        layout.addWidget(card)
        layout.addStretch()

        self.load_config_page()
        return page

    def load_config_page(self):
        self.cfg_work_days.setValue(int(database.get_setting("payroll_working_days", "26") or 26))
        self.cfg_work_hours.setValue(int(database.get_setting("payroll_work_hours", "8") or 8))
        self.cfg_incentive.setValue(float(database.get_setting("payroll_default_incentive", "50.0") or 50.0))
        self.cfg_target_income.setValue(float(database.get_setting("payroll_target_income", "14000.0") or 14000.0))
        self.cfg_target_bonus.setValue(float(database.get_setting("payroll_target_bonus", "50.0") or 50.0))
        self.cfg_ot_rate.setValue(float(database.get_setting("payroll_ot_rate", "1.5") or 1.5))

    def save_config_page(self):
        database.set_setting("payroll_working_days", self.cfg_work_days.value())
        database.set_setting("payroll_work_hours", self.cfg_work_hours.value())
        database.set_setting("payroll_default_incentive", self.cfg_incentive.value())
        database.set_setting("payroll_target_income", self.cfg_target_income.value())
        database.set_setting("payroll_target_bonus", self.cfg_target_bonus.value())
        database.set_setting("payroll_ot_rate", self.cfg_ot_rate.value())
        QMessageBox.information(self, "ជោគជ័យ (Saved)", "✅ បានរក្សាទុកការកំណត់អត្រាបៀវត្សដោយជោគជ័យ!")

    def load_payroll(self):
        records = database.get_payroll_records()
        self.table.setRowCount(len(records))

        for r, rec in enumerate(records):
            chk_it = QTableWidgetItem()
            chk_it.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_it.setCheckState(Qt.CheckState.Unchecked)
            chk_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 0, chk_it)

            it_code = QTableWidgetItem(rec.get("emp_code", ""))
            it_code.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 1, it_code)

            emp_name = f"{rec['name']} ({rec['khmer_name']})"
            it_emp = QTableWidgetItem(emp_name)
            self.table.setItem(r, 2, it_emp)

            # 1. Base Salary (ប្រាក់ខែគោល)
            it_base = QTableWidgetItem(f"${float(rec.get('base_salary', 0) or 0):,.2f}")
            it_base.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 3, it_base)

            # 2. Incentive (ប្រាក់លើកទឹកចិត្ត)
            inc_val = rec.get("incentive")
            if inc_val is None:
                inc_val = rec.get("allowance", 45.0)
            it_inc = QTableWidgetItem(f"${float(inc_val or 0):,.2f}")
            it_inc.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 4, it_inc)

            # 3. Target 14k+
            it_target = QTableWidgetItem(f"${float(rec.get('target_bonus', 0) or 0):,.2f}")
            it_target.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 5, it_target)

            # 4. Over time
            it_ot = QTableWidgetItem(f"${float(rec.get('ot_pay', 0) or 0):,.2f}")
            it_ot.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 6, it_ot)

            # 5. Over day off almost 1 day
            day_off_val = float(rec.get("over_day_off_deduction", 0) or 0)
            it_off = QTableWidgetItem(f"-${day_off_val:,.2f}" if day_off_val > 0 else "$0.00")
            it_off.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if day_off_val > 0:
                it_off.setForeground(Qt.GlobalColor.red)
            self.table.setItem(r, 7, it_off)

            # Net Salary (ប្រាក់បើកសុទ្ធ)
            it_net = QTableWidgetItem(f"${float(rec.get('net_salary', 0) or 0):,.2f}")
            it_net.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font = it_net.font()
            font.setBold(True)
            it_net.setFont(font)
            it_net.setForeground(Qt.GlobalColor.darkMagenta)
            self.table.setItem(r, 8, it_net)

            # Open Payslip button in clean container
            btn_container = QWidget()
            btn_container.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(6, 4, 6, 4)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_slip = QPushButton("📄 Payslip")
            btn_slip.setFixedHeight(30)
            btn_slip.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_slip.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #4338CA;
                    font-weight: 700;
                    font-size: 11.5px;
                    padding: 4px 10px;
                    border-radius: 6px;
                    border: 1px solid #818CF8;
                }
                QPushButton:hover {
                    background-color: #4338CA;
                    color: #FFFFFF;
                }
            """)
            rec_id = rec["id"]
            btn_slip.clicked.connect(lambda checked, pid=rec_id: self.open_payslip(pid))
            btn_layout.addWidget(btn_slip)
            self.table.setCellWidget(r, 9, btn_container)

    def generate_payroll(self):
        m = self.spin_month.value()
        y = self.spin_year.value()
        count = database.generate_monthly_payroll(m, y)
        if count > 0:
            QMessageBox.information(self, "ជោគជ័យ (Success)", f"បានបង្កើត និងធ្វើបច្ចុប្បន្នភាពប័ណ្ណបើកប្រាក់ចំនួន {count} នាក់សម្រាប់ខែ {m}/{y}!\nSuccessfully generated/synced {count} employee payslips for {m}/{y}!")
        else:
            QMessageBox.information(self, "ដំណឹង (Notice)", f"ប័ណ្ណបើកប្រាក់សម្រាប់ខែ {m}/{y} ត្រូវបានធ្វើបច្ចុប្បន្នភាពរួចរាល់ទាំងអស់ហើយ។\nPayroll for {m}/{y} is already up to date.")
        self.load_payroll()

    def open_payslip(self, pid):
        slip = database.get_payroll_by_id(pid)
        if slip:
            dlg = PayslipDialog(slip, parent=self)
            dlg.exec()
