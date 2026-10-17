"""
Clinic Settings & Configuration View for Mercy Dental Care.
Fully scrollable, responsive, beautifully styled cards.
Includes Role-Based Permissions for Staff configured by Administrator.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QMessageBox, QGridLayout,
    QScrollArea, QCheckBox, QListView
)
from PyQt6.QtCore import Qt, pyqtSignal

import database
from theme import tr, PRIMARY, set_language, setup_styled_combobox

class SettingsView(QWidget):
    language_changed = pyqtSignal(str)
    permissions_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout with ScrollArea so cards NEVER squash on any screen size
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        container = QWidget()
        container.setObjectName("settingsContainer")
        container.setStyleSheet("""
            QWidget#settingsContainer {
                background-color: transparent;
            }
            QFrame.settings-card {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 12px;
            }
            QLineEdit, QComboBox {
                min-height: 42px;
                max-height: 42px;
                padding: 0 14px;
                font-size: 13.5px;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #1E293B;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1.5px solid #5648A6;
                background-color: #FFFFFF;
            }
            QLineEdit:read-only {
                background-color: #F8FAFC;
                color: #64748B;
                border-color: #CBD5E1;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: 1.5px solid #CBD5E1;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
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
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 4px;
                outline: none;
                selection-background-color: #EDE9FE;
                selection-color: #5648A6;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 6px 12px;
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
            QCheckBox {
                font-size: 13px;
                font-weight: 700;
                color: #1E293B;
                spacing: 10px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 28)
        layout.setSpacing(20)

        # 1. Header
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        title = QLabel("Clinic Configuration & Settings / ការកំណត់គ្លីនិក")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1E293B;")
        sub_title = QLabel("Manage clinic profile, staff permissions, working shifts, and administrator security")
        sub_title.setStyleSheet("font-size: 13px; color: #64748B;")
        header_box.addWidget(title)
        header_box.addWidget(sub_title)
        layout.addLayout(header_box)

        # 2. Card: Staff Access & Page Permissions (Requested by User)
        card_perms = QFrame()
        card_perms.setProperty("class", "settings-card")
        p_layout = QVBoxLayout(card_perms)
        p_layout.setContentsMargins(20, 18, 20, 20)
        p_layout.setSpacing(14)

        p_header_row = QHBoxLayout()
        p_titles_box = QVBoxLayout()
        p_titles_box.setSpacing(3)
        sec_perms = QLabel("🛡️ Staff Access & Page Permissions / ការកំណត់សិទ្ធិមើល និងប្រើប្រាស់របស់បុគ្គលិក")
        sec_perms.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        sec_perms_sub = QLabel("កំណត់ទំព័រណាខ្លះដែលបុគ្គលិក (Staff) អាចមើលឃើញ និងចូលប្រើបាន នៅពេល Login (Admin មានសិទ្ធិពេញលេញជានិច្ច)")
        sec_perms_sub.setStyleSheet("font-size: 12px; color: #64748B;")
        p_titles_box.addWidget(sec_perms)
        p_titles_box.addWidget(sec_perms_sub)
        p_header_row.addLayout(p_titles_box)

        p_header_row.addStretch()

        # Quick action buttons for permissions
        btn_sel_all = QPushButton("✔️ ជ្រើសទាំងអស់")
        btn_sel_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sel_all.setStyleSheet("""
            QPushButton {
                background-color: #EEEDFB;
                color: #5648A6;
                font-weight: 600;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #D6D3F7;
            }
            QPushButton:hover {
                background-color: #5648A6;
                color: #FFFFFF;
            }
        """)
        btn_sel_all.clicked.connect(self._select_all_perms)
        p_header_row.addWidget(btn_sel_all)

        btn_default_perms = QPushButton("↩️ លំនាំដើមសុវត្ថិភាព")
        btn_default_perms.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_default_perms.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                font-weight: 600;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_default_perms.clicked.connect(self._reset_default_perms)
        p_header_row.addWidget(btn_default_perms)

        p_layout.addLayout(p_header_row)

        # Grid of permission items
        self.perm_items = [
            ("dashboard", "📊", "Dashboard / ផ្ទាំងព័ត៌មាន", "មើលសេចក្តីសង្ខេប និងស្ថិតិវត្តមានប្រចាំថ្ងៃ"),
            ("employees", "👥", "Employees / បញ្ជីបុគ្គលិក", "មើលប្រវត្តិរូប និងព័ត៌មានបុគ្គលិកទាំងអស់"),
            ("attendance", "⏱️", "Attendance / វត្តមាន", "ពិនិត្យបញ្ជីវត្តមាន ម៉ោងចូល និងចេញ"),
            ("leave", "📅", "Leave / ច្បាប់ឈប់សម្រាក", "មើល និងដាក់ពាក្យស្នើសុំច្បាប់ឈប់សម្រាក"),
            ("payroll", "💵", "Payroll / បើកប្រាក់ខែ", "មើលរបាយការណ៍ និងទិន្នន័យប្រាក់បៀវត្សរ៍ (ទិន្នន័យសម្ងាត់)"),
            ("requests", "🔔", "Requests / សេចក្តីជូនដំណឹងផ្សេងៗ", "សេចក្តីជូនដំណឹង ព័ត៌មាន ឬលិខិតការងារផ្សេងៗ"),
            ("kiosk", "📱", "Kiosk / ស្កេនវត្តមានរហ័ស", "ផ្ទាំងស្កេន Check-In / Check-Out វត្តមានបុគ្គលិក"),
            ("settings", "⚙️", "Settings / ការកំណត់", "ការកំណត់គ្លីនិក និងពាក្យសម្ងាត់ប្រព័ន្ធ (Admin Only)")
        ]

        grid_perms = QGridLayout()
        grid_perms.setVerticalSpacing(10)
        grid_perms.setHorizontalSpacing(14)

        self.perm_checkboxes = {}
        row = 0
        col = 0
        for key, icon, title_str, desc_str in self.perm_items:
            item_card = QFrame()
            item_card.setObjectName("permItemCard")
            item_card.setStyleSheet("""
                QFrame#permItemCard {
                    background-color: #F8FAFC;
                    border: 1.5px solid #CBD5E1;
                    border-radius: 10px;
                    padding: 8px 12px;
                }
                QFrame#permItemCard:hover {
                    border-color: #5648A6;
                    background-color: #F5F3FF;
                }
            """)
            i_layout = QVBoxLayout(item_card)
            i_layout.setContentsMargins(6, 6, 6, 6)
            i_layout.setSpacing(4)

            chk = QCheckBox(f"{icon}  {title_str}")
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            self.perm_checkboxes[key] = chk
            i_layout.addWidget(chk)

            desc_lbl = QLabel(desc_str)
            desc_lbl.setStyleSheet("font-size: 11px; color: #64748B; padding-left: 28px; background: transparent; border: none;")
            i_layout.addWidget(desc_lbl)

            grid_perms.addWidget(item_card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        p_layout.addLayout(grid_perms)
        layout.addWidget(card_perms)

        # 3. Card: Clinic Profile
        card_profile = QFrame()
        card_profile.setProperty("class", "settings-card")
        c_layout = QVBoxLayout(card_profile)
        c_layout.setContentsMargins(20, 18, 20, 20)
        c_layout.setSpacing(16)

        sec1 = QLabel("🏢 Clinic Profile / ព័ត៌មានគ្លីនិក")
        sec1.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        c_layout.addWidget(sec1)

        grid1 = QGridLayout()
        grid1.setVerticalSpacing(14)
        grid1.setHorizontalSpacing(20)

        # Col 0: Name EN, Col 1: Name KH
        self.in_name_en = QLineEdit()
        grid1.addLayout(self._field_layout("Clinic Name (English) / ឈ្មោះគ្លីនិក (អង់គ្លេស)", self.in_name_en), 0, 0)

        self.in_name_kh = QLineEdit()
        grid1.addLayout(self._field_layout("Clinic Name (Khmer) / ឈ្មោះគ្លីនិក (ខ្មែរ)", self.in_name_kh), 0, 1)

        # Col 0: Phone, Col 1: Email
        self.in_phone = QLineEdit()
        grid1.addLayout(self._field_layout("Contact Phone / លេខទូរស័ព្ទ", self.in_phone), 1, 0)

        self.in_email = QLineEdit()
        grid1.addLayout(self._field_layout("Official Email / អ៊ីមែល", self.in_email), 1, 1)

        # Span 2: Address
        self.in_address = QLineEdit()
        grid1.addLayout(self._field_layout("Location & Address / ទីតាំង និងអាសយដ្ឋានគ្លីនិក", self.in_address), 2, 0, 1, 2)

        # Row 3: Interface Language
        self.combo_lang = QComboBox()
        setup_styled_combobox(self.combo_lang)
        self.combo_lang.addItem("🇰🇭 ភាសាខ្មែរ (Khmer)", "kh")
        self.combo_lang.addItem("🇬🇧 English (English)", "en")
        grid1.addLayout(self._field_layout("Interface Language / ភាសាប្រព័ន្ធ", self.combo_lang), 3, 0)

        c_layout.addLayout(grid1)
        layout.addWidget(card_profile)

        # 4. Card: Working Hours & Biometric Rules
        card_shift = QFrame()
        card_shift.setProperty("class", "settings-card")
        s_layout = QVBoxLayout(card_shift)
        s_layout.setContentsMargins(20, 18, 20, 20)
        s_layout.setSpacing(16)

        sec2 = QLabel("⏱️ Working Hours & Biometric Rules / ម៉ោងធ្វើការ និងលក្ខខណ្ឌ")
        sec2.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        s_layout.addWidget(sec2)

        grid2 = QGridLayout()
        grid2.setVerticalSpacing(14)
        grid2.setHorizontalSpacing(20)

        # Col 0: Shift Start, Col 1: Shift End
        self.in_start = QLineEdit()
        grid2.addLayout(self._field_layout("Shift Start Time / ម៉ោងចូលធ្វើការ (HH:MM)", self.in_start), 0, 0)

        self.in_end = QLineEdit()
        grid2.addLayout(self._field_layout("Shift End Time / ម៉ោងចេញពីធ្វើការ (HH:MM)", self.in_end), 0, 1)

        # Col 0: Grace Period, Col 1: Currency
        self.in_grace = QLineEdit()
        grid2.addLayout(self._field_layout("Late Grace Period (Minutes) / រយៈពេលអនុគ្រោះមកយឺត (នាទី)", self.in_grace), 1, 0)

        self.in_curr = QLineEdit()
        grid2.addLayout(self._field_layout("Default Currency / រូបិយប័ណ្ណទូទាត់", self.in_curr), 1, 1)

        # Col 0: Overtime in Minutes & Hours, Col 1: Overtime Rate in Dollars ($)
        self.in_overtime_time = QLineEdit()
        self.in_overtime_time.setPlaceholderText("ឧ. គិតជានាទី និង ម៉ោង (Minutes & Hours)")
        grid2.addLayout(self._field_layout("Overtime (OT) / ថែមម៉ោង (គិតជានាទី និង ម៉ោង)", self.in_overtime_time), 2, 0)

        self.in_overtime_usd = QLineEdit()
        self.in_overtime_usd.setPlaceholderText("ឧ. $1.5 / ម៉ោង (30 នាទី=$0.75, 1 ម៉ោង=$1.50)")
        grid2.addLayout(self._field_layout("Overtime Rate ($) / តម្លៃថែមម៉ោង (30 នាទី=$0.75 • 1 ម៉ោង=$1.50)", self.in_overtime_usd), 2, 1)

        s_layout.addLayout(grid2)
        layout.addWidget(card_shift)

        # 5. Card: Mobile Attendance & Wi-Fi / GPS Geofence Settings
        card_mobile = QFrame()
        card_mobile.setProperty("class", "settings-card")
        m_layout = QVBoxLayout(card_mobile)
        m_layout.setContentsMargins(20, 18, 20, 20)
        m_layout.setSpacing(16)

        sec_m = QLabel("📶 Mobile Attendance & Clinic Wi-Fi / GPS Settings (ស្កេនតាមទូរស័ព្ទដៃ)")
        sec_m.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        m_layout.addWidget(sec_m)

        desc_m = QLabel("កំណត់ទីតាំង Wi-Fi និង GPS គ្លីនិក ដើម្បីការពារកុំឱ្យបុគ្គលិកបន្លំស្កេនពីផ្ទះ ឬពីក្រៅគ្លីនិក។\n(សម្គាល់៖ ប្រសិនបើលោកអ្នកមិនទាន់នៅគ្លីនិក លោកអ្នកអាចដោះធីក Enforce ដើម្បីអាចតេស្តសាកល្បងបានពីគ្រប់ទីកន្លែង)")
        desc_m.setStyleSheet("font-size: 12px; color: #64748B; line-height: 1.4;")
        m_layout.addWidget(desc_m)

        grid_m = QGridLayout()
        grid_m.setVerticalSpacing(14)
        grid_m.setHorizontalSpacing(20)

        # Row 0: Wi-Fi SSID, Wi-Fi Enforce
        self.in_wifi_ssid = QLineEdit()
        self.in_wifi_ssid.setPlaceholderText("ឧ. Mercy Dental Clinic ឬ Wi-Fi បច្ចុប្បន្ន")
        grid_m.addLayout(self._field_layout("Clinic Wi-Fi Name (SSID) / ឈ្មោះ Wi-Fi គ្លីនិក", self.in_wifi_ssid), 0, 0)

        self.chk_wifi_enforce = QCheckBox("តម្រូវឱ្យភ្ជាប់ Wi-Fi គ្លីនិក (Enforce Clinic Wi-Fi)")
        self.chk_wifi_enforce.setStyleSheet("font-size: 13px; font-weight: 600; color: #334155;")
        wifi_box = QVBoxLayout()
        wifi_box.setSpacing(6)
        lbl_w_enforce = QLabel("Wi-Fi Security Lock / ការចាក់សោ Wi-Fi")
        lbl_w_enforce.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569;")
        wifi_box.addWidget(lbl_w_enforce)
        wifi_box.addWidget(self.chk_wifi_enforce)
        grid_m.addLayout(wifi_box, 0, 1)

        # Row 1: Clinic Public IP with Auto-detect button
        self.in_clinic_ip = QLineEdit()
        self.in_clinic_ip.setPlaceholderText("ឧ. 119.13.157.36 (IP Router អ៊ីនធឺណិតគ្លីនិក)")
        ip_widget = QWidget()
        ip_h = QHBoxLayout(ip_widget)
        ip_h.setContentsMargins(0, 0, 0, 0)
        ip_h.setSpacing(8)
        ip_h.addWidget(self.in_clinic_ip, 1)
        btn_detect_ip = QPushButton("🔍 ចាប់យក IP គ្លីនិកស្វ័យប្រវត្ត")
        btn_detect_ip.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detect_ip.setStyleSheet("""
            QPushButton {
                background-color: #EDE9FE;
                color: #5648A6;
                font-weight: 600;
                font-size: 12.5px;
                padding: 0 14px;
                min-height: 42px;
                border: 1.5px solid #DDD6FE;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5648A6;
                color: #FFFFFF;
            }
        """)
        btn_detect_ip.clicked.connect(self.auto_detect_clinic_ip)
        ip_h.addWidget(btn_detect_ip)
        grid_m.addLayout(self._field_layout("Clinic Public IP / អាសយដ្ឋាន IP អ៊ីនធឺណិតគ្លីនិក (Router)", ip_widget), 1, 0, 1, 2)

        # Row 2: Clinic Lat, Clinic Lng
        self.in_clinic_lat = QLineEdit()
        self.in_clinic_lat.setPlaceholderText("ឧ. 11.556400")
        grid_m.addLayout(self._field_layout("Clinic Latitude / រយៈទទឹង GPS គ្លីនិក (Lat)", self.in_clinic_lat), 2, 0)

        self.in_clinic_lng = QLineEdit()
        self.in_clinic_lng.setPlaceholderText("ឧ. 104.928200")
        grid_m.addLayout(self._field_layout("Clinic Longitude / រយៈបណ្តោយ GPS គ្លីនិក (Lng)", self.in_clinic_lng), 2, 1)

        # Row 3: Allowed Radius, GPS Enforce
        self.in_gps_radius = QLineEdit()
        self.in_gps_radius.setPlaceholderText("ឧ. 50 (គិតជាម៉ែត្រ)")
        grid_m.addLayout(self._field_layout("Allowed Radius (Meters) / កាំរង្វង់អនុញ្ញាត (ម៉ែត្រ)", self.in_gps_radius), 3, 0)

        self.chk_gps_enforce = QCheckBox("តម្រូវឱ្យផ្ទៀងផ្ទាត់ GPS (Enforce Geofence)")
        self.chk_gps_enforce.setStyleSheet("font-size: 13px; font-weight: 600; color: #334155;")
        gps_box = QVBoxLayout()
        gps_box.setSpacing(6)
        lbl_g_enforce = QLabel("GPS Geofence Lock / ការចាក់សោ GPS")
        lbl_g_enforce.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569;")
        gps_box.addWidget(lbl_g_enforce)
        gps_box.addWidget(self.chk_gps_enforce)
        grid_m.addLayout(gps_box, 3, 1)

        # Row 4: Cloudflare Subdomain / Public URL
        self.in_public_url = QLineEdit()
        self.in_public_url.setPlaceholderText("ឧ. https://attendance.yourdomain.com (Cloudflare Tunnel)")
        grid_m.addLayout(self._field_layout("Cloudflare Subdomain / Public URL (អាសយដ្ឋានលើអ៊ីនធឺណិត)", self.in_public_url), 4, 0, 1, 2)

        m_layout.addLayout(grid_m)

        # Mobile Portal Action & QR Code preview
        mobile_act_box = QFrame()
        mobile_act_box.setObjectName("mobileActBox")
        mobile_act_box.setStyleSheet("""
            QFrame#mobileActBox {
                background-color: #F8FAFC;
                border: 1.5px solid #CBD5E1;
                border-radius: 12px;
                padding: 12px 16px;
            }
        """)
        m_act_h = QHBoxLayout(mobile_act_box)
        m_act_h.setContentsMargins(8, 4, 8, 4)

        from mobile_server import get_local_ip
        local_ip = get_local_ip()
        self.lbl_mob_info = QLabel(f"📱 អាសយដ្ឋាន Mobile Portal: <b style='color:#5648A6;'>http://{local_ip}:5000</b>")
        self.lbl_mob_info.setStyleSheet("font-size: 13px; color: #1E293B;")
        m_act_h.addWidget(self.lbl_mob_info)
        m_act_h.addStretch()

        btn_show_qr = QPushButton("📷 បង្ហាញ QR Code សម្រាប់ទូរស័ព្ទស្កេន")
        btn_show_qr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_show_qr.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: white;
                font-weight: 700;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
                font-size: 12.5px;
            }
            QPushButton:hover {
                background-color: #493D90;
            }
        """)
        btn_show_qr.clicked.connect(self.show_mobile_qr)
        m_act_h.addWidget(btn_show_qr)

        m_layout.addWidget(mobile_act_box)
        layout.addWidget(card_mobile)

        # 6. Card: Administrator Security & Password
        card_admin = QFrame()
        card_admin.setProperty("class", "settings-card")
        a_layout = QVBoxLayout(card_admin)
        a_layout.setContentsMargins(20, 18, 20, 20)
        a_layout.setSpacing(16)

        sec3 = QLabel("🔐 Administrator Security & Password / គណនី និងពាក្យសម្ងាត់ Admin")
        sec3.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        a_layout.addWidget(sec3)

        grid3 = QGridLayout()
        grid3.setVerticalSpacing(14)
        grid3.setHorizontalSpacing(20)

        self.in_admin_user = QLineEdit("admin")
        self.in_admin_user.setReadOnly(True)
        grid3.addLayout(self._field_layout("Admin Username / គណនី Admin", self.in_admin_user), 0, 0)

        # Admin Password with eye button
        pwd_field_box = QVBoxLayout()
        pwd_field_box.setSpacing(6)
        lbl_pwd = QLabel("Admin Password / ពាក្យសម្ងាត់ Admin")
        lbl_pwd.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569;")
        pwd_field_box.addWidget(lbl_pwd)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)
        self.in_admin_pwd = QLineEdit()
        self.in_admin_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_eye_admin = QPushButton("👁️")
        self.btn_eye_admin.setFixedSize(42, 42)
        self.btn_eye_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye_admin.setToolTip("Show/Hide Password")
        self.btn_eye_admin.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                border-color: #5648A6;
            }
        """)
        self.btn_eye_admin.clicked.connect(self._toggle_admin_pwd)
        pwd_row.addWidget(self.in_admin_pwd)
        pwd_row.addWidget(self.btn_eye_admin)
        pwd_field_box.addLayout(pwd_row)

        grid3.addLayout(pwd_field_box, 0, 1)

        a_layout.addLayout(grid3)
        layout.addWidget(card_admin)

        # 6. Bottom Actions
        act_h = QHBoxLayout()
        act_h.setContentsMargins(4, 8, 4, 12)
        act_h.setSpacing(12)

        btn_clear_data = QPushButton("🗑️ លុបឈ្មោះចាស់ៗទាំងអស់ (Clear Old Data)")
        btn_clear_data.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear_data.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #DC2626;
                font-weight: 700;
                padding: 10px 18px;
                border-radius: 8px;
                border: 1.5px solid #FCA5A5;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        btn_clear_data.clicked.connect(self.clear_all_old_data)
        act_h.addWidget(btn_clear_data)

        btn_reset = QPushButton("🔄 Reset Demo Data")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                font-weight: 600;
                padding: 10px 16px;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_reset.clicked.connect(self.reset_demo)
        act_h.addWidget(btn_reset)

        act_h.addStretch()

        btn_save = QPushButton("💾 Save Settings & Permissions / រក្សាទុក")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: white;
                font-weight: 700;
                padding: 11px 28px;
                border-radius: 8px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #493D90;
            }
        """)
        btn_save.clicked.connect(self.save_settings)
        act_h.addWidget(btn_save)

        layout.addLayout(act_h)

        # Mini By Departments card below Settings
        from components.pie_chart import DepartmentPieChartWidget
        self.dept_pie = DepartmentPieChartWidget()
        self.dept_pie.setMaximumWidth(360)
        layout.addWidget(self.dept_pie)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Load values from DB
        self.load_settings()

    def _field_layout(self, label_text: str, widget) -> QVBoxLayout:
        box = QVBoxLayout()
        box.setSpacing(6)
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569;")
        box.addWidget(lbl)
        if hasattr(widget, "addWidget") or hasattr(widget, "addLayout"):
            box.addLayout(widget)
        else:
            box.addWidget(widget)
        return box

    def _select_all_perms(self):
        for chk in self.perm_checkboxes.values():
            chk.setChecked(True)

    def _reset_default_perms(self):
        defaults = database.DEFAULT_STAFF_PERMISSIONS
        for key, chk in self.perm_checkboxes.items():
            chk.setChecked(defaults.get(key, False))

    def load_settings(self):
        # 1. Clinic profile matching Google Maps pin: 11.5834188, 104.8811696
        self.in_name_en.setText(database.get_setting("clinic_name_en", "Mercy Dental Care"))
        self.in_name_kh.setText(database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី"))
        self.in_phone.setText(database.get_setting("clinic_phone", "085 796 704"))
        self.in_email.setText(database.get_setting("clinic_email", "info@mercydentalcare.com"))
        self.in_address.setText(database.get_setting("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ"))

        # 2. Shifts
        self.in_start.setText(database.get_setting("shift_start", "07:30"))
        self.in_end.setText(database.get_setting("shift_end", "18:00"))
        self.in_grace.setText(database.get_setting("late_grace", "15"))
        self.in_curr.setText(database.get_setting("currency", "USD ($)"))
        self.in_overtime_time.setText(database.get_setting("overtime_time_rule", "គិតជានាទី និង ម៉ោង (Minutes & Hours)"))
        self.in_overtime_usd.setText(database.get_setting("overtime_rate_usd", "$1.5 / ម៉ោង"))

        lang = database.get_setting("language", "kh")
        idx = self.combo_lang.findData(lang)
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)

        # 3. Mobile Web & Wi-Fi / GPS settings matching Mercy Dental Care
        self.in_wifi_ssid.setText(database.get_setting("wifi_ssid", "Mercy Dental Care"))
        self.chk_wifi_enforce.setChecked(database.get_setting("wifi_enforce", "0") == "1")
        self.in_clinic_ip.setText(database.get_setting("clinic_public_ip", "119.13.157.36"))
        self.in_clinic_lat.setText(database.get_setting("clinic_lat", "11.5834188"))
        self.in_clinic_lng.setText(database.get_setting("clinic_lng", "104.8811696"))
        self.in_gps_radius.setText(database.get_setting("gps_radius", "50"))
        self.chk_gps_enforce.setChecked(database.get_setting("gps_enforce", "0") == "1")
        pub_url = database.get_setting("mobile_public_url", "")
        self.in_public_url.setText(pub_url)
        if pub_url:
            self.lbl_mob_info.setText(f"📱 អាសយដ្ឋាន Mobile Portal: <b style='color:#5648A6;'>{pub_url}</b>")

        # 4. Admin credentials
        admin_creds = database.get_admin_credentials()
        self.in_admin_user.setText(admin_creds.get("username", "admin"))
        self.in_admin_pwd.setText(admin_creds.get("password", "admin123"))

        # 5. Staff permissions
        perms = database.get_staff_permissions()
        for key, chk in self.perm_checkboxes.items():
            chk.setChecked(perms.get(key, False))

        if hasattr(self, 'dept_pie'):
            self.dept_pie.set_data(database.get_dept_distribution())

    def show_mobile_qr(self):
        from components.mobile_qr_dialog import MobileQrDialog
        dlg = MobileQrDialog(parent=self)
        dlg.exec()

    def _toggle_admin_pwd(self):
        if self.in_admin_pwd.echoMode() == QLineEdit.EchoMode.Password:
            self.in_admin_pwd.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_eye_admin.setText("🔒")
        else:
            self.in_admin_pwd.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_eye_admin.setText("👁️")

    def save_settings(self):
        database.set_setting("clinic_name_en", self.in_name_en.text().strip())
        database.set_setting("clinic_name_kh", self.in_name_kh.text().strip())
        database.set_setting("clinic_phone", self.in_phone.text().strip())
        database.set_setting("clinic_email", self.in_email.text().strip())
        database.set_setting("clinic_address", self.in_address.text().strip())

        database.set_setting("shift_start", self.in_start.text().strip())
        database.set_setting("shift_end", self.in_end.text().strip())
        database.set_setting("late_grace", self.in_grace.text().strip())
        database.set_setting("currency", self.in_curr.text().strip())
        database.set_setting("overtime_time_rule", self.in_overtime_time.text().strip())
        ot_usd_str = self.in_overtime_usd.text().strip() or "$1.5 / ម៉ោង"
        database.set_setting("overtime_rate_usd", ot_usd_str)
        database.set_setting("overtime_rate", ot_usd_str)
        import re
        m = re.search(r"(\d+(\.\d+)?)", ot_usd_str)
        if m:
            database.set_setting("payroll_ot_rate", m.group(1))

        # Save mobile Wi-Fi & GPS
        database.set_setting("wifi_ssid", self.in_wifi_ssid.text().strip())
        database.set_setting("wifi_enforce", "1" if self.chk_wifi_enforce.isChecked() else "0")
        database.set_setting("clinic_public_ip", self.in_clinic_ip.text().strip())
        database.set_setting("clinic_lat", self.in_clinic_lat.text().strip())
        database.set_setting("clinic_lng", self.in_clinic_lng.text().strip())
        database.set_setting("gps_radius", self.in_gps_radius.text().strip())
        database.set_setting("gps_enforce", "1" if self.chk_gps_enforce.isChecked() else "0")

    def auto_detect_clinic_ip(self):
        try:
            import urllib.request
            ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode("utf-8").strip()
            if ip:
                self.in_clinic_ip.setText(ip)
                QMessageBox.information(self, "ជោគជ័យ", f"បានចាប់យក IP អ៊ីនធឺណិតគ្លីនិកស្វ័យប្រវត្តជោគជ័យ៖\n\nIP: {ip}\n\nសូមចុចប៊ូតុង 'រក្សាទុកការកំណត់' ដើម្បី Update។")
        except Exception as e:
            QMessageBox.warning(self, "កំហុស", f"មិនអាចទាញយក IP បានទេ៖ {e}")

        pub_url = self.in_public_url.text().strip()
        if pub_url and not pub_url.startswith("http://") and not pub_url.startswith("https://"):
            pub_url = "https://" + pub_url
        database.set_setting("mobile_public_url", pub_url)
        if pub_url:
            self.lbl_mob_info.setText(f"📱 អាសយដ្ឋាន Mobile Portal: <b style='color:#5648A6;'>{pub_url}</b>")
        else:
            from mobile_server import get_local_ip
            self.lbl_mob_info.setText(f"📱 អាសយដ្ឋាន Mobile Portal: <b style='color:#5648A6;'>http://{get_local_ip()}:5000</b>")

        lang = self.combo_lang.currentData()
        database.set_setting("language", lang)
        set_language(lang)
        self.language_changed.emit(lang)

        new_pwd = self.in_admin_pwd.text().strip() or "admin123"
        database.update_admin_password(new_pwd)

        # Save staff permissions
        perms = {}
        for key, chk in self.perm_checkboxes.items():
            perms[key] = chk.isChecked()
        database.set_staff_permissions(perms)
        self.permissions_changed.emit(perms)

        QMessageBox.information(
            self, "ជោគជ័យ (Success)",
            f"ការកំណត់គ្លីនិក និងសិទ្ធិបុគ្គលិក (Staff Permissions) ត្រូវបានរក្សាទុកដោយជោគជ័យ!\n"
            f"Settings and Staff Permissions saved successfully!\n"
            f"Admin Password: {new_pwd}"
        )

    def clear_all_old_data(self):
        reply = QMessageBox.question(
            self, "លុបឈ្មោះចាស់ៗទាំងអស់ (Clear Old Data)",
            "តើលោកអ្នកពិតជាចង់លុបឈ្មោះបុគ្គលិកចាស់ៗ និងទិន្នន័យវត្តមានសាកល្បងទាំងអស់មែនទេ?\n"
            "(ទិន្នន័យបុគ្គលិក វត្តមាន សំណើ និងប្រាក់ខែចាស់ៗទាំងអស់នឹងត្រូវលុបចេញ ដើម្បីឱ្យលោកអ្នកអាចបញ្ចូលបុគ្គលិកពិតប្រាកដរបស់គ្លីនិកបានដោយស្រស់ស្អាត)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.clear_all_staff_and_demo_data()
            self.load_settings()
            QMessageBox.information(
                self, "ជោគជ័យ (Success)",
                "ទិន្នន័យ និងឈ្មោះបុគ្គលិកចាស់ៗទាំងអស់ត្រូវបានលុបចេញដោយជោគជ័យ!\n"
                "ប្រព័ន្ធឥឡូវនេះស្ថិតក្នុងលក្ខណៈថ្មីស្រឡាង (Fresh System) រួចរាល់សម្រាប់ការចុះឈ្មោះបុគ្គលិកពិតប្រាកដ។"
            )

    def reset_demo(self):
        reply = QMessageBox.question(
            self, "Reset Demo", "Are you sure you want to re-seed demo data for Mercy Dental Care?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            conn = database.get_connection()
            c = conn.cursor()
            for tbl in ["attendance", "leave_requests", "payroll", "staff_requests", "employees", "departments", "leave_types", "settings"]:
                c.execute(f"DROP TABLE IF EXISTS {tbl}")
            conn.commit()
            conn.close()
            database.init_db()
            self.load_settings()
            self.permissions_changed.emit(database.get_staff_permissions())
            QMessageBox.information(self, "Success", "Demo data reset successfully!")
