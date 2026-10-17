"""
Design System, QSS Styles, Palette, and Bilingual Translations
for Mercy Dental Care Attendance & HR System (QT6).
"""

# Theme Colors
PRIMARY = "#5648A6"       # Click HR signature royal violet
PRIMARY_HOVER = "#6758C4"
PRIMARY_ACTIVE = "#463A8D"
PRIMARY_LIGHT = "#EEEDFB"

ACCENT = "#6366F1"
BG_MAIN = "#F6F8FB"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F8FAFC"
BORDER = "#CBD5E1"
BORDER_FOCUS = "#5648A6"

TEXT_MAIN = "#1E293B"
TEXT_MUTED = "#64748B"
TEXT_LIGHT = "#94A3B8"

SUCCESS = "#10B981"
SUCCESS_BG = "#ECFDF5"
SUCCESS_TEXT = "#065F46"

WARNING = "#F59E0B"
WARNING_BG = "#FEF3C7"
WARNING_TEXT = "#92400E"

DANGER = "#EF4444"
DANGER_BG = "#FEE2E2"
DANGER_TEXT = "#991B1B"

INFO = "#3B82F6"
INFO_BG = "#EFF6FF"
INFO_TEXT = "#1E40AF"

PURPLE_CARD_1 = "#584BA2"
PURPLE_CARD_2 = "#514397"
PURPLE_CARD_3 = "#4A3D8B"

# Bilingual Dictionary (Khmer & English)
TEXTS = {
    "en": {
        "app_title": "Mercy Dental Care - HR & Attendance Management",
        "company_name": "Mercy Dental Care",
        "company_subtitle": "Dental Clinic & Surgery",
        "good_morning": "Good Morning!",
        "good_afternoon": "Good Afternoon!",
        "administrator": "Administrator",
        "view_profile": "View Profile",
        # Navigation
        "nav_dashboard": "Dashboard",
        "nav_employees": "Employees",
        "nav_attendances": "Attendances",
        "nav_leave": "Leave",
        "nav_payroll": "Payroll",
        "nav_requests": "Requests",
        "nav_kiosk": "Quick Kiosk",
        "nav_settings": "Settings",
        # Dashboard
        "dash_title": "Dashboard",
        "dash_action": "Dashboard Action",
        "total_departments": "Total Departments",
        "total_positions": "Total Job Positions",
        "total_employees": "Total Employees",
        "gender_ratio": "Gender (Male/Female)",
        "turnover_rate": "Turnover Rate",
        "birthdays_month": "Birthdays This Month",
        "present_today": "Present Today",
        "by_departments": "By Departments",
        "new_employees": "New Employees",
        "attendance_summary": "Attendance Summary",
        "late_in": "Late In",
        "early_out": "Early Out",
        "leave": "Leave",
        # Employees
        "create_emp": "+ Create",
        "import_emp": "Import",
        "export_emp": "Export CSV",
        "col_emp_id": "Employee ID",
        "col_employee": "Employee",
        "col_work_phone": "Work Phone",
        "col_company": "Company",
        "col_department": "Department",
        "col_job_position": "Job Position",
        "col_status": "Status",
        "col_actions": "Actions",
        "search_placeholder": "Search employee by name, ID, phone...",
        "all_departments": "All Departments",
        # Profile Dialog
        "tab_work_info": "Work Information",
        "tab_resume": "Resume",
        "tab_personal_info": "Personal Information",
        "tab_contract_salary": "Contract & Salary",
        "tab_compliance": "Compliance",
        "login_users": "Login Users",
        "joining_date": "Joining Date",
        "work_email": "Work Email",
        "work_address": "Work Address",
        "coach": "Coach",
        "pin_code": "PIN Code",
        "badge_id": "Badge ID",
        "working_hours": "Working Hours",
        "btn_edit": "Edit",
        "btn_chat": "Chat",
        "btn_move_pos": "Move Position",
        "btn_print_badge": "Print Badge",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        # Attendance
        "att_today": "Today's Attendance",
        "att_check_in": "Check In",
        "att_check_out": "Checked Out",
        "col_time_in": "Time In",
        "col_time_out": "Time Out",
        "col_worked_hours": "Worked Hours",
        "col_ot_hours": "Overtime",
        "col_notes": "Notes",
        "status_on_time": "On Time",
        "status_late": "Late",
        "status_early_out": "Early Out",
        "status_absent": "Absent",
        "btn_manual_record": "+ Manual Attendance",
        "btn_quick_punch": "Punch In/Out Now",
        # Leave
        "leave_types": "Leave Types",
        "leave_requests": "Leave Requests",
        "col_display_name": "Display Name",
        "col_code": "Code",
        "col_mode": "Mode",
        "col_validation": "Validation",
        "btn_request_leave": "+ Request Leave",
        "leave_type": "Leave Type",
        "start_date": "Start Date",
        "end_date": "End Date",
        "reason": "Reason",
        "btn_approve": "Approve",
        "btn_reject": "Reject",
        "status_pending": "Pending",
        "status_approved": "Approved",
        "status_rejected": "Rejected",
        # Payroll
        "payroll_title": "Payroll",
        "btn_generate_payroll": "+ Generate Payroll",
        "payslip_title": "Open: Payslips",
        "col_payslip": "Payroll / Payslip",
        "col_period": "Date From / Period",
        "col_base_salary": "Base Salary",
        "col_worked_days": "Worked Days",
        "col_allowance": "Allowance",
        "col_gross": "Gross Salary",
        "col_net": "Net Salary",
        "wage": "Wage",
        "ot_normal": "Overtime Normal Pay",
        "ot_x15": "Overtime x1.5 Pay",
        "ot_x2": "Overtime x2 Pay",
        "tax_salary": "Tax on Salary",
        "salary_to_pay": "Amount to Pay",
        "btn_print": "Print Payslip",
        "btn_send_email": "Send By Email",
        "btn_reset_draft": "Reset to Draft",
        # Requests
        "requests_title": "Requests",
        "request_detail": "Request Detail",
        "col_req_code": "Request No",
        "col_subject": "Subject",
        "col_date": "Submit Date",
        "document_type": "Document Type",
        "description": "Description",
        "attachments": "Attachments",
        # Kiosk
        "kiosk_title": "Mercy Dental Care Kiosk",
        "digital_card": "Digital Card",
        "overtime": "Overtime",
        "approval": "Approval",
        "roster": "Roster",
        "remote_work": "Remote Work",
        "announcements": "Announcements",
        "more": "More",
        # Settings
        "settings_title": "Clinic Configuration",
        "general_settings": "General Information",
        "clinic_phone": "Contact Phone",
        "clinic_email": "Official Email",
        "clinic_address": "Clinic Location",
        "working_schedule": "Working Schedule",
        "lang_setting": "Application Language",
        "btn_save_settings": "Save Settings",
        "btn_reset_demo": "Reset Demo Data"
    },
    "kh": {
        "app_title": "គ្លីនិកធ្មេញ Mercy Dental Care - ប្រព័ន្ធគ្រប់គ្រងបុគ្គលិក & ស្រង់វត្តមាន",
        "company_name": "Mercy Dental Care",
        "company_subtitle": "គ្លីនិកព្យាបាល និងវះកាត់ធ្មេញ",
        "good_morning": "អរុណសួស្តី!",
        "good_afternoon": "ទិវាសួស្តី!",
        "administrator": "អ្នកគ្រប់គ្រង (Admin)",
        "view_profile": "មើលព័ត៌មានគណនី",
        # Navigation
        "nav_dashboard": "ផ្ទាំងព័ត៌មាន",
        "nav_employees": "បុគ្គលិក",
        "nav_attendances": "វត្តមាន",
        "nav_leave": "ច្បាប់ឈប់សម្រាក",
        "nav_payroll": "បើកប្រាក់ខែ",
        "nav_requests": "សេចក្តីជូនដំណឹងផ្សេងៗ",
        "nav_kiosk": "ស្កេនវត្តមានរហ័ស",
        "nav_settings": "ការកំណត់",
        # Dashboard
        "dash_title": "ផ្ទាំងគ្រប់គ្រងទូទៅ",
        "dash_action": "សកម្មភាពគ្រប់គ្រង",
        "total_departments": "ផ្នែកសរុប",
        "total_positions": "មុខតំណែងសរុប",
        "total_employees": "បុគ្គលិកសរុប",
        "gender_ratio": "ភេទ (ប្រុស/ស្រី)",
        "turnover_rate": "អត្រាផ្លាស់ប្តូរ",
        "birthdays_month": "ខួបកំណើតខែនេះ",
        "present_today": "វត្តមានថ្ងៃនេះ",
        "by_departments": "តាមផ្នែកការងារ",
        "new_employees": "បុគ្គលិកចូលថ្មី",
        "attendance_summary": "សង្ខេបវត្តមាន",
        "late_in": "មកយឺត",
        "early_out": "ចេញមុន",
        "leave": "ច្បាប់សម្រាក",
        # Employees
        "create_emp": "+ បង្កើតថ្មី",
        "import_emp": "នាំចូល",
        "export_emp": "នាំចេញ CSV",
        "col_emp_id": "អត្តលេខ",
        "col_employee": "ឈ្មោះបុគ្គលិក",
        "col_work_phone": "លេខទូរស័ព្ទ",
        "col_company": "ស្ថាប័ន",
        "col_department": "ផ្នែក",
        "col_job_position": "មុខតំណែង",
        "col_status": "ស្ថានភាព",
        "col_actions": "សកម្មភាព",
        "search_placeholder": "ស្វែងរកបុគ្គលិកតាម ឈ្មោះ, អត្តលេខ, ទូរស័ព្ទ...",
        "all_departments": "ផ្នែកទាំងអស់",
        # Profile Dialog
        "tab_work_info": "ព័ត៌មានការងារ",
        "tab_resume": "ប្រវត្តិរូប",
        "tab_personal_info": "ព័ត៌មានផ្ទាល់ខ្លួន",
        "tab_contract_salary": "កិច្ចសន្យា & ប្រាក់ខែ",
        "tab_compliance": "បទបញ្ជាផ្ទៃក្នុង",
        "login_users": "គណនីចូលប្រព័ន្ធ",
        "joining_date": "កាលបរិច្ឆេទចូលធ្វើការ",
        "work_email": "អ៊ីមែលការងារ",
        "work_address": "អាសយដ្ឋានកន្លែងធ្វើការ",
        "coach": "អ្នកបង្ហាត់បង្រៀន",
        "pin_code": "លេខកូដសម្ងាត់ PIN",
        "badge_id": "កាតសម្គាល់បុគ្គលិក",
        "working_hours": "ម៉ោងធ្វើការងារ",
        "btn_edit": "កែប្រែ",
        "btn_chat": "ផ្ញើសារ",
        "btn_move_pos": "ប្តូរមុខតំណែង",
        "btn_print_badge": "បោះពុម្ពកាត",
        "btn_save": "រក្សាទុក",
        "btn_cancel": "បោះបង់",
        "btn_close": "បិទ",
        # Attendance
        "att_today": "បញ្ជីវត្តមានប្រចាំថ្ងៃ",
        "att_check_in": "ចូលធ្វើការ (Check In)",
        "att_check_out": "ចេញពីធ្វើការ (Check Out)",
        "col_time_in": "ម៉ោងចូល",
        "col_time_out": "ម៉ោងចេញ",
        "col_worked_hours": "ម៉ោងធ្វើការ",
        "col_ot_hours": "ម៉ោងបន្ថែម (OT)",
        "col_notes": "កំណត់សម្គាល់",
        "status_on_time": "ទាន់ពេល",
        "status_late": "មកយឺត",
        "status_early_out": "ចេញមុនម៉ោង",
        "status_absent": "អវត្តមាន",
        "btn_manual_record": "+ បញ្ចូលវត្តមានដោយដៃ",
        "btn_quick_punch": "កត់វត្តមានភ្លាមៗ",
        # Leave
        "leave_types": "ប្រភេទច្បាប់ឈប់សម្រាក",
        "leave_requests": "សំណើសុំច្បាប់ឈប់សម្រាក",
        "col_display_name": "ឈ្មោះប្រភេទច្បាប់",
        "col_code": "កូដសម្គាល់",
        "col_mode": "របៀបអនុញ្ញាត",
        "col_validation": "អ្នកអនុម័ត",
        "btn_request_leave": "+ ស្នើសុំច្បាប់",
        "leave_type": "ប្រភេទច្បាប់",
        "start_date": "កាលបរិច្ឆេទចាប់ផ្តើម",
        "end_date": "កាលបរិច្ឆេទបញ្ចប់",
        "reason": "មូលហេតុ",
        "btn_approve": "យល់ព្រម",
        "btn_reject": "បដិសេធ",
        "status_pending": "រង់ចាំអនុម័ត",
        "status_approved": "បានយល់ព្រម",
        "status_rejected": "មិនអនុញ្ញាត",
        # Payroll
        "payroll_title": "បើកប្រាក់បៀវត្ស (Payroll)",
        "btn_generate_payroll": "+ គណនាប្រាក់ខែប្រចាំខែ",
        "payslip_title": "ប័ណ្ណបើកប្រាក់ខែ (Payslip)",
        "col_payslip": "លេខប័ណ្ណបើកប្រាក់",
        "col_period": "រយៈពេល / កាលបរិច្ឆេទ",
        "col_base_salary": "ប្រាក់ខែគោល",
        "col_worked_days": "ថ្ងៃធ្វើការ",
        "col_allowance": "ប្រាក់ឧបត្ថម្ភ",
        "col_gross": "ប្រាក់បៀវត្សសរុប",
        "col_net": "ប្រាក់ត្រូវបើកសុទ្ធ",
        "wage": "ប្រាក់ឈ្នួលគោល",
        "ot_normal": "ប្រាក់ម៉ោងបន្ថែមធម្មតា",
        "ot_x15": "ប្រាក់ម៉ោងបន្ថែម x1.5",
        "ot_x2": "ប្រាក់ម៉ោងបន្ថែម x2",
        "tax_salary": "ពន្ធលើប្រាក់បៀវត្ស",
        "salary_to_pay": "ប្រាក់ត្រូវបើកជាក់ស្តែង",
        "btn_print": "បោះពុម្ពប័ណ្ណបើកប្រាក់",
        "btn_send_email": "ផ្ញើតាមអ៊ីមែល",
        "btn_reset_draft": "កំណត់ឡើងវិញ",
        # Requests
        "requests_title": "សំណើ និងឯកសារផ្សេងៗ",
        "request_detail": "ព័ត៌មានលម្អិតនៃសំណើ",
        "col_req_code": "លេខកូដសំណើ",
        "col_subject": "ប្រធានបទ",
        "col_date": "កាលបរិច្ឆេទស្នើសុំ",
        "document_type": "ប្រភេទឯកសារ",
        "description": "ការពិពណ៌នា",
        "attachments": "ឯកសារភ្ជាប់",
        # Kiosk
        "kiosk_title": "ម៉ាស៊ីនស្កេនវត្តមាន Mercy Dental Care",
        "digital_card": "កាតឌីជីថល",
        "overtime": "ម៉ោងបន្ថែម",
        "approval": "ការអនុម័ត",
        "roster": "កាលវិភាគវេន",
        "remote_work": "ធ្វើការពីផ្ទះ",
        "announcements": "សេចក្តីជូនដំណឹង",
        "more": "ផ្សេងៗ",
        # Settings
        "settings_title": "ការកំណត់គ្លីនិក",
        "general_settings": "ព័ត៌មានទូទៅនៃគ្លីនិក",
        "clinic_phone": "លេខទូរស័ព្ទទំនាក់ទំនង",
        "clinic_email": "អ៊ីមែលផ្លូវការ",
        "clinic_address": "ទីតាំងគ្លីនិក",
        "working_schedule": "កាលវិភាគម៉ោងធ្វើការ",
        "lang_setting": "ភាសាក្នុងកម្មវិធី",
        "btn_save_settings": "រក្សាទុកការកំណត់",
        "btn_reset_demo": "កំណត់ទិន្នន័យគំរូឡើងវិញ"
    }
}

CURRENT_LANG = "kh"

def tr(key):
    """Get translated text for given key."""
    return TEXTS.get(CURRENT_LANG, TEXTS["en"]).get(key, key)

def set_language(lang):
    global CURRENT_LANG
    if lang in ("kh", "en"):
        CURRENT_LANG = lang

def setup_styled_combobox(combo):
    """Ensure QComboBox dropdown popup view and container have crisp white backgrounds."""
    from PyQt6.QtWidgets import QListView
    lv = QListView()
    combo.setView(lv)
    container = lv.parentWidget()
    if container:
        container.setStyleSheet("background-color: #FFFFFF; border: 1.5px solid #CBD5E1; border-radius: 8px;")
    lv.setStyleSheet("""
        QListView {
            background-color: #FFFFFF;
            color: #1E293B;
            border: none;
            outline: none;
            padding: 4px;
        }
        QListView::item {
            background-color: #FFFFFF;
            color: #1E293B;
            min-height: 28px;
            padding: 6px 10px;
            border-radius: 5px;
        }
        QListView::item:hover {
            background-color: #F1F5F9;
            color: #5648A6;
        }
        QListView::item:selected {
            background-color: #EDE9FE;
            color: #5648A6;
            font-weight: 600;
        }
    """)
    return combo

# Main Application Stylesheet (QSS)
APP_STYLE = f"""
* {{
    font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
    outline: none;
}}

QMainWindow, QDialog {{
    background-color: {BG_MAIN};
}}

QWidget#sidebarContainer {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}

/* Sidebar Brand */
QFrame#brandFrame {{
    border-radius: 10px;
    padding: 2px 4px;
}}

QFrame#brandFrame:hover {{
    background-color: {PRIMARY_LIGHT};
}}

QLabel#brandTitle {{
    color: {PRIMARY};
    font-size: 15px;
    font-weight: 700;
}}

QLabel#brandSubtitle {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

/* Sidebar Nav Buttons */
QPushButton.nav-btn {{
    text-align: left;
    padding: 11px 16px;
    font-size: 13px;
    font-weight: 500;
    color: {TEXT_MUTED};
    background-color: transparent;
    border: none;
    border-radius: 8px;
    margin: 2px 8px;
}}

QPushButton.nav-btn:hover {{
    color: {PRIMARY};
    background-color: {PRIMARY_LIGHT};
}}

QPushButton.nav-btn:checked {{
    color: {PRIMARY};
    background-color: {PRIMARY_LIGHT};
    font-weight: 700;
    border-left: 4px solid {PRIMARY};
}}

/* Top Header Bar */
QWidget#topHeader {{
    background-color: {SURFACE};
    border-bottom: 1px solid {BORDER};
    min-height: 60px;
    max-height: 60px;
}}

QLabel#headerBreadcrumb {{
    color: {TEXT_MUTED};
    font-size: 13px;
}}

QLabel#headerTitle {{
    color: {TEXT_MAIN};
    font-size: 17px;
    font-weight: 700;
}}

/* Cards */
QFrame.kpi-card {{
    background-color: {PURPLE_CARD_1};
    border-radius: 12px;
    border: none;
    padding: 16px;
}}

QFrame.white-card {{
    background-color: {SURFACE};
    border-radius: 12px;
    border: 1px solid {BORDER};
    padding: 16px;
}}

/* Buttons */
QPushButton.btn-primary {{
    background-color: {PRIMARY};
    color: #FFFFFF;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 18px;
    border-radius: 8px;
    border: none;
}}

QPushButton.btn-primary:hover {{
    background-color: {PRIMARY_HOVER};
}}

QPushButton.btn-primary:pressed {{
    background-color: {PRIMARY_ACTIVE};
}}

QPushButton.btn-secondary {{
    background-color: {SURFACE};
    color: {TEXT_MAIN};
    font-weight: 600;
    font-size: 13px;
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid {BORDER};
}}

QPushButton.btn-secondary:hover {{
    background-color: {SURFACE_ALT};
    border-color: {PRIMARY};
    color: {PRIMARY};
}}

QPushButton.btn-danger {{
    background-color: {DANGER};
    color: #FFFFFF;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
}}

QPushButton.btn-danger:hover {{
    background-color: #DC2626;
}}

QPushButton.btn-success {{
    background-color: {SUCCESS};
    color: #FFFFFF;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
}}

QPushButton.btn-success:hover {{
    background-color: #059669;
}}

/* Inputs */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {{
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
    color: {TEXT_MAIN};
    min-height: 22px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 2px solid {PRIMARY};
    background-color: #FFFFFF;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #CBD5E1;
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
    background-color: #F8FAFC;
}}

QComboBox::down-arrow {{
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #64748B;
    margin-right: 2px;
}}

QComboBox QAbstractItemView {{
    background-color: #FFFFFF;
    color: {TEXT_MAIN};
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {PRIMARY};
}}

QComboBox QAbstractItemView::item {{
    background-color: #FFFFFF;
    min-height: 28px;
    padding: 6px 10px;
    border-radius: 6px;
    color: {TEXT_MAIN};
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: #F1F5F9;
    color: {PRIMARY};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {PRIMARY};
    font-weight: 600;
}}

/* Modern Table Widget with Crisp, High-Visibility Gridlines */
QTableWidget {{
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    gridline-color: #CBD5E1;
    font-size: 13px;
    color: {TEXT_MAIN};
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {PRIMARY};
    outline: none;
}}

QTableWidget:focus {{
    outline: none;
}}

QTableWidget QLineEdit {{
    padding: 2px 6px;
    margin: 0px;
    border: 2px solid {PRIMARY};
    border-radius: 4px;
    background-color: #FFFFFF;
    font-size: 13px;
    color: {TEXT_MAIN};
}}

QHeaderView::section {{
    background-color: #F1F5F9;
    color: #334155;
    padding: 10px 8px;
    border: none;
    border-right: 1px solid #CBD5E1;
    border-bottom: 2px solid #94A3B8;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}}

QTableWidget::item {{
    padding: 6px 10px;
    border-right: 1px solid #CBD5E1;
    border-bottom: 1px solid #CBD5E1;
    outline: none;
}}

QTableWidget::item:focus {{
    outline: none;
}}

QTableWidget::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {PRIMARY};
    font-weight: 600;
}}

QTableWidget::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid #94A3B8;
    border-radius: 4px;
    background-color: #FFFFFF;
}}

QTableWidget::indicator:checked {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {SURFACE_ALT};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: #CBD5E1;
    min-height: 25px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #94A3B8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Tabs */
QTabWidget::pane {{
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    background-color: #FFFFFF;
    top: -1px;
}}

QTabBar::tab {{
    background: {SURFACE_ALT};
    border: 1.5px solid #CBD5E1;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 4px;
    font-size: 12px;
    font-weight: 600;
    color: {TEXT_MUTED};
}}

QTabBar::tab:selected {{
    background: #FFFFFF;
    color: {PRIMARY};
    font-weight: 700;
    border-bottom: 2px solid {PRIMARY};
}}

/* Badge Chips */
QLabel.badge-green {{
    background-color: {SUCCESS_BG};
    color: {SUCCESS_TEXT};
    border: 1px solid #A7F3D0;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel.badge-amber {{
    background-color: {WARNING_BG};
    color: {WARNING_TEXT};
    border: 1px solid #FDE68A;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel.badge-red {{
    background-color: {DANGER_BG};
    color: {DANGER_TEXT};
    border: 1px solid #FECACA;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel.badge-blue {{
    background-color: {INFO_BG};
    color: {INFO_TEXT};
    border: 1px solid #BFDBFE;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}
"""
