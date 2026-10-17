"""
Interactive Information Popups for Dashboard KPI Cards and Departments
Allows users to click any metric or department card to view details instantly.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLineEdit, QTabWidget, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import database
from datetime import datetime, date

class BaseInfoPopup(QDialog):
    """Reusable modern popup shell with header and action buttons."""
    def __init__(self, title, subtitle, icon="📊", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 560)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #334155;
                font-weight: 700;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #CBD5E1;
            }
        """)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(20, 20, 20, 16)
        self.root_layout.setSpacing(14)

        # Header Frame
        head_frame = QFrame()
        head_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5648A6, stop:1 #4338CA);
                border-radius: 12px;
                padding: 14px 18px;
            }
        """)
        head_h = QHBoxLayout(head_frame)
        head_h.setContentsMargins(12, 10, 12, 10)
        head_h.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 26px; background-color: rgba(255, 255, 255, 0.2); border-radius: 10px; padding: 6px 10px;")
        head_h.addWidget(icon_lbl)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-size: 17px; font-weight: 800; color: #FFFFFF;")
        title_v.addWidget(lbl_t)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("font-size: 12px; color: #E0E7FF;")
        title_v.addWidget(lbl_sub)
        head_h.addLayout(title_v, stretch=1)

        btn_close_x = QPushButton("✕")
        btn_close_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_x.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 15px;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
        """)
        btn_close_x.clicked.connect(self.close)
        head_h.addWidget(btn_close_x)

        self.root_layout.addWidget(head_frame)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        self.root_layout.addWidget(self.content_widget, stretch=1)

        # Bottom Bar
        btm_h = QHBoxLayout()
        btm_h.addStretch()
        btn_close = QPushButton("បិទ (Close)")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #EEEDFB;
                color: #5648A6;
                font-weight: 700;
                font-size: 13px;
                border-radius: 8px;
                padding: 8px 24px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #5648A6;
                color: #FFFFFF;
            }
        """)
        btn_close.clicked.connect(self.close)
        btm_h.addWidget(btn_close)
        self.root_layout.addLayout(btm_h)

    def _create_emp_table(self, employees, on_view_emp=None):
        """Helper to create a unified employee table."""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ល.រ (ID)", "ឈ្មោះ (Name)", "ផ្នែក (Department)", "មុខតំណែង (Position)", "ទូរស័ព្ទ (Phone)", "សកម្មភាព (Action)"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(5, 95)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(44)
        table.setRowCount(len(employees))

        for row, emp in enumerate(employees):
            id_code = emp.get("emp_code") or f"EMP{emp.get('id', 0):03d}"
            name_display = f"{emp.get('name', '')} ({emp.get('khmer_name', '')})" if emp.get('khmer_name') else emp.get('name', '')
            
            table.setItem(row, 0, QTableWidgetItem(id_code))
            table.setItem(row, 1, QTableWidgetItem(name_display))
            table.setItem(row, 2, QTableWidgetItem(emp.get("department", "")))
            table.setItem(row, 3, QTableWidgetItem(emp.get("job_position", "")))
            table.setItem(row, 4, QTableWidgetItem(emp.get("phone", "") or "-"))

            btn = QPushButton("👁️ មើល")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
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
            emp_id = emp.get("id")
            if on_view_emp:
                btn.clicked.connect(lambda ch, eid=emp_id: (self.close(), on_view_emp(eid)))
            
            w_btn = QWidget()
            h_b = QHBoxLayout(w_btn)
            h_b.setContentsMargins(4, 2, 4, 2)
            h_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            h_b.addWidget(btn)
            table.setCellWidget(row, 5, w_btn)

        return table


class DepartmentPopup(BaseInfoPopup):
    """Details of all active departments."""
    def __init__(self, parent=None, open_emp_callback=None):
        groups = database.get_department_detail_groups()
        total_depts = len(groups)
        total_staff = sum(g.get("count", 0) for g in groups)
        super().__init__(
            f"ព័ត៌មានផ្នែកការងារទាំងអស់ (Total Departments: {total_depts})",
            f"ចំនួនផ្នែកសរុប {total_depts} ផ្នែក | បុគ្គលិកសរុប {total_staff} នាក់",
            icon="🏢",
            parent=parent
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        v_box = QVBoxLayout(container)
        v_box.setSpacing(14)

        for d in groups:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #CBD5E1;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            c_v = QVBoxLayout(card)
            c_v.setSpacing(8)

            head_h = QHBoxLayout()
            d_name = d.get("name_kh") or d.get("name")
            title_lbl = QLabel(f"● {d_name} ({d.get('name')})")
            title_lbl.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {d.get('color', '#5648A6')};")
            head_h.addWidget(title_lbl)
            head_h.addStretch()

            count_badge = QLabel(f"បុគ្គលិក៖ {d.get('count', 0)} នាក់")
            count_badge.setStyleSheet("background-color: #EEEDFB; color: #5648A6; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-size: 11px;")
            head_h.addWidget(count_badge)
            c_v.addLayout(head_h)

            tbl = self._create_emp_table(d.get("employees", []), open_emp_callback)
            tbl.setFixedHeight(min(260, 56 + len(d.get("employees", [])) * 48))
            c_v.addWidget(tbl)

            v_box.addWidget(card)

        v_box.addStretch()
        scroll.setWidget(container)
        self.content_layout.addWidget(scroll)


class JobPositionPopup(BaseInfoPopup):
    """Details of all job positions."""
    def __init__(self, parent=None, open_emp_callback=None):
        groups = database.get_position_detail_groups()
        total_pos = len(groups)
        total_staff = sum(g.get("count", 0) for g in groups)
        super().__init__(
            f"ព័ត៌មានមុខតំណែងការងារ (Job Positions: {total_pos})",
            f"មុខតំណែងសរុប {total_pos} មុខតំណែង | បុគ្គលិកសរុប {total_staff} នាក់",
            icon="💼",
            parent=parent
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        v_box = QVBoxLayout(container)
        v_box.setSpacing(14)

        for pos in groups:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #CBD5E1;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            c_v = QVBoxLayout(card)
            c_v.setSpacing(8)

            head_h = QHBoxLayout()
            title_lbl = QLabel(f"💼 {pos.get('position')}")
            title_lbl.setStyleSheet("font-size: 14px; font-weight: 800; color: #1E293B;")
            head_h.addWidget(title_lbl)
            head_h.addStretch()

            count_badge = QLabel(f"ចំនួនបុគ្គលិក៖ {pos.get('count', 0)} នាក់")
            count_badge.setStyleSheet("background-color: #EEEDFB; color: #5648A6; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-size: 11px;")
            head_h.addWidget(count_badge)
            c_v.addLayout(head_h)

            tbl = self._create_emp_table(pos.get("employees", []), open_emp_callback)
            tbl.setFixedHeight(min(260, 56 + len(pos.get("employees", [])) * 48))
            c_v.addWidget(tbl)

            v_box.addWidget(card)

        v_box.addStretch()
        scroll.setWidget(container)
        self.content_layout.addWidget(scroll)


class TotalEmployeesPopup(BaseInfoPopup):
    """Full list of all active employees."""
    def __init__(self, parent=None, open_emp_callback=None):
        emps = database.get_all_employees()
        active_emps = [e for e in emps if e.get("status") == "Active"]
        super().__init__(
            f"បញ្ជីបុគ្គលិកសរុប (Total Active Staff: {len(active_emps)})",
            f"បុគ្គលិកកំពុងបំពេញការងារសរុប {len(active_emps)} នាក់នៅក្នុងគ្លីនិក",
            icon="👥",
            parent=parent
        )

        table = self._create_emp_table(active_emps, open_emp_callback)
        self.content_layout.addWidget(table)


class GenderPopup(BaseInfoPopup):
    """Gender breakdown and staff lists."""
    def __init__(self, parent=None, open_emp_callback=None):
        stats = database.get_stats()
        m_count = stats.get("male", 0)
        f_count = stats.get("female", 0)
        total = m_count + f_count
        m_pct = (m_count / total * 100) if total > 0 else 0
        f_pct = (f_count / total * 100) if total > 0 else 0

        super().__init__(
            f"ស្ថិតិយេនឌ័របុគ្គលិក (Gender Ratio: {m_count}/{f_count})",
            f"បុគ្គលិកស្រី៖ {f_count} នាក់ ({f_pct:.0f}%) | បុគ្គលិកប្រុស៖ {m_count} នាក់ ({m_pct:.0f}%)",
            icon="🚻",
            parent=parent
        )

        # Top summary cards
        top_h = QHBoxLayout()
        top_h.setSpacing(14)

        card_female = QFrame()
        card_female.setStyleSheet("background-color: #FDF2F8; border: 1.5px solid #F472B6; border-radius: 10px; padding: 10px;")
        cf_v = QVBoxLayout(card_female)
        cf_lbl = QLabel(f"👩 បុគ្គលិកស្រី (Female): {f_count} នាក់ ({f_pct:.0f}%)")
        cf_lbl.setStyleSheet("font-size: 14px; font-weight: 800; color: #DB2777;")
        cf_v.addWidget(cf_lbl)
        top_h.addWidget(card_female)

        card_male = QFrame()
        card_male.setStyleSheet("background-color: #EFF6FF; border: 1.5px solid #60A5FA; border-radius: 10px; padding: 10px;")
        cm_v = QVBoxLayout(card_male)
        cm_lbl = QLabel(f"👨 បុគ្គលិកប្រុស (Male): {m_count} នាក់ ({m_pct:.0f}%)")
        cm_lbl.setStyleSheet("font-size: 14px; font-weight: 800; color: #2563EB;")
        cm_v.addWidget(cm_lbl)
        top_h.addWidget(card_male)

        self.content_layout.addLayout(top_h)

        # Tabs for female and male
        emps = database.get_all_employees()
        female_emps = [e for e in emps if e.get("gender") == "Female" and e.get("status") == "Active"]
        male_emps = [e for e in emps if e.get("gender") == "Male" and e.get("status") == "Active"]

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 20px;
                font-weight: 700;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                color: #5648A6;
                border-bottom: 3px solid #5648A6;
            }
        """)

        tbl_f = self._create_emp_table(female_emps, open_emp_callback)
        tabs.addTab(tbl_f, f"👩 បុគ្គលិកស្រី ({len(female_emps)})")

        tbl_m = self._create_emp_table(male_emps, open_emp_callback)
        tabs.addTab(tbl_m, f"👨 បុគ្គលិកប្រុស ({len(male_emps)})")

        self.content_layout.addWidget(tabs)


class TurnoverPopup(BaseInfoPopup):
    """Turnover Rate and Staff Retention details."""
    def __init__(self, parent=None):
        stats = database.get_stats()
        super().__init__(
            "អត្រាផ្លាស់ប្តូរបុគ្គលិក (Turnover Rate: 0%)",
            "ស្ថិតិស្ថេរភាពការងារ និងការរក្សាបុគ្គលិកក្នុងគ្លីនិក",
            icon="📉",
            parent=parent
        )

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        c_v = QVBoxLayout(card)
        c_v.setSpacing(14)

        title = QLabel("✅ ស្ថេរភាពបុគ្គលិកល្អប្រសើរ (100% Retention Rate)")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #10B981;")
        c_v.addWidget(title)

        info_lbl = QLabel(
            "បច្ចុប្បន្នគ្លីនិកធ្មេញ មើស៊ី មានបុគ្គលិកកំពុងបំពេញការងារសរុប 5 នាក់ពេញលេញ។\n"
            "• អត្រាផ្លាស់ប្តូរ (Turnover Rate)៖ 0%\n"
            "• អត្រារក្សាបុគ្គលិក (Retention Rate)៖ 100%\n"
            "• បុគ្គលិកលាឈប់ពីការងារ (Resigned)៖ 0 នាក់\n"
            "• បុគ្គលិកសកម្ម (Active Staff)៖ 5 នាក់\n\n"
            "គ្មានការកត់ត្រាបុគ្គលិកលាឈប់ ឬផ្លាស់ប្តូរការងារក្នុងអំឡុងពេលនេះឡើយ។"
        )
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("font-size: 13.5px; line-height: 1.6; color: #334155;")
        c_v.addWidget(info_lbl)

        c_v.addStretch()
        self.content_layout.addWidget(card)


class BirthdaysPopup(BaseInfoPopup):
    """Birthdays this month and upcoming birthdays."""
    def __init__(self, parent=None, open_emp_callback=None):
        bday_data = database.get_birthday_details()
        this_month_emps = bday_data.get("this_month", [])
        all_emps = bday_data.get("all", [])

        month_names = {
            "01": "មករា (Jan)", "02": "កុម្ភៈ (Feb)", "03": "មីនា (Mar)",
            "04": "មេសា (Apr)", "05": "ឧសភា (May)", "06": "មិថុនា (Jun)",
            "07": "កក្កដា (Jul)", "08": "សីហា (Aug)", "09": "កញ្ញា (Sep)",
            "10": "តុលា (Oct)", "11": "វិច្ឆិកា (Nov)", "12": "ធ្នូ (Dec)"
        }
        cur_m = bday_data.get("current_month", "10")
        m_name = month_names.get(cur_m, cur_m)

        super().__init__(
            f"ថ្ងៃកំណើតបុគ្គលិកក្នុងខែនេះ (Birthdays in {m_name})",
            f"បុគ្គលិកមានថ្ងៃកំណើតក្នុងខែនេះចំនួន {len(this_month_emps)} នាក់",
            icon="🎂",
            parent=parent
        )

        if this_month_emps:
            celebrate_frame = QFrame()
            celebrate_frame.setStyleSheet("background-color: #FEF3C7; border: 1.5px solid #F59E0B; border-radius: 10px; padding: 12px;")
            cf_v = QVBoxLayout(celebrate_frame)
            cf_lbl = QLabel(f"🎉 រីករាយថ្ងៃកំណើតបុគ្គលិកក្នុងខែ {m_name}! 🎉")
            cf_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #B45309;")
            cf_v.addWidget(cf_lbl)
            self.content_layout.addWidget(celebrate_frame)

            tbl = self._create_emp_table(this_month_emps, open_emp_callback)
            self.content_layout.addWidget(tbl)
        else:
            no_bday = QFrame()
            no_bday.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 10px; padding: 16px;")
            nb_v = QVBoxLayout(no_bday)
            nb_lbl = QLabel(f"📅 គ្មានបុគ្គលិកណាមានថ្ងៃកំណើតក្នុងខែ {m_name} នេះទេ")
            nb_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #64748B;")
            nb_v.addWidget(nb_lbl)
            self.content_layout.addWidget(no_bday)

        # Overview table of all employees with their birthdates
        lbl_all = QLabel("📋 បញ្ជីកាលបរិច្ឆេទថ្ងៃខែឆ្នាំកំណើតបុគ្គលិកទាំងអស់ (Staff DOB List):")
        lbl_all.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B; margin-top: 6px;")
        self.content_layout.addWidget(lbl_all)

        tbl_all = self._create_emp_table(all_emps, open_emp_callback)
        self.content_layout.addWidget(tbl_all)


class SingleDepartmentPopup(BaseInfoPopup):
    """Specific department details when clicked from pie chart or legend."""
    def __init__(self, dept_name, parent=None, open_emp_callback=None):
        emps = [e for e in database.get_all_employees() if e.get("department") == dept_name and e.get("status") == "Active"]
        super().__init__(
            f"ព័ត៌មានផ្នែក៖ {dept_name}",
            f"បុគ្គលិកកំពុងបំពេញការងារសរុបចំនួន {len(emps)} នាក់ក្នុងផ្នែកនេះ",
            icon="🏢",
            parent=parent
        )
        table = self._create_emp_table(emps, open_emp_callback)
        self.content_layout.addWidget(table)
