"""
Interactive Mobile / Kiosk Attendance Card Widget
Faithful recreation of Click HR mobile kiosk interface from IMG_7453 & IMG_7454.
Features live Check In / Check Out, counters, and quick actions for Mercy Dental Care.
"""

import os
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox, QComboBox, QListView
)
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import database
from theme import tr, PRIMARY, DANGER, WARNING, SUCCESS, setup_styled_combobox

class KioskWidget(QFrame):
    attendance_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kioskFrame")
        self.setStyleSheet("""
            QFrame#kioskFrame {
                background-color: #52449F;
                border-radius: 24px;
                border: 2px solid #6354B8;
            }
        """)
        self.setFixedWidth(420)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # 1. Top Header: User Profile & Greeting
        top_header = QHBoxLayout()
        top_header.setContentsMargins(0, 0, 0, 0)

        # Avatar
        avatar_lbl = QLabel("👤")
        avatar_lbl.setFixedSize(44, 44)
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_lbl.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.25);
            border-radius: 22px;
            font-size: 22px;
        """)
        top_header.addWidget(avatar_lbl)

        # Name and Greeting
        greet_v = QVBoxLayout()
        greet_v.setSpacing(1)
        self.greet_lbl = QLabel("Good Morning!")
        self.greet_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px; font-weight: 500;")
        self.user_lbl = QLabel("Administrator")
        self.user_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        self.sub_profile = QLabel("Mercy Dental Care")
        self.sub_profile.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 11px;")
        greet_v.addWidget(self.greet_lbl)
        greet_v.addWidget(self.user_lbl)
        greet_v.addWidget(self.sub_profile)
        top_header.addLayout(greet_v)

        top_header.addStretch()

        # Bell notification icon with badge
        bell_btn = QPushButton("🔔 25")
        bell_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #FFFFFF;
                border: none;
                border-radius: 14px;
                padding: 6px 10px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        top_header.addWidget(bell_btn)
        main_layout.addLayout(top_header)

        # 2. Main White Inner Card
        inner_card = QFrame()
        inner_card.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 18px;
            padding: 14px;
        """)
        inner_layout = QVBoxLayout(inner_card)
        inner_layout.setContentsMargins(12, 12, 12, 12)
        inner_layout.setSpacing(10)

        # Branding Logo (Mercy Dental Care)
        self.logo_lbl = QLabel()
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setFixedHeight(135)
        self.logo_lbl.setStyleSheet("background: transparent; border: none; padding: 2px;")
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.jpg")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaledToHeight(130, Qt.TransformationMode.SmoothTransformation)
            self.logo_lbl.setPixmap(pix)
        else:
            self.logo_lbl.setText("🦷 Mercy Dental Care")
            self.logo_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #5648A6;")
        inner_layout.addWidget(self.logo_lbl)

        # Live Clock & Staff selector
        clock_layout = QHBoxLayout()
        self.staff_combo = QComboBox()
        setup_styled_combobox(self.staff_combo)
        self.staff_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 600;
                background-color: #F8FAFC;
                color: #1E293B;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #CBD5E1;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
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
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px;
                outline: none;
                selection-background-color: #EDE9FE;
                selection-color: #5648A6;
            }
            QComboBox QAbstractItemView::item {
                min-height: 26px;
                padding: 4px 8px;
                border-radius: 4px;
                color: #1E293B;
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
        self.load_staff_list()
        clock_layout.addWidget(self.staff_combo, stretch=2)

        self.live_clock_lbl = QLabel()
        self.live_clock_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.live_clock_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #5648A6;")
        clock_layout.addWidget(self.live_clock_lbl, stretch=1)
        inner_layout.addLayout(clock_layout)

        # Check In / Check Out        # Action Buttons
        btn_box = QVBoxLayout()
        btn_box.setSpacing(8)

        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(10)

        self.btn_check_in = QPushButton("Check In")
        self.btn_check_in.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_in.setFixedHeight(44)
        self.btn_check_in.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                font-size: 13.5px;
                font-weight: 700;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #6757C4;
            }
        """)
        self.btn_check_in.clicked.connect(self.handle_check_in)
        btn_row1.addWidget(self.btn_check_in)

        self.btn_check_out = QPushButton("Checked Out")
        self.btn_check_out.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_out.setFixedHeight(44)
        self.btn_check_out.setStyleSheet("""
            QPushButton {
                background-color: #EA4335;
                color: #FFFFFF;
                font-size: 13.5px;
                font-weight: 700;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.btn_check_out.setToolTip("Checked Out (ចេញធម្មតា • គ្មានអ្នកជំងឺ មិនគិតប្រាក់ថែមម៉ោង)")
        self.btn_check_out.clicked.connect(self.handle_check_out)
        btn_row1.addWidget(self.btn_check_out)

        btn_box.addLayout(btn_row1)

        # Dedicated "Checked out with Overtime" Button requested by User
        self.btn_check_out_ot = QPushButton("⭐ ចេញថែមម៉ោង (OT សម្រាប់តែមានអ្នកជំងឺ)")
        self.btn_check_out_ot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_out_ot.setFixedHeight(42)
        self.btn_check_out_ot.setStyleSheet("""
            QPushButton {
                background-color: #D97706;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #B45309;
            }
        """)
        self.btn_check_out_ot.setToolTip("Checked out with Overtime (ចេញថែមម៉ោង • សម្រាប់តែពេលមានអ្នកជំងឺ $1.50/ម៉ោង គិតតាមនាទីជាក់ស្តែងចាប់ពី 10 នាទីឡើង)")
        self.btn_check_out_ot.clicked.connect(self.handle_check_out_overtime)
        btn_box.addWidget(self.btn_check_out_ot)

        inner_layout.addLayout(btn_box)
        main_layout.addWidget(inner_card)

        # 3. Attendance Summary Cards (Late In, Early Out, Leave)
        summary_header = QHBoxLayout()
        self.summary_title = QLabel("Attendance Summary")
        self.summary_title.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 700;")
        summary_header.addWidget(self.summary_title)
        summary_header.addStretch()

        week_pill = QLabel("This Week  ▼")
        week_pill.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            color: #FFFFFF;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        """)
        summary_header.addWidget(week_pill)
        main_layout.addLayout(summary_header)

        # 3 Mini Stat Boxes matching IMG_7453
        stats_h = QHBoxLayout()
        stats_h.setSpacing(8)

        # Late In Box (Soft Pink)
        self.late_box, self.late_num = self._create_mini_box("Late In", "0", "#FCE8E6", "#C5221F")
        stats_h.addWidget(self.late_box)

        # Early Out Box (Soft Yellow/Orange)
        self.early_box, self.early_num = self._create_mini_box("Early Out", "0", "#FEF7E0", "#B06000")
        stats_h.addWidget(self.early_box)

        # Leave Box (Soft Blue)
        self.leave_box, self.leave_num = self._create_mini_box("Leave", "0", "#E8F0FE", "#1A73E8")
        stats_h.addWidget(self.leave_box)

        main_layout.addLayout(stats_h)

        # 4. White App Card with only 2 Features (ស្នើរសុំច្បាប់ & Digital Card)
        feature_card = QFrame()
        feature_card.setStyleSheet("""
            background-color: #FFFFFF;
            border: 1.5px solid #CBD5E1;
            border-radius: 16px;
        """)
        f_layout = QHBoxLayout(feature_card)
        f_layout.setSpacing(14)
        f_layout.setContentsMargins(14, 12, 14, 12)

        features = [
            ("📱", "ស្កេនតាមទូរស័ព្ទ (QR)", self.on_feature_mobile_qr),
            ("➡️", "ស្នើរសុំច្បាប់", self.on_feature_leave),
            ("🪪", "Digital Card", self.on_feature_badge)
        ]

        for icon, title, callback in features:
            f_btn = QPushButton(f"{icon}\n{title}")
            f_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            f_btn.setFixedHeight(62)
            f_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8FAFC;
                    color: #1E293B;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 600;
                    line-height: 1.4;
                }
                QPushButton:hover {
                    background-color: #EEEDFB;
                    color: #5648A6;
                    border-color: #5648A6;
                }
            """)
            f_btn.clicked.connect(callback)
            f_layout.addWidget(f_btn)

        main_layout.addWidget(feature_card)

        # Timer for live clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_live_clock)
        self.timer.start(1000)
        self.update_live_clock()
        self.refresh_summary()

    def _create_mini_box(self, label, value, bg, text_color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {bg};
            border: 1.5px solid rgba(0, 0, 0, 0.08);
            border-radius: 10px;
            padding: 8px;
        """)
        v = QVBoxLayout(frame)
        v.setContentsMargins(6, 6, 6, 6)
        v.setSpacing(2)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {text_color}; font-size: 11px; font-weight: 600;")
        v.addWidget(lbl)

        val = QLabel(value)
        val.setAlignment(Qt.AlignmentFlag.AlignRight)
        val.setStyleSheet(f"color: {text_color}; font-size: 20px; font-weight: 800;")
        v.addWidget(val)

        return frame, val

    def load_staff_list(self):
        self.staff_combo.clear()
        emps = [e for e in database.get_all_employees() if e.get("khmer_name") != "គាំ មិថុនា" and e.get("name") != "Kam Mithona"]
        for e in emps:
            self.staff_combo.addItem(f"{e['emp_code']} - {e['name']} ({e['khmer_name']})", e['id'])

    def update_live_clock(self):
        now = datetime.now()
        self.live_clock_lbl.setText(now.strftime("%H:%M:%S"))
        hour = now.hour
        if hour < 12:
            self.greet_lbl.setText("Good Morning! / អរុណសួស្តី!")
        elif hour < 17:
            self.greet_lbl.setText("Good Afternoon! / ទិវាសួស្តី!")
        else:
            self.greet_lbl.setText("Good Evening! / សាយណ្ហសួស្តី!")

    def refresh_summary(self):
        stats = database.get_stats()
        self.late_num.setText(str(stats["late_today"]))
        self.early_num.setText("0")
        self.leave_num.setText(str(stats["leave_today"]))

    def _authenticate_staff(self, emp_id, action_name):
        from components.staff_auth_dialog import StaffAuthDialog
        pwd_dlg = StaffAuthDialog(emp_id, action_name=action_name, parent=self)
        if pwd_dlg.exec():
            return True, "Kiosk PIN/Password Verified"
        return False, None

    def handle_check_in(self):
        emp_id = self.staff_combo.currentData()
        ok, notes = self._authenticate_staff(emp_id, "Check In / ចូលធ្វើការ")
        if not ok:
            return

        status, check_time = database.record_check_in(emp_id, notes=notes)
        QMessageBox.information(self, "ជោគជ័យ (Success)", f"✅ ស្កេនចូលធ្វើការជោគជ័យ (Check In)!\nម៉ោង៖ {check_time} ({status})")
        self.refresh_summary()
        self.attendance_updated.emit()

    def handle_check_out(self):
        emp_id = self.staff_combo.currentData()
        ok, notes = self._authenticate_staff(emp_id, "Checked Out (ចេញធម្មតា)")
        if not ok:
            return

        database.record_check_out(emp_id, has_overtime=False, notes=notes)
        QMessageBox.information(self, "ជោគជ័យ (Success)", "👋 ស្កេនចេញធ្វើការជោគជ័យ (Checked Out)!")
        self.refresh_summary()
        self.attendance_updated.emit()

    def handle_check_out_overtime(self):
        emp_id = self.staff_combo.currentData()
        if not emp_id:
            QMessageBox.warning(self, "ជូនដំណឹង", "សូមជ្រើសរើសបុគ្គលិកជាមុនសិន!")
            return

        from datetime import datetime
        shift_end = database.get_setting("shift_end", "18:00")
        now_hm = datetime.now().strftime("%H:%M")
        if now_hm < shift_end[:5]:
            QMessageBox.warning(
                self, "មិនទាន់ដល់ម៉ោងថែម",
                f"⚠️ មិនទាន់ដល់ម៉ោងចេញធ្វើការ ({shift_end}) នៅឡើយទេ! (ម៉ោងបច្ចុប្បន្ន៖ {now_hm})\n\nការថែមម៉ោង (OT) គិតតែចាប់ពីម៉ោង {shift_end} ឡើងទៅប៉ុណ្ណោះ។\n\nប្រសិនបើលោកអ្នកចេញពេលនេះ សូមចុចប៊ូតុង 'Checked Out' ធម្មតា។"
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
        ok, notes = self._authenticate_staff(emp_id, f"Checked out with Overtime (អ្នកជំងឺ៖ {patient_name})")
        if not ok:
            return

        t, ot_h, ot_p = database.record_check_out(emp_id, has_overtime=True, patient_name=patient_name, notes=notes)
        if ot_h > 0:
            mins = int(round(ot_h * 60))
            QMessageBox.information(
                self, "ជោគជ័យ (Success)", 
                f"⭐ ស្កេនចេញថែមម៉ោងជោគជ័យ!\n\n👤 អ្នកជំងឺ៖ {patient_name}\n⏰ ម៉ោងចេញ៖ {t}\n💰 ថែមបាន៖ +{ot_h} ម៉ោង ({mins} នាទី) = +${ot_p:.2f}\n(30 នាទី=$0.75 • 1 ម៉ោង=$1.50)"
            )
        else:
            QMessageBox.information(
                self, "ស្កេនចេញជោគជ័យ", 
                f"👋 ស្កេនចេញជោគជ័យ (នៅម៉ោង {t})!\n\n👤 អ្នកជំងឺ៖ {patient_name}\n⚠️ លើសតិចជាង ១៥ នាទី មិនទាន់គ្រប់លក្ខខណ្ឌគិតម៉ោងថែម (OT) ឡើយ។"
            )
        self.refresh_summary()
        self.attendance_updated.emit()

    def on_feature_attendance(self):
        self.attendance_updated.emit()

    def on_feature_leave(self):
        from components.leave_dialog import LeaveRequestDialog
        emp_id = self.staff_combo.currentData()
        dlg = LeaveRequestDialog(emp_id=emp_id, parent=self)
        if dlg.exec():
            self.refresh_summary()
            self.attendance_updated.emit()

    def on_feature_overtime(self):
        QMessageBox.information(self, "Overtime Management", "Overtime hours are automatically calculated upon Check-Out past 18:00 (when attending to patients >= 10 mins) and synced with Mercy Dental Care payroll.")

    def on_feature_approval(self):
        QMessageBox.information(self, "Pending Approvals", "You have 2 pending leave requests and 2 clinic equipment purchase requests awaiting review.")

    def on_feature_roster(self):
        QMessageBox.information(self, "Clinic Shift Roster", "Current Shift: Monday - Saturday (07:30 to 18:00)\nLunch Break: 12:00 to 13:00\nOn-call emergency dentist rotation active.")

    def on_feature_badge(self):
        from components.badge_dialog import BadgeDialog
        emp_id = self.staff_combo.currentData()
        emp = database.get_employee_by_id(emp_id)
        if emp:
            dlg = BadgeDialog(emp, parent=self)
            dlg.exec()

    def on_feature_mobile_qr(self):
        from components.mobile_qr_dialog import MobileQrDialog
        dlg = MobileQrDialog(parent=self)
        dlg.exec()
