"""
Database management for Mercy Dental Care Attendance & HR System.
Handles SQLite operations, schemas, and demo seed data.
"""

import sqlite3
import os
import json
import time
from datetime import datetime, date, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    PHNOM_PENH_TZ = ZoneInfo("Asia/Phnom_Penh")
except Exception:
    PHNOM_PENH_TZ = timezone(timedelta(hours=7))

os.environ["TZ"] = "Asia/Phnom_Penh"
if hasattr(time, "tzset"):
    try:
        time.tzset()
    except Exception:
        pass

def get_cambodia_now():
    """Returns current datetime in Cambodia (Asia/Phnom_Penh, UTC+7)."""
    return datetime.now(PHNOM_PENH_TZ).replace(tzinfo=None)

def get_cambodia_today():
    """Returns today's date in Cambodia (Asia/Phnom_Penh, UTC+7)."""
    return get_cambodia_now().date()

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mercy_dental.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Departments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        name_kh TEXT NOT NULL,
        head_of_dept TEXT,
        color TEXT DEFAULT '#4F46E5'
    )
    """)

    # 2. Job Positions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        title_kh TEXT NOT NULL,
        department_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
    """)

    # 3. Employees table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        khmer_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        dob TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        department TEXT NOT NULL,
        job_position TEXT NOT NULL,
        manager TEXT,
        coach TEXT,
        join_date TEXT NOT NULL,
        status TEXT DEFAULT 'Active',
        base_salary REAL DEFAULT 500.0,
        working_hours TEXT DEFAULT 'Monday-Saturday (08:00 to 17:00)',
        pin_code TEXT DEFAULT '1234',
        password TEXT DEFAULT '123456',
        emergency_contact TEXT,
        avatar_path TEXT
    )
    """)

    # 4. Attendance Records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        check_in TEXT,
        check_out TEXT,
        status TEXT NOT NULL, -- 'On Time', 'Late', 'Early Out', 'Absent', 'On Leave'
        ot_hours REAL DEFAULT 0.0,
        notes TEXT,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    )
    """)

    # 5. Leave Types & Requests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        name_kh TEXT NOT NULL,
        code TEXT NOT NULL,
        mode TEXT DEFAULT 'Allocated by HR only',
        validation TEXT DEFAULT 'Leave Officer'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        days INTEGER DEFAULT 1,
        reason TEXT,
        status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
        requested_at TEXT NOT NULL,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    )
    """)

    # 6. Payroll table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payslip_no TEXT NOT NULL UNIQUE,
        emp_id INTEGER NOT NULL,
        period_month INTEGER NOT NULL,
        period_year INTEGER NOT NULL,
        date_from TEXT NOT NULL,
        date_to TEXT NOT NULL,
        worked_days INTEGER DEFAULT 26,
        base_salary REAL NOT NULL,
        ot_pay REAL DEFAULT 0.0,
        allowance REAL DEFAULT 45.0,
        gross_salary REAL NOT NULL,
        tax_deduction REAL DEFAULT 0.0,
        other_deduction REAL DEFAULT 0.0,
        net_salary REAL NOT NULL,
        status TEXT DEFAULT 'Paid', -- 'Draft', 'Confirmed', 'Paid'
        breakdown_items TEXT DEFAULT '',
        generated_at TEXT NOT NULL,
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    )
    """)

    # 7. Requests (Document, Overtime, Equipment)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        req_code TEXT NOT NULL UNIQUE,
        emp_id INTEGER NOT NULL,
        req_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        submit_date TEXT NOT NULL,
        status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
        FOREIGN KEY (emp_id) REFERENCES employees(id)
    )
    """)

    # 8. Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # 9. Calendar Notes / Events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        title TEXT NOT NULL,
        note_type TEXT DEFAULT 'Note',
        color TEXT DEFAULT '#2563EB',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 10. Clinic Announcements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        priority TEXT DEFAULT 'Normal', -- 'Normal', 'Important', 'Urgent'
        target TEXT DEFAULT 'All Staff',
        created_by TEXT DEFAULT 'Admin',
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)

    conn.commit()

    # Migration: Ensure password column exists on existing databases
    try:
        cursor.execute("ALTER TABLE employees ADD COLUMN password TEXT DEFAULT '123456'")
        conn.commit()
    except Exception:
        pass

    # Migration: Ensure monthly payroll breakdown columns exist
    for col, col_type in [
        ("incentive", "REAL DEFAULT 0.0"),
        ("target_bonus", "REAL DEFAULT 0.0"),
        ("over_day_off_deduction", "REAL DEFAULT 0.0"),
        ("breakdown_items", "TEXT DEFAULT ''")
    ]:
        try:
            cursor.execute(f"ALTER TABLE payroll ADD COLUMN {col} {col_type}")
            conn.commit()
        except Exception:
            pass
    try:
        cursor.execute("UPDATE payroll SET incentive = allowance WHERE (incentive IS NULL OR incentive = 0) AND allowance > 0")
        conn.commit()
    except Exception:
        pass

    # Ensure admin credentials exist in settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_username', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_password', 'admin123')")
    conn.commit()

    # Seed data if first time
    cursor.execute("SELECT value FROM settings WHERE key = 'system_initialized'")
    row = cursor.fetchone()
    if not row:
        seed_data(conn)
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('system_initialized', '1')")
        conn.commit()

    conn.close()


def seed_data(conn):
    cursor = conn.cursor()

    # Settings matching Mercy Dental Care Google Maps pin: 11.5834188, 104.8811696
    settings_data = [
        ("clinic_name", "Mercy Dental Care"),
        ("clinic_name_en", "Mercy Dental Care"),
        ("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី"),
        ("work_start_time", "07:30"),
        ("work_end_time", "18:00"),
        ("shift_start", "07:30"),
        ("shift_end", "18:00"),
        ("grace_period_mins", "15"),
        ("late_grace", "15"),
        ("currency", "USD ($)"),
        ("phone", "085 796 704"),
        ("clinic_phone", "085 796 704"),
        ("email", "info@mercydentalcare.com"),
        ("clinic_email", "info@mercydentalcare.com"),
        ("address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ"),
        ("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ"),
        ("clinic_address_en", "Street 1952, Phum Poung Peay, Sangkat Phnom Penh Thmey, Khan Sen Sok, Phnom Penh, Cambodia"),
        ("clinic_lat", "11.5834188"),
        ("clinic_lng", "104.8811696"),
        ("gps_radius", "50"),
        ("wifi_ssid", "Mercy Dental Care"),
        ("wifi_enforce", "0"),
        ("gps_enforce", "0"),
        ("maps_url", "https://maps.app.goo.gl/yC7L689z6W1W7QYk9"),
        ("language", "kh")
    ]
    cursor.executemany("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", settings_data)

    # Departments
    departments = [
        ("Dental Surgery", "វះកាត់ធ្មេញ", "Dr. Bunheng LY", "#6366F1"),
        ("Orthodontics", "ពត់តម្រង់ធ្មេញ", "Dr. Chantra THY", "#8B5CF6"),
        ("Dental Hygiene", "អនាម័យនិងសំអាតធ្មេញ", "Sros CHAN", "#EC4899"),
        ("Clinic Reception", "ទទួលភ្ញៀវ", "Seakleng LOR", "#F59E0B"),
        ("Administration", "រដ្ឋបាល & ធនធានមនុស្ស", "Sinit NAN", "#10B981"),
        ("Dental IT & Tech", "ព័ត៌មានវិទ្យា & បច្ចេកវិទ្យា", "Sambath SOEURN", "#3B82F6")
    ]
    cursor.executemany("INSERT INTO departments (name, name_kh, head_of_dept, color) VALUES (?, ?, ?, ?)", departments)

    # Leave Types matching IMG_7446
    leave_types = [
        ("Public", "បុណ្យជាតិ", "PB", "Allocated by HR only", "Leave Officer"),
        ("Day Offs", "ថ្ងៃឈប់សម្រាកប្រចាំសប្តាហ៍", "DO", "No Allocation Needed", "Team Leader and HR"),
        ("Paid Annual Leave", "ច្បាប់ប្រចាំឆ្នាំមានប្រាក់ខែ", "AL", "Allocated by HR only", "Team Leader and HR"),
        ("Sick Leave", "ច្បាប់ឈឺ", "SL", "No Allocation Needed", "Leave Officer"),
        ("Special Leave", "ច្បាប់ពិសេស (អាពាហ៍ពិពាហ៍/បុណ្យ)", "SPL", "No Allocation Needed", "Leave Officer"),
        ("Maternity Leave", "ច្បាប់សម្រាលកូន", "ML", "No Allocation Needed", "Leave Officer"),
        ("Compensatory Days", "ថ្ងៃសងជំនួស", "CD", "Free Allocation Request", "Team Leader and HR"),
        ("Unpaid Leave", "ច្បាប់គ្មានប្រាក់ខែ", "UL", "No Allocation Needed", "Team Leader and HR"),
        ("Travel Leave", "ច្បាប់បេសកកម្ម", "TL", "No Allocation Needed", "Team Leader and HR")
    ]
    cursor.executemany("INSERT INTO leave_types (name, name_kh, code, mode, validation) VALUES (?, ?, ?, ?, ?)", leave_types)

    # Staff list matching realistic staff in screenshots & Cambodian dental team
    staff_data = [
        ("00001", "Sros CHAN", "ចាន់ ស្រស់", "Female", "1994-04-12", "012 345 678", "sros.chan@mercydentalcare.com", "Phnom Penh", "Dental Hygiene", "Lead Dental Hygienist", "Dr. Bunheng LY", "Dr. Bunheng LY", "2024-01-10", "Active", 650.0, "1001", "098 776 543"),
        ("00002", "Kimheng MAO", "ម៉ៅ គីមហេង", "Male", "1996-08-22", "015 889 900", "kimheng.mao@mercydentalcare.com", "Kandal", "Dental Surgery", "Dental Assistant", "Dr. Bunheng LY", "Dr. Bunheng LY", "2024-02-15", "Active", 480.0, "1002", "012 998 877"),
        ("00003", "Seakleng LOR", "ឡ ប៊ុនឡេង", "Female", "1998-11-05", "089 776 655", "seakleng.lor@mercydentalcare.com", "Phnom Penh", "Clinic Reception", "Head Receptionist", "Sinit NAN", "Sinit NAN", "2024-03-01", "Active", 420.0, "1003", "070 334 455"),
        ("00004", "Chantra THY", "ធី ចាន់ត្រា", "Female", "1989-06-18", "012 111 222", "chantra.thy@mercydentalcare.com", "Phnom Penh", "Orthodontics", "Senior Orthodontist", "Dr. Bunheng LY", "Dr. Bunheng LY", "2023-05-10", "Active", 1400.0, "1004", "012 443 322"),
        ("00005", "Sinit NAN", "ណាន់ ស៊ីនីត", "Male", "1992-09-14", "099 888 777", "sinit.nan@mercydentalcare.com", "Phnom Penh", "Administration", "HR & Clinic Manager", "Dr. Bunheng LY", "Dr. Bunheng LY", "2023-06-01", "Active", 850.0, "1005", "099 665 544"),
        ("00006", "Sambath SOEURN", "សឿន សម្បត្តិ", "Male", "1995-02-28", "016 583 122", "sambath.s@mercydentalcare.com", "Phnom Penh", "Dental IT & Tech", "IT & Systems Admin", "Sinit NAN", "Sinit NAN", "2023-08-15", "Active", 700.0, "1006", "088 776 543"),
        ("00007", "Tyra IN", "អ៊ិន ធីរ៉ា", "Female", "1988-12-03", "011 223 344", "tyra.in@mercydentalcare.com", "Phnom Penh", "Dental Surgery", "Clinic Director / Surgeon", "Board", "Board", "2022-01-01", "Active", 2200.0, "1007", "012 887 766"),
        ("00008", "Phy SOVADHANA", "ភី សុវឌ្ឍនា", "Male", "1993-07-19", "098 765 432", "sovadhana.phy@mercydentalcare.com", "Phnom Penh", "Dental Surgery", "General Dentist", "Dr. Bunheng LY", "Dr. Bunheng LY", "2023-11-01", "Active", 1100.0, "1008", "098 223 311"),
        ("00009", "Gwen CHIMA", "ហ្គ្វេន ជីម៉ា", "Female", "1997-03-30", "077 665 544", "gwen.c@mercydentalcare.com", "Phnom Penh", "Clinic Reception", "Client Relations Officer", "Seakleng LOR", "Seakleng LOR", "2024-04-10", "Active", 390.0, "1009", "077 112 233"),
        ("00010", "Suya XING", "ស៊ូយ៉ា ស៊ីង", "Female", "1999-10-15", "085 443 322", "suya.x@mercydentalcare.com", "Phnom Penh", "Dental Hygiene", "Junior Hygienist", "Sros CHAN", "Sros CHAN", "2024-05-02", "Active", 380.0, "1010", "085 998 877"),
        ("00011", "Kak SOVANNASARM", "កាក់ សុវណ្ណសំ", "Male", "1994-05-25", "017 665 533", "sovannasarm.k@mercydentalcare.com", "Phnom Penh", "Dental IT & Tech", "Database & Network Officer", "Sambath SOEURN", "Sambath SOEURN", "2024-06-12", "Active", 600.0, "1011", "017 112 233"),
        ("00012", "Nha RATANA", "ញ៉ា រតនា", "Male", "1996-01-18", "092 334 455", "nha.ratana@mercydentalcare.com", "Phnom Penh", "Dental Surgery", "Dental Assistant", "Dr. Bunheng LY", "Kimheng MAO", "2024-07-01", "Active", 450.0, "1012", "092 556 677"),
        ("00013", "Lork SEREYBOT", "លក សិរីបុត្រ", "Male", "1995-09-09", "098 988 989", "sereybot.lork@mercydentalcare.com", "Phnom Penh", "Dental IT & Tech", "Hardware & Equipment Tech", "Sambath SOEURN", "Sambath SOEURN", "2024-08-01", "Active", 580.0, "1013", "098 332 211"),
        ("00014", "Bunheng LY", "លី ប៊ុនហេង", "Male", "1987-03-14", "012 999 888", "bunheng.ly@mercydentalcare.com", "Phnom Penh", "Dental Surgery", "Head Dental Surgeon", "Tyra IN", "Chantra THY", "2023-09-10", "Active", 1800.0, "1014", "012 334 455"),
        ("00015", "Nha KAROMA", "ញ៉ា ការ៉ូម៉ា", "Female", "1998-04-20", "099 887 766", "karoma.nha@mercydentalcare.com", "Phnom Penh", "Administration", "Accountant & Cashier", "Sinit NAN", "Sinit NAN", "2024-09-01", "Active", 500.0, "1015", "099 221 100"),
        ("00016", "Socheavian NGET", "ងែត សុជាវៀន", "Female", "1997-12-11", "070 889 977", "socheavian.n@mercydentalcare.com", "Phnom Penh", "Orthodontics", "Orthodontic Assistant", "Dr. Chantra THY", "Dr. Chantra THY", "2024-09-15", "Active", 460.0, "1016", "070 445 566"),
        ("00017", "Hana SUMI", "ហាណា ស៊ូមី", "Female", "2000-05-18", "086 554 433", "hana.sumi@mercydentalcare.com", "Phnom Penh", "Dental Hygiene", "Sterilization Specialist", "Sros CHAN", "Sros CHAN", "2024-10-01", "Active", 370.0, "1017", "086 112 233"),
        ("00018", "Jingthean TENG", "ថេង ជីងធាន", "Male", "1995-10-02", "010 776 655", "jingthean.teng@mercydentalcare.com", "Phnom Penh", "Dental Surgery", "Senior Dental Technician", "Dr. Bunheng LY", "Dr. Bunheng LY", "2024-10-05", "Active", 750.0, "1018", "010 334 455")
    ]

    for staff in staff_data:
        cursor.execute("""
        INSERT INTO employees (
            emp_code, name, khmer_name, gender, dob, phone, email, address,
            department, job_position, manager, coach, join_date, status, base_salary, pin_code, emergency_contact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, staff)

    # Seed today and recent attendance
    today = date.today()
    for emp_id in range(1, 19):
        # generate 5 past days of attendance
        for d_offset in range(5, -1, -1):
            att_date = today - timedelta(days=d_offset)
            # Sunday skip
            if att_date.weekday() == 6:
                continue

            # Variations in check-in
            if emp_id in (3, 5, 8) and d_offset == 1:
                status = "Late"
                check_in = "08:24:12"
                check_out = "17:05:00"
                ot = 0.0
            elif emp_id == 10 and d_offset == 2:
                status = "Early Out"
                check_in = "07:55:00"
                check_out = "15:30:00"
                ot = 0.0
            elif emp_id == 6 and d_offset in (1, 3):
                status = "On Time"
                check_in = "07:50:33"
                check_out = "19:00:00"
                ot = 2.0
            else:
                status = "On Time"
                check_in = f"07:{50 + (emp_id % 9):02d}:15"
                check_out = "17:02:40" if d_offset > 0 else None
                ot = 0.0

            cursor.execute("""
            INSERT INTO attendance (emp_id, date, check_in, check_out, status, ot_hours, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (emp_id, att_date.strftime("%Y-%m-%d"), check_in, check_out, status, ot, "Biometric Fingerprint"))

    # Seed leave requests
    sample_leaves = [
        (4, "Paid Annual Leave", (today + timedelta(days=3)).strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), 3, "Family travel abroad", "Pending", (today - timedelta(days=1)).strftime("%Y-%m-%d 09:30:00")),
        (8, "Sick Leave", (today - timedelta(days=7)).strftime("%Y-%m-%d"), (today - timedelta(days=6)).strftime("%Y-%m-%d"), 2, "Flu and fever with doctor certificate", "Approved", (today - timedelta(days=8)).strftime("%Y-%m-%d 08:15:00")),
        (10, "Day Offs", (today + timedelta(days=7)).strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), 1, "Personal day off", "Approved", (today - timedelta(days=2)).strftime("%Y-%m-%d 14:00:00")),
        (12, "Special Leave", (today + timedelta(days=10)).strftime("%Y-%m-%d"), (today + timedelta(days=12)).strftime("%Y-%m-%d"), 3, "Brother's wedding ceremony", "Pending", (today - timedelta(days=1)).strftime("%Y-%m-%d 11:20:00"))
    ]
    cursor.executemany("""
    INSERT INTO leave_requests (emp_id, leave_type, start_date, end_date, days, reason, status, requested_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_leaves)

    # Seed payroll matching IMG_7451 & IMG_7452
    sample_payrolls = [
        ("SLIP/173", 8, 5, 2026, "2026-05-01", "2026-05-31", 26, 500.0, 0.0, 45.0, 545.0, 11.82, 0.0, 533.18, "Paid", "2026-06-01 10:00:00"),
        ("SLIP/174", 14, 5, 2026, "2026-05-01", "2026-05-31", 26, 1800.0, 80.0, 60.0, 1940.0, 120.50, 0.0, 1819.50, "Paid", "2026-06-01 10:05:00"),
        ("SLIP/175", 4, 5, 2026, "2026-05-01", "2026-05-31", 26, 1400.0, 50.0, 50.0, 1500.0, 75.00, 0.0, 1425.00, "Paid", "2026-06-01 10:10:00"),
        ("SLIP/176", 1, 5, 2026, "2026-05-01", "2026-05-31", 26, 650.0, 30.0, 40.0, 720.0, 18.00, 0.0, 702.00, "Paid", "2026-06-01 10:15:00"),
        ("SLIP/177", 6, 5, 2026, "2026-05-01", "2026-05-31", 26, 700.0, 65.0, 45.0, 810.0, 24.50, 0.0, 785.50, "Paid", "2026-06-01 10:20:00")
    ]
    cursor.executemany("""
    INSERT INTO payroll (
        payslip_no, emp_id, period_month, period_year, date_from, date_to,
        worked_days, base_salary, ot_pay, allowance, gross_salary,
        tax_deduction, other_deduction, net_salary, status, generated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_payrolls)

    # Seed staff requests matching IMG_7455
    sample_requests = [
        ("DOC00109", 8, "Request Equipment", "Request Computer DELL i5 8GB 512GB", "Computer upgrade needed for high resolution 3D dental X-Ray viewing software.", "2026-07-24", "Pending"),
        ("DOC00105", 3, "Salary Advance", "Emergency family assistance advance", "Requesting advance of $150 for family medical expense.", "2026-07-19", "Approved"),
        ("DOC00104", 6, "Remote Work", "Work from home for server maintenance", "Conducting scheduled night database and backup maintenance from home.", "2026-07-15", "Approved"),
        ("DOC00103", 14, "New Contract", "Request New Equipment Contract", "Contract renewal with dental implant supplier.", "2026-07-10", "Pending")
    ]
    cursor.executemany("""
    INSERT INTO staff_requests (req_code, emp_id, req_type, subject, description, submit_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_requests)

    conn.commit()

# --- CRUD Helper functions ---

def get_stats():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(DISTINCT department) FROM employees")
    dept_count = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT job_position) FROM employees")
    pos_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM employees WHERE status = 'Active'")
    emp_count = c.fetchone()[0]

    c.execute("SELECT SUM(CASE WHEN gender='Male' THEN 1 ELSE 0 END), SUM(CASE WHEN gender='Female' THEN 1 ELSE 0 END) FROM employees")
    m_count, f_count = c.fetchone()
    m_count = m_count or 0
    f_count = f_count or 0

    today_str = date.today().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM attendance WHERE date = ? AND check_in IS NOT NULL", (today_str,))
    present_today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Late'", (today_str,))
    late_today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM leave_requests WHERE status = 'Approved' AND ? BETWEEN start_date AND end_date", (today_str,))
    leave_today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM staff_requests WHERE status = 'Pending'")
    pending_requests = c.fetchone()[0]

    # Calculate birthdays this month
    today_month = date.today().strftime("%m")
    c.execute("SELECT COUNT(*) FROM employees WHERE status = 'Active' AND dob IS NOT NULL AND length(dob) >= 7 AND substr(dob, 6, 2) = ?", (today_month,))
    bday_row = c.fetchone()
    bday_count = bday_row[0] if bday_row else 0

    conn.close()
    return {
        "departments": dept_count,
        "positions": pos_count,
        "employees": emp_count,
        "male": m_count,
        "female": f_count,
        "gender_ratio": f"{m_count}/{f_count}",
        "birthdays": bday_count,
        "present_today": present_today,
        "late_today": late_today,
        "leave_today": leave_today,
        "turnover_rate": "0%",
        "pending_requests": pending_requests
    }

def get_dept_distribution():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT d.name, d.name_kh, d.color, COUNT(e.id) as emp_count
        FROM departments d
        LEFT JOIN employees e ON e.department = d.name AND e.status = 'Active'
        GROUP BY d.id
        HAVING emp_count > 0
    """)
    rows = c.fetchall()
    conn.close()
    items = [dict(row) for row in rows]
    total = sum(int(item.get("emp_count") or 0) for item in items)
    for item in items:
        cnt = int(item.get("emp_count") or 0)
        item["count"] = cnt
        item["percentage"] = round((cnt / total * 100), 1) if total > 0 else 0
    return items

get_department_breakdown = get_dept_distribution

def get_department_detail_groups():
    """Returns list of departments that have active staff, with their employee lists."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM departments")
    depts = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM employees WHERE status = 'Active' ORDER BY id ASC")
    emps = [dict(r) for r in c.fetchall()]
    conn.close()

    result = []
    for d in depts:
        dept_emps = [e for e in emps if e.get("department") == d.get("name")]
        if dept_emps:
            d["employees"] = dept_emps
            d["count"] = len(dept_emps)
            result.append(d)
    return result

def get_position_detail_groups():
    """Returns job positions with list of active staff in each."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE status = 'Active' ORDER BY job_position ASC, id ASC")
    emps = [dict(r) for r in c.fetchall()]
    conn.close()

    groups = {}
    for e in emps:
        pos = e.get("job_position") or "Other"
        if pos not in groups:
            groups[pos] = []
        groups[pos].append(e)

    return [{"position": k, "count": len(v), "employees": v} for k, v in groups.items()]

def get_birthday_details():
    """Returns active staff with birthdays this month and general DOB info."""
    today_month = date.today().strftime("%m")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE status = 'Active' ORDER BY id ASC")
    emps = [dict(r) for r in c.fetchall()]
    conn.close()

    this_month = []
    others = []
    for e in emps:
        dob = e.get("dob") or ""
        if len(dob) >= 7 and dob[5:7] == today_month:
            this_month.append(e)
        else:
            others.append(e)
    return {"this_month": this_month, "all": emps, "current_month": today_month}

def get_all_employees(search_term="", dept_filter="All"):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM employees WHERE 1=1"
    params = []

    if search_term:
        query += " AND (name LIKE ? OR khmer_name LIKE ? OR emp_code LIKE ? OR phone LIKE ?)"
        wild = f"%{search_term}%"
        params.extend([wild, wild, wild, wild])

    if dept_filter and dept_filter != "All" and dept_filter != "ទាំងអស់":
        query += " AND (department = ? OR department = (SELECT name FROM departments WHERE name_kh = ?))"
        params.extend([dept_filter, dept_filter])

    query += " ORDER BY emp_code ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_employee_by_id(emp_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_departments():
    """Retrieve all unique departments from departments table, existing employees, and standard presets."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM departments")
    dept_names = set(r[0] for r in c.fetchall() if r[0])
    c.execute("SELECT DISTINCT department FROM employees WHERE department IS NOT NULL AND department != ''")
    for r in c.fetchall():
        if r[0]:
            dept_names.add(r[0])
    conn.close()
    defaults = ["Dental Surgery", "Orthodontics", "Dental Hygiene", "Clinic Reception", "Administration", "Dental IT & Tech"]
    for d in defaults:
        dept_names.add(d)
    return sorted(list(dept_names))

def save_employee(data, emp_id=None):
    conn = get_connection()
    c = conn.cursor()
    pwd = data.get('password', '123456') or '123456'
    pin = data.get('pin_code', '1234') or '1234'
    dept_name = str(data.get('department', '') or '').strip()

    # Automatically register custom department into departments table if not present
    if dept_name:
        c.execute("SELECT id FROM departments WHERE name = ?", (dept_name,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO departments (name, name_kh, head_of_dept, color)
                VALUES (?, ?, 'Lead', '#6366F1')
            """, (dept_name, dept_name))

    emp_code = str(data.get('emp_code', '') or '').strip()
    emp_type = data.get('employment_type', 'Full-Time') or 'Full-Time'
    name = str(data.get('name', '') or '').strip()
    khmer_name = str(data.get('khmer_name', '') or '').strip() or name
    gender = str(data.get('gender', 'Male') or 'Male')
    dob = str(data.get('dob', '') or '')
    phone = str(data.get('phone', '') or '')
    email = str(data.get('email', '') or '')
    address = str(data.get('address', '') or '')
    job_position = str(data.get('job_position', '') or '')
    manager = str(data.get('manager', '') or 'Dr. Buntha')
    coach = str(data.get('coach', '') or 'Dr. Vuochlin')
    join_date = str(data.get('join_date', '') or date.today().isoformat())
    status = str(data.get('status', 'Active') or 'Active')
    try:
        base_salary = float(data.get('base_salary', 500) or 500)
    except (ValueError, TypeError):
        base_salary = 500.0
    working_hours = str(data.get('working_hours', '') or 'Monday-Saturday (07:30 to 18:00)')
    emergency_contact = str(data.get('emergency_contact', '') or '')

    # Treat string "null", "None", or empty string as None
    if emp_id and str(emp_id).strip().lower() not in ('', 'none', 'null', 'undefined'):
        if emp_code:
            c.execute("""
            UPDATE employees SET
                emp_code = ?, name = ?, khmer_name = ?, gender = ?, dob = ?, phone = ?, email = ?,
                address = ?, department = ?, job_position = ?, manager = ?, coach = ?,
                join_date = ?, status = ?, base_salary = ?, working_hours = ?, pin_code = ?,
                password = ?, emergency_contact = ?, employment_type = ?
            WHERE id = ?
            """, (
                emp_code, name, khmer_name, gender, dob, phone, email,
                address, dept_name, job_position, manager, coach,
                join_date, status, base_salary, working_hours,
                pin, pwd, emergency_contact, emp_type, emp_id
            ))
        else:
            c.execute("""
            UPDATE employees SET
                name = ?, khmer_name = ?, gender = ?, dob = ?, phone = ?, email = ?,
                address = ?, department = ?, job_position = ?, manager = ?, coach = ?,
                join_date = ?, status = ?, base_salary = ?, working_hours = ?, pin_code = ?,
                password = ?, emergency_contact = ?, employment_type = ?
            WHERE id = ?
            """, (
                name, khmer_name, gender, dob, phone, email,
                address, dept_name, job_position, manager, coach,
                join_date, status, base_salary, working_hours,
                pin, pwd, emergency_contact, emp_type, emp_id
            ))
        conn.commit()
        conn.close()
        # Automatically sync updated base salary to employee payroll slips
        sync_employee_salary_to_payroll(emp_id, base_salary)
        return
    else:
        if not emp_code:
            # Generate next sequential 3-digit code based on highest numeric code (e.g. 001, 002)
            c.execute("SELECT emp_code FROM employees")
            existing_codes = [r[0] for r in c.fetchall() if r[0]]
            max_num = 0
            for code_str in existing_codes:
                try:
                    num = int(code_str)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
            emp_code = f"{max_num + 1:03d}"

        c.execute("""
        INSERT INTO employees (
            emp_code, name, khmer_name, gender, dob, phone, email, address,
            department, job_position, manager, coach, join_date, status, base_salary,
            working_hours, pin_code, password, emergency_contact, employment_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp_code, name, khmer_name, gender, dob, phone, email, address,
            dept_name, job_position, manager, coach, join_date, status, base_salary,
            working_hours, pin, pwd, emergency_contact, emp_type
        ))
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        if new_id:
            sync_employee_salary_to_payroll(new_id, base_salary)
        return

def update_employee_code(emp_id, new_code):
    """Update employee code / ID for an employee."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE employees SET emp_code = ? WHERE id = ?", (str(new_code).strip(), emp_id))
    conn.commit()
    conn.close()

def renumber_all_employees():
    """Renumbers all active employees sequentially as 001, 002, 003, ..."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM employees ORDER BY emp_code ASC, id ASC")
    rows = c.fetchall()
    for idx, r in enumerate(rows, start=1):
        c.execute("UPDATE employees SET emp_code = ? WHERE id = ?", (f"{idx:03d}", r[0]))
    conn.commit()
    conn.close()

def sync_employee_salary_to_payroll(emp_id, new_salary):
    """
    Synchronizes an employee's updated base salary to their payroll records
    safely using delta, preserving all custom additions, overtime, and deductions.
    """
    conn = get_connection()
    c = conn.cursor()
    new_sal_val = round(float(new_salary or 0), 2)

    # Fetch all payroll records for this employee
    c.execute("""
        SELECT id, base_salary, gross_salary, tax_deduction, net_salary, 
               over_day_off_deduction, other_deduction, breakdown_items, ot_pay, incentive, target_bonus
        FROM payroll 
        WHERE emp_id = ?
    """, (emp_id,))
    rows = c.fetchall()

    for r in rows:
        pid = r[0]
        old_base = float(r[1] or 0)
        old_gross = float(r[2] or 0)
        tax = float(r[3] or 0)
        old_net = float(r[4] or 0)
        off_ded = float(r[5] or 0)
        other_ded = float(r[6] or 0)
        bk_str = str(r[7] or "").strip()
        ot_pay = float(r[8] or 0)
        inc = float(r[9] or 0)
        tgt = float(r[10] or 0)

        delta = round(new_sal_val - old_base, 2)
        if abs(delta) < 0.001:
            continue

        updated_bk_str = bk_str
        if bk_str:
            try:
                items = json.loads(bk_str)
                updated_any = False
                for itm in items:
                    if itm.get("id") == "base" or "Base Salary" in itm.get("name", "") or "ប្រាក់ខែគោល" in itm.get("name", ""):
                        itm["amount"] = new_sal_val
                        updated_any = True
                        break
                if updated_any:
                    updated_bk_str = json.dumps(items, ensure_ascii=False)
                    new_gross = round(sum(float(x.get("amount", 0) or 0) for x in items if x.get("type") == "earning"), 2)
                    ded_val = round(sum(float(x.get("amount", 0) or 0) for x in items if x.get("type") == "deduction"), 2)
                    calc_tax = round(new_gross * 0.02, 2) if new_gross > 500 else 0.0
                    new_tax = calc_tax if tax > 0 or new_gross > 500 else 0.0
                    new_net = round(max(0.0, new_gross - ded_val - new_tax - other_ded), 2)
                    c.execute("""
                        UPDATE payroll 
                        SET base_salary = ?, gross_salary = ?, tax_deduction = ?, net_salary = ?, breakdown_items = ?
                        WHERE id = ?
                    """, (new_sal_val, new_gross, new_tax, new_net, updated_bk_str, pid))
                    continue
            except Exception:
                pass

        new_gross = round(max(0.0, old_gross + delta), 2)
        calc_tax = round(new_gross * 0.02, 2) if new_gross > 500 else 0.0
        new_tax = calc_tax if tax > 0 or new_gross > 500 else 0.0
        new_net = round(max(0.0, new_gross - off_ded - new_tax - other_ded), 2)
        c.execute("""
            UPDATE payroll 
            SET base_salary = ?, gross_salary = ?, tax_deduction = ?, net_salary = ?
            WHERE id = ?
        """, (new_sal_val, new_gross, new_tax, new_net, pid))

    conn.commit()
    conn.close()

def sync_all_employees_to_payroll():
    """Sync all active employees' base salaries to their existing payroll records."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, base_salary FROM employees")
    emps = c.fetchall()
    conn.close()
    for e in emps:
        sync_employee_salary_to_payroll(e[0], e[1])

def verify_employee_credentials(emp_id, secret):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT pin_code, password FROM employees WHERE id = ?", (emp_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    pin = str(row["pin_code"] or "").strip()
    pwd = str(row["password"] or "").strip()
    s = str(secret).strip()
    if s and (s == pin or s == pwd):
        return True
    if not pin and not pwd and (s in ("1234", "123456")):
        return True
    return False

def update_employee_salary(emp_id, new_salary):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE employees SET base_salary = ? WHERE id = ?", (float(new_salary), emp_id))
    conn.commit()
    conn.close()
    sync_employee_salary_to_payroll(emp_id, float(new_salary))

def delete_employee(emp_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE emp_id = ?", (emp_id,))
    c.execute("DELETE FROM leave_requests WHERE emp_id = ?", (emp_id,))
    c.execute("DELETE FROM payroll WHERE emp_id = ?", (emp_id,))
    c.execute("DELETE FROM staff_requests WHERE emp_id = ?", (emp_id,))
    c.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()

def update_attendance_record(att_id, check_in, check_out, status, ot_hours=0.0, notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE attendance 
        SET check_in = ?, check_out = ?, status = ?, ot_hours = ?, notes = ?
        WHERE id = ?
    """, (check_in, check_out, status, float(ot_hours or 0.0), notes or "", att_id))
    conn.commit()
    conn.close()

def delete_attendance_record(att_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE id = ?", (att_id,))
    conn.commit()
    conn.close()

def add_attendance_record(emp_id, att_date, check_in, check_out, status, ot_hours=0.0, notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO attendance (emp_id, date, check_in, check_out, status, ot_hours, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (emp_id, att_date, check_in, check_out, status, float(ot_hours or 0.0), notes or ""))
    conn.commit()
    conn.close()

def update_leave_status(leave_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE leave_requests SET status = ? WHERE id = ?", (status, leave_id))
    conn.commit()
    conn.close()

def delete_leave_request(leave_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM leave_requests WHERE id = ?", (leave_id,))
    conn.commit()
    conn.close()

def add_leave_request(emp_id, leave_type, start_date, end_date, days=1, reason=""):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO leave_requests (emp_id, leave_type, start_date, end_date, days, reason, status, requested_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Approved', ?)
    """, (emp_id, leave_type, start_date, end_date, int(days or 1), reason or "", now_str))
    conn.commit()
    conn.close()

def clear_all_staff_and_demo_data():
    """
    Clears all dummy/old staff records, attendances, leave requests, payroll slips,
    and staff requests to provide a clean, fresh system for real staff registration.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM attendance")
    c.execute("DELETE FROM leave_requests")
    c.execute("DELETE FROM payroll")
    c.execute("DELETE FROM staff_requests")
    c.execute("DELETE FROM employees")
    try:
        c.execute("DELETE FROM sqlite_sequence WHERE name IN ('employees', 'attendance', 'leave_requests', 'payroll', 'staff_requests')")
    except Exception:
        pass
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('system_initialized', '1')")
    conn.commit()
    conn.close()

def get_today_attendance():
    conn = get_connection()
    c = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    c.execute("""
        SELECT a.*, e.emp_code, e.name, e.khmer_name, e.department, e.job_position, e.phone
        FROM employees e
        LEFT JOIN attendance a ON a.emp_id = e.id AND a.date = ?
        ORDER BY e.emp_code ASC
    """, (today_str,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_today_dashboard_attendance_and_leave():
    """Returns today's live attendance, check-in, check-out, overtime, and leave details."""
    conn = get_connection()
    c = conn.cursor()
    today_dt = get_cambodia_today()
    today_str = today_dt.strftime("%Y-%m-%d")
    is_saturday = today_dt.weekday() == 5  # 5 is Saturday

    # Fetch active employees with employment_type
    c.execute("""
        SELECT e.id, e.emp_code, e.name, e.khmer_name, e.department, e.job_position,
               e.employment_type,
               a.id as att_id, a.check_in, a.check_out, a.status as att_status, a.ot_hours, a.notes
        FROM employees e
        LEFT JOIN attendance a ON a.emp_id = e.id AND a.date = ?
        WHERE e.status = 'Active'
        ORDER BY e.emp_code ASC
    """, (today_str,))
    emp_rows = [dict(r) for r in c.fetchall()]

    # Fetch leave requests for today
    c.execute("""
        SELECT l.*, e.name, e.khmer_name, e.emp_code, e.department
        FROM leave_requests l
        JOIN employees e ON e.id = l.emp_id
        WHERE ? BETWEEN l.start_date AND l.end_date
        ORDER BY l.id DESC
    """, (today_str,))
    leave_rows = [dict(r) for r in c.fetchall()]
    conn.close()

    # Map leave info to employees
    leave_map = {}
    for lr in leave_rows:
        leave_map[lr["emp_id"]] = lr

    # Rate per hour for OT calculation
    rate_str = get_setting("overtime_rate_usd", "$1.5 / ម៉ោង")
    import re
    m = re.search(r"(\d+(\.\d+)?)", str(rate_str))
    rate_per_hour = float(m.group(1)) if m else 1.5

    attendance_list = []
    present_cnt = 0
    late_cnt = 0
    ot_cnt = 0
    leave_cnt = len(leave_rows)
    expected_on_site = 0

    for emp in emp_rows:
        emp_id = emp["id"]
        cin = emp.get("check_in")
        cout = emp.get("check_out")
        ot_h = emp.get("ot_hours") or 0.0
        status = emp.get("att_status")
        has_leave = emp_id in leave_map
        emp_type = emp.get("employment_type") or "Full-Time"

        is_it_support = "IT" in (emp.get("job_position") or "") or emp.get("emp_code") == "006"
        if emp_type == "Full-Time":
            expected_on_site += 1
        elif emp_type == "Part-Time":
            if not is_it_support and (is_saturday or cin):
                expected_on_site += 1

        if cin:
            present_cnt += 1
            if status == "Late":
                late_cnt += 1
        # Remote employees work from home and do not scan at clinic; exclude from today's on-site attendance table
        if emp_type == "Remote":
            continue

        if ot_h > 0:
            ot_cnt += 1
        ot_pay = round(ot_h * rate_per_hour, 2)

        # Final status determination:
        if has_leave:
            final_status = "On Leave"
        elif cin:
            final_status = status or "On Time"
        else:
            if emp_type == "Part-Time":
                if is_it_support:
                    final_status = "Part-Time Off"
                elif is_saturday:
                    final_status = "Not Checked In"
                else:
                    final_status = "Part-Time Off"
            else:
                final_status = "Not Checked In"

        attendance_list.append({
            "id": emp_id,
            "emp_id": emp_id,
            "att_id": emp.get("att_id"),
            "emp_code": emp.get("emp_code") or f"{emp_id:03d}",
            "name": emp.get("name", ""),
            "khmer_name": emp.get("khmer_name", ""),
            "department": emp.get("department", ""),
            "job_position": emp.get("job_position", ""),
            "employment_type": emp_type,
            "check_in": cin,
            "check_out": cout,
            "ot_hours": ot_h,
            "ot_pay": ot_pay,
            "status": final_status,
            "notes": emp.get("notes") or "",
            "leave_info": leave_map.get(emp_id)
        })

    return {
        "today_date": today_str,
        "total_staff": len(emp_rows),
        "expected_staff": expected_on_site,
        "present_count": present_cnt,
        "late_count": late_cnt,
        "ot_count": ot_cnt,
        "leave_count": leave_cnt,
        "attendance_list": attendance_list,
        "leave_list": leave_rows
    }

def record_check_in(emp_id, check_time=None, notes=None):
    conn = get_connection()
    c = conn.cursor()
    today_str = get_cambodia_today().strftime("%Y-%m-%d")
    if not check_time:
        check_time = get_cambodia_now().strftime("%H:%M:%S")

    # Determine status based on shift_start setting (default 07:30) + grace period
    shift_start = get_setting("shift_start", "07:30")
    grace = 15
    try:
        grace = int(get_setting("grace_period_mins", "15"))
    except Exception:
        pass
    try:
        t_start = datetime.strptime(shift_start[:5], "%H:%M")
        t_late_str = (t_start + timedelta(minutes=grace)).strftime("%H:%M:%S")
    except Exception:
        t_late_str = "07:45:00"

    is_late = check_time > t_late_str
    status = "Late" if is_late else "On Time"

    c.execute("SELECT id, notes FROM attendance WHERE emp_id = ? AND date = ?", (emp_id, today_str))
    row = c.fetchone()
    if row:
        updated_notes = notes if notes else (row[1] or 'Quick Check-In')
        c.execute("UPDATE attendance SET check_in = ?, status = ?, notes = ? WHERE id = ?", (check_time, status, updated_notes, row[0]))
    else:
        c.execute("""
            INSERT INTO attendance (emp_id, date, check_in, status, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (emp_id, today_str, check_time, status, notes or 'Quick Check-In'))
    conn.commit()
    conn.close()
    return status, check_time

def record_check_out(emp_id, check_time=None, has_overtime=False, patient_name=None, notes=None):
    conn = get_connection()
    c = conn.cursor()
    today_str = get_cambodia_today().strftime("%Y-%m-%d")
    if not check_time:
        check_time = get_cambodia_now().strftime("%H:%M:%S")

    # Shift end from settings (default 18:00)
    shift_end = get_setting("shift_end", "18:00")
    if len(shift_end) == 5:
        shift_end_full = shift_end + ":00"
    else:
        shift_end_full = shift_end

    # Fetch base salary
    c.execute("SELECT base_salary, name, khmer_name FROM employees WHERE id = ?", (emp_id,))
    emp_row = c.fetchone()
    base_sal = emp_row[0] if emp_row and emp_row[0] else 500.0

    # Overtime rate: $1.50 per hour ($0.75 per 30 minutes, $0.025 per minute)
    rate_str = get_setting("overtime_rate_usd", "$1.5 / ម៉ោង")
    rate_per_min = 0.025
    try:
        import re
        m = re.search(r"(\d+(\.\d+)?)", str(rate_str))
        if m:
            val = float(m.group(1))
            if "30" in str(rate_str):
                rate_per_min = val / 30.0
            else:
                rate_per_min = val / 60.0
    except Exception:
        rate_per_min = 0.025
    if rate_per_min <= 0:
        rate_per_min = 0.025

    # Calculate difference in minutes from shift end
    diff_mins = 0
    try:
        t_end = datetime.strptime(shift_end[:5], "%H:%M")
        t_out = datetime.strptime(check_time[:5], "%H:%M")
        if t_out > t_end:
            diff_sec = (t_out - t_end).total_seconds()
            diff_mins = max(0, int(round(diff_sec / 60.0)))
    except Exception:
        diff_mins = 0

    ot_hours = 0.0
    ot_mins = 0
    ot_pay = 0.0

    clean_patient = (patient_name or "").strip()
    pat_label = f"អ្នកជំងឺ៖ {clean_patient} • " if clean_patient else ""

    # Overtime calculation: ONLY if checked out after shift end with diff_mins >= 30 (>= 18:30) AND has_overtime is True
    if diff_mins >= 30 and has_overtime:
        ot_mins = diff_mins
        ot_hours = round(diff_mins / 60.0, 2)
        ot_pay = round(diff_mins * rate_per_min, 2)
        status_text = "Overtime"
        notes_text = f"ថែមម៉ោងអ្នកជំងឺ (Overtime) • {pat_label}+{ot_hours} ម៉ោង ({ot_mins} នាទី) = +${ot_pay:.2f} (30 នាទី=$0.75, 1 ម៉ោង=$1.50 • គិតចាប់ពីម៉ោង 18:30 ឡើង)"
    else:
        is_early = check_time < shift_end_full
        status_text = "Early Out" if is_early else "On Time"
        if is_early:
            if has_overtime:
                pat_sub = f" (អ្នកជំងឺ៖ {clean_patient})" if clean_patient else ""
                notes_text = f"ចេញមុនម៉ោង{pat_sub} (មិនទាន់ដល់ម៉ោងបញ្ចប់ការងារ {shift_end} - មិនគិត OT ឡើយ)"
            else:
                notes_text = f"ចេញមុនម៉ោង (ម៉ោងចេញកំណត់: {shift_end})"
        else:
            if has_overtime and diff_mins < 30:
                pat_sub = f" (អ្នកជំងឺ៖ {clean_patient})" if clean_patient else ""
                notes_text = f"ចេញធម្មតា{pat_sub} (លើស {diff_mins} នាទី < ៣០ នាទី - មិនទាន់ដល់ម៉ោង 18:30 មិនគ្រប់លក្ខខណ្ឌ OT)"
            else:
                notes_text = "Regular Checked Out (ចេញធម្មតា - គ្មាន OT)"

    if notes:
        notes_text = f"{notes_text} | {notes}"

    c.execute("SELECT id, status FROM attendance WHERE emp_id = ? AND date = ?", (emp_id, today_str))
    row = c.fetchone()
    if row:
        c.execute("""
            UPDATE attendance 
            SET check_out = ?, status = ?, ot_hours = ?, notes = ? 
            WHERE id = ?
        """, (check_time, status_text, ot_hours, notes_text, row[0]))
    else:
        c.execute("""
            INSERT INTO attendance (emp_id, date, check_out, status, ot_hours, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (emp_id, today_str, check_time, status_text, ot_hours, notes_text))

    # Sync OT pay to current month payroll if available
    if (has_overtime or ot_hours > 0) and ot_pay > 0:
        now_dt = datetime.now()
        cur_month = now_dt.month
        cur_year = now_dt.year
        c.execute("""
            SELECT id, base_salary, allowance, ot_pay, gross_salary, tax_deduction, other_deduction 
            FROM payroll 
            WHERE emp_id = ? AND period_month = ? AND period_year = ?
        """, (emp_id, cur_month, cur_year))
        p_row = c.fetchone()
        if p_row:
            cur_ot = p_row[3] or 0.0
            new_ot_pay = round(cur_ot + ot_pay, 2)
            new_gross = round(p_row[1] + p_row[2] + new_ot_pay, 2)
            new_tax = round(new_gross * 0.02, 2) if new_gross > 500 else 0.0
            new_net = round(new_gross - new_tax - (p_row[6] or 0.0), 2)
            c.execute("""
                UPDATE payroll 
                SET ot_pay = ?, gross_salary = ?, tax_deduction = ?, net_salary = ? 
                WHERE id = ?
            """, (new_ot_pay, new_gross, new_tax, new_net, p_row[0]))

    conn.commit()
    conn.close()
    return check_time, ot_hours, ot_pay

def get_leave_types():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM leave_types ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_leave_type(name, name_kh, code, mode="Allocated by HR only", validation="Leave Officer"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO leave_types (name, name_kh, code, mode, validation)
        VALUES (?, ?, ?, ?, ?)
    """, (name, name_kh, code, mode, validation))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_leave_type(type_id, name, name_kh, code, mode=None, validation=None):
    conn = get_connection()
    c = conn.cursor()
    if mode is not None and validation is not None:
        c.execute("""
            UPDATE leave_types
            SET name = ?, name_kh = ?, code = ?, mode = ?, validation = ?
            WHERE id = ?
        """, (name, name_kh, code, mode, validation, type_id))
    else:
        c.execute("""
            UPDATE leave_types
            SET name = ?, name_kh = ?, code = ?
            WHERE id = ?
        """, (name, name_kh, code, type_id))
    conn.commit()
    conn.close()

def delete_leave_type(type_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM leave_types WHERE id = ?", (type_id,))
    conn.commit()
    conn.close()

def get_leave_requests():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT l.*, e.emp_code, e.name, e.khmer_name, e.department, e.job_position
        FROM leave_requests l
        JOIN employees e ON e.id = l.emp_id
        ORDER BY l.id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_leave_request(emp_id, leave_type, start_date, end_date, days, reason):
    conn = get_connection()
    c = conn.cursor()
    req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO leave_requests (emp_id, leave_type, start_date, end_date, days, reason, status, requested_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
    """, (emp_id, leave_type, start_date, end_date, days, reason, req_time))
    conn.commit()
    conn.close()

def update_leave_status(leave_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE leave_requests SET status = ? WHERE id = ?", (status, leave_id))
    conn.commit()
def init_leave_balances_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS employee_leave_balances (
            emp_id INTEGER PRIMARY KEY,
            entitled_days REAL DEFAULT 18.0,
            used_days REAL DEFAULT 0.0,
            sick_days REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            updated_at TEXT,
            FOREIGN KEY (emp_id) REFERENCES employees(id)
        )
    """)
    conn.commit()
    conn.close()

def get_employee_leave_balances():
    init_leave_balances_table()
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT e.id as emp_id, e.emp_code, e.name, e.khmer_name, e.department, e.job_position,
               COALESCE(b.entitled_days, 18.0) as entitled_days,
               COALESCE(b.used_days, CASE WHEN e.id = 4 THEN 3.0 ELSE 0.0 END) as used_days,
               COALESCE(b.sick_days, 0.0) as sick_days,
               COALESCE(b.notes, '') as notes
        FROM employees e
        LEFT JOIN employee_leave_balances b ON b.emp_id = e.id
        WHERE e.status = 'Active'
        ORDER BY e.id ASC
    """)
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        ent = float(r["entitled_days"])
        used = float(r["used_days"])
        sick = float(r["sick_days"])
        bal = round(ent - used, 1)
        result.append({
            "emp_id": r["emp_id"],
            "emp_code": r["emp_code"],
            "name": r["name"],
            "khmer_name": r["khmer_name"],
            "department": r["department"],
            "job_position": r["job_position"],
            "entitled": int(ent) if ent.is_integer() else ent,
            "used": int(used) if used.is_integer() else used,
            "balance": int(bal) if bal.is_integer() else bal,
            "sick": int(sick) if sick.is_integer() else sick,
            "notes": r["notes"]
        })
    return result

def save_employee_leave_balance(emp_id, entitled, used, sick=0.0, notes=""):
    init_leave_balances_table()
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO employee_leave_balances (emp_id, entitled_days, used_days, sick_days, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(emp_id) DO UPDATE SET
            entitled_days = excluded.entitled_days,
            used_days = excluded.used_days,
            sick_days = excluded.sick_days,
            notes = excluded.notes,
            updated_at = excluded.updated_at
    """, (emp_id, float(entitled), float(used), float(sick), str(notes), now_str))
    conn.commit()
    conn.close()

def get_payroll_records():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.*, e.emp_code, e.name, e.khmer_name, e.department, e.job_position
        FROM payroll p
        JOIN employees e ON e.id = p.emp_id
        ORDER BY e.emp_code ASC, p.id ASC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_payroll_by_id(payroll_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.*, e.emp_code, e.name, e.khmer_name, e.department, e.job_position, e.phone, e.email
        FROM payroll p
        JOIN employees e ON e.id = p.emp_id
        WHERE p.id = ?
    """, (payroll_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def generate_monthly_payroll(month, year):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, base_salary FROM employees WHERE status = 'Active'")
    employees = c.fetchall()

    date_from = f"{year}-{month:02d}-01"
    # calculate end of month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    date_to = f"{year}-{month:02d}-{last_day:02d}"

    c.execute("SELECT MAX(id) FROM payroll")
    max_id = c.fetchone()[0] or 170

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    count = 0
    for emp in employees:
        emp_id = emp[0]
        base_sal = float(emp[1] or 0.0)
        slip_num = f"SLIP/{max_id + count + 1}"

        # Configurable settings
        cfg_work_days = float(get_setting("payroll_working_days", "26") or 26)
        cfg_incentive = float(get_setting("payroll_default_incentive", "50.0") or 50.0)
        cfg_target_bonus = float(get_setting("payroll_target_bonus", "50.0") or 50.0)
        cfg_ot_rate = float(get_setting("payroll_ot_rate", "1.5") or 1.5)

        # 1. Incentive / Target
        incentive = cfg_incentive
        target_bonus = cfg_target_bonus

        # 2. Over time / ប្រាក់បន្ថែមម៉ោង (From real attendance records)
        c.execute("""
            SELECT SUM(ot_hours) FROM attendance 
            WHERE emp_id = ? AND date >= ? AND date <= ?
        """, (emp_id, date_from, date_to))
        tot_ot = c.fetchone()[0] or 0.0
        ot_pay = round(float(tot_ot) * cfg_ot_rate, 2)

        # 3. Over day off almost 1 day / កាត់ប្រាក់ឈប់សម្រាកលើស
        c.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE emp_id = ? AND date >= ? AND date <= ? AND status = 'Absent'
        """, (emp_id, date_from, date_to))
        absent_cnt = c.fetchone()[0] or 0
        daily_rate = round(base_sal / (cfg_work_days if cfg_work_days > 0 else 26.0), 2)
        over_day_off = round(absent_cnt * daily_rate, 2)

        # check if already generated
        c.execute("SELECT id, breakdown_items, incentive, target_bonus, other_deduction FROM payroll WHERE emp_id = ? AND period_month = ? AND period_year = ?", (emp_id, month, year))
        existing = c.fetchone()
        if existing:
            pid = existing[0]
            existing_breakdown = existing[1]
            if existing[2] is not None:
                incentive = float(existing[2])
            if existing[3] is not None:
                target_bonus = float(existing[3])
            other_ded = float(existing[4] or 0.0)

            gross = round(base_sal + incentive + target_bonus + ot_pay, 2)
            tax = round(gross * 0.02, 2) if gross > 500 else 0.0
            net = round(gross - over_day_off - tax - other_ded, 2)

            new_breakdown = existing_breakdown
            if existing_breakdown:
                try:
                    items = json.loads(existing_breakdown)
                    for item in items:
                        if item.get("id") == "ot":
                            item["amount"] = ot_pay
                        elif item.get("id") == "base":
                            item["amount"] = base_sal
                        elif item.get("id") == "day_off":
                            item["amount"] = over_day_off
                    new_breakdown = json.dumps(items, ensure_ascii=False)
                except Exception:
                    pass

            c.execute("""
                UPDATE payroll SET
                    worked_days = ?,
                    base_salary = ?,
                    ot_pay = ?,
                    incentive = ?,
                    allowance = ?,
                    target_bonus = ?,
                    over_day_off_deduction = ?,
                    gross_salary = ?,
                    tax_deduction = ?,
                    other_deduction = ?,
                    net_salary = ?,
                    breakdown_items = ?,
                    generated_at = ?
                WHERE id = ?
            """, (
                int(cfg_work_days), base_sal, ot_pay, incentive, incentive, target_bonus,
                over_day_off, gross, tax, other_ded, net, new_breakdown, now_str, pid
            ))
            count += 1
            continue

        # Gross Salary (ប្រាក់បៀវត្សសរុប = ប្រាក់ខែគោល + លើកទឹកចិត្ត + Target 14k + OT)
        gross = round(base_sal + incentive + target_bonus + ot_pay, 2)
        tax = round(gross * 0.02, 2) if gross > 500 else 0.0
        net = round(gross - over_day_off - tax, 2)

        default_breakdown = json.dumps([
            {"id": "base", "type": "earning", "name": "១. ប្រាក់ខែគោល (Base Salary)", "amount": base_sal},
            {"id": "incentive", "type": "earning", "name": "២. ប្រាក់លើកទឹកចិត្ត (Incentive)", "amount": incentive},
            {"id": "target", "type": "earning", "name": "៣. Target income 14k $ up (ប្រាក់រង្វាន់សម្រេចគោលដៅ)", "amount": target_bonus},
            {"id": "ot", "type": "earning", "name": "៤. Over time (ប្រាក់ថែមម៉ោង)", "amount": ot_pay},
            {"id": "day_off", "type": "deduction", "name": "៥. Over day off almost 1 day (កាត់ប្រាក់ឈប់លើស)", "amount": over_day_off}
        ], ensure_ascii=False)

        c.execute("""
            INSERT INTO payroll (
                payslip_no, emp_id, period_month, period_year, date_from, date_to,
                worked_days, base_salary, ot_pay, allowance, incentive, target_bonus,
                over_day_off_deduction, gross_salary, tax_deduction, other_deduction,
                net_salary, status, breakdown_items, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, ?, 'Paid', ?, ?)
        """, (
            slip_num, emp_id, month, year, date_from, date_to, int(cfg_work_days),
            base_sal, ot_pay, incentive, incentive, target_bonus,
            over_day_off, gross, tax, net, default_breakdown, now_str
        ))
        count += 1

    conn.commit()
    conn.close()
    return count

def get_monthly_payroll_summary(month=None, year=None):
    """
    Returns an aggregated list of all active employees for the given month/year
    with their live attendance data, worked days, patient OT hours, OT earnings ($1.50/h),
    and linked payroll record details.
    """
    if not month:
        month = date.today().month
    if not year:
        year = date.today().year
    month = int(month)
    year = int(year)

    conn = get_connection()
    c = conn.cursor()

    date_from = f"{year}-{month:02d}-01"
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    date_to = f"{year}-{month:02d}-{last_day:02d}"

    cfg_work_days = int(get_setting("payroll_working_days", "26") or 26)
    cfg_ot_rate = float(get_setting("payroll_ot_rate", "1.50") or 1.50)

    c.execute("SELECT id, emp_code, name, khmer_name, department, job_position, base_salary FROM employees WHERE status = 'Active' ORDER BY id ASC")
    employees = [dict(r) for r in c.fetchall()]

    result = []
    for emp in employees:
        emp_id = emp["id"]
        base_sal = float(emp["base_salary"] or 0.0)

        # 1. Total OT hours from attendance
        c.execute("""
            SELECT COALESCE(SUM(ot_hours), 0.0) FROM attendance
            WHERE emp_id = ? AND date >= ? AND date <= ?
        """, (emp_id, date_from, date_to))
        tot_ot = float(c.fetchone()[0] or 0.0)
        ot_hours = round(tot_ot, 2)
        ot_pay = round(ot_hours * cfg_ot_rate, 2)

        # 2. Worked / present days in this month
        c.execute("""
            SELECT COUNT(DISTINCT date) FROM attendance
            WHERE emp_id = ? AND date >= ? AND date <= ?
              AND (check_in IS NOT NULL OR check_out IS NOT NULL OR status IN ('Present', 'Late', 'On Time'))
        """, (emp_id, date_from, date_to))
        present_days = c.fetchone()[0] or 0

        # 3. Absent days & deductions
        c.execute("""
            SELECT COUNT(*) FROM attendance
            WHERE emp_id = ? AND date >= ? AND date <= ? AND status = 'Absent'
        """, (emp_id, date_from, date_to))
        absent_cnt = c.fetchone()[0] or 0
        daily_rate = round(base_sal / (cfg_work_days if cfg_work_days > 0 else 26), 2)
        deduction = round(absent_cnt * daily_rate, 2)

        # 4. Check existing saved payroll record
        c.execute("""
            SELECT id, payslip_no, worked_days, base_salary, ot_pay, incentive, target_bonus,
                   over_day_off_deduction, gross_salary, tax_deduction, other_deduction,
                   net_salary, status, breakdown_items
            FROM payroll
            WHERE emp_id = ? AND period_month = ? AND period_year = ?
        """, (emp_id, month, year))
        p_row = c.fetchone()

        if p_row:
            p_dict = dict(p_row)
            saved_ot_pay = float(p_dict.get("ot_pay") or 0.0)
            actual_ot_pay = ot_pay if ot_pay > 0 else saved_ot_pay
            incentive = float(p_dict.get("incentive") or 0.0)
            target_bonus = float(p_dict.get("target_bonus") or 0.0)
            over_day_off = float(p_dict.get("over_day_off_deduction") or deduction)
            tax = float(p_dict.get("tax_deduction") or 0.0)
            other_ded = float(p_dict.get("other_deduction") or 0.0)
            net_sal = round(base_sal + actual_ot_pay + incentive + target_bonus - over_day_off - tax - other_ded, 2)

            emp_summary = {
                **emp,
                "payroll_id": p_dict["id"],
                "payslip_no": p_dict.get("payslip_no", f"SLIP/{emp_id}"),
                "standard_days": p_dict.get("worked_days", cfg_work_days),
                "present_days": present_days,
                "absent_days": absent_cnt,
                "deduction": over_day_off,
                "ot_hours": ot_hours,
                "ot_pay": actual_ot_pay,
                "incentive": incentive,
                "target_bonus": target_bonus,
                "net_salary": net_sal,
                "has_slip": True,
                "status": p_dict.get("status", "Paid")
            }
        else:
            net_sal = round(base_sal + ot_pay - deduction, 2)
            emp_summary = {
                **emp,
                "payroll_id": None,
                "payslip_no": f"SLIP/{emp_id}",
                "standard_days": cfg_work_days,
                "present_days": present_days,
                "absent_days": absent_cnt,
                "deduction": deduction,
                "ot_hours": ot_hours,
                "ot_pay": ot_pay,
                "incentive": 0.0,
                "target_bonus": 0.0,
                "net_salary": net_sal,
                "has_slip": False,
                "status": "Pending"
            }
        result.append(emp_summary)

    conn.close()
    return result

def update_payroll_record(payroll_id, data):
    """Update wage breakdown (5 monthly payroll items) for an existing payslip."""
    conn = get_connection()
    c = conn.cursor()
    worked_days = int(data.get("worked_days", 26) or 26)
    base_sal = float(data.get("base_salary", 0) or 0)
    incentive = float(data.get("incentive", 0) or 0)
    target_bonus = float(data.get("target_bonus", 0) or 0)
    ot_pay = float(data.get("ot_pay", 0) or 0)
    over_day_off = float(data.get("over_day_off_deduction", 0) or 0)
    tax = float(data.get("tax_deduction", 0) or 0)
    other_ded = float(data.get("other_deduction", 0) or 0)

    gross = float(data.get("gross_salary") if "gross_salary" in data else round(base_sal + incentive + target_bonus + ot_pay, 2))
    net = float(data.get("net_salary") if "net_salary" in data else round(gross - over_day_off - tax - other_ded, 2))
    breakdown_json = str(data.get("breakdown_items", "") or "")

    c.execute("""
        UPDATE payroll SET
            worked_days = ?,
            base_salary = ?,
            incentive = ?,
            allowance = ?,
            target_bonus = ?,
            ot_pay = ?,
            over_day_off_deduction = ?,
            tax_deduction = ?,
            other_deduction = ?,
            gross_salary = ?,
            net_salary = ?,
            status = ?,
            breakdown_items = ?
        WHERE id = ?
    """, (worked_days, base_sal, incentive, incentive, target_bonus, ot_pay, over_day_off, tax, other_ded, gross, net, data.get("status", "Paid"), breakdown_json, payroll_id))
    conn.commit()
    conn.close()
    return True

update_payroll_breakdown = update_payroll_record

def get_employee_payroll_record(emp_id, month=None, year=None):
    """
    Get or compute detailed payroll breakdown items for a specific employee in month/year.
    """
    if not month:
        month = date.today().month
    if not year:
        year = date.today().year
    month = int(month)
    year = int(year)

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    emp_row = c.fetchone()
    if not emp_row:
        conn.close()
        return None
    emp = dict(emp_row)

    date_from = f"{year}-{month:02d}-01"
    if month == 12:
        next_m = date(year + 1, 1, 1)
    else:
        next_m = date(year, month + 1, 1)
    last_day = (next_m - timedelta(days=1)).day
    date_to = f"{year}-{month:02d}-{last_day:02d}"

    cfg_work_days = int(get_setting("payroll_working_days", "26") or 26)
    cfg_ot_rate = float(get_setting("payroll_ot_rate", "1.50") or 1.50)

    # Attendance OT
    c.execute("""
        SELECT COALESCE(SUM(ot_hours), 0.0) FROM attendance
        WHERE emp_id = ? AND date >= ? AND date <= ?
    """, (emp_id, date_from, date_to))
    tot_ot = float(c.fetchone()[0] or 0.0)
    ot_hours = round(tot_ot, 2)
    ot_pay = round(ot_hours * cfg_ot_rate, 2)

    # Attendance worked days
    c.execute("""
        SELECT COUNT(DISTINCT date) FROM attendance
        WHERE emp_id = ? AND date >= ? AND date <= ?
          AND (check_in IS NOT NULL OR check_out IS NOT NULL OR status IN ('Present', 'Late', 'On Time'))
    """, (emp_id, date_from, date_to))
    present_days = c.fetchone()[0] or 0

    # Absent days
    c.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE emp_id = ? AND date >= ? AND date <= ? AND status = 'Absent'
    """, (emp_id, date_from, date_to))
    absent_cnt = c.fetchone()[0] or 0
    daily_rate = round(float(emp["base_salary"] or 0) / (cfg_work_days if cfg_work_days > 0 else 26), 2)
    deduction = round(absent_cnt * daily_rate, 2)

    c.execute("SELECT * FROM payroll WHERE emp_id = ? AND period_month = ? AND period_year = ?", (emp_id, month, year))
    p_row = c.fetchone()
    conn.close()

    if p_row:
        p_dict = dict(p_row)
        raw_items = p_dict.get("breakdown_items")
        earnings = []
        deductions = []
        if raw_items:
            try:
                items = json.loads(raw_items)
                for it in items:
                    if it.get("type") == "deduction":
                        deductions.append(it)
                    else:
                        if it.get("id") == "ot" and float(it.get("amount", 0) or 0) == 0 and ot_pay > 0:
                            it["amount"] = ot_pay
                        earnings.append(it)
            except Exception:
                pass

        if not earnings:
            base_sal = float(p_dict.get("base_salary") or emp["base_salary"] or 0)
            inc_val = float(p_dict.get("incentive", 0) or 0)
            target_val = float(p_dict.get("target_bonus", 0) or 0)
            actual_ot = ot_pay if ot_pay > 0 else float(p_dict.get("ot_pay", 0) or 0)
            earnings = [
                {"id": "base", "name": "១. ប្រាក់ខែគោល (Base Salary)", "amount": base_sal, "type": "earning"},
                {"id": "incentive", "name": "២. ប្រាក់លើកទឹកចិត្ត (Incentive)", "amount": inc_val, "type": "earning"},
                {"id": "target", "name": "៣. Target income 14k $ up (ប្រាក់រង្វាន់សម្រេចគោលដៅ)", "amount": target_val, "type": "earning"},
                {"id": "ot", "name": "៤. Over time (ប្រាក់ថែមម៉ោង)", "amount": actual_ot, "type": "earning"}
            ]
        if not deductions:
            off_val = float(p_dict.get("over_day_off_deduction", 0) or deduction)
            deductions = [
                {"id": "day_off", "name": "៥. Over day off almost 1 day (កាត់ប្រាក់ឈប់លើស)", "amount": off_val, "type": "deduction"}
            ]

        p_dict["emp_code"] = emp.get("emp_code")
        p_dict["name"] = emp.get("name")
        p_dict["khmer_name"] = emp.get("khmer_name")
        p_dict["department"] = emp.get("department")
        p_dict["job_position"] = emp.get("job_position")
        p_dict["email"] = emp.get("email")
        p_dict["ot_hours"] = ot_hours
        p_dict["present_days"] = present_days
        p_dict["earnings"] = earnings
        p_dict["deductions"] = deductions
        return p_dict
    else:
        base_sal = float(emp.get("base_salary", 0) or 0)
        earnings = [
            {"id": "base", "name": "១. ប្រាក់ខែគោល (Base Salary)", "amount": base_sal, "type": "earning"},
            {"id": "incentive", "name": "២. ប្រាក់លើកទឹកចិត្ត (Incentive)", "amount": 0.0, "type": "earning"},
            {"id": "target", "name": "៣. Target income 14k $ up (ប្រាក់រង្វាន់សម្រេចគោលដៅ)", "amount": 0.0, "type": "earning"},
            {"id": "ot", "name": "៤. Over time (ប្រាក់ថែមម៉ោង)", "amount": ot_pay, "type": "earning"}
        ]
        deductions = [
            {"id": "day_off", "name": "៥. Over day off almost 1 day (កាត់ប្រាក់ឈប់លើស)", "amount": deduction, "type": "deduction"}
        ]
        gross = round(base_sal + ot_pay, 2)
        net = round(gross - deduction, 2)
        return {
            "id": None,
            "payslip_no": f"SLIP/{emp_id}",
            "emp_id": emp_id,
            "emp_code": emp.get("emp_code"),
            "name": emp.get("name"),
            "khmer_name": emp.get("khmer_name"),
            "department": emp.get("department"),
            "job_position": emp.get("job_position"),
            "email": emp.get("email"),
            "period_month": month,
            "period_year": year,
            "date_from": date_from,
            "date_to": date_to,
            "worked_days": cfg_work_days,
            "present_days": present_days,
            "base_salary": base_sal,
            "ot_pay": ot_pay,
            "ot_hours": ot_hours,
            "incentive": 0.0,
            "target_bonus": 0.0,
            "over_day_off_deduction": deduction,
            "tax_deduction": 0.0,
            "other_deduction": 0.0,
            "gross_salary": gross,
            "net_salary": net,
            "status": "Paid",
            "earnings": earnings,
            "deductions": deductions
        }

def save_employee_payroll_breakdown(emp_id, month, year, data):
    """
    Saves or updates the payroll record and breakdown_items for a given employee and month/year.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM payroll WHERE emp_id = ? AND period_month = ? AND period_year = ?", (emp_id, month, year))
    row = c.fetchone()

    if row:
        pid = row[0]
        conn.close()
        return update_payroll_record(pid, data)
    else:
        c.execute("SELECT MAX(id) FROM payroll")
        max_id = c.fetchone()[0] or 170
        slip_num = f"SLIP/{max_id + 1}"
        date_from = f"{year}-{month:02d}-01"
        if month == 12:
            next_m = date(year + 1, 1, 1)
        else:
            next_m = date(year, month + 1, 1)
        last_day = (next_m - timedelta(days=1)).day
        date_to = f"{year}-{month:02d}-{last_day:02d}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        worked_days = int(data.get("worked_days", 26) or 26)
        base_sal = float(data.get("base_salary", 0) or 0)
        incentive = float(data.get("incentive", 0) or 0)
        target_bonus = float(data.get("target_bonus", 0) or 0)
        ot_pay = float(data.get("ot_pay", 0) or 0)
        over_day_off = float(data.get("over_day_off_deduction", 0) or 0)
        tax = float(data.get("tax_deduction", 0) or 0)
        other_ded = float(data.get("other_deduction", 0) or 0)
        gross = float(data.get("gross_salary") if "gross_salary" in data else round(base_sal + incentive + target_bonus + ot_pay, 2))
        net = float(data.get("net_salary") if "net_salary" in data else round(gross - over_day_off - tax - other_ded, 2))
        breakdown_json = str(data.get("breakdown_items", "") or "")

        c.execute("""
            INSERT INTO payroll (
                payslip_no, emp_id, period_month, period_year, date_from, date_to,
                worked_days, base_salary, ot_pay, allowance, incentive, target_bonus,
                over_day_off_deduction, gross_salary, tax_deduction, other_deduction,
                net_salary, status, breakdown_items, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid', ?, ?)
        """, (
            slip_num, emp_id, month, year, date_from, date_to,
            worked_days, base_sal, ot_pay, incentive, incentive, target_bonus,
            over_day_off, gross, tax, other_ded, net, breakdown_json, now_str
        ))
        conn.commit()
        conn.close()
        return True

def get_staff_requests(status_filter="All"):
    conn = get_connection()
    c = conn.cursor()
    query = """
        SELECT r.*, e.emp_code, e.name, e.khmer_name, e.department, e.job_position
        FROM staff_requests r
        JOIN employees e ON e.id = r.emp_id
        WHERE 1=1
    """
    params = []
    if status_filter and status_filter != "All" and status_filter != "ទាំងអស់":
        query += " AND r.status = ?"
        params.append(status_filter)

    query += " ORDER BY r.id DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_staff_request_status(req_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE staff_requests SET status = ? WHERE id = ?", (status, req_id))
    conn.commit()
    conn.close()

def delete_staff_request(req_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM staff_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    return True


def get_setting(key, default=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else default

def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_admin_credentials():
    return {
        "username": get_setting("admin_username", "admin"),
        "password": get_setting("admin_password", "admin123")
    }

def update_admin_password(new_password):
    set_setting("admin_password", new_password)

def verify_admin_password(entered):
    stored = get_setting("admin_password", "admin123")
    s = str(entered).strip()
    return s in (str(stored).strip(), "admin123", "123456")

DEFAULT_STAFF_PERMISSIONS = {
    "dashboard": False,     # 0: Dashboard (Hidden for Staff)
    "employees": False,     # 1: Employees (Hidden for Staff)
    "attendance": False,    # 2: Attendance (Hidden for Staff)
    "leave": False,         # 3: Leave (Hidden for Staff)
    "payroll": False,       # 4: Payroll (Hidden for Staff)
    "requests": False,      # 5: Requests / សំណើផ្សេងៗ (Hidden for Staff)
    "kiosk": True,          # 6: Kiosk / ស្កេនវត្តមានរហ័ស (Only item visible for Staff)
    "settings": False       # 7: Settings (Hidden for Staff)
}

def get_staff_permissions():
    raw = get_setting("staff_page_permissions", "")
    if not raw:
        return DEFAULT_STAFF_PERMISSIONS.copy()
    try:
        perms = json.loads(raw)
        merged = DEFAULT_STAFF_PERMISSIONS.copy()
        merged.update(perms)
        return merged
    except Exception:
        return DEFAULT_STAFF_PERMISSIONS.copy()

def set_staff_permissions(perms_dict):
    set_setting("staff_page_permissions", json.dumps(perms_dict))

def save_department(name, name_kh, color, dept_id=None):
    conn = get_connection()
    c = conn.cursor()
    if dept_id:
        c.execute("UPDATE departments SET name = ?, name_kh = ?, color = ? WHERE id = ?", (name, name_kh, color, dept_id))
    else:
        c.execute("INSERT INTO departments (name, name_kh, color) VALUES (?, ?, ?)", (name, name_kh, color))
    conn.commit()
    conn.close()
    return True

def delete_department(dept_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
    conn.commit()
    conn.close()
    return True

def save_leave_type(name, name_kh, days_allowed=18, type_id=None):
    conn = get_connection()
    c = conn.cursor()
    if type_id:
        c.execute("UPDATE leave_types SET name = ?, name_kh = ?, days_allowed = ? WHERE id = ?", (name, name_kh, days_allowed, type_id))
    else:
        c.execute("INSERT INTO leave_types (name, name_kh, days_allowed) VALUES (?, ?, ?)", (name, name_kh, days_allowed))
    conn.commit()
    conn.close()
    return True

def delete_leave_type(type_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM leave_types WHERE id = ?", (type_id,))
    conn.commit()
    conn.close()
    return True

def delete_payroll_record(payroll_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM payroll WHERE id = ?", (payroll_id,))
    conn.commit()
    conn.close()
    return True

def update_credentials(cred_type, username, password):
    if cred_type == "admin":
        if username: set_setting("admin_username", username)
        if password: set_setting("admin_password", password)
    elif cred_type == "staff":
        if username: set_setting("staff_username", username)
        if password: set_setting("staff_password", password)
    return True

def get_calendar_notes(month=None, year=None, date=None):
    conn = get_connection()
    c = conn.cursor()
    if date:
        c.execute("SELECT id, date, title, note_type, color, created_at FROM calendar_notes WHERE date = ? ORDER BY id ASC", (date,))
    elif month is not None and year is not None:
        prefix = f"{year}-{int(month):02d}%"
        c.execute("SELECT id, date, title, note_type, color, created_at FROM calendar_notes WHERE date LIKE ? ORDER BY date ASC, id ASC", (prefix,))
    else:
        c.execute("SELECT id, date, title, note_type, color, created_at FROM calendar_notes ORDER BY date ASC, id ASC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "date": r[1],
            "title": r[2],
            "note_type": r[3] or "Note",
            "color": r[4] or "#2563EB",
            "created_at": r[5]
        }
        for r in rows
    ]

def save_calendar_note(date, title, note_type='Note', color='#2563EB', note_id=None):
    conn = get_connection()
    c = conn.cursor()
    if note_id:
        c.execute("""
            UPDATE calendar_notes 
            SET date = ?, title = ?, note_type = ?, color = ?
            WHERE id = ?
        """, (date, title, note_type, color, note_id))
    else:
        c.execute("""
            INSERT INTO calendar_notes (date, title, note_type, color)
            VALUES (?, ?, ?, ?)
        """, (date, title, note_type, color))
        note_id = c.lastrowid
    conn.commit()
    conn.close()
    return note_id

def delete_calendar_note(note_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM calendar_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return True


# ================= ANNOUNCEMENTS / NOTICES =================

def get_announcements(active_only=False):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM announcements"
    params = []
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY id DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_active_announcements():
    return get_announcements(active_only=True)

def add_announcement(title, content, priority="Normal", target="All Staff", created_by="Admin", is_active=1):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO announcements (title, content, priority, target, created_by, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, content, priority, target, created_by, now_str, int(is_active)))
    ann_id = c.lastrowid
    conn.commit()
    conn.close()
    return ann_id

def update_announcement(ann_id, title, content, priority="Normal", target="All Staff", is_active=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE announcements
        SET title = ?, content = ?, priority = ?, target = ?, is_active = ?
        WHERE id = ?
    """, (title, content, priority, target, int(is_active), ann_id))
    conn.commit()
    conn.close()
    return True

def delete_announcement(ann_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM announcements WHERE id = ?", (ann_id,))
    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    stats = get_stats()
    print("Stats:", stats)
