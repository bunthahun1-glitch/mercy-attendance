"""
Employees Management View matching Click HR screenshot IMG_7445.
Features Create, Search, Department Filter, CSV Export, and Profile views.
"""

import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QMessageBox, QFileDialog, QListView
)
from PyQt6.QtCore import Qt, pyqtSignal

import database
from components.employee_dialog import EmployeeDialog
from components.badge_dialog import BadgeDialog
from theme import tr, PRIMARY, BORDER, setup_styled_combobox

class EmployeesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Breadcrumb path matching IMG_7445
        self.breadcrumb_lbl = QLabel("Dashboard Action  /  Total Employees")
        self.breadcrumb_lbl.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.breadcrumb_lbl)

        # 2. Action Toolbar matching IMG_7445 (+ Create, Import, Export)
        tool_row = QHBoxLayout()
        tool_row.setSpacing(10)

        self.btn_create = QPushButton("+ Create")
        self.btn_create.setStyleSheet("""
            background-color: #5648A6;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 13px;
            padding: 8px 18px;
            border-radius: 8px;
        """)
        self.btn_create.clicked.connect(self.create_employee)
        tool_row.addWidget(self.btn_create)

        tool_row.addStretch()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search employee by name, ID, phone...")
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self.load_employees)
        tool_row.addWidget(self.search_input)

        # Department Filter
        self.combo_dept = QComboBox()
        setup_styled_combobox(self.combo_dept)
        self.combo_dept.setFixedWidth(180)
        self.refresh_department_filter()
        self.combo_dept.currentTextChanged.connect(self.load_employees)
        tool_row.addWidget(self.combo_dept)

        layout.addLayout(tool_row)

        # 3. Employee Table matching IMG_7445
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Select", "Employee ID", "Employee", "Work Phone", "Company", "Department", "Job Position", "Actions"
        ])
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 55)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(3, 110)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(4, 130)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(5, 125)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(6, 150)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 235)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)
        layout.addWidget(self.table)

        self.load_employees()

    def load_employees(self):
        search = self.search_input.text().strip()
        dept = self.combo_dept.currentText()
        dept_filter = "All" if dept == "All Departments" else dept

        emps = database.get_all_employees(search, dept_filter)
        self.table.setRowCount(len(emps))

        for row, emp in enumerate(emps):
            # Checkbox item (Native checkable item - perfectly aligned and clear)
            chk_it = QTableWidgetItem()
            chk_it.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_it.setCheckState(Qt.CheckState.Unchecked)
            chk_it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, chk_it)

            # Emp ID
            it_id = QTableWidgetItem(emp["emp_code"])
            it_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, it_id)

            # Employee Name
            name_str = f"{emp['name']} ({emp['khmer_name']})"
            it_name = QTableWidgetItem(name_str)
            it_name.setData(Qt.ItemDataRole.UserRole, emp["id"])
            self.table.setItem(row, 2, it_name)

            # Phone
            it_phone = QTableWidgetItem(emp["phone"] or "")
            self.table.setItem(row, 3, it_phone)

            # Company (Mercy Dental Care)
            it_comp = QTableWidgetItem("Mercy Dental Care")
            self.table.setItem(row, 4, it_comp)

            # Department
            it_dept = QTableWidgetItem(emp["department"])
            self.table.setItem(row, 5, it_dept)

            # Job Position
            it_pos = QTableWidgetItem(emp["job_position"])
            self.table.setItem(row, 6, it_pos)

            # Action Buttons widget
            act_widget = QWidget()
            act_widget.setStyleSheet("background: transparent;")
            act_layout = QHBoxLayout(act_widget)
            act_layout.setContentsMargins(6, 4, 6, 4)
            act_layout.setSpacing(6)

            eid = emp["id"]

            btn_view = QPushButton("👁️ View")
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #EEEDFB;
                    color: #4338CA;
                    font-weight: 700;
                    font-size: 11.5px;
                    padding: 5px 10px;
                    border-radius: 6px;
                    border: 1.5px solid #818CF8;
                }
                QPushButton:hover {
                    background-color: #4338CA;
                    color: #FFFFFF;
                }
            """)
            btn_view.clicked.connect(lambda checked, i=eid: self.open_employee_profile(i))
            act_layout.addWidget(btn_view)

            btn_badge = QPushButton("🪪 Badge")
            btn_badge.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_badge.setToolTip("Print/View Badge")
            btn_badge.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #1E293B;
                    font-weight: 700;
                    font-size: 11.5px;
                    padding: 5px 10px;
                    border-radius: 6px;
                    border: 1.5px solid #94A3B8;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                }
            """)
            btn_badge.clicked.connect(lambda checked, e=emp: BadgeDialog(e, self).exec())
            act_layout.addWidget(btn_badge)

            btn_del = QPushButton("✕")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setToolTip("Delete Staff")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #FEE2E2;
                    color: #DC2626;
                    font-weight: 700;
                    font-size: 12px;
                    padding: 5px 8px;
                    border-radius: 6px;
                    border: 1.5px solid #F87171;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                    color: #FFFFFF;
                }
            """)
            btn_del.clicked.connect(lambda checked, i=eid, n=emp['name']: self.delete_employee(i, n))
            act_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 7, act_widget)

    def on_row_double_clicked(self, item):
        row = item.row()
        name_item = self.table.item(row, 2)
        if name_item:
            emp_id = name_item.data(Qt.ItemDataRole.UserRole)
            self.open_employee_profile(emp_id)

    def refresh_department_filter(self):
        curr = self.combo_dept.currentText() if hasattr(self, 'combo_dept') else "All Departments"
        self.combo_dept.blockSignals(True)
        self.combo_dept.clear()
        self.combo_dept.addItem("All Departments")
        for d in database.get_all_departments():
            self.combo_dept.addItem(d)
        idx = self.combo_dept.findText(curr)
        if idx >= 0:
            self.combo_dept.setCurrentIndex(idx)
        else:
            self.combo_dept.setCurrentIndex(0)
        self.combo_dept.blockSignals(False)

    def create_employee(self):
        dlg = EmployeeDialog(emp_id=None, parent=self)
        if dlg.exec():
            self.refresh_department_filter()
            self.load_employees()

    def open_employee_profile(self, emp_id):
        dlg = EmployeeDialog(emp_id=emp_id, parent=self)
        if dlg.exec():
            self.refresh_department_filter()
            self.load_employees()

    def delete_employee(self, emp_id, name):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to remove staff member '{name}' and all associated records?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_employee(emp_id)
            self.refresh_department_filter()
            self.load_employees()

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Employees", "mercy_dental_employees.csv", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        emps = database.get_all_employees()
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Employee ID", "English Name", "Khmer Name", "Gender", "Phone",
                "Email", "Department", "Job Position", "Join Date", "Base Salary ($)"
            ])
            for e in emps:
                writer.writerow([
                    e["emp_code"], e["name"], e["khmer_name"], e["gender"], e["phone"],
                    e["email"], e["department"], e["job_position"], e["join_date"], e["base_salary"]
                ])

        QMessageBox.information(self, "Export Successful", f"Saved employee directory to:\n{file_path}")
