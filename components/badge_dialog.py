"""
Digital Staff ID Card & Badge Dialog for Mercy Dental Care.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF

class BadgeDialog(QDialog):
    def __init__(self, emp, parent=None):
        super().__init__(parent)
        self.emp = emp
        self.setWindowTitle(f"Digital Staff Card - {emp.get('name', 'Employee')}")
        self.setFixedSize(360, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ID Card Container
        card = QFrame()
        card.setObjectName("idCard")
        card.setStyleSheet("""
            QFrame#idCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5648A6, stop:0.35 #43368E, stop:0.36 #FFFFFF, stop:1 #FFFFFF);
                border-radius: 18px;
                border: 1px solid #CBD5E1;
            }
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(18, 18, 18, 18)
        c_layout.setSpacing(10)

        # Top Header: Logo + Clinic Name
        h_top = QHBoxLayout()
        logo_lbl = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.jpg")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaledToHeight(40, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("🦷")
            logo_lbl.setStyleSheet("font-size: 24px;")
        h_top.addWidget(logo_lbl)

        v_head = QVBoxLayout()
        v_head.setSpacing(0)
        c_name = QLabel("MERCY DENTAL CARE")
        c_name.setStyleSheet("color: #FFFFFF; font-weight: 800; font-size: 13px; letter-spacing: 1px;")
        c_sub = QLabel("គ្លីនិកព្យាបាល និងវះកាត់ធ្មេញ")
        c_sub.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 10px;")
        v_head.addWidget(c_name)
        v_head.addWidget(c_sub)
        h_top.addLayout(v_head)
        h_top.addStretch()
        c_layout.addLayout(h_top)

        c_layout.addSpacing(16)

        # Avatar photo placeholder
        avatar_lbl = QLabel("👨‍⚕️" if emp.get("gender") == "Male" else "👩‍⚕️")
        avatar_lbl.setFixedSize(88, 88)
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_lbl.setStyleSheet("""
            background-color: #EEEDFB;
            border: 3px solid #5648A6;
            border-radius: 44px;
            font-size: 42px;
        """)
        c_layout.addWidget(avatar_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # Name in English & Khmer
        name_en = QLabel(emp.get("name", ""))
        name_en.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_en.setStyleSheet("color: #1E293B; font-size: 17px; font-weight: 800;")
        c_layout.addWidget(name_en)

        name_kh = QLabel(emp.get("khmer_name", ""))
        name_kh.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_kh.setStyleSheet("color: #64748B; font-size: 14px; font-weight: 600;")
        c_layout.addWidget(name_kh)

        # Job Position & Department badge
        pos_badge = QLabel(f"{emp.get('job_position', '')}")
        pos_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_badge.setStyleSheet("""
            background-color: #EEEDFB;
            color: #5648A6;
            font-weight: 700;
            font-size: 12px;
            border-radius: 12px;
            padding: 4px 12px;
        """)
        c_layout.addWidget(pos_badge, alignment=Qt.AlignmentFlag.AlignCenter)

        dept_lbl = QLabel(f"Department: {emp.get('department', '')}")
        dept_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dept_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        c_layout.addWidget(dept_lbl)

        # Info row (ID & Join Date)
        info_row = QHBoxLayout()
        id_box = QLabel(f"ID: {emp.get('emp_code', '')}")
        id_box.setStyleSheet("font-weight: 800; font-size: 13px; color: #1E293B;")
        info_row.addWidget(id_box)
        info_row.addStretch()
        join_box = QLabel(f"Joined: {emp.get('join_date', '')}")
        join_box.setStyleSheet("font-size: 11px; color: #64748B;")
        info_row.addWidget(join_box)
        c_layout.addLayout(info_row)

        # QR Code representation placeholder
        qr_box = QLabel("⬛⬜⬛ 000" + str(emp.get('emp_code', '')) + " ⬛⬜⬛\nSCAN TO VERIFY")
        qr_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_box.setStyleSheet("""
            background-color: #F1F5F9;
            border: 1px dashed #94A3B8;
            border-radius: 8px;
            padding: 8px;
            font-size: 10px;
            font-weight: 700;
            color: #475569;
        """)
        c_layout.addWidget(qr_box)

        layout.addWidget(card)

        # Actions: Print and Close
        btn_h = QHBoxLayout()
        print_btn = QPushButton("🖨️ Print Badge")
        print_btn.setStyleSheet("""
            background-color: #5648A6;
            color: white;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
        """)
        print_btn.clicked.connect(lambda: QMessageBox.information(self, "Print Badge", f"Printing badge for {emp.get('name')} to default clinic card printer..."))
        btn_h.addWidget(print_btn)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            background-color: #E2E8F0;
            color: #334155;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
        """)
        close_btn.clicked.connect(self.accept)
        btn_h.addWidget(close_btn)

        layout.addLayout(btn_h)
