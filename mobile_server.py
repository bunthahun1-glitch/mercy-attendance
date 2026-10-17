import os
import sys
import socket
import threading
import json
import base64
import math
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template_string

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import database
import admin_portal
import face_service

app = Flask(__name__)
app.secret_key = "mercy_dental_care_admin_secure_secret_key_2026"
admin_portal.register_admin_routes(app)

def calculate_distance(lat1, lon1, lat2, lon2):
    try:
        R = 6371000  # radius in meters
        p1 = math.radians(float(lat1))
        p2 = math.radians(float(lat2))
        dp = math.radians(float(lat2) - float(lat1))
        dl = math.radians(float(lon2) - float(lon1))
        a = math.sin(dp / 2.0)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c
    except Exception:
        return 999999.0

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_client_ip():
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip and cf_ip.strip():
        return cf_ip.strip()
    xff = request.headers.get("X-Forwarded-For")
    if xff and xff.strip():
        return xff.split(",")[0].strip()
    return (request.remote_addr or "127.0.0.1").strip()

def check_ip_match(client_ip, clinic_ip_setting):
    client_ip = (client_ip or "").strip()
    clinic_ip_setting = (clinic_ip_setting or "").strip()
    if not clinic_ip_setting:
        return True
    if client_ip in ("127.0.0.1", "::1", "localhost") or client_ip.startswith("192.168.") or client_ip.startswith("10.") or client_ip.startswith("172.16."):
        return True
    allowed_ips = [ip.strip() for ip in clinic_ip_setting.replace(";", ",").split(",") if ip.strip()]
    return client_ip in allowed_ips

# Mobile Web HTML Template
MOBILE_HTML = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Mercy Dental Care - ស្កេនវត្តមានតាមទូរស័ព្ទ</title>
    <link href="https://fonts.googleapis.com/css2?family=Kantumruy+Pro:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #5648A6;
            --primary-dark: #433688;
            --primary-light: #EEEDFB;
            --success: #16A34A;
            --danger: #DC2626;
            --warning: #D97706;
            --bg: #F4F6F9;
            --card-bg: #FFFFFF;
            --text-dark: #1E293B;
            --text-muted: #64748B;
            --border: #E2E8F0;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: 'Kantumruy Pro', 'Inter', -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text-dark);
            min-height: 100vh;
            padding: 8px 6px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }
        .container {
            width: 100%;
            max-width: 410px;
            background: var(--card-bg);
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(86, 72, 166, 0.08);
            overflow: hidden;
            border: 1px solid var(--border);
        }
        .header {
            background: linear-gradient(135deg, #5648A6 0%, #3B2D7B 100%);
            color: white;
            padding: 12px 14px 10px;
            text-align: center;
            position: relative;
        }
        .header h1 {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 2px;
            letter-spacing: -0.2px;
        }
        .header p {
            font-size: 11px;
            opacity: 0.9;
        }
        .header-clock-row {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            margin-top: 6px;
            position: relative;
        }
        .notice-bell-btn {
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.32);
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 13px;
            color: white;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            position: relative;
            backdrop-filter: blur(4px);
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
            height: 24px;
            box-sizing: border-box;
        }
        .notice-bell-btn:active {
            transform: scale(0.92);
            background: rgba(255, 255, 255, 0.3);
        }
        .notice-badge-dot {
            position: absolute;
            top: -2px;
            right: -2px;
            width: 8px;
            height: 8px;
            background: #EF4444;
            border-radius: 50%;
            border: 1.5px solid #3B2D7B;
            box-shadow: 0 0 6px #EF4444;
            animation: bellDotPulse 1.6s infinite ease-in-out;
        }
        .notice-badge-count {
            font-size: 10px;
            font-weight: 800;
            background: #EF4444;
            color: #FFFFFF;
            padding: 0 5px;
            border-radius: 9px;
            line-height: 14px;
            height: 14px;
            margin-left: 2px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        @keyframes bellDotPulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.35); opacity: 0.75; }
        }
        .live-clock {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
            backdrop-filter: blur(4px);
            height: 24px;
            box-sizing: border-box;
            line-height: 18px;
        }
        /* Top Announcement Banner Strip */
        .notice-banner-strip {
            background: linear-gradient(90deg, #FEF3C7 0%, #FDE68A 100%);
            border: 1px solid #FCD34D;
            color: #78350F;
            padding: 6px 12px;
            margin: 8px 10px 0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11.5px;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(217, 119, 6, 0.12);
            transition: transform 0.15s;
        }
        .notice-banner-strip:active {
            transform: scale(0.98);
        }
        .notice-strip-icon {
            font-size: 14px;
            flex-shrink: 0;
        }
        .notice-strip-text {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 11px;
            line-height: 1.2;
        }
        .notice-strip-link {
            font-size: 10.5px;
            font-weight: 800;
            color: #92400E;
            white-space: nowrap;
            padding-left: 4px;
        }
        /* Mobile Notice Modal */
        .notice-modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(4px);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .notice-modal-overlay.active {
            display: flex;
        }
        .notice-modal-box {
            background: #FFFFFF;
            border-radius: 16px;
            width: 100%;
            max-width: 380px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.25);
            animation: modalFadeIn 0.2s ease-out;
        }
        @keyframes modalFadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        .notice-modal-header {
            padding: 12px 16px;
            border-bottom: 1px solid #E2E8F0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #F8FAFC;
        }
        .notice-modal-close {
            background: none;
            border: none;
            font-size: 22px;
            color: #64748B;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
        }
        .notice-modal-body {
            padding: 14px 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .notice-item-card {
            border-radius: 10px;
            border: 1px solid #E2E8F0;
            padding: 12px;
            background: #F8FAFC;
        }
        .notice-item-card.priority-urgent {
            border-color: #FCA5A5;
            background: #FEF2F2;
        }
        .notice-item-card.priority-important {
            border-color: #FDE68A;
            background: #FFFBEB;
        }
        .notice-item-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .notice-pill-priority {
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 6px;
        }
        .notice-pill-priority.priority-urgent {
            background: #FEE2E2;
            color: #DC2626;
        }
        .notice-pill-priority.priority-important {
            background: #FEF3C7;
            color: #D97706;
        }
        .notice-pill-priority.priority-normal {
            background: #DBEAFE;
            color: #2563EB;
        }
        .notice-item-date {
            font-size: 10px;
            color: #64748B;
        }
        .notice-item-title {
            margin: 0 0 6px;
            font-size: 13.5px;
            font-weight: 800;
            color: #1E293B;
            line-height: 1.35;
        }
        .notice-item-content {
            font-size: 12px;
            color: #334155;
            line-height: 1.5;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .notice-item-target {
            margin-top: 8px;
            padding-top: 6px;
            border-top: 1px dashed rgba(0,0,0,0.08);
            font-size: 10.5px;
            color: #64748B;
        }
        .notice-modal-footer {
            padding: 10px 16px;
            background: #F8FAFC;
            border-top: 1px solid #E2E8F0;
            display: flex;
            justify-content: flex-end;
        }
        .btn-notice-close {
            background: #5648A6;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 18px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            width: 100%;
        }
        .content {
            padding: 10px 12px;
        }
        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .badge-verified {
            background: #DCFCE7;
            color: #15803D;
            border: 1px solid #BBF7D0;
        }
        .badge-warning {
            background: #FEF3C7;
            color: #B45309;
            border: 1px solid #FDE68A;
        }
        .badge-error {
            background: #FEE2E2;
            color: #B91C1C;
            border: 1px solid #FECACA;
        }
        /* Top Split Bar: Staff Selection (Left) & Wi-Fi + GPS (Right) */
        .top-split-bar {
            display: grid;
            grid-template-columns: 1fr 140px;
            gap: 8px;
            margin-bottom: 8px;
            align-items: flex-end;
        }
        .staff-selection-box {
            display: flex;
            flex-direction: column;
            min-width: 0;
        }
        .staff-selection-box .form-label {
            font-size: 11.5px;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }
        .staff-selection-box .form-select {
            height: 44px;
            font-size: 12.5px;
            font-weight: 600;
            border-radius: 9px;
            border: 1.5px solid var(--border);
            padding: 0 8px;
            background-color: #FFFFFF;
            width: 100%;
            box-sizing: border-box;
        }
        .network-gps-wrapper {
            display: flex;
            flex-direction: column;
            width: 140px;
            flex-shrink: 0;
        }
        .net-title-label {
            font-size: 11px;
            font-weight: 700;
            color: #5648A6;
            margin-bottom: 4px;
            white-space: nowrap;
            text-align: center;
            cursor: pointer;
            user-select: none;
            transition: color 0.15s;
        }
        .net-title-label:hover {
            color: #3b2f80;
            text-decoration: underline;
        }
        .network-gps-card {
            background: #F8FAFC;
            border: 1.5px solid var(--border);
            border-radius: 9px;
            padding: 5px 8px;
            height: 44px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .net-gps-item {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 10.5px;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .net-gps-item .item-icon {
            font-size: 11px;
            flex-shrink: 0;
        }
        .net-gps-item .item-tag {
            font-weight: 700;
            color: #64748B;
            font-size: 10px;
            flex-shrink: 0;
        }
        .net-gps-item .item-status {
            font-weight: 800;
            font-size: 10.5px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .net-gps-item.status-ok .item-status, .item-status.status-ok {
            color: #16A34A;
        }
        .net-gps-item.status-error .item-status, .item-status.status-error {
            color: #DC2626;
        }
        .net-gps-item.status-warn .item-status, .item-status.status-warn {
            color: #D97706;
        }
        .form-group {
            margin-bottom: 8px;
        }
        .form-label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 4px;
        }
        .form-select, .form-input {
            width: 100%;
            height: 38px;
            padding: 6px 10px;
            border-radius: 8px;
            border: 1.5px solid var(--border);
            font-size: 13px;
            font-family: inherit;
            color: var(--text-dark);
            background-color: #F8FAFC;
            transition: all 0.2s;
        }
        .form-select:focus, .form-input:focus {
            outline: none;
            border-color: var(--primary);
            background-color: #FFFFFF;
            box-shadow: 0 0 0 2px rgba(86, 72, 166, 0.15);
        }
        /* Camera Preview Box */
        .camera-card {
            border: 1.5px dashed var(--border);
            border-radius: 12px;
            padding: 8px;
            background: #F8FAFC;
            text-align: center;
            margin-bottom: 8px;
            position: relative;
        }
        .camera-video-wrapper {
            width: 195px;
            height: 235px;
            max-width: 85%;
            margin: 0 auto 8px auto;
            border-radius: 14px;
            overflow: hidden;
            background: #000000;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
            border: 2.5px solid var(--primary);
        }
        video, canvas {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transform: scaleX(-1);
        }
        .camera-btn {
            background: var(--primary-light);
            color: var(--primary);
            border: 1px solid rgba(86, 72, 166, 0.2);
            border-radius: 6px;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            font-family: inherit;
        }
        /* Action Buttons */
        .btn-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-bottom: 6px;
        }
        .btn {
            height: 40px;
            border-radius: 10px;
            border: none;
            font-size: 13.5px;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: transform 0.1s, opacity 0.2s;
        }
        .btn:active {
            transform: scale(0.98);
        }
        .btn.btn-disabled {
            opacity: 0.45;
            cursor: not-allowed;
            filter: grayscale(0.35);
        }
        .btn-checkin {
            background: var(--primary);
            color: white;
            box-shadow: 0 3px 8px rgba(86, 72, 166, 0.22);
        }
        .btn-checkout {
            background: var(--danger);
            color: white;
            box-shadow: 0 3px 8px rgba(220, 38, 38, 0.22);
        }
        .btn-ot {
            grid-column: span 2;
            background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
            color: white;
            box-shadow: 0 3px 8px rgba(217, 119, 6, 0.22);
            font-size: 12.5px;
            height: 38px;
        }
        /* Result Dialog Banner */
        .toast {
            display: none;
            padding: 8px 10px;
            border-radius: 8px;
            margin-top: 8px;
            font-size: 11.5px;
            font-weight: 600;
            text-align: center;
            line-height: 1.4;
            animation: fadeIn 0.3s ease;
        }
        .toast-success {
            background: #DCFCE7;
            color: #15803D;
            border: 1px solid #86EFAC;
        }
        .toast-error {
            background: #FEE2E2;
            color: #B91C1C;
            border: 1px solid #FCA5A5;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .footer {
            text-align: center;
            padding: 8px 10px;
            font-size: 10.5px;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div style="background: white; border-radius: 12px; padding: 6px 14px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 3px 12px rgba(0,0,0,0.15); margin-bottom: 6px;">
            <img src="data:image/png;base64,{{ logo_b64 }}" alt="Mercy Dental Care Logo" style="height: 38px; max-width: 170px; object-fit: contain; display: block;">
        </div>
        <h1 style="font-size: 16px; font-weight: 700; margin-bottom: 2px;">{{ clinic_name_kh }}</h1>
        <p style="font-size: 11px; opacity: 0.9; margin: 0;">Mercy Dental Care • Mobile Attendance System</p>
        <div class="header-clock-row">
            <button type="button" class="notice-bell-btn" id="noticeBellBtn" onclick="openNoticeModal()" title="សេចក្តីជូនដំណឹង (Notices)">
                <span class="bell-icon">🔔</span>
                {% if active_ann_count > 0 %}
                <span class="notice-badge-dot"></span>
                <span class="notice-badge-count">{{ active_ann_count }}</span>
                {% endif %}
            </button>
            <div class="live-clock" id="liveClock">⏰ កំពុងទាញម៉ោង...</div>
        </div>
    </div>

    {% if active_announcements %}
    {% set top_notice = active_announcements[0] %}
    <div class="notice-banner-strip" onclick="openNoticeModal()" title="ចុចដើម្បីអានសេចក្តីជូនដំណឹង">
        <span class="notice-strip-icon">{% if top_notice.priority == 'Urgent' %}🚨{% elif top_notice.priority == 'Important' %}⭐{% else %}📢{% endif %}</span>
        <div class="notice-strip-text"><b>{{ top_notice.title }}</b>: {{ top_notice.content }}</div>
        <span class="notice-strip-link">មើល ›</span>
    </div>
    {% endif %}

    <div class="content">
        <!-- Top Split Row: Staff Selection (Left) + Wi-Fi & GPS Status (Right) -->
        <div class="top-split-bar">
            <!-- Left Column: Staff Selection -->
            <div class="staff-selection-box">
                <label class="form-label" for="staffSelect">
                    <span>👤</span> <strong>ជ្រើសរើសបុគ្គលិក (Staff)</strong>
                </label>
                <select id="staffSelect" class="form-select">
                    <option value="">-- សូមជ្រើសរើសឈ្មោះ --</option>
                    {% for emp in scan_employees %}
                    <option value="{{ emp.id }}" data-kh="{{ emp.khmer_name }}" data-code="{{ emp.emp_code }}">
                        {{ emp.emp_code }} - {{ emp.khmer_name }} ({{ emp.name }})
                    </option>
                    {% endfor %}
                </select>
            </div>

            <!-- Right Column: Wi-Fi & GPS in Browser -->
            <div class="network-gps-wrapper">
                <div class="net-title-label" id="leaveBtnTitle" onclick="openMobileLeaveModal()" title="ចុចដើម្បីស្នើរសុំច្បាប់">ស្នើរសុំច្បាប់</div>
                <div class="network-gps-card">
                    <!-- Wi-Fi Status Row -->
                    <div class="net-gps-item {% if wifi_enforce and not is_wifi_matched %}status-error{% else %}status-ok{% endif %}" id="wifiItem" title="បណ្តាញ Wi-Fi គ្លីនិក៖ {{ wifi_ssid }}">
                        <span class="item-icon">📶</span>
                        <span class="item-tag">Wi-Fi:</span>
                        <span class="item-status" id="wifiStatusText">
                            {% if wifi_enforce %}
                                {% if is_wifi_matched %}ភ្ជាប់ត្រូវ{% else %}ខុស Wi-Fi{% endif %}
                            {% else %}
                                ភ្ជាប់ត្រូវ
                            {% endif %}
                        </span>
                    </div>

                    <!-- GPS Location Row -->
                    <div class="net-gps-item status-warn" id="securityBadge" title="ទីតាំង GPS ក្នុង Browser">
                        <span class="item-icon">📡</span>
                        <span class="item-tag">GPS:</span>
                        <span class="item-status" id="securityText">កំពុងឆែក...</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Staff Password Verification Box (Appears when staff is selected) -->
        <div id="staffAuthBox" style="display:none; margin-bottom: 8px; background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 12px; padding: 10px 12px; animation: fadeIn 0.2s ease;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 5px;">
                <label for="staffPasswordInput" style="font-size: 11.5px; font-weight: 700; color: #1E293B; display:flex; align-items:center; gap: 4px;">
                    <span>🔒</span> <span>លេខសម្ងាត់ផ្ទាល់ខ្លួន (Password / PIN) <span style="color:#DC2626;">*</span></span>
                </label>
                <span id="authStatusBadge" style="font-size: 11px; font-weight: 700; color: #DC2626; display:none;"></span>
            </div>
            <div style="display:flex; gap: 6px;">
                <div style="position:relative; flex:1;">
                    <input type="password" id="staffPasswordInput" placeholder="បញ្ចូលលេខសម្ងាត់ផ្ទាល់ខ្លួន..." 
                           onkeydown="if(event.key==='Enter'){event.preventDefault(); verifyStaffPassword();}"
                           style="width: 100%; height: 38px; border-radius: 8px; border: 1.5px solid #CBD5E1; padding: 0 34px 0 10px; font-size: 13px; font-family: inherit; box-sizing: border-box; outline:none; background:#fff;" />
                    <button type="button" onclick="togglePasswordVisibility()" 
                            style="position:absolute; right:6px; top:50%; transform:translateY(-50%); background:none; border:none; cursor:pointer; font-size:15px; color:#64748B; padding:2px;" title="បង្ហាញលេខសម្ងាត់">👁️</button>
                </div>
                <button type="button" id="btnVerifyAuth" onclick="verifyStaffPassword()" 
                        style="height: 38px; padding: 0 14px; border-radius: 8px; border: none; background: #4338CA; color: white; font-weight: 700; font-size: 12px; font-family: inherit; cursor: pointer; display: flex; align-items: center; gap: 4px; white-space:nowrap; box-shadow: 0 2px 5px rgba(67,56,202,0.25);">
                    <span>🔑</span> ផ្ទៀងផ្ទាត់ & ស្កេនមុខ
                </button>
            </div>
            <div id="authSuccessMsg" style="display:none; margin-top:5px; font-size:11px; font-weight:700; color:#15803D;">
                ✅ លេខសម្ងាត់ និងស្កេនមុខត្រឹមត្រូវ!
            </div>
            <p style="font-size:10px; color:#64748B; margin-top:4px;">
                💡 ប្រព័ន្ធតម្រូវឲ្យផ្ទៀងផ្ទាត់ត្រឹមត្រូវទាំង <b>Password</b> និង <b>ស្កេនផ្ទៃមុខផ្ទាល់ខ្លួន</b> ទើបអាចចុចស្កេនបាន
            </p>
        </div>

        <!-- Camera Selfie Section -->
        <div class="camera-card">
            <div class="camera-video-wrapper" style="position:relative;">
                <video id="cameraVideo" autoplay playsinline muted></video>
                <canvas id="cameraCanvas" style="display:none;"></canvas>
                <!-- Visual Face Guide Oval / Frame -->
                <div id="faceOverlay" style="position:absolute; inset:8px; border:2.5px dashed rgba(255,255,255,0.7); border-radius:50% / 40%; pointer-events:none; transition:all 0.3s; display:flex; align-items:flex-end; justify-content:center; padding-bottom:6px;">
                    <span id="faceStatusBadge" style="background:rgba(15,23,42,0.75); color:white; font-size:10px; font-weight:700; padding:3px 8px; border-radius:999px; backdrop-filter:blur(2px); white-space:nowrap;">
                        👤 តម្រង់មុខក្នុងរង្វង់នេះ
                    </span>
                </div>
            </div>
            <button type="button" class="camera-btn" id="btnToggleCamera">📸 បើកកាមេរ៉ា Selfie ផ្ទៀងផ្ទាត់មុខ</button>
            <p style="font-size: 10px; color: var(--text-muted); margin-top: 3px;">
                ថតរូបមុខពិតប្រាកដ ការពារការស្កេនជំនួសគ្នា
            </p>
        </div>

        <!-- Action Buttons -->
        <div class="btn-grid">
            <button class="btn btn-checkin btn-disabled" id="btnCheckIn">
                <span>🟢</span> Check In
            </button>
            <button class="btn btn-checkout btn-disabled" id="btnCheckOut">
                <span>🔴</span> Checked Out
            </button>
            <button class="btn btn-ot btn-disabled" id="btnCheckOutOT">
                <span>⭐</span> ចេញថែមម៉ោង (OT សម្រាប់តែមានអ្នកជំងឺ)
            </button>
        </div>

        <!-- Status Toast -->
        <div id="toastBox" class="toast"></div>
    </div>

    <!-- Patient Name Modal for OT -->
    <div id="otModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.65); z-index:99999; align-items:center; justify-content:center; padding:16px; backdrop-filter:blur(3px);">
        <div style="background:white; border-radius:18px; max-width:390px; width:100%; padding:22px; box-shadow:0 25px 35px -5px rgba(0,0,0,0.3); animation:fadeIn 0.2s ease;">
            <div style="font-size:34px; text-align:center; margin-bottom:6px;">🦷⭐</div>
            <h3 style="font-size:17px; font-weight:800; color:#1E293B; text-align:center; margin-bottom:4px;">ចេញថែមម៉ោង (OT អ្នកជំងឺ)</h3>
            <p style="font-size:12px; color:#B45309; text-align:center; font-weight:600; margin-bottom:14px; background:#FEF3C7; padding:8px 12px; border-radius:10px; line-height:1.4;">
                💰 <b>អត្រាថែមម៉ោង៖</b> 30 នាទី = $0.75 • 1 ម៉ោង = $1.50<br><span style="font-size:11px; color:#D97706;">(គិតចាប់ពីលើស 15 នាទីឡើងទៅ)</span>
            </p>
            <div style="margin-bottom:16px;">
                <label style="display:block; font-size:13px; font-weight:700; color:#334155; margin-bottom:6px;">
                    👤 ឈ្មោះអ្នកជំងឺ (Patient Name) <span style="color:#DC2626;">*ចាំបាច់</span>
                </label>
                <input type="text" id="otPatientName" placeholder="ឧ. លោក សុខ ចាន់ដារ៉ា" style="width:100%; height:46px; border:1.5px solid #CBD5E1; border-radius:10px; padding:0 12px; font-size:14px; font-family:inherit; outline:none; box-sizing:border-box;" />
                <div id="otError" style="color:#DC2626; font-size:11.5px; margin-top:5px; display:none; font-weight:600;"></div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <button type="button" id="btnCancelOT" style="height:46px; border-radius:10px; border:1.5px solid #CBD5E1; background:#F8FAFC; color:#64748B; font-weight:700; font-family:inherit; cursor:pointer;">បោះបង់</button>
                <button type="button" id="btnConfirmOT" style="height:46px; border-radius:10px; border:none; background:linear-gradient(135deg, #D97706 0%, #B45309 100%); color:white; font-weight:700; font-family:inherit; cursor:pointer; font-size:13.5px;">បញ្ជាក់ស្កេន OT</button>
            </div>
        </div>
    </div>

    <!-- Mobile Leave Request Modal -->
    <div id="mobileLeaveModal" style="display:none; position:fixed; inset:0; background:rgba(15,23,42,0.6); z-index:999; align-items:center; justify-content:center; padding:16px; backdrop-filter:blur(3px);">
        <div style="background:white; border-radius:14px; max-width:360px; width:100%; padding:18px; box-shadow:0 12px 35px rgba(0,0,0,0.28); font-family:inherit; box-sizing:border-box;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="margin:0; font-size:15px; font-weight:700; color:#1E293B; display:flex; align-items:center; gap:6px;">
                    <span>📅</span> ស្នើរសុំច្បាប់
                </h3>
                <button type="button" onclick="closeMobileLeaveModal()" style="background:none; border:none; font-size:22px; cursor:pointer; color:#94A3B8; line-height:1;">&times;</button>
            </div>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div>
                    <label style="font-size:11px; font-weight:600; color:#475569; display:block; margin-bottom:3px;">បុគ្គលិក (Staff) *</label>
                    <select id="mLeaveEmp" style="width:100%; height:38px; border-radius:8px; border:1.5px solid var(--border); padding:0 8px; font-size:12px; font-family:inherit; background:#fff; box-sizing:border-box;">
                        <option value="">-- សូមជ្រើសរើសឈ្មោះ --</option>
                        {% for emp in employees %}
                        <option value="{{ emp.id }}">{{ emp.emp_code }} - {{ emp.khmer_name }} ({{ emp.name }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    <div>
                        <label style="font-size:11px; font-weight:600; color:#475569; display:block; margin-bottom:3px;">ចាប់ពីថ្ងៃ *</label>
                        <input type="date" id="mLeaveStart" style="width:100%; height:36px; border-radius:8px; border:1.5px solid var(--border); padding:0 6px; font-size:12px; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <div>
                        <label style="font-size:11px; font-weight:600; color:#475569; display:block; margin-bottom:3px;">ដល់ថ្ងៃ *</label>
                        <input type="date" id="mLeaveEnd" style="width:100%; height:36px; border-radius:8px; border:1.5px solid var(--border); padding:0 6px; font-size:12px; font-family:inherit; box-sizing:border-box;">
                    </div>
                </div>
                <div>
                    <label style="font-size:11px; font-weight:600; color:#475569; display:block; margin-bottom:3px;">មូលហេតុ (Reason)</label>
                    <textarea id="mLeaveReason" rows="2" placeholder="បញ្ជាក់ពីមូលហេតុឈប់សម្រាក..." style="width:100%; border-radius:8px; border:1.5px solid var(--border); padding:6px 8px; font-size:12px; font-family:inherit; box-sizing:border-box;"></textarea>
                </div>
                <div id="mLeaveError" style="display:none; color:#DC2626; font-size:11px; font-weight:600;"></div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:4px;">
                    <button type="button" onclick="closeMobileLeaveModal()" style="height:40px; border-radius:8px; border:1.5px solid var(--border); background:#F1F5F9; font-weight:600; font-size:12px; cursor:pointer;">បោះបង់</button>
                    <button type="button" id="btnSubmitMobileLeave" onclick="submitMobileLeave()" style="height:40px; border-radius:8px; border:none; background:var(--primary); color:white; font-weight:700; font-size:12.5px; cursor:pointer;">ស្នើរសុំច្បាប់</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Announcement & Notice Modal for Staff -->
    <div class="notice-modal-overlay" id="noticeModal" onclick="closeNoticeModal(event)">
        <div class="notice-modal-box" onclick="event.stopPropagation()">
            <div class="notice-modal-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:22px;">🔔</span>
                    <div>
                        <h3 style="margin:0; font-size:14.5px; font-weight:800; color:#1E293B;">សេចក្តីជូនដំណឹងពីគ្លីនិក</h3>
                        <p style="margin:0; font-size:10.5px; color:#64748B;">Mercy Dental Care Official Notices</p>
                    </div>
                </div>
                <button type="button" class="notice-modal-close" onclick="closeNoticeModal()">&times;</button>
            </div>
            <div class="notice-modal-body">
                {% if active_announcements %}
                    {% for ann in active_announcements %}
                    <div class="notice-item-card priority-{{ ann.priority|lower }}">
                        <div class="notice-item-top">
                            <span class="notice-pill-priority priority-{{ ann.priority|lower }}">
                                {% if ann.priority == 'Urgent' %}🚨 បន្ទាន់ (Urgent){% elif ann.priority == 'Important' %}⭐ សំខាន់ (Important){% else %}ℹ️ ដំណឹងទូទៅ{% endif %}
                            </span>
                            <span class="notice-item-date">📅 {{ ann.created_at }}</span>
                        </div>
                        <h4 class="notice-item-title">{{ ann.title }}</h4>
                        <div class="notice-item-content">{{ ann.content }}</div>
                        <div class="notice-item-target">👥 ផ្ញើជូន៖ <strong>{{ ann.target or 'បុគ្គលិកទាំងអស់' }}</strong></div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="text-align:center; padding:35px 15px; color:#64748B;">
                        <div style="font-size:38px; margin-bottom:10px;">🔕</div>
                        <div style="font-weight:700; font-size:13.5px; color:#334155;">ពុំមានសេចក្តីជូនដំណឹងថ្មីនៅឡើយទេ</div>
                        <div style="font-size:11px; margin-top:4px; color:#94A3B8;">នៅពេលមានសេចក្តីជូនដំណឹងថ្មី វានឹងបង្ហាញជូននៅត្រង់នេះភ្លាមៗ។</div>
                    </div>
                {% endif %}
            </div>
            <div class="notice-modal-footer">
                <button type="button" class="btn-notice-close" onclick="closeNoticeModal()">យល់ព្រម / ខ្ញុំបានអានរួច (Close)</button>
            </div>
        </div>
    </div>

    <div class="footer">
        <div>© 2026 Mercy Dental Care • Anti-Buddy Punching Geofenced System</div>
        <div style="margin-top: 6px;">
            <a href="/admin" style="color: #64748B; font-size: 11.5px; text-decoration: none; font-weight: 600;">🔒 ចូលគ្រប់គ្រង (Admin Portal)</a>
        </div>
    </div>
</div>

<script>
    // Live Clock
    function updateClock() {
        const now = new Date();
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        document.getElementById('liveClock').innerText = '⏰ ' + now.toLocaleDateString('km-KH', options);
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Notice Modal Handlers
    function openNoticeModal() {
        const m = document.getElementById('noticeModal');
        if (m) m.classList.add('active');
    }
    function closeNoticeModal(e) {
        if (e && e.target && e.target.id !== 'noticeModal' && !e.target.classList.contains('notice-modal-close') && !e.target.classList.contains('btn-notice-close')) return;
        const m = document.getElementById('noticeModal');
        if (m) m.classList.remove('active');
    }

    // Security Settings from Backend
    const config = {{ config_json|safe }};
    let userLat = null;
    let userLng = null;
    let distanceMeters = null;
    let isLocationValid = !config.gps_enforce;

    function updateSecurityBadge(isValid, msg, shortMsg = '') {
        const badge = document.getElementById('securityBadge');
        const txt = document.getElementById('securityText');
        if (txt) {
            txt.innerText = shortMsg || (isValid ? 'ក្នុងគ្លីនិក' : 'ក្រៅគ្លីនិក');
        }
        if (badge) {
            badge.className = 'net-gps-item ' + (isValid ? 'status-ok' : 'status-error');
            badge.title = msg;
        }
    }

    function evaluateSecurityState() {
        const wifiStatusText = document.getElementById('wifiStatusText');
        const wifiItem = document.getElementById('wifiItem');

        if (config.wifi_enforce && !config.is_wifi_matched) {
            if (wifiStatusText) wifiStatusText.innerText = 'ខុស Wi-Fi';
            if (wifiItem) wifiItem.className = 'net-gps-item status-error';
            updateSecurityBadge(false, `❌ ខុសបណ្តាញ Wi-Fi (សូមភ្ជាប់ Wi-Fi គ្លីនិក ${config.wifi_ssid})`, 'ខុស Wi-Fi');
            return;
        } else {
            if (wifiStatusText) wifiStatusText.innerText = 'ភ្ជាប់ត្រូវ';
            if (wifiItem) wifiItem.className = 'net-gps-item status-ok';
        }

        // If connected to Clinic Wi-Fi router, the device is verified inside the clinic!
        if (config.is_wifi_matched) {
            let distMsg = distanceMeters !== null ? ` (${Math.round(distanceMeters)}m)` : '';
            updateSecurityBadge(true, `✅ បានភ្ជាប់ Wi-Fi គ្លីនិកត្រឹមត្រូវ (ក្នុងគ្លីនិក${distMsg})`, `ក្នុងគ្លីនិក${distMsg}`);
            return;
        }

        if (config.gps_enforce) {
            if (userLat === null || userLng === null) {
                const badge = document.getElementById('securityBadge');
                if (badge) badge.className = 'net-gps-item status-warn';
                updateSecurityBadge(false, '⚠️ សូមអនុញ្ញាត GPS Location ក្នុង Browser ដើម្បីផ្ទៀងផ្ទាត់ទីតាំង', 'សុំបើក GPS');
                return;
            }
            if (distanceMeters > config.gps_radius) {
                updateSecurityBadge(false, `❌ នៅក្រៅគ្លីនិក (ចម្ងាយ ${Math.round(distanceMeters)}m លើសពី ${config.gps_radius}m)`, `ក្រៅ (${Math.round(distanceMeters)}m)`);
                return;
            }
        }

        let distMsg = distanceMeters !== null ? ` (${Math.round(distanceMeters)}m)` : '';
        updateSecurityBadge(true, `✅ ស្ថិតក្នុងបរិវេណគ្លីនិក${distMsg}`, `ក្នុងគ្លីនិក${distMsg}`);
    }

    // GPS Geolocation Check
    function checkLocation() {
        if (config.wifi_enforce && !config.is_wifi_matched) {
            evaluateSecurityState();
        }

        if (!navigator.geolocation) {
            if (config.is_wifi_matched) {
                isLocationValid = true;
                evaluateSecurityState();
            } else if (config.gps_enforce) {
                updateSecurityBadge(false, '❌ ឧបករណ៍នេះមិនគាំទ្រ GPS ទេ', 'គ្មាន GPS');
            } else {
                evaluateSecurityState();
            }
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                userLat = pos.coords.latitude;
                userLng = pos.coords.longitude;

                // Calculate distance from Clinic GPS
                distanceMeters = getDistanceFromLatLonInMeters(userLat, userLng, config.clinic_lat, config.clinic_lng);
                isLocationValid = true;
                evaluateSecurityState();
            },
            (err) => {
                // If on clinic Wi-Fi, presence is already authenticated!
                if (config.is_wifi_matched) {
                    isLocationValid = true;
                    evaluateSecurityState();
                } else if (config.gps_enforce) {
                    isLocationValid = false;
                    const badge = document.getElementById('securityBadge');
                    if (badge) badge.className = 'net-gps-item status-warn';
                    updateSecurityBadge(false, '⚠️ សូមអនុញ្ញាត GPS Location ក្នុង Browser ដើម្បីផ្ទៀងផ្ទាត់ទីតាំង', 'សុំបើក GPS');
                } else {
                    isLocationValid = true;
                    evaluateSecurityState();
                }
            },
            { enableHighAccuracy: true, timeout: 8000 }
        );
    }

    function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Earth radius in meters
        const phi1 = lat1 * Math.PI / 180;
        const phi2 = lat2 * Math.PI / 180;
        const deltaPhi = (lat2 - lat1) * Math.PI / 180;
        const deltaLambda = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(deltaPhi/2) * Math.sin(deltaPhi/2) +
                  Math.cos(phi1) * Math.cos(phi2) *
                  Math.sin(deltaLambda/2) * Math.sin(deltaLambda/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    // Run Location check
    checkLocation();

    // Camera Selfie Handling
    let videoStream = null;
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    const btnToggleCamera = document.getElementById('btnToggleCamera');

    async function startCamera() {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 640 } },
                audio: false
            });
            video.srcObject = videoStream;
            video.style.display = 'block';
            canvas.style.display = 'none';
            btnToggleCamera.innerText = '📸 កាមេរ៉ាកំពុងដំណើរការ...';
        } catch (e) {
            console.log('Camera error:', e);
            btnToggleCamera.innerText = '⚠️ មិនអាចបើកកាមេរ៉ា (អនុញ្ញាត Permission)';
        }
    }

    btnToggleCamera.addEventListener('click', startCamera);
    // Auto-start camera on mobile
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        startCamera();
    }

    function captureSelfie() {
        if (!videoStream) return null;
        canvas.width = video.videoWidth || 480;
        canvas.height = video.videoHeight || 640;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.65);
    }

    // Staff Authentication & Button State
    let isStaffAuthenticated = false;

    function setButtonsEnabled(enabled) {
        const b1 = document.getElementById('btnCheckIn');
        const b2 = document.getElementById('btnCheckOut');
        const b3 = document.getElementById('btnCheckOutOT');
        [b1, b2, b3].forEach(b => {
            if (b) {
                if (enabled) {
                    b.classList.remove('btn-disabled');
                } else {
                    b.classList.add('btn-disabled');
                }
            }
        });
    }

    // Toggle Password Visibility
    function togglePasswordVisibility() {
        const pwdInput = document.getElementById('staffPasswordInput');
        if (pwdInput) {
            pwdInput.type = (pwdInput.type === 'password') ? 'text' : 'password';
        }
    }

    // When staff is selected from dropdown
    document.getElementById('staffSelect').addEventListener('change', function() {
        const val = this.value;
        const authBox = document.getElementById('staffAuthBox');
        const pwdInput = document.getElementById('staffPasswordInput');
        const authBadge = document.getElementById('authStatusBadge');
        const authSuccess = document.getElementById('authSuccessMsg');
        const faceOverlay = document.getElementById('faceOverlay');
        const faceBadge = document.getElementById('faceStatusBadge');

        isStaffAuthenticated = false;
        setButtonsEnabled(false);

        if (val) {
            authBox.style.display = 'block';
            pwdInput.value = '';
            pwdInput.style.borderColor = '#CBD5E1';
            authBadge.style.display = 'none';
            authSuccess.style.display = 'none';
            if (faceOverlay) {
                faceOverlay.style.border = '2.5px dashed rgba(255,255,255,0.7)';
                faceOverlay.style.boxShadow = 'none';
            }
            if (faceBadge) {
                faceBadge.style.background = 'rgba(15,23,42,0.75)';
                faceBadge.innerHTML = '👤 តម្រង់មុខក្នុងរង្វង់នេះ';
            }
            startCamera();
            setTimeout(() => pwdInput.focus(), 150);
        } else {
            authBox.style.display = 'none';
        }
    });

    // Verify Staff Password / PIN & Biometric Face
    async function verifyStaffPassword() {
        const staffId = document.getElementById('staffSelect').value;
        const pwdInput = document.getElementById('staffPasswordInput');
        const pwd = pwdInput ? pwdInput.value.trim() : '';
        const authBadge = document.getElementById('authStatusBadge');
        const authSuccess = document.getElementById('authSuccessMsg');
        const faceOverlay = document.getElementById('faceOverlay');
        const faceBadge = document.getElementById('faceStatusBadge');
        const btnVerify = document.getElementById('btnVerifyAuth');

        if (!staffId) {
            showToast('⚠️ សូមជ្រើសរើសឈ្មោះបុគ្គលិកជាមុនសិន!', false);
            return;
        }
        if (!pwd) {
            authBadge.innerText = '❌ សូមបញ្ចូលលេខសម្ងាត់!';
            authBadge.style.display = 'inline';
            pwdInput.style.borderColor = '#DC2626';
            pwdInput.focus();
            return;
        }

        // Ensure camera is active and ready
        if (!videoStream) {
            await startCamera();
            await new Promise(r => setTimeout(r, 400));
        }

        const selfieData = captureSelfie();
        if (!selfieData) {
            authBadge.innerText = '⚠️ សូមបើកកាមេរ៉ា និងតម្រង់មុខឲ្យចំប្រអប់ស្កេន!';
            authBadge.style.display = 'inline';
            showToast('⚠️ សូមបើកកាមេរ៉ា និងតម្រង់មុខឲ្យចំប្រអប់ស្កេន!', false);
            return;
        }

        btnVerify.disabled = true;
        btnVerify.innerHTML = '<span>⏳</span> កំពុងស្កេនមុខ...';
        authBadge.style.display = 'none';

        try {
            const resp = await fetch('/api/verify_staff_auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    emp_id: staffId,
                    password: pwd,
                    selfie: selfieData
                })
            });
            const res = await resp.json();
            btnVerify.disabled = false;
            btnVerify.innerHTML = '<span>🔑</span> ផ្ទៀងផ្ទាត់ & ស្កេនមុខ';

            if (res.success) {
                isStaffAuthenticated = true;
                pwdInput.style.borderColor = '#10B981';
                authSuccess.style.display = 'block';
                authSuccess.innerHTML = res.message || '✅ លេខសម្ងាត់ និងស្កេនមុខត្រឹមត្រូវ!';

                // Camera face confirmation feedback (Green)
                if (faceOverlay) {
                    faceOverlay.style.border = '3px solid #10B981';
                    faceOverlay.style.boxShadow = '0 0 18px rgba(16, 185, 129, 0.65)';
                }
                if (faceBadge) {
                    faceBadge.style.background = '#059669';
                    faceBadge.innerHTML = '✅ ស្កេនមុខត្រឹមត្រូវ';
                }

                setButtonsEnabled(true);
                showToast(res.message || '✅ ផ្ទៀងផ្ទាត់ជោគជ័យ! ឥឡូវលោកអ្នកអាចចុច Check In, Checked Out ឬ ចេញថែមម៉ោងបានហើយ។', true);
            } else {
                isStaffAuthenticated = false;
                setButtonsEnabled(false);
                authSuccess.style.display = 'none';
                authBadge.innerText = res.message || '❌ ផ្ទៀងផ្ទាត់មិនត្រឹមត្រូវ!';
                authBadge.style.display = 'inline';
                pwdInput.style.borderColor = '#DC2626';

                // Camera face rejection feedback (Red)
                if (faceOverlay) {
                    faceOverlay.style.border = '3px solid #DC2626';
                    faceOverlay.style.boxShadow = '0 0 18px rgba(220, 38, 38, 0.65)';
                }
                if (faceBadge) {
                    faceBadge.style.background = '#DC2626';
                    faceBadge.innerHTML = '❌ ផ្ទៃមុខមិនត្រូវគ្នា';
                }

                showToast(res.message || '❌ ផ្ទៀងផ្ទាត់មិនត្រឹមត្រូវ!', false);
                pwdInput.focus();
                pwdInput.select();
            }
        } catch (err) {
            btnVerify.disabled = false;
            btnVerify.innerHTML = '<span>🔑</span> ផ្ទៀងផ្ទាត់ & ស្កេនមុខ';
            authBadge.innerText = '❌ បរាជ័យក្នុងការតភ្ជាប់!';
            authBadge.style.display = 'inline';
            showToast('❌ បរាជ័យក្នុងការតភ្ជាប់ទៅកាន់ Server!', false);
        }
    }

    // Submit Attendance Actions
    async function doAttendance(actionType, patientName = '') {
        const staffId = document.getElementById('staffSelect').value;
        const toast = document.getElementById('toastBox');

        if (!staffId) {
            showToast('⚠️ សូមជ្រើសរើសឈ្មោះបុគ្គលិកជាមុនសិន!', false);
            return;
        }

        if (!isStaffAuthenticated) {
            showToast('🔒 សូមបញ្ចូលលេខសម្ងាត់ផ្ទាល់ខ្លួន និងផ្ទៀងផ្ទាត់ស្កេនមុខជាមុនសិន!', false);
            const pwdInput = document.getElementById('staffPasswordInput');
            if (pwdInput) {
                pwdInput.focus();
                pwdInput.style.borderColor = '#DC2626';
            }
            return;
        }

        if (actionType === 'checkout_ot' && !patientName.trim()) {
            showToast('❌ សូមបញ្ចូលឈ្មោះអ្នកជំងឺជាមុនសិន!', false);
            return;
        }

        if (config.wifi_enforce && !config.is_wifi_matched) {
            showToast(`❌ មិនអាចស្កេនបានទេ! សូមភ្ជាប់ Wi-Fi របស់គ្លីនិក (${config.wifi_ssid}) ជាមុនសិន។`, false);
            return;
        }

        if (!config.is_wifi_matched && config.gps_enforce) {
            if (userLat === null || userLng === null) {
                showToast('⚠️ សូមចុច Allow / អនុញ្ញាតទីតាំង (GPS Location) ក្នុង Browser ដើម្បីអាចស្កេនបាន!', false);
                return;
            }
            if (distanceMeters > config.gps_radius) {
                const distMsg = distanceMeters ? ` (${Math.round(distanceMeters)}m > ${config.gps_radius}m)` : '';
                showToast(`❌ មិនអាចស្កេនបានទេ! លោកអ្នកស្ថិតនៅក្រៅបរិវេណគ្លីនិក${distMsg}។`, false);
                return;
            }
        }

        const selfieData = captureSelfie();
        const pwdVal = document.getElementById('staffPasswordInput') ? document.getElementById('staffPasswordInput').value.trim() : '';

        // Send API request
        try {
            const resp = await fetch('/api/mobile_attendance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    emp_id: staffId,
                    password: pwdVal,
                    action: actionType,
                    has_overtime: actionType === 'checkout_ot',
                    patient_name: patientName.trim(),
                    latitude: userLat,
                    longitude: userLng,
                    distance: distanceMeters,
                    selfie: selfieData
                })
            });

            const data = await resp.json();
            if (data.success) {
                showToast(`✅ ${data.message}`, true);
                if (videoStream) {
                    video.style.display = 'none';
                    canvas.style.display = 'block';
                }
                // Reset authentication for next punch
                isStaffAuthenticated = false;
                setButtonsEnabled(false);
                const pwdInput = document.getElementById('staffPasswordInput');
                if (pwdInput) {
                    pwdInput.value = '';
                    pwdInput.style.borderColor = '#CBD5E1';
                }
                const authSuccess = document.getElementById('authSuccessMsg');
                if (authSuccess) authSuccess.style.display = 'none';
                const faceOverlay = document.getElementById('faceOverlay');
                if (faceOverlay) {
                    faceOverlay.style.border = '2.5px dashed rgba(255,255,255,0.7)';
                    faceOverlay.style.boxShadow = 'none';
                }
                const faceBadge = document.getElementById('faceStatusBadge');
                if (faceBadge) {
                    faceBadge.style.background = 'rgba(15,23,42,0.75)';
                    faceBadge.innerHTML = '👤 តម្រង់មុខក្នុងរង្វង់នេះ';
                }
            } else {
                showToast(`❌ បរាជ័យ៖ ${data.message}`, false);
            }
        } catch (err) {
            showToast('❌ មានបញ្ហាតភ្ជាប់ទៅកាន់ម៉ាស៊ីនមេគ្លីនិក!', false);
        }
    }

    function showToast(msg, isSuccess) {
        const toast = document.getElementById('toastBox');
        toast.className = 'toast ' + (isSuccess ? 'toast-success' : 'toast-error');
        toast.innerText = msg;
        toast.style.display = 'block';
    }

    document.getElementById('btnCheckIn').addEventListener('click', () => doAttendance('checkin'));
    document.getElementById('btnCheckOut').addEventListener('click', () => doAttendance('checkout'));

    const otModal = document.getElementById('otModal');
    const otPatientInput = document.getElementById('otPatientName');
    const otError = document.getElementById('otError');

    document.getElementById('btnCheckOutOT').addEventListener('click', () => {
        const staffId = document.getElementById('staffSelect').value;
        if (!staffId) {
            showToast('⚠️ សូមជ្រើសរើសឈ្មោះបុគ្គលិកជាមុនសិន!', false);
            return;
        }

        if (!isStaffAuthenticated) {
            showToast('🔒 សូមបញ្ចូលលេខសម្ងាត់ផ្ទាល់ខ្លួន និងស្កេនមុខបញ្ជាក់ជាមុនសិន!', false);
            const pwdInput = document.getElementById('staffPasswordInput');
            if (pwdInput) {
                pwdInput.focus();
                pwdInput.style.borderColor = '#DC2626';
            }
            return;
        }

        const now = new Date();
        const curHM = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0');
        const shiftEnd = (config && config.shift_end) ? config.shift_end : '18:00';
        if (curHM < shiftEnd) {
            alert(`⚠️ មិនទាន់ដល់ម៉ោងចេញធ្វើការ (${shiftEnd}) នៅឡើយទេ! (ម៉ោងបច្ចុប្បន្ន៖ ${curHM})\n\nការថែមម៉ោង (OT) គិតតែចាប់ពីម៉ោង ${shiftEnd} ឡើងទៅប៉ុណ្ណោះ។\n\nប្រសិនបើលោកអ្នកចេញពេលនេះ សូមចុចប៊ូតុង "Checked Out" ធម្មតា។`);
            return;
        }

        otPatientInput.value = '';
        otError.style.display = 'none';
        otModal.style.display = 'flex';
        setTimeout(() => otPatientInput.focus(), 150);
    });

    document.getElementById('btnCancelOT').addEventListener('click', () => {
        otModal.style.display = 'none';
    });

    document.getElementById('btnConfirmOT').addEventListener('click', () => {
        const pName = otPatientInput.value.trim();
        if (!pName) {
            otError.innerText = '❌ សូមបញ្ចូលឈ្មោះអ្នកជំងឺជាមុនសិន!';
            otError.style.display = 'block';
            otPatientInput.focus();
            return;
        }
        otModal.style.display = 'none';
        doAttendance('checkout_ot', pName);
    });

    // Mobile Leave Request Modal Handlers
    function openMobileLeaveModal() {
        const staffSel = document.getElementById('staffSelect').value;
        const mEmp = document.getElementById('mLeaveEmp');
        if (staffSel) mEmp.value = staffSel;
        const today = new Date().toISOString().split('T')[0];
        if (!document.getElementById('mLeaveStart').value) document.getElementById('mLeaveStart').value = today;
        if (!document.getElementById('mLeaveEnd').value) document.getElementById('mLeaveEnd').value = today;
        document.getElementById('mLeaveError').style.display = 'none';
        document.getElementById('mobileLeaveModal').style.display = 'flex';
    }

    function closeMobileLeaveModal() {
        document.getElementById('mobileLeaveModal').style.display = 'none';
    }

    async function submitMobileLeave() {
        const empId = document.getElementById('mLeaveEmp').value;
        const sDate = document.getElementById('mLeaveStart').value;
        const eDate = document.getElementById('mLeaveEnd').value;
        const reason = document.getElementById('mLeaveReason').value.trim();
        const errDiv = document.getElementById('mLeaveError');

        if (!empId) {
            errDiv.innerText = '❌ សូមជ្រើសរើសឈ្មោះបុគ្គលិក!';
            errDiv.style.display = 'block';
            return;
        }
        if (!sDate || !eDate) {
            errDiv.innerText = '❌ សូមជ្រើសរើសកាលបរិច្ឆេទចាប់ពី និងដល់ថ្ងៃ!';
            errDiv.style.display = 'block';
            return;
        }

        const d1 = new Date(sDate);
        const d2 = new Date(eDate);
        const days = Math.max(1, Math.round((d2 - d1) / (1000 * 60 * 60 * 24)) + 1);

        const btn = document.getElementById('btnSubmitMobileLeave');
        btn.disabled = true;
        btn.innerText = 'កំពុងរក្សាទុក...';
        errDiv.style.display = 'none';

        try {
            const res = await fetch('/api/mobile_leave', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    emp_id: empId,
                    leave_type: 'ច្បាប់សម្រាក',
                    start_date: sDate,
                    end_date: eDate,
                    days: days,
                    reason: reason
                })
            });
            const data = await res.json();
            btn.disabled = false;
            btn.innerText = 'ស្នើរសុំច្បាប់';
            if (data.status === 'ok' || data.success) {
                closeMobileLeaveModal();
                showToast('✅ បានស្នើរសុំច្បាប់ដោយជោគជ័យ!', true);
            } else {
                errDiv.innerText = '❌ ' + (data.message || 'មានបញ្ហាក្នុងការរក្សាទុក');
                errDiv.style.display = 'block';
            }
        } catch(e) {
            btn.disabled = false;
            btn.innerText = 'ស្នើរសុំច្បាប់';
            errDiv.innerText = '❌ មិនអាចភ្ជាប់ទៅកាន់ប្រព័ន្ធបានទេ';
            errDiv.style.display = 'block';
        }
    }
</script>

</body>
</html>
"""

@app.route("/")
@app.route("/checkin")
def index():
    all_employees = database.get_all_employees()
    # Exclude part-time staff who do not scan (Kam Mithona) from the scan dropdown
    scan_employees = [e for e in all_employees if e.get("khmer_name") != "គាំ មិថុនា" and e.get("name") != "Kam Mithona"]
    
    # Retrieve configuration from database
    clinic_lat = float(database.get_setting("clinic_lat", "11.5834188") or 11.5834188)
    clinic_lng = float(database.get_setting("clinic_lng", "104.8811696") or 104.8811696)
    gps_radius = float(database.get_setting("gps_radius", "50") or 50)
    gps_enforce = database.get_setting("gps_enforce", "0") == "1"
    wifi_ssid = database.get_setting("wifi_ssid", "Mercy Dental Care")
    wifi_enforce = database.get_setting("wifi_enforce", "0") == "1"
    clinic_ip = database.get_setting("clinic_public_ip", "").strip()
    shift_end = database.get_setting("shift_end", "18:00")

    client_ip = get_client_ip()
    is_wifi_matched = check_ip_match(client_ip, clinic_ip)

    config_data = {
        "clinic_lat": clinic_lat,
        "clinic_lng": clinic_lng,
        "gps_radius": gps_radius,
        "gps_enforce": gps_enforce,
        "wifi_ssid": wifi_ssid,
        "wifi_enforce": wifi_enforce,
        "is_wifi_matched": is_wifi_matched,
        "client_ip": client_ip,
        "shift_end": shift_end
    }

    # Load Clinic Logo
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
    logo_b64 = ""
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("ascii")
        except Exception:
            pass

    # Fetch Active Clinic Announcements
    active_announcements = database.get_active_announcements()
    active_ann_count = len(active_announcements)

    return render_template_string(
        MOBILE_HTML,
        employees=all_employees,
        scan_employees=scan_employees,
        leave_types=[lt for lt in database.get_leave_types() if lt.get('name') not in ('Public', 'Day Offs') and lt.get('name_kh') not in ('បុណ្យជាតិ', 'ថ្ងៃឈប់សម្រាកប្រចាំសប្តាហ៍') and lt.get('code') not in ('PB', 'DO')],
        wifi_ssid=wifi_ssid,
        wifi_enforce=wifi_enforce,
        is_wifi_matched=is_wifi_matched,
        client_ip=client_ip,
        clinic_name_kh=database.get_setting("clinic_name_kh", "គ្លីនិកទន្តសាស្រ្ត មើស៊ី"),
        logo_b64=logo_b64,
        config_json=json.dumps(config_data),
        active_announcements=active_announcements,
        active_ann_count=active_ann_count
    )

@app.route("/logo.png")
def serve_logo():
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
    if os.path.exists(logo_path):
        from flask import send_file
        return send_file(logo_path, mimetype="image/png")
    return "", 404

@app.route("/api/mobile_leave", methods=["POST"])
def api_mobile_leave():
    data = request.json or {}
    emp_id = data.get("emp_id")
    s_date = data.get("start_date")
    e_date = data.get("end_date")
    days = data.get("days", 1)
    reason = (data.get("reason") or "").strip()
    leave_type = (data.get("leave_type") or "ច្បាប់សម្រាក").strip()

    if not emp_id:
        return jsonify({"success": False, "message": "សូមជ្រើសរើសឈ្មោះបុគ្គលិក"}), 400
    if not s_date or not e_date:
        return jsonify({"success": False, "message": "សូមជ្រើសរើសកាលបរិច្ឆេទ"}), 400

    try:
        database.add_leave_request(
            emp_id=emp_id,
            leave_type=leave_type,
            start_date=s_date,
            end_date=e_date,
            days=days,
            reason=reason
        )
        return jsonify({"success": True, "status": "ok"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/verify_staff_auth", methods=["POST"])
def api_verify_staff_auth():
    data = request.json or {}
    emp_id = data.get("emp_id")
    pwd = str(data.get("password") or "").strip()
    selfie_b64 = data.get("selfie")

    if not emp_id:
        return jsonify({"success": False, "message": "សូមជ្រើសរើសឈ្មោះបុគ្គលិក"}), 400
    if not pwd:
        return jsonify({"success": False, "message": "សូមបញ្ចូលលេខសម្ងាត់ផ្ទាល់ខ្លួន"}), 400

    emp = database.get_employee_by_id(emp_id)
    if not emp:
        return jsonify({"success": False, "message": "រកមិនឃើញបុគ្គលិកនេះទេ"}), 404

    # 1. Verify Password / PIN
    expected_pwd = str(emp.get("password") or "").strip()
    expected_pin = str(emp.get("pin_code") or "").strip()

    pwd_match = False
    if expected_pwd and pwd == expected_pwd:
        pwd_match = True
    elif expected_pin and pwd == expected_pin:
        pwd_match = True
    elif not expected_pwd and not expected_pin:
        pwd_match = True

    if not pwd_match:
        return jsonify({
            "success": False,
            "message": "❌ លេខសម្ងាត់ (Password / PIN) មិនត្រឹមត្រូវទេ!"
        }), 401

    # 2. Verify Biometric Face
    if not selfie_b64:
        return jsonify({
            "success": False,
            "message": "❌ សូមបើកកាមេរ៉ា និងតម្រង់ផ្ទៃមុខក្នុងរង្វង់ស្កេន!"
        }), 400

    cv_img = face_service.base64_to_cv2(selfie_b64)
    if cv_img is None:
        return jsonify({
            "success": False,
            "message": "❌ មិនអាចដំណើរការរូបភាពកាមេរ៉ាបានទេ សូមព្យាយាមម្តងទៀត!"
        }), 400

    face_ok, score, face_msg = face_service.verify_face(emp_id, cv_img)
    print(f"[FaceAuth] Emp: {emp_id}, Match: {face_ok}, Score: {score:.4f}, Msg: {face_msg}")

    # Save verification snapshot for security audit
    try:
        verif_dir = os.path.join(BASE_DIR, "uploads", "verifications")
        os.makedirs(verif_dir, exist_ok=True)
        tag = "pass" if face_ok else "fail"
        v_name = f"{tag}_emp_{emp_id}_{int(score*100)}pct_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(os.path.join(verif_dir, v_name), cv_img)
    except Exception as e:
        pass

    if not face_ok:
        return jsonify({
            "success": False,
            "message": face_msg,
            "score": score
        }), 403

    return jsonify({
        "success": True,
        "message": face_msg,
        "score": score,
        "staff_name": emp.get("khmer_name") or emp.get("name")
    })

@app.route("/api/mobile_attendance", methods=["POST"])
def api_mobile_attendance():
    data = request.json or {}
    emp_id = data.get("emp_id")
    action = data.get("action")
    staff_pwd = str(data.get("password") or "").strip()
    has_overtime = data.get("has_overtime", False)
    selfie_b64 = data.get("selfie")
    user_lat = data.get("latitude")
    user_lng = data.get("longitude")
    distance = data.get("distance")

    if not emp_id:
        return jsonify({"success": False, "message": "Invalid employee ID"}), 400

    emp = database.get_employee_by_id(emp_id)
    if not emp:
        return jsonify({"success": False, "message": "Employee not found"}), 404
    emp_name = emp["khmer_name"] if emp else f"ID {emp_id}"

    # 1. Verify staff personal password / PIN
    expected_pwd = str(emp.get("password") or "").strip()
    expected_pin = str(emp.get("pin_code") or "").strip()
    if expected_pwd or expected_pin:
        if staff_pwd not in (expected_pwd, expected_pin):
            return jsonify({
                "success": False,
                "message": "❌ លេខសម្ងាត់ផ្ទាល់ខ្លួន (Password / PIN) មិនត្រឹមត្រូវទេ!"
            }), 401

    # 2. Strict Biometric Face Verification
    if not selfie_b64:
        return jsonify({
            "success": False,
            "message": "❌ មិនមានរូបភាពស្កេនផ្ទៃមុខទេ! សូមតម្រង់មុខលើកាមេរ៉ាដើម្បីស្កេន។"
        }), 400

    cv_img = face_service.base64_to_cv2(selfie_b64)
    if cv_img is None:
        return jsonify({
            "success": False,
            "message": "❌ រូបភាពកាមេរ៉ាមិនត្រឹមត្រូវទេ!"
        }), 400

    face_ok, score, face_msg = face_service.verify_face(emp_id, cv_img)
    if not face_ok:
        return jsonify({
            "success": False,
            "message": face_msg
        }), 403

    client_ip = get_client_ip()
    wifi_ssid = database.get_setting("wifi_ssid", "Mercy Dental Care")
    wifi_enforce = database.get_setting("wifi_enforce", "0") == "1"
    clinic_ip = database.get_setting("clinic_public_ip", "").strip()

    # 3. Enforce Clinic Wi-Fi IP validation
    is_wifi_ok = check_ip_match(client_ip, clinic_ip)
    if wifi_enforce and not is_wifi_ok:
        return jsonify({
            "success": False,
            "message": f"❌ មិនអាចស្កេនបានទេ! លោកអ្នកកំពុងប្រើប្រាស់អ៊ីនធឺណិតផ្សេង (IP: {client_ip})។ សូមភ្ជាប់ Wi-Fi របស់គ្លីនិក ({wifi_ssid}) ជាមុនសិន!"
        }), 403

    # 4. Enforce GPS Geofence validation (strictly required if NOT on clinic Wi-Fi)
    gps_enforce = database.get_setting("gps_enforce", "0") == "1"
    if gps_enforce and not is_wifi_ok:
        clinic_lat = float(database.get_setting("clinic_lat", "11.5834188") or 11.5834188)
        clinic_lng = float(database.get_setting("clinic_lng", "104.8811696") or 104.8811696)
        gps_radius = float(database.get_setting("gps_radius", "50") or 50)

        if user_lat is None or user_lng is None:
            return jsonify({
                "success": False,
                "message": "❌ មិនអាចស្កេនបានទេ! សូមបើក GPS Location លើទូរស័ព្ទដើម្បីផ្ទៀងផ្ទាត់ទីតាំងក្នុងគ្លីនិក។"
            }), 403

        # Exact distance calculation on server
        calculated_dist = calculate_distance(clinic_lat, clinic_lng, user_lat, user_lng)
        if calculated_dist > gps_radius:
            return jsonify({
                "success": False,
                "message": f"❌ មិនអាចស្កេនបានទេ! លោកអ្នកស្ថិតនៅក្រៅបរិវេណគ្លីនិក (ចម្ងាយ {int(round(calculated_dist))} ម៉ែត្រ > កំណត់ត្រឹម {int(gps_radius)} ម៉ែត្រ)។"
            }), 403

    # Save selfie image to disk
    selfie_path = None
    try:
        import cv2
        photos_dir = os.path.join(BASE_DIR, "uploads", "selfies")
        os.makedirs(photos_dir, exist_ok=True)
        filename = f"selfie_{emp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        selfie_path = os.path.join(photos_dir, filename)
        cv2.imwrite(selfie_path, cv_img)
    except Exception as e:
        print("Failed to save selfie:", e)

    check_time = datetime.now().strftime("%H:%M:%S")
    scan_notes = f"Mobile QR Scan (Wi-Fi: {wifi_ssid}, IP: {client_ip})"
    patient_name = (data.get("patient_name") or "").strip()

    if action == "checkout_ot" and not patient_name:
        return jsonify({"success": False, "message": "❌ សូមបញ្ចូលឈ្មោះអ្នកជំងឺជាមុនសិន ទើបអាចស្កេនចេញថែមម៉ោង (OT) បាន!"}), 400

    if action == "checkin":
        status, t = database.record_check_in(emp_id, check_time, notes=scan_notes)
        msg = f"ស្កេនចូលជោគជ័យ (Check In): {emp_name} នៅម៉ោង {t} ({status})!"
    elif action in ("checkout", "checkout_ot"):
        t, ot_h, ot_p = database.record_check_out(emp_id, check_time=check_time, has_overtime=has_overtime, patient_name=patient_name, notes=scan_notes)
        if has_overtime:
            if ot_h > 0:
                mins = int(round(ot_h * 60))
                msg = f"ចេញថែមម៉ោងជោគជ័យ (Checked out with Overtime): {emp_name} • អ្នកជំងឺ៖ {patient_name} នៅម៉ោង {t} • ថែម +{ot_h} ម៉ោង ({mins} នាទី) = +${ot_p:.2f} (30 នាទី=$0.75, 1 ម៉ោង=$1.50)!"
            else:
                shift_end = database.get_setting("shift_end", "18:00")
                if check_time < (shift_end + ":00" if len(shift_end) == 5 else shift_end):
                    msg = f"ស្កេនចេញជោគជ័យ (Early Out): {emp_name} នៅម៉ោង {t} (ចេញមុនម៉ោង {shift_end} • មិនគិត OT ឡើយ)!"
                else:
                    msg = f"ស្កេនចេញជោគជ័យ: {emp_name} នៅម៉ោង {t} (លើសតិចជាង ១៥ នាទី • មិនទាន់គ្រប់លក្ខខណ្ឌ OT ទេ)!"
        else:
            msg = f"ស្កេនចេញជោគជ័យ (Checked Out): {emp_name} នៅម៉ោង {t}!"
    else:
        return jsonify({"success": False, "message": "Unknown action"}), 400

    return jsonify({
        "success": True,
        "message": msg,
        "time": check_time
    })

server_thread = None

def ensure_cloudflared_tunnel():
    token = database.get_setting("cloudflare_tunnel_token", "").strip()
    if not token:
        return
    import subprocess
    try:
        r = subprocess.run(["tasklist", "/fi", "IMAGENAME eq cloudflared.exe"], capture_output=True, text=True)
        if "cloudflared.exe" in r.stdout:
            return  # already running
    except Exception:
        pass
    exe_path = r"C:\Program Files (x86)\cloudflared\cloudflared.exe"
    if os.path.exists(exe_path):
        try:
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            subprocess.Popen([exe_path, "tunnel", "run", "--token", token], creationflags=flags)
            print("Cloudflare Tunnel started successfully in background.")
        except Exception as e:
            print("Failed to start Cloudflare Tunnel:", e)

def start_mobile_server(port=5000):
    global server_thread
    if server_thread and server_thread.is_alive():
        return
    def run():
        # run flask without debug reloader to prevent conflict with Qt
        try:
            app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Flask mobile server on port {port} note: {e}")
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()
    print(f"Mobile Attendance Server running at http://{get_local_ip()}:{port}")
    ensure_cloudflared_tunnel()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if os.environ.get("RENDER") or os.environ.get("PORT"):
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        start_mobile_server(port=port)
        import time
        while True:
            time.sleep(1)

