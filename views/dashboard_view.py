"""
Main HR & Attendance Dashboard View
Faithful recreation of Click HR screenshot IMG_7444.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

import database
from components.stat_card import StatCard
from components.pie_chart import DepartmentPieChartWidget
from components.today_attendance_card import TodayAttendanceCard
from theme import tr, PRIMARY, SURFACE, BORDER

class DashboardView(QWidget):
    open_employee = pyqtSignal(int)
    open_attendance = pyqtSignal()
    request_leave_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(10)

        # 1. Section Header
        head_row = QHBoxLayout()
        self.title_lbl = QLabel("Dashboard")
        self.title_lbl.setStyleSheet("font-size: 17px; font-weight: 800; color: #1E293B;")
        head_row.addWidget(self.title_lbl)
        head_row.addStretch()
        self.layout.addLayout(head_row)

        # 2. Middle Section: Today's Live Attendance & Leave Card (Full Width)
        self.today_att_card = TodayAttendanceCard()
        self.today_att_card.open_attendance_clicked.connect(self.open_attendance.emit)
        self.today_att_card.open_leave_dialog_clicked.connect(self.request_leave_requested.emit)
        self.layout.addWidget(self.today_att_card)
        self.layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        # Refresh Live Attendance & Leave Card
        if hasattr(self, 'today_att_card'):
            self.today_att_card.refresh_data()

    def show_depts_popup(self):
        from components.dashboard_popups import DepartmentPopup
        dlg = DepartmentPopup(self, open_emp_callback=self.open_employee.emit)
        dlg.exec()

    def show_pos_popup(self):
        from components.dashboard_popups import JobPositionPopup
        dlg = JobPositionPopup(self, open_emp_callback=self.open_employee.emit)
        dlg.exec()

    def show_emps_popup(self):
        from components.dashboard_popups import TotalEmployeesPopup
        dlg = TotalEmployeesPopup(self, open_emp_callback=self.open_employee.emit)
        dlg.exec()

    def show_gender_popup(self):
        from components.dashboard_popups import GenderPopup
        dlg = GenderPopup(self, open_emp_callback=self.open_employee.emit)
        dlg.exec()

    def show_turnover_popup(self):
        from components.dashboard_popups import TurnoverPopup
        dlg = TurnoverPopup(self)
        dlg.exec()

    def show_bday_popup(self):
        from components.dashboard_popups import BirthdaysPopup
        dlg = BirthdaysPopup(self, open_emp_callback=self.open_employee.emit)
        dlg.exec()

    def show_single_dept_popup(self, dept_name):
        from components.dashboard_popups import SingleDepartmentPopup
        dlg = SingleDepartmentPopup(dept_name, self, open_emp_callback=self.open_employee.emit)
        dlg.exec()
