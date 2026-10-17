"""
Admin Web Portal for Mercy Dental Care.
Faithful 1:1 recreation of the Desktop HR & Attendance Management System.
Features:
- Pure Khmer navigation items matching Desktop (Pages 1 to 8):
  1. 📊 ផ្ទាំងព័ត៌មាន (Dashboard)
  2. 👥 បុគ្គលិក (Employees)
  3. ⏱️ វត្តមាន (Attendance)
  4. 📅 ច្បាប់ឈប់សម្រាក (Leaves - 4 Subtabs)
  5. 💵 បើកប្រាក់ខែ (Payroll & Payslips)
  6. 📋 សំណើផ្សេងៗ (Staff Requests)
  7. 📱 ស្កេនវត្តមានរហ័ស (Kiosk Punch)
  8. ⚙️ ការកំណត់ (Settings - 6 Cards)
- Full CRUD operations & interactive modals
"""

import os
import io
import csv
import json
import base64
import urllib.request
from datetime import datetime, date
from flask import request, jsonify, render_template_string, session, redirect, url_for, Response

import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mercy Dental Care - Admin Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #5648A6;
            --primary-dark: #3F337E;
            --bg: #0F172A;
            --card-bg: rgba(255, 255, 255, 0.96);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Kantumruy Pro', 'Inter', -apple-system, sans-serif;
            min-height: 100vh;
            background: radial-gradient(circle at top right, #3B2D7B 0%, #0F172A 70%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-card {
            background: var(--card-bg);
            border-radius: 24px;
            max-width: 410px;
            width: 100%;
            padding: 34px 28px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.45);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            animation: slideUp 0.35s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .logo-box {
            background: white;
            border-radius: 16px;
            padding: 10px 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(86, 72, 166, 0.15);
            margin-bottom: 14px;
        }
        .logo-box img {
            height: 52px;
            max-width: 190px;
            object-fit: contain;
        }
        h2 {
            font-size: 20px;
            font-weight: 800;
            color: #1E293B;
            margin-bottom: 4px;
        }
        .subtitle {
            font-size: 12.5px;
            color: #64748B;
            margin-bottom: 22px;
        }
        .input-group {
            text-align: left;
            margin-bottom: 14px;
        }
        .input-group label {
            display: block;
            font-size: 12px;
            font-weight: 700;
            color: #334155;
            margin-bottom: 5px;
        }
        .input-group input {
            width: 100%;
            height: 44px;
            border: 1.5px solid #CBD5E1;
            border-radius: 10px;
            padding: 0 12px;
            font-size: 13.5px;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
            background: #F8FAFC;
        }
        .input-group input:focus {
            border-color: var(--primary);
            background: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(86, 72, 166, 0.15);
        }
        .btn-login {
            width: 100%;
            height: 46px;
            background: linear-gradient(135deg, #5648A6 0%, #3F337E 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 14.5px;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(86, 72, 166, 0.35);
            transition: all 0.2s;
            margin-top: 8px;
        }
        .btn-login:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(86, 72, 166, 0.45);
        }
        .error-banner {
            background: #FEE2E2;
            color: #B91C1C;
            border: 1px solid #FCA5A5;
            padding: 9px 12px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 600;
            margin-bottom: 14px;
        }
        .back-link {
            display: inline-block;
            margin-top: 18px;
            font-size: 12.5px;
            color: #64748B;
            text-decoration: none;
            font-weight: 600;
        }
        .back-link:hover { color: var(--primary); }
    </style>
</head>
<body>

<div class="login-card">
    <div class="logo-box">
        <img src="data:image/png;base64,{{ logo_b64 }}" alt="Mercy Dental Care Logo">
    </div>
    <h2>ចូលគ្រប់គ្រង (Admin Login)</h2>
    <p class="subtitle">Mercy Dental Care • HR & Attendance Management System</p>

    {% if error %}
    <div class="error-banner">❌ {{ error }}</div>
    {% endif %}

    <form method="POST" action="/admin/login">
        <div class="input-group">
            <label for="username">👤 ឈ្មោះគណនី (Username)</label>
            <input type="text" id="username" name="username" value="admin" required autofocus>
        </div>
        <div class="input-group">
            <label for="password">🔒 ពាក្យសម្ងាត់ (Password)</label>
            <input type="password" id="password" name="password" placeholder="បញ្ចូលពាក្យសម្ងាត់ Admin" required>
        </div>
        <button type="submit" class="btn-login">ចូលប្រព័ន្ធ (Sign In)</button>
    </form>

    <a href="/" class="back-link">← ត្រឡប់ទៅផ្ទាំងស្កេនវត្តមាន (Mobile Portal)</a>
</div>

</body>
</html>
"""

def get_main_app_html():
    """Loads the main portal HTML template from templates/admin_main.html."""
    template_path = os.path.join(BASE_DIR, "templates", "admin_main.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Admin Portal Template Missing (templates/admin_main.html)</h1>"


def register_admin_portal(app):
    """Registers Admin Portal routes and handlers on the Flask app."""
    if not app.secret_key:
        app.secret_key = "mercy_dental_care_admin_secure_secret_key_2026"

    def get_logo_b64():
        logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(BASE_DIR, "assets", "logo.jpg")
        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("ascii")
            except Exception:
                pass
        return ""

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if session.get("admin_logged_in"):
            return redirect("/admin")

        error = None
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            
            stored_creds = database.get_admin_credentials()
            if username == stored_creds.get("username", "admin") and database.verify_admin_password(password):
                session["admin_logged_in"] = True
                session["admin_username"] = username
                return redirect("/admin")
            else:
                error = "ឈ្មោះគណនី ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!"

        return render_template_string(LOGIN_HTML, error=error, logo_b64=get_logo_b64())

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_logged_in", None)
        session.pop("admin_username", None)
        return redirect("/admin/login")

    @app.route("/admin")
    def admin_dashboard():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        today_date = date.today().isoformat()
        current_year = date.today().year
        current_month_num = date.today().month
        current_month = f"{current_year}-{current_month_num:02d}"

        # Determine filter period (monthly by default, or daily)
        period_type = request.args.get("period_type", "").strip()
        filter_date = request.args.get("date", "").strip() or today_date
        
        req_month = request.args.get("month", "").strip()
        req_year = request.args.get("year", "").strip()
        req_month_num = request.args.get("month_num", "").strip()

        if req_year and req_month_num:
            try:
                filter_month = f"{int(req_year):04d}-{int(req_month_num):02d}"
            except Exception:
                filter_month = current_month
        elif req_month:
            filter_month = req_month
        else:
            filter_month = current_month

        try:
            parts = filter_month.split("-")
            sel_year = int(parts[0])
            sel_month = int(parts[1])
        except Exception:
            sel_year = current_year
            sel_month = current_month_num

        filter_emp_id = request.args.get("emp_id", "").strip()

        if not period_type:
            if "date" in request.args and "month" not in request.args and "month_num" not in request.args:
                period_type = "day"
            else:
                period_type = "month"

        stats = database.get_stats()
        employees = database.get_all_employees()

        filter_emp_name = ""
        if filter_emp_id:
            for emp in employees:
                if str(emp.get("id")) == str(filter_emp_id):
                    filter_emp_name = f"{emp.get('khmer_name')} ({emp.get('name')})"
                    break

        # Get today live attendance, OT calculations & status breakdown matching desktop app
        today_dash = database.get_today_dashboard_attendance_and_leave()
        today_attendance = today_dash.get("attendance_list", [])
        today_ot_count = today_dash.get("ot_count", 0)
        present_count = today_dash.get("present_count", 0)
        late_count = today_dash.get("late_count", 0)
        expected_staff = today_dash.get("expected_staff", stats.get("employees", 0))

        # KPI detail groups matching Desktop popups
        dept_groups = database.get_department_detail_groups()
        pos_groups = database.get_position_detail_groups()
        birthday_data = database.get_birthday_details()
        dept_distribution = database.get_dept_distribution()

        # History rows for the filtered date / month and employee
        conn = database.get_connection()
        c = conn.cursor()
        sql = """
            SELECT a.id, a.emp_id, a.date, a.check_in, a.check_out, a.status, a.ot_hours, a.notes,
                   e.emp_code, e.name, e.khmer_name,
                   e.department, e.job_position
            FROM attendance a
            JOIN employees e ON a.emp_id = e.id
            WHERE 1=1
        """
        params = []
        if period_type == "day":
            sql += " AND a.date = ?"
            params.append(filter_date)
        else:
            sql += " AND a.date LIKE ?"
            params.append(f"{filter_month}%")

        # In attendance tab, load all rows for the month/day so user can switch between employees instantly in the browser dropdown
        # (CSV export still filters strictly by filter_emp_id)
        # if filter_emp_id:
        #     sql += " AND a.emp_id = ?"
        #     params.append(filter_emp_id)

        sql += " ORDER BY a.date DESC, a.check_in DESC"
        c.execute(sql, tuple(params))
        history_rows = [dict(row) for row in c.fetchall()]
        import re
        for r in history_rows:
            ot_h = float(r.get("ot_hours") or 0.0)
            ot_pay = round(ot_h * 1.50, 2)
            notes_str = r.get("notes") or ""
            m = re.search(r"\+\$(\d+\.\d{2})", notes_str)
            if m:
                try:
                    ot_pay = float(m.group(1))
                except Exception:
                    pass
            r["ot_pay"] = ot_pay

            # Extract patient name for clean display in notes column
            pat_match = re.search(r"អ្នកជំងឺ[៖:]\s*([^•\)\(\|,]+)", notes_str)
            if pat_match:
                r["patient_display"] = pat_match.group(1).strip()
            elif any(k in notes_str for k in ["Regular Checked Out", "Mobile QR Scan", "Checked out with Overtime"]):
                r["patient_display"] = "--"
            else:
                r["patient_display"] = notes_str or "--"

        total_ot_hours = round(sum(float(r.get("ot_hours") or 0.0) for r in history_rows), 1)
        total_ot_pay = round(sum(float(r.get("ot_pay") or 0.0) for r in history_rows), 2)

        # Departments list with employee count
        c.execute("""
            SELECT d.*, COUNT(e.id) as staff_count
            FROM departments d
            LEFT JOIN employees e ON (e.department = d.name OR e.department = d.name_kh) AND e.status != 'Resigned'
            GROUP BY d.id
            ORDER BY d.id ASC
        """)
        departments_full = [dict(row) for row in c.fetchall()]
        conn.close()

        # Leave requests & leave types
        leave_requests = database.get_leave_requests()
        leave_count = len(leave_requests)
        leave_types = database.get_leave_types()

        # Payroll records & live monthly OT summary
        payroll_month = int(request.args.get("payroll_month", date.today().month))
        payroll_year = int(request.args.get("payroll_year", date.today().year))
        payroll_summary = database.get_monthly_payroll_summary(payroll_month, payroll_year)
        payroll_records = database.get_payroll_records()

        # Staff requests
        staff_requests = database.get_staff_requests("All")

        # Staff permissions
        staff_permissions = database.get_staff_permissions()

        # Credentials & Clinic Info
        admin_creds = database.get_admin_credentials()
        staff_username = database.get_setting("staff_username", "staff")
        wifi_ssid = database.get_setting("wifi_ssid", "Mercy Dental Care")
        clinic_ip = database.get_setting("clinic_public_ip", "119.13.157.36")
        shift_start = database.get_setting("shift_start", "07:30")
        shift_end = database.get_setting("shift_end", "18:00")
        ot_rate = database.get_setting("ot_rate_per_hour", "1.50")
        clinic_name_en = database.get_setting("clinic_name_en", "Mercy Dental Care")
        clinic_name_kh = database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី")
        clinic_phone = database.get_setting("clinic_phone", "085 796 704")
        clinic_email = database.get_setting("clinic_email", "info@mercydentalcare.com")
        clinic_address = database.get_setting("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ")

        today_kh = date.today().strftime("%d-%b-%Y")

        payroll_config = {
            "working_days": int(database.get_setting("payroll_working_days", "26") or 26),
            "work_hours": int(database.get_setting("payroll_work_hours", "8") or 8),
            "incentive": float(database.get_setting("payroll_default_incentive", "50.0") or 50.0),
            "target_income": float(database.get_setting("payroll_target_income", "14000.0") or 14000.0),
            "target_bonus": float(database.get_setting("payroll_target_bonus", "50.0") or 50.0),
            "ot_rate": float(database.get_setting("payroll_ot_rate", "1.5") or 1.5)
        }

        leave_balances = database.get_employee_leave_balances()

        return render_template_string(
            get_main_app_html(),
            logo_b64=get_logo_b64(),
            stats=stats,
            today_date=today_date,
            today_kh=today_kh,
            period_type=period_type,
            filter_date=filter_date,
            filter_month=filter_month,
            sel_year=sel_year,
            sel_month=sel_month,
            filter_emp_id=filter_emp_id,
            filter_emp_name=filter_emp_name,
            total_ot_hours=total_ot_hours,
            total_ot_pay=total_ot_pay,
            today_attendance=today_attendance,
            today_ot_count=today_ot_count,
            present_count=present_count,
            late_count=late_count,
            expected_staff=expected_staff,
            dept_groups=dept_groups,
            pos_groups=pos_groups,
            birthday_data=birthday_data,
            dept_distribution=dept_distribution,
            departments_full=departments_full,
            leave_count=leave_count,
            leave_types=leave_types,
            leave_balances=leave_balances,
            payroll_records=payroll_records,
            payroll_summary=payroll_summary,
            payroll_month=payroll_month,
            payroll_year=payroll_year,
            payroll_config=payroll_config,
            staff_requests=staff_requests,
            staff_permissions=staff_permissions,
            admin_creds=admin_creds,
            staff_username=staff_username,
            clinic_name_en=clinic_name_en,
            clinic_name_kh=clinic_name_kh,
            clinic_phone=clinic_phone,
            clinic_email=clinic_email,
            clinic_address=clinic_address,
            history_rows=history_rows,
            employees=employees,
            leave_requests=leave_requests,
            wifi_ssid=wifi_ssid,
            clinic_ip=clinic_ip,
            shift_start=shift_start,
            shift_end=shift_end,
            ot_rate=ot_rate
        )

    # --- API ENDPOINTS FOR FULL CRUD ON WEBSITE ---

    @app.route("/admin/api/employee/save", methods=["POST"])
    def admin_api_employee_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        emp_id = data.get("emp_id")
        try:
            database.save_employee(data, emp_id=emp_id)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/employee/delete", methods=["POST"])
    def admin_api_employee_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        emp_id = data.get("id")
        if emp_id:
            database.delete_employee(emp_id)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing employee ID"}), 400

    @app.route("/admin/api/attendance/save", methods=["POST"])
    def admin_api_attendance_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        att_id = data.get("id")
        if att_id:
            database.update_attendance_record(
                att_id=att_id,
                check_in=data.get("check_in"),
                check_out=data.get("check_out"),
                status=data.get("status", "On Time"),
                ot_hours=data.get("ot_hours", 0.0),
                notes=data.get("notes", "")
            )
            return jsonify({"success": True})
        else:
            # New manual attendance punch
            emp_id = data.get("emp_id")
            att_date = data.get("date", date.today().isoformat())
            if emp_id:
                conn = database.get_connection()
                c = conn.cursor()
                c.execute("""
                    INSERT INTO attendance (emp_id, date, check_in, check_out, status, ot_hours, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (emp_id, att_date, data.get("check_in"), data.get("check_out"), data.get("status", "On Time"), data.get("ot_hours", 0.0), data.get("notes", "")))
                conn.commit()
                conn.close()
                return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    @app.route("/admin/api/attendance/delete", methods=["POST"])
    def admin_api_attendance_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        att_id = data.get("id")
        if att_id:
            database.delete_attendance_record(att_id)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing ID"}), 400

    @app.route("/admin/api/attendance/quick_punch", methods=["POST"])
    def admin_api_attendance_quick():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        emp_id = data.get("emp_id")
        p_type = data.get("type", "in")
        patient = data.get("patient_name", "")

        try:
            if p_type == "in":
                status, t = database.record_check_in(emp_id)
                return jsonify({"success": True, "message": f"Check-In កត់ត្រានៅម៉ោង {t} ({status})!"})
            elif p_type == "out":
                t, ot_h, ot_p = database.record_check_out(emp_id, has_overtime=False)
                return jsonify({"success": True, "message": f"Checked-Out កត់ត្រានៅម៉ោង {t}!"})
            elif p_type == "ot":
                t, ot_h, ot_p = database.record_check_out(emp_id, has_overtime=True, patient_name=patient)
                return jsonify({"success": True, "message": f"ចេញថែមម៉ោង OT ម៉ោង {t}! (+{ot_h} ម៉ោង = +${ot_p:.2f})"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/attendance/export_csv")
    def admin_api_attendance_export_csv():
        if not session.get("admin_logged_in"):
            return "Unauthorized", 401
        today_date = date.today().isoformat()
        current_month = date.today().strftime("%Y-%m")
        period_type = request.args.get("period_type", "month")
        filter_date = request.args.get("date", today_date)
        filter_month = request.args.get("month", current_month)
        filter_emp_id = request.args.get("emp_id", "").strip()

        conn = database.get_connection()
        c = conn.cursor()
        sql = """
            SELECT a.date, e.emp_code, e.name, e.khmer_name, e.department, e.job_position,
                   a.check_in, a.check_out, a.status, a.ot_hours, a.notes
            FROM attendance a
            JOIN employees e ON a.emp_id = e.id
            WHERE 1=1
        """
        params = []
        if period_type == "day":
            sql += " AND a.date = ?"
            params.append(filter_date)
            file_tag = filter_date
        else:
            sql += " AND a.date LIKE ?"
            params.append(f"{filter_month}%")
            file_tag = filter_month

        if filter_emp_id:
            sql += " AND a.emp_id = ?"
            params.append(filter_emp_id)
            file_tag += f"_emp{filter_emp_id}"

        sql += " ORDER BY a.date DESC, a.check_in ASC"
        c.execute(sql, tuple(params))
        rows = c.fetchall()
        conn.close()

        output = io.StringIO()
        output.write("\ufeff")  # BOM for Excel Khmer support
        writer = csv.writer(output)
        writer.writerow(["Date", "Employee ID", "English Name", "Khmer Name", "Department", "Position", "Check In", "Check Out", "Status", "OT Hours", "Notes"])
        for r in rows:
            writer.writerow([r["date"], r["emp_code"], r["name"], r["khmer_name"], r["department"], r["job_position"], r["check_in"] or "", r["check_out"] or "", r["status"] or "", r["ot_hours"] or 0, r["notes"] or ""])
        
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename=attendance_{file_tag}.csv"})

    @app.route("/admin/api/attendance/export_pdf")
    def admin_api_attendance_export_pdf():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        today_date = date.today().isoformat()
        current_month = date.today().strftime("%Y-%m")
        period_type = request.args.get("period_type", "month")
        filter_date = request.args.get("date", today_date)
        req_month = request.args.get("month", "").strip()
        req_year = request.args.get("year", "").strip()
        req_month_num = request.args.get("month_num", "").strip()

        if req_year and req_month_num:
            try:
                filter_month = f"{int(req_year):04d}-{int(req_month_num):02d}"
            except Exception:
                filter_month = req_month or current_month
        else:
            filter_month = req_month or current_month

        filter_emp_id = request.args.get("emp_id", "").strip()

        conn = database.get_connection()
        c = conn.cursor()
        sql = """
            SELECT a.date, a.check_in, a.check_out, a.status, a.ot_hours, a.notes,
                   e.id as emp_id, e.emp_code, e.name, e.khmer_name, e.department, e.job_position
            FROM attendance a
            JOIN employees e ON a.emp_id = e.id
            WHERE 1=1
        """
        params = []
        if period_type == "day":
            sql += " AND a.date = ?"
            params.append(filter_date)
            period_title = f"ប្រចាំថ្ងៃ៖ {filter_date}"
        else:
            sql += " AND a.date LIKE ?"
            params.append(f"{filter_month}%")
            period_title = f"ប្រចាំខែ៖ {filter_month}"

        if filter_emp_id:
            sql += " AND a.emp_id = ?"
            params.append(filter_emp_id)

        sql += " ORDER BY a.date ASC, a.check_in ASC"
        c.execute(sql, tuple(params))
        rows = [dict(row) for row in c.fetchall()]
        conn.close()

        total_ot_hours = 0.0
        total_ot_pay = 0.0
        filter_emp_name = ""
        import re
        for r in rows:
            if filter_emp_id and str(r.get("emp_id")) == str(filter_emp_id) and not filter_emp_name:
                filter_emp_name = f"{r.get('emp_code')} - {r.get('khmer_name')} ({r.get('name')})"

            ot_h = float(r.get("ot_hours") or 0.0)
            ot_pay = round(ot_h * 1.50, 2)
            notes_str = r.get("notes") or ""
            m = re.search(r"\+\$(\d+\.\d{2})", notes_str)
            if m:
                try:
                    ot_pay = float(m.group(1))
                except Exception:
                    pass
            r["ot_pay"] = ot_pay
            total_ot_hours += ot_h
            total_ot_pay += ot_pay

            pat_match = re.search(r"អ្នកជំងឺ[៖:]\s*([^•\)\(\|,]+)", notes_str)
            if pat_match:
                r["patient_display"] = pat_match.group(1).strip()
            elif any(k in notes_str for k in ["Regular Checked Out", "Mobile QR Scan", "Checked out with Overtime"]):
                r["patient_display"] = "--"
            else:
                r["patient_display"] = notes_str or "--"

        clinic_name_kh = database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី")
        clinic_name_en = database.get_setting("clinic_name_en", "Mercy Dental Care")
        clinic_address = database.get_setting("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ")
        clinic_phone = database.get_setting("clinic_phone", "012 999 888 / 098 776 543")
        logo_b64 = get_logo_b64()

        table_rows_html = ""
        for idx, r in enumerate(rows, start=1):
            cin = r.get("check_in") or "--:--"
            cout = r.get("check_out") or "--:--"
            ot_h = float(r.get("ot_hours") or 0.0)
            ot_p = float(r.get("ot_pay") or 0.0)
            ot_str = f"+{ot_h:.1f}h (${ot_p:.2f})" if ot_h > 0 else "0"
            stat = r.get("status") or "On Time"
            pat = r.get("patient_display") or "--"
            table_rows_html += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="text-align:center; padding:6px 4px; font-size:11px; color:#64748B;">{idx}</td>
                <td style="text-align:center; padding:6px 4px; font-weight:700; color:#4338CA; font-family:monospace; font-size:11.5px;">{r.get('emp_code', '')}</td>
                <td style="padding:6px 8px; font-size:11.5px; white-space:nowrap;">
                    <span style="font-weight:700; color:#0F172A; white-space:nowrap;">{r.get('khmer_name', '')}</span>
                    <span style="font-size:10px; color:#64748B; white-space:nowrap;">({r.get('name', '')})</span>
                </td>
                <td style="padding:6px 8px; font-size:11px; color:#334155;">{r.get('job_position', '')}</td>
                <td style="text-align:center; padding:6px 6px; font-size:11px; white-space:nowrap;">{r.get('date', '')}</td>
                <td style="text-align:center; padding:6px 4px; font-size:11.5px; font-weight:600; color:#059669;">{cin}</td>
                <td style="text-align:center; padding:6px 4px; font-size:11.5px; font-weight:600; color:#DC2626;">{cout}</td>
                <td style="text-align:center; padding:6px 6px; font-size:11px;">{stat}</td>
                <td style="text-align:center; padding:6px 6px; font-size:11.5px; font-weight:700; color:#7C3AED;">{ot_str}</td>
                <td style="padding:6px 8px; font-size:11px; color:#475569; max-width:140px;">{pat}</td>
            </tr>
            """

        if not rows:
            table_rows_html = """
            <tr>
                <td colspan="10" style="text-align:center; padding:30px; color:#94A3B8;">ពុំមានទិន្នន័យវត្តមានត្រូវនឹងលក្ខខណ្ឌស្វែងរកនេះទេ</td>
            </tr>
            """

        logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="max-height:60px; max-width:110px;" />' if logo_b64 else '<h3>Mercy Dental</h3>'
        filter_emp_badge = f'<div style="font-size:12.5px; color:#1E293B; margin-top:4px;">បុគ្គលិក៖ <strong>{filter_emp_name}</strong></div>' if filter_emp_name else ''

        pdf_html = f"""<!DOCTYPE html>
<html lang="km">
<head>
<meta charset="utf-8">
<title>របាយការណ៍វត្តមាន_{period_title.replace(' ', '_')}</title>
<link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;500;600;700&family=Outfit:wght@400;600;700;800&family=Moul&display=swap" rel="stylesheet">
<style>
    @page {{
        size: A4 landscape;
        margin: 10mm 10mm 12mm 10mm;
    }}
    * {{
        box-sizing: border-box;
    }}
    body {{
        font-family: 'Kantumruy Pro', 'Segoe UI', Arial, sans-serif;
        color: #0F172A;
        background: #F1F5F9;
        margin: 0;
        padding: 20px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
    .print-sheet {{
        background: #FFFFFF;
        max-width: 1050px;
        margin: 0 auto;
        padding: 24px 30px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }}
    .print-actions {{
        max-width: 1050px;
        margin: 0 auto 14px auto;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }}
    .btn-print {{
        background: #4338CA;
        color: #FFFFFF;
        border: none;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 6px rgba(67,56,202,0.25);
    }}
    .btn-close {{
        background: #E2E8F0;
        color: #334155;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
    }}
    @media print {{
        body {{
            background: #FFFFFF;
            padding: 0;
        }}
        .print-sheet {{
            box-shadow: none;
            padding: 0;
            max-width: 100%;
        }}
        .no-print {{
            display: none !important;
        }}
    }}
</style>
</head>
<body>

<div class="print-actions no-print">
    <button class="btn-print" onclick="window.print()">💾 រក្សាទុកជា PDF (Save as PDF) / បោះពុម្ព</button>
    <button class="btn-close" onclick="window.close()">❌ បិទ (Close)</button>
</div>

<div class="print-sheet">
    <table style="width:100%; border-bottom:2px solid #4338CA; padding-bottom:10px; margin-bottom:12px;">
        <tr>
            <td style="width:15%; vertical-align:middle;">
                {logo_img}
            </td>
            <td style="width:55%; vertical-align:middle; padding-left:14px;">
                <h2 style="margin:0; font-family:'Moul', serif; font-size:16px; color:#4338CA;">{clinic_name_kh}</h2>
                <h3 style="margin:2px 0 0 0; font-family:'Outfit', sans-serif; font-size:13px; color:#1E293B; letter-spacing:0.5px;">{clinic_name_en}</h3>
                <div style="font-size:10.5px; color:#64748B; margin-top:3px;">{clinic_address}</div>
                <div style="font-size:10.5px; color:#64748B;">ទូរស័ព្ទ៖ {clinic_phone}</div>
            </td>
            <td style="width:30%; vertical-align:top; text-align:right; font-size:11px; color:#475569;">
                <div><strong>កាលបរិច្ឆេទរបាយការណ៍៖</strong> {today_date}</div>
                <div style="margin-top:2px; font-weight:700; color:#4338CA;">{period_title}</div>
                <div style="margin-top:2px;">ចំនួនកំណត់ត្រាសរុប៖ <strong>{len(rows)}</strong></div>
            </td>
        </tr>
    </table>

    <div style="text-align:center; margin-bottom:14px; background:#EEEDFB; border:1px solid #C7D2FE; border-radius:6px; padding:8px;">
        <h1 style="margin:0; font-size:15px; color:#4338CA;">របាយការណ៍វត្តមាន និងម៉ោងបន្ថែមបុគ្គលិក (Staff Attendance & OT Report)</h1>
        {filter_emp_badge}
    </div>

    <table style="width:100%; border-collapse:collapse; margin-bottom:14px; font-size:11.5px;">
        <thead>
            <tr style="background:#F8FAFC; border-bottom:2px solid #CBD5E1; color:#334155;">
                <th style="padding:8px 4px; text-align:center; width:35px;">ល.រ</th>
                <th style="padding:8px 6px; text-align:center; width:55px;">កូដ</th>
                <th style="padding:8px 8px; text-align:left;">ឈ្មោះបុគ្គលិក</th>
                <th style="padding:8px 8px; text-align:left;">តួនាទី</th>
                <th style="padding:8px 6px; text-align:center; width:85px;">កាលបរិច្ឆេទ</th>
                <th style="padding:8px 4px; text-align:center; width:65px;">ចូល (In)</th>
                <th style="padding:8px 4px; text-align:center; width:65px;">ចេញ (Out)</th>
                <th style="padding:8px 6px; text-align:center; width:75px;">ស្ថានភាព</th>
                <th style="padding:8px 6px; text-align:center; width:95px;">ថែមម៉ោង (OT)</th>
                <th style="padding:8px 8px; text-align:left;">អ្នកជំងឺ / សម្គាល់</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
        <tfoot>
            <tr style="background:#F8FAFC; border-top:2px solid #CBD5E1; font-weight:bold;">
                <td colspan="8" style="text-align:right; padding:10px 10px; font-size:12px; color:#1E293B;">
                    ⚡ សរុបម៉ោងថែមទាំងអស់ (Auto Total OT):
                </td>
                <td style="text-align:center; padding:10px 8px; font-size:12.5px; font-weight:800; color:#7C3AED; background:#FAF5FF; border-left:1px solid #E2E8F0; border-right:1px solid #E2E8F0; white-space:nowrap;">
                    +{total_ot_hours:.1f}h (${total_ot_pay:.2f})
                </td>
                <td style="background:#F8FAFC;"></td>
            </tr>
        </tfoot>
    </table>

    <table style="width:100%; margin-top:28px; text-align:center; font-size:11.5px; color:#334155;">
        <tr>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">អ្នករៀបចំ (Prepared By)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">ប្រធានធនធានមនុស្ស (HR / Accountant)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:34%; vertical-align:top;">
                <div style="font-weight:700;">ប្រធានគ្លីនិក (Clinic Director)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងត្រា</div>
            </td>
        </tr>
    </table>
</div>

<script>
    window.addEventListener('load', () => {{
        setTimeout(() => {{
            window.print();
        }}, 400);
    }});
</script>
</body>
</html>"""
        return Response(pdf_html, mimetype="text/html")

    @app.route("/admin/api/employees/export_pdf")
    def admin_api_employees_export_pdf():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        dept_filter = request.args.get("dept", "").strip().lower()
        q_filter = request.args.get("q", "").strip().lower()

        emps = database.get_all_employees()
        filtered = []
        for e in emps:
            e_dept = (e.get("department") or "").lower()
            e_text = f"{e.get('emp_code', '')} {e.get('khmer_name', '')} {e.get('name', '')} {e.get('job_position', '')}".lower()
            if dept_filter and dept_filter not in e_dept:
                continue
            if q_filter and q_filter not in e_text:
                continue
            filtered.append(e)

        today_date = date.today().isoformat()
        clinic_name_kh = database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី")
        clinic_name_en = database.get_setting("clinic_name_en", "Mercy Dental Care")
        clinic_address = database.get_setting("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ")
        clinic_phone = database.get_setting("clinic_phone", "085 796 704")
        logo_b64 = get_logo_b64()

        male_count = sum(1 for e in filtered if (e.get("gender") or "").lower() in ["male", "ប្រុស"])
        female_count = sum(1 for e in filtered if (e.get("gender") or "").lower() in ["female", "ស្រី"])
        total_salary = sum(float(e.get("base_salary") or 0.0) for e in filtered)

        table_rows_html = ""
        for idx, e in enumerate(filtered, start=1):
            sal_str = f"${float(e.get('base_salary') or 0.0):.2f}"
            phone_str = e.get("phone") or "--"
            table_rows_html += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="text-align:center; padding:7px 4px; font-size:11px; color:#64748B;">{idx}</td>
                <td style="text-align:center; padding:7px 4px; font-weight:700; color:#4338CA; font-family:monospace; font-size:12px;">{e.get('emp_code', '')}</td>
                <td style="padding:7px 8px; font-size:12px;">
                    <div style="font-weight:700; color:#0F172A;">{e.get('khmer_name', '')}</div>
                    <div style="font-size:10.5px; color:#64748B;">{e.get('name', '')}</div>
                </td>
                <td style="text-align:center; padding:7px 6px; font-size:11.5px;">{e.get('gender', '')}</td>
                <td style="padding:7px 8px; font-size:11.5px; color:#334155;">{e.get('job_position', '')}</td>
                <td style="text-align:center; padding:7px 6px; font-size:11.5px;">{phone_str}</td>
                <td style="text-align:right; padding:7px 8px; font-size:12px; font-weight:700; color:#15803D;">{sal_str}</td>
                <td style="text-align:center; padding:7px 6px; font-size:11px;"><span style="color:#16A34A; font-weight:700;">● {e.get('status', 'Active')}</span></td>
            </tr>
            """

        if not filtered:
            table_rows_html = '<tr><td colspan="8" style="text-align:center; padding:30px; color:#94A3B8;">ពុំមានទិន្នន័យបុគ្គលិកទេ</td></tr>'

        logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="max-height:60px; max-width:110px;" />' if logo_b64 else '<h3>Mercy Dental</h3>'

        html = f"""<!DOCTYPE html>
<html lang="km">
<head>
<meta charset="utf-8">
<title>របាយការណ៍បញ្ជីបុគ្គលិក_{today_date}</title>
<link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;500;600;700&family=Outfit:wght@400;600;700;800&family=Moul&display=swap" rel="stylesheet">
<style>
    @page {{ size: A4 portrait; margin: 12mm 10mm 14mm 10mm; }}
    * {{ box-sizing: border-box; }}
    body {{
        font-family: 'Kantumruy Pro', 'Segoe UI', Arial, sans-serif;
        color: #0F172A;
        background: #F1F5F9;
        margin: 0;
        padding: 20px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
    .print-sheet {{
        background: #FFFFFF;
        max-width: 900px;
        margin: 0 auto;
        padding: 24px 30px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }}
    .print-actions {{
        max-width: 900px;
        margin: 0 auto 14px auto;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }}
    .btn-print {{
        background: #4338CA;
        color: #FFFFFF;
        border: none;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}
    .btn-close {{
        background: #E2E8F0;
        color: #334155;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
    }}
    @media print {{
        body {{ background: #FFFFFF; padding: 0; }}
        .print-sheet {{ box-shadow: none; padding: 0; max-width: 100%; }}
        .no-print {{ display: none !important; }}
    }}
</style>
</head>
<body>
<div class="print-actions no-print">
    <button class="btn-print" onclick="window.print()">💾 រក្សាទុកជា PDF (Save as PDF) / បោះពុម្ព</button>
    <button class="btn-close" onclick="window.close()">❌ បិទ (Close)</button>
</div>
<div class="print-sheet">
    <table style="width:100%; border-bottom:2px solid #4338CA; padding-bottom:10px; margin-bottom:12px;">
        <tr>
            <td style="width:15%; vertical-align:middle;">{logo_img}</td>
            <td style="width:55%; vertical-align:middle; padding-left:14px;">
                <h2 style="margin:0; font-family:'Moul', serif; font-size:16px; color:#4338CA;">{clinic_name_kh}</h2>
                <h3 style="margin:2px 0 0 0; font-family:'Outfit', sans-serif; font-size:13px; color:#1E293B; letter-spacing:0.5px;">{clinic_name_en}</h3>
                <div style="font-size:10.5px; color:#64748B; margin-top:3px;">{clinic_address}</div>
                <div style="font-size:10.5px; color:#64748B;">ទូរស័ព្ទ៖ {clinic_phone}</div>
            </td>
            <td style="width:30%; vertical-align:top; text-align:right; font-size:11px; color:#475569;">
                <div><strong>កាលបរិច្ឆេទរបាយការណ៍៖</strong> {today_date}</div>
                <div style="margin-top:3px;">ចំនួនបុគ្គលិកសរុប៖ <strong>{len(filtered)} នាក់</strong></div>
                <div style="font-size:10px; color:#64748B;">(ប្រុស: {male_count} / ស្រី: {female_count})</div>
            </td>
        </tr>
    </table>
    <div style="text-align:center; margin-bottom:14px; background:#EEEDFB; border:1px solid #C7D2FE; border-radius:6px; padding:8px;">
        <h1 style="margin:0; font-size:15px; color:#4338CA;">របាយការណ៍បញ្ជីបុគ្គលិកគ្លីនិក (Clinic Staff Directory Report)</h1>
    </div>
    <table style="width:100%; border-collapse:collapse; margin-bottom:14px; font-size:11.5px;">
        <thead>
            <tr style="background:#F8FAFC; border-bottom:2px solid #CBD5E1; color:#334155;">
                <th style="padding:8px 4px; text-align:center; width:35px;">ល.រ</th>
                <th style="padding:8px 6px; text-align:center; width:60px;">កូដ</th>
                <th style="padding:8px 8px; text-align:left;">ឈ្មោះបុគ្គលិក</th>
                <th style="padding:8px 6px; text-align:center; width:55px;">ភេទ</th>
                <th style="padding:8px 8px; text-align:left;">តួនាទី (Position)</th>
                <th style="padding:8px 6px; text-align:center; width:95px;">លេខទូរស័ព្ទ</th>
                <th style="padding:8px 8px; text-align:right; width:95px;">ប្រាក់ខែគោល</th>
                <th style="padding:8px 6px; text-align:center; width:70px;">ស្ថានភាព</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
        <tfoot>
            <tr style="background:#F8FAFC; border-top:2px solid #CBD5E1; font-weight:bold;">
                <td colspan="6" style="text-align:right; padding:10px 10px; font-size:12px; color:#1E293B;">
                    សរុបថវិកាបៀវត្សគោលប្រចាំខែ (Total Base Payroll):
                </td>
                <td style="text-align:right; padding:10px 8px; font-size:12.5px; font-weight:800; color:#15803D; white-space:nowrap;">
                    ${total_salary:.2f}
                </td>
                <td></td>
            </tr>
        </tfoot>
    </table>
    <table style="width:100%; margin-top:28px; text-align:center; font-size:11.5px; color:#334155;">
        <tr>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">អ្នករៀបចំ (Prepared By)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">ប្រធានធនធានមនុស្ស (HR Manager)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">នាយកគ្លីនិក (Clinic Director)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងត្រា</div>
            </td>
        </tr>
    </table>
</div>
<script>
    window.addEventListener('load', () => {{
        setTimeout(() => {{
            window.print();
        }}, 500);
    }});
</script>
</body>
</html>"""
        return Response(html, mimetype="text/html")

    @app.route("/admin/api/leave/export_pdf")
    def admin_api_leave_export_pdf():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        dept_filter = request.args.get("dept", "").strip().lower()
        q_filter = request.args.get("q", "").strip().lower()

        bals = database.get_employee_leave_balances()
        filtered = []
        for b in bals:
            b_dept = (b.get("department") or "").lower()
            b_text = f"{b.get('emp_code', '')} {b.get('khmer_name', '')} {b.get('name', '')} {b.get('job_position', '')}".lower()
            if dept_filter and dept_filter not in b_dept:
                continue
            if q_filter and q_filter not in b_text:
                continue
            filtered.append(b)

        today_date = date.today().isoformat()
        clinic_name_kh = database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី")
        clinic_name_en = database.get_setting("clinic_name_en", "Mercy Dental Care")
        clinic_address = database.get_setting("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ")
        clinic_phone = database.get_setting("clinic_phone", "085 796 704")
        logo_b64 = get_logo_b64()

        table_rows_html = ""
        for idx, b in enumerate(filtered, start=1):
            table_rows_html += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="text-align:center; padding:7px 4px; font-size:11px; color:#64748B;">{idx}</td>
                <td style="text-align:center; padding:7px 4px; font-weight:700; color:#4338CA; font-family:monospace; font-size:12px;">{b.get('emp_code', '')}</td>
                <td style="padding:7px 8px; font-size:12px;">
                    <div style="font-weight:700; color:#0F172A;">{b.get('khmer_name', '')}</div>
                    <div style="font-size:10.5px; color:#64748B;">{b.get('name', '')}</div>
                </td>
                <td style="padding:7px 8px; font-size:11.5px; color:#334155;">{b.get('job_position', '')}</td>
                <td style="text-align:center; padding:7px 6px; font-size:11.5px; font-weight:700; color:#DC2626;">{b.get('used', 0)} ថ្ងៃ</td>
                <td style="text-align:center; padding:7px 6px; font-size:11.5px; font-weight:700; color:#15803D;">{b.get('balance', 18)} ថ្ងៃ</td>
                <td style="text-align:center; padding:7px 6px; font-size:11.5px; color:#B45309;">{b.get('sick', 0)} ថ្ងៃ</td>
            </tr>
            """

        if not filtered:
            table_rows_html = '<tr><td colspan="7" style="text-align:center; padding:30px; color:#94A3B8;">ពុំមានទិន្នន័យច្បាប់ទេ</td></tr>'

        logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="max-height:60px; max-width:110px;" />' if logo_b64 else '<h3>Mercy Dental</h3>'

        html = f"""<!DOCTYPE html>
<html lang="km">
<head>
<meta charset="utf-8">
<title>របាយការណ៍សមតុល្យច្បាប់_{today_date}</title>
<link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;500;600;700&family=Outfit:wght@400;600;700;800&family=Moul&display=swap" rel="stylesheet">
<style>
    @page {{ size: A4 portrait; margin: 12mm 10mm 14mm 10mm; }}
    * {{ box-sizing: border-box; }}
    body {{
        font-family: 'Kantumruy Pro', 'Segoe UI', Arial, sans-serif;
        color: #0F172A;
        background: #F1F5F9;
        margin: 0;
        padding: 20px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
    .print-sheet {{
        background: #FFFFFF;
        max-width: 900px;
        margin: 0 auto;
        padding: 24px 30px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }}
    .print-actions {{
        max-width: 900px;
        margin: 0 auto 14px auto;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }}
    .btn-print {{
        background: #4338CA;
        color: #FFFFFF;
        border: none;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}
    .btn-close {{
        background: #E2E8F0;
        color: #334155;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
    }}
    @media print {{
        body {{ background: #FFFFFF; padding: 0; }}
        .print-sheet {{ box-shadow: none; padding: 0; max-width: 100%; }}
        .no-print {{ display: none !important; }}
    }}
</style>
</head>
<body>
<div class="print-actions no-print">
    <button class="btn-print" onclick="window.print()">💾 រក្សាទុកជា PDF (Save as PDF) / បោះពុម្ព</button>
    <button class="btn-close" onclick="window.close()">❌ បិទ (Close)</button>
</div>
<div class="print-sheet">
    <table style="width:100%; border-bottom:2px solid #4338CA; padding-bottom:10px; margin-bottom:12px;">
        <tr>
            <td style="width:15%; vertical-align:middle;">{logo_img}</td>
            <td style="width:55%; vertical-align:middle; padding-left:14px;">
                <h2 style="margin:0; font-family:'Moul', serif; font-size:16px; color:#4338CA;">{clinic_name_kh}</h2>
                <h3 style="margin:2px 0 0 0; font-family:'Outfit', sans-serif; font-size:13px; color:#1E293B; letter-spacing:0.5px;">{clinic_name_en}</h3>
                <div style="font-size:10.5px; color:#64748B; margin-top:3px;">{clinic_address}</div>
                <div style="font-size:10.5px; color:#64748B;">ទូរស័ព្ទ៖ {clinic_phone}</div>
            </td>
            <td style="width:30%; vertical-align:top; text-align:right; font-size:11px; color:#475569;">
                <div><strong>កាលបរិច្ឆេទរបាយការណ៍៖</strong> {today_date}</div>
                <div style="margin-top:3px;">ចំនួនបុគ្គលិកសរុប៖ <strong>{len(filtered)} នាក់</strong></div>
            </td>
        </tr>
    </table>
    <div style="text-align:center; margin-bottom:14px; background:#EEEDFB; border:1px solid #C7D2FE; border-radius:6px; padding:8px;">
        <h1 style="margin:0; font-size:15px; color:#4338CA;">របាយការណ៍សមតុល្យច្បាប់ឈប់សម្រាកបុគ្គលិក (Staff Leave Balances Report)</h1>
    </div>
    <table style="width:100%; border-collapse:collapse; margin-bottom:14px; font-size:11.5px;">
        <thead>
            <tr style="background:#F8FAFC; border-bottom:2px solid #CBD5E1; color:#334155;">
                <th style="padding:8px 4px; text-align:center; width:35px;">ល.រ</th>
                <th style="padding:8px 6px; text-align:center; width:60px;">កូដ</th>
                <th style="padding:8px 8px; text-align:left;">ឈ្មោះបុគ្គលិក</th>
                <th style="padding:8px 8px; text-align:left;">តួនាទី</th>
                <th style="padding:8px 6px; text-align:center; width:95px;">បានឈប់ (Used)</th>
                <th style="padding:8px 6px; text-align:center; width:95px;">នៅសល់ (Balance)</th>
                <th style="padding:8px 6px; text-align:center; width:90px;">ច្បាប់ឈឺ (Sick)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
    <table style="width:100%; margin-top:28px; text-align:center; font-size:11.5px; color:#334155;">
        <tr>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">អ្នករៀបចំ (Prepared By)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">ប្រធានធនធានមនុស្ស (HR Manager)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">នាយកគ្លីនិក (Clinic Director)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងត្រា</div>
            </td>
        </tr>
    </table>
</div>
<script>
    window.addEventListener('load', () => {{
        setTimeout(() => {{
            window.print();
        }}, 500);
    }});
</script>
</body>
</html>"""
        return Response(html, mimetype="text/html")

    @app.route("/admin/api/payroll/export_pdf")
    def admin_api_payroll_export_pdf():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        req_month = request.args.get("month", "10").strip()
        req_year = request.args.get("year", "2026").strip()

        records = database.get_payroll_records()
        today_date = date.today().isoformat()
        clinic_name_kh = database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី")
        clinic_name_en = database.get_setting("clinic_name_en", "Mercy Dental Care")
        clinic_address = database.get_setting("clinic_address", "ផ្លូវ ១៩៥២, ភូមិពោងពាយ, សង្កាត់ភ្នំពេញថ្មី, ខណ្ឌសែនសុខ, រាជធានីភ្នំពេញ")
        clinic_phone = database.get_setting("clinic_phone", "085 796 704")
        logo_b64 = get_logo_b64()

        total_net_payout = 0.0
        total_base = 0.0
        table_rows_html = ""
        for idx, r in enumerate(records, start=1):
            base_s = float(r.get("base_salary") or 0.0)
            gross_s = float(r.get("gross_salary") or 0.0)
            net_s = float(r.get("net_salary") or 0.0)
            total_base += base_s
            total_net_payout += net_s
            table_rows_html += f"""
            <tr style="border-bottom: 1px solid #E2E8F0;">
                <td style="text-align:center; padding:7px 4px; font-size:11px; color:#64748B;">{idx}</td>
                <td style="text-align:center; padding:7px 6px; font-weight:700; color:#4338CA; font-family:monospace; font-size:11.5px;">{r.get('emp_code', '')}</td>
                <td style="padding:7px 8px; font-size:12px;">
                    <div style="font-weight:700; color:#0F172A;">{r.get('khmer_name', '')}</div>
                    <div style="font-size:10.5px; color:#64748B;">{r.get('name', '')}</div>
                </td>
                <td style="padding:7px 8px; font-size:11.5px; color:#334155;">{r.get('department', '')}</td>
                <td style="text-align:center; padding:7px 6px; font-size:11px;">{r.get('date_from', '')} - {r.get('date_to', '')}</td>
                <td style="text-align:right; padding:7px 8px; font-size:12px; font-weight:600;">${base_s:.2f}</td>
                <td style="text-align:right; padding:7px 8px; font-size:12px; font-weight:600; color:#4338CA;">${gross_s:.2f}</td>
                <td style="text-align:right; padding:7px 8px; font-size:12.5px; font-weight:800; color:#15803D;">${net_s:.2f}</td>
            </tr>
            """

        if not records:
            table_rows_html = '<tr><td colspan="8" style="text-align:center; padding:30px; color:#94A3B8;">ពុំមានទិន្នន័យប្រាក់បៀវត្សទេ</td></tr>'

        logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="max-height:60px; max-width:110px;" />' if logo_b64 else '<h3>Mercy Dental</h3>'

        html = f"""<!DOCTYPE html>
<html lang="km">
<head>
<meta charset="utf-8">
<title>របាយការណ៍ប្រាក់បៀវត្ស_{req_year}_{req_month}</title>
<link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;500;600;700&family=Outfit:wght@400;600;700;800&family=Moul&display=swap" rel="stylesheet">
<style>
    @page {{ size: A4 landscape; margin: 10mm 10mm 12mm 10mm; }}
    * {{ box-sizing: border-box; }}
    body {{
        font-family: 'Kantumruy Pro', 'Segoe UI', Arial, sans-serif;
        color: #0F172A;
        background: #F1F5F9;
        margin: 0;
        padding: 20px;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
    .print-sheet {{
        background: #FFFFFF;
        max-width: 1050px;
        margin: 0 auto;
        padding: 24px 30px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }}
    .print-actions {{
        max-width: 1050px;
        margin: 0 auto 14px auto;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }}
    .btn-print {{
        background: #4338CA;
        color: #FFFFFF;
        border: none;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}
    .btn-close {{
        background: #E2E8F0;
        color: #334155;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
    }}
    @media print {{
        body {{ background: #FFFFFF; padding: 0; }}
        .print-sheet {{ box-shadow: none; padding: 0; max-width: 100%; }}
        .no-print {{ display: none !important; }}
    }}
</style>
</head>
<body>
<div class="print-actions no-print">
    <button class="btn-print" onclick="window.print()">💾 រក្សាទុកជា PDF (Save as PDF) / បោះពុម្ព</button>
    <button class="btn-close" onclick="window.close()">❌ បិទ (Close)</button>
</div>
<div class="print-sheet">
    <table style="width:100%; border-bottom:2px solid #4338CA; padding-bottom:10px; margin-bottom:12px;">
        <tr>
            <td style="width:15%; vertical-align:middle;">{logo_img}</td>
            <td style="width:55%; vertical-align:middle; padding-left:14px;">
                <h2 style="margin:0; font-family:'Moul', serif; font-size:16px; color:#4338CA;">{clinic_name_kh}</h2>
                <h3 style="margin:2px 0 0 0; font-family:'Outfit', sans-serif; font-size:13px; color:#1E293B; letter-spacing:0.5px;">{clinic_name_en}</h3>
                <div style="font-size:10.5px; color:#64748B; margin-top:3px;">{clinic_address}</div>
                <div style="font-size:10.5px; color:#64748B;">ទូរស័ព្ទ៖ {clinic_phone}</div>
            </td>
            <td style="width:30%; vertical-align:top; text-align:right; font-size:11px; color:#475569;">
                <div><strong>កាលបរិច្ឆេទរបាយការណ៍៖</strong> {today_date}</div>
                <div style="margin-top:2px; font-weight:700; color:#4338CA;">ប្រចាំខែ៖ {req_year}-{req_month}</div>
                <div style="margin-top:2px;">ចំនួនបុគ្គលិកសរុប៖ <strong>{len(records)} នាក់</strong></div>
            </td>
        </tr>
    </table>
    <div style="text-align:center; margin-bottom:14px; background:#EEEDFB; border:1px solid #C7D2FE; border-radius:6px; padding:8px;">
        <h1 style="margin:0; font-size:15px; color:#4338CA;">របាយការណ៍ចំណាយបៀវត្សបុគ្គលិក (Staff Monthly Payroll Sheet)</h1>
    </div>
    <table style="width:100%; border-collapse:collapse; margin-bottom:14px; font-size:11.5px;">
        <thead>
            <tr style="background:#F8FAFC; border-bottom:2px solid #CBD5E1; color:#334155;">
                <th style="padding:8px 4px; text-align:center; width:35px;">ល.រ</th>
                <th style="padding:8px 6px; text-align:center; width:70px;">កូដ (Code)</th>
                <th style="padding:8px 8px; text-align:left;">ឈ្មោះបុគ្គលិក</th>
                <th style="padding:8px 8px; text-align:left;">ផ្នែក</th>
                <th style="padding:8px 6px; text-align:center; width:140px;">កាលបរិច្ឆេទបើក</th>
                <th style="padding:8px 8px; text-align:right; width:95px;">ប្រាក់ខែគោល</th>
                <th style="padding:8px 8px; text-align:right; width:95px;">ប្រាក់សរុប (Gross)</th>
                <th style="padding:8px 8px; text-align:right; width:110px;">ប្រាក់ជាក់ស្តែង (Net)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
        <tfoot>
            <tr style="background:#F8FAFC; border-top:2px solid #CBD5E1; font-weight:bold;">
                <td colspan="5" style="text-align:right; padding:10px 10px; font-size:12px; color:#1E293B;">
                    សរុបប្រាក់បៀវត្សជាក់ស្តែង (Total Net Payout):
                </td>
                <td style="text-align:right; padding:10px 8px; font-size:12px; font-weight:700;">${total_base:.2f}</td>
                <td></td>
                <td style="text-align:right; padding:10px 8px; font-size:13px; font-weight:800; color:#15803D; white-space:nowrap;">
                    ${total_net_payout:.2f}
                </td>
            </tr>
        </tfoot>
    </table>
    <table style="width:100%; margin-top:28px; text-align:center; font-size:11.5px; color:#334155;">
        <tr>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">អ្នករៀបចំ (Prepared By)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">ប្រធានគណនេយ្យ / HR</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងឈ្មោះ</div>
            </td>
            <td style="width:33%; vertical-align:top;">
                <div style="font-weight:700;">នាយកគ្លីនិក (Clinic Director)</div>
                <div style="height:60px;"></div>
                <div style="border-top:1px dashed #94A3B8; width:70%; margin:0 auto; padding-top:4px;">ហត្ថលេខា និងត្រា</div>
            </td>
        </tr>
    </table>
</div>
<script>
    window.addEventListener('load', () => {{
        setTimeout(() => {{
            window.print();
        }}, 500);
    }});
</script>
</body>
</html>"""
        return Response(html, mimetype="text/html")

    @app.route("/admin/api/leave/save", methods=["POST"])
    def admin_api_leave_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        try:
            database.add_leave_request(
                emp_id=data.get("emp_id"),
                leave_type=data.get("leave_type", "Annual"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                days=data.get("days", 1),
                reason=data.get("reason", "")
            )
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/leave/status", methods=["POST"])
    def admin_api_leave_status():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        leave_id = data.get("id")
        status = data.get("status")
        if leave_id and status:
            database.update_leave_status(leave_id, status)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing fields"}), 400

    @app.route("/admin/api/leave/delete", methods=["POST"])
    def admin_api_leave_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        leave_id = data.get("id")
        if leave_id:
            database.delete_leave_request(leave_id)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing ID"}), 400

    @app.route("/admin/api/leave_type/save", methods=["POST"])
    def admin_api_leave_type_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        try:
            database.save_leave_type(
                name=data.get("name", "").strip(),
                name_kh=data.get("name_kh", "").strip(),
                days_allowed=int(data.get("days_allowed", 18)),
                type_id=data.get("id")
            )
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/leave_type/delete", methods=["POST"])
    def admin_api_leave_type_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        tid = data.get("id")
        if tid:
            database.delete_leave_type(tid)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing ID"}), 400

    @app.route("/admin/api/leave_balance/list", methods=["GET"])
    def admin_api_leave_balance_list():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        try:
            bals = database.get_employee_leave_balances()
            return jsonify({"success": True, "data": bals})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/leave_balance/save", methods=["POST"])
    def admin_api_leave_balance_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        emp_id = data.get("emp_id")
        entitled = float(data.get("entitled", 18.0) or 18.0)
        used = float(data.get("used", 0.0) or 0.0)
        sick = float(data.get("sick", 0.0) or 0.0)
        notes = data.get("notes", "")
        if not emp_id:
            return jsonify({"success": False, "message": "Missing emp_id"}), 400
        try:
            database.save_employee_leave_balance(int(emp_id), entitled, used, sick, notes)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/calendar_notes", methods=["GET"])
    def admin_api_calendar_notes():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        m = request.args.get("month")
        y = request.args.get("year")
        d = request.args.get("date")
        try:
            notes = database.get_calendar_notes(month=int(m) if m else None, year=int(y) if y else None, date=d)
            return jsonify({"success": True, "data": notes})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/calendar_notes/save", methods=["POST"])
    def admin_api_calendar_notes_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        date_str = (data.get("date") or "").strip()
        title = (data.get("title") or "").strip()
        note_type = data.get("note_type", "Note")
        color = data.get("color", "#2563EB")
        note_id = data.get("id")
        if not date_str or not title:
            return jsonify({"success": False, "message": "សូមបញ្ចូលកាលបរិច្ឆេទ និងខ្លឹមសារកំណត់សម្គាល់"}), 400
        try:
            nid = database.save_calendar_note(date=date_str, title=title, note_type=note_type, color=color, note_id=int(note_id) if note_id else None)
            return jsonify({"success": True, "id": nid})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/calendar_notes/delete", methods=["POST"])
    def admin_api_calendar_notes_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        note_id = data.get("id")
        if not note_id:
            return jsonify({"success": False, "message": "Missing note id"}), 400
        try:
            database.delete_calendar_note(int(note_id))
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400


    @app.route("/admin/api/payroll/summary", methods=["GET"])
    def admin_api_payroll_summary():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        m = int(request.args.get("month", date.today().month))
        y = int(request.args.get("year", date.today().year))
        try:
            summary = database.get_monthly_payroll_summary(m, y)
            return jsonify({"success": True, "month": m, "year": y, "data": summary})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/payroll/generate", methods=["POST"])
    def admin_api_payroll_generate():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        m = int(data.get("month", date.today().month))
        y = int(data.get("year", date.today().year))
        try:
            cnt = database.generate_monthly_payroll(m, y)
            return jsonify({"success": True, "count": cnt})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/payroll/record", methods=["GET"])
    def admin_api_payroll_record():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        pid = request.args.get("id")
        if pid:
            try:
                rec = database.get_payroll_by_id(int(pid))
                return jsonify({"success": True, "record": rec})
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 400
        emp_id = int(request.args.get("emp_id", 0))
        m = int(request.args.get("month", date.today().month))
        y = int(request.args.get("year", date.today().year))
        try:
            rec = database.get_employee_payroll_record(emp_id, m, y)
            return jsonify({"success": True, "record": rec})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/payroll/records", methods=["GET"])
    def admin_api_payroll_records():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        m = request.args.get("month")
        y = request.args.get("year")
        try:
            records = database.get_payroll_records()
            if m and y:
                m_int = int(m)
                y_int = int(y)
                records = [r for r in records if r.get("period_month") == m_int and r.get("period_year") == y_int]
            return jsonify({"success": True, "records": records})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/payroll/breakdown_save", methods=["POST"])
    def admin_api_payroll_breakdown_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        emp_id = data.get("emp_id")
        m = int(data.get("month", date.today().month))
        y = int(data.get("year", date.today().year))
        pid = data.get("id")
        try:
            if pid:
                database.update_payroll_record(pid, data)
            elif emp_id:
                database.save_employee_payroll_breakdown(emp_id, m, y, data)
            else:
                return jsonify({"success": False, "message": "Missing ID or employee"}), 400
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/payroll/delete", methods=["POST"])
    def admin_api_payroll_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        pid = data.get("id")
        if pid:
            database.delete_payroll_record(pid)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing ID"}), 400

    @app.route("/admin/api/payroll/salary", methods=["POST"])
    def admin_api_payroll_salary():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        emp_id = data.get("emp_id")
        sal = data.get("base_salary")
        if emp_id and sal is not None:
            database.update_employee_salary(emp_id, float(sal))
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing fields"}), 400

    @app.route("/admin/api/payroll/config", methods=["GET", "POST"])
    def admin_api_payroll_config():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        if request.method == "POST":
            data = request.json or {}
            if "working_days" in data:
                database.set_setting("payroll_working_days", data["working_days"])
            if "work_hours" in data:
                database.set_setting("payroll_work_hours", data["work_hours"])
            if "incentive" in data:
                database.set_setting("payroll_default_incentive", data["incentive"])
            if "target_income" in data:
                database.set_setting("payroll_target_income", data["target_income"])
            if "target_bonus" in data:
                database.set_setting("payroll_target_bonus", data["target_bonus"])
            if "ot_rate" in data:
                database.set_setting("payroll_ot_rate", data["ot_rate"])
            return jsonify({"success": True})
        else:
            return jsonify({
                "success": True,
                "working_days": int(database.get_setting("payroll_working_days", "26") or 26),
                "work_hours": int(database.get_setting("payroll_work_hours", "8") or 8),
                "incentive": float(database.get_setting("payroll_default_incentive", "50.0") or 50.0),
                "target_income": float(database.get_setting("payroll_target_income", "14000.0") or 14000.0),
                "target_bonus": float(database.get_setting("payroll_target_bonus", "50.0") or 50.0),
                "ot_rate": float(database.get_setting("payroll_ot_rate", "1.5") or 1.5)
            })

    @app.route("/admin/api/payroll/export_csv")
    def admin_api_payroll_export_csv():
        if not session.get("admin_logged_in"):
            return "Unauthorized", 401
        records = database.get_payroll_records()
        output = io.StringIO()
        output.write("\ufeff")  # BOM for Excel Khmer support
        writer = csv.writer(output)
        writer.writerow(["Slip No", "Employee", "Department", "Period", "Base Salary", "Gross", "Net"])
        for r in records:
            writer.writerow([
                r.get("payslip_no", ""),
                f"{r.get('name', '')} ({r.get('khmer_name', '')})",
                r.get("department", ""),
                f"{r.get('date_from', '')} - {r.get('date_to', '')}",
                r.get("base_salary", 0),
                r.get("gross_salary", 0),
                r.get("net_salary", 0)
            ])
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=mercy_dental_payroll_report.csv"}
        )

    @app.route("/admin/api/request/save", methods=["POST"])
    def admin_api_request_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        try:
            emp_id = data.get("emp_id")
            subj = data.get("subject", "")
            cat = data.get("category", "General")
            desc = data.get("description", "")
            conn = database.get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO staff_requests (emp_id, category, subject, description, submit_date, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (emp_id, cat, subj, desc, date.today().isoformat()))
            conn.commit()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/request/status", methods=["POST"])
    def admin_api_request_status():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        req_id = data.get("id")
        status = data.get("status")
        if req_id and status:
            database.update_staff_request_status(req_id, status)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing fields"}), 400

    @app.route("/admin/api/request/delete", methods=["POST"])
    def admin_api_request_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        req_id = data.get("id")
        if req_id:
            database.delete_staff_request(req_id)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing ID"}), 400

    @app.route("/admin/api/department/save", methods=["POST"])
    def admin_api_department_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        raw_id = data.get("id")
        dept_id = int(raw_id) if raw_id else None
        try:
            database.save_department(
                name=data.get("name", "").strip(),
                name_kh=data.get("name_kh", "").strip(),
                color=data.get("color", "#6366F1"),
                dept_id=dept_id
            )
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/department/delete", methods=["POST"])
    def admin_api_department_delete():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        did = data.get("id")
        if did:
            database.delete_department(did)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing ID"}), 400

    @app.route("/admin/api/permissions/save", methods=["POST"])
    def admin_api_permissions_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        perms = data.get("permissions", {})
        try:
            database.set_staff_permissions(perms)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/credentials/save", methods=["POST"])
    def admin_api_credentials_save():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        c_type = data.get("type", "admin")
        user = data.get("username", "").strip()
        pwd = data.get("password", "").strip()
        try:
            database.update_credentials(c_type, user, pwd)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/admin/api/setting", methods=["POST"])
    def admin_api_setting():
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.json or {}
        k = data.get("key")
        v = data.get("value")
        if k:
            database.set_setting(k, str(v))
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Missing key"}), 400

# Alias for compatibility
register_admin_routes = register_admin_portal
