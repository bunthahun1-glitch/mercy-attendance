"""
Staff Document, Equipment & General Requests View
Faithful recreation of Click HR screenshot IMG_7455.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QTextEdit, QLineEdit, QSplitter, QListView
)
from PyQt6.QtCore import Qt

import database
from theme import tr, PRIMARY, SUCCESS, DANGER, setup_styled_combobox

class RequestsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Top Header
        top_h = QHBoxLayout()
        title = QLabel("🔔 Notifications & Requests / សេចក្តីជូនដំណឹងផ្សេងៗ")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1E293B;")
        top_h.addWidget(title)
        top_h.addStretch()

        top_h.addWidget(QLabel("Filter:"))
        self.combo_filter = QComboBox()
        setup_styled_combobox(self.combo_filter)
        self.combo_filter.addItems(["All", "Pending", "Approved", "Rejected"])
        self.combo_filter.currentTextChanged.connect(self.load_requests)
        top_h.addWidget(self.combo_filter)

        btn_new = QPushButton("+ New Request")
        btn_new.setStyleSheet("background-color: #5648A6; color: white; padding: 7px 16px; border-radius: 6px; font-weight: 700;")
        btn_new.clicked.connect(self.new_request_dialog)
        top_h.addWidget(btn_new)

        layout.addLayout(top_h)

        # Splitter: Left Table, Right Request Detail matching IMG_7455
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Table
        left_widget = QWidget()
        l_v = QVBoxLayout(left_widget)
        l_v.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Req No", "Staff", "Subject", "Submit Date", "Status"])
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 110)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 110)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        l_v.addWidget(self.table)
        splitter.addWidget(left_widget)

        # Right: Request Detail Panel matching IMG_7455
        self.detail_frame = QFrame()
        self.detail_frame.setObjectName("requestDetailFrame")
        self.detail_frame.setStyleSheet("""
            QFrame#requestDetailFrame {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 12px;
            }
        """)
        d_layout = QVBoxLayout(self.detail_frame)
        d_layout.setContentsMargins(18, 18, 18, 18)
        d_layout.setSpacing(10)

        d_head = QLabel("Request Detail")
        d_head.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        d_layout.addWidget(d_head)

        self.lbl_req_id = QLabel("Requests: DOC00109")
        self.lbl_req_id.setStyleSheet("color: #64748B; font-size: 12px;")
        d_layout.addWidget(self.lbl_req_id)

        self.lbl_status = QLabel("Status: Pending")
        self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 700; font-size: 13px;")
        d_layout.addWidget(self.lbl_status)

        d_layout.addWidget(QLabel("<b>Document Type:</b> Request"))

        self.lbl_date = QLabel("Submit Date: 2026-07-24")
        self.lbl_date.setStyleSheet("color: #64748B; font-size: 12px;")
        d_layout.addWidget(self.lbl_date)

        self.lbl_subject = QLabel("Subject: Request Computer")
        self.lbl_subject.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B;")
        d_layout.addWidget(self.lbl_subject)

        d_layout.addWidget(QLabel("<b>Description:</b>"))
        self.lbl_desc = QLabel("Equipment description...")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("background-color: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 6px; padding: 10px; color: #334155;")
        d_layout.addWidget(self.lbl_desc)

        d_layout.addWidget(QLabel("<b>Attachments:</b>"))
        self.lbl_attach = QLabel("📎 photo-by-camera-0.jpg")
        self.lbl_attach.setStyleSheet("background-color: #EEEDFB; color: #5648A6; border: 1px solid #C7D2FE; border-radius: 6px; padding: 6px 10px; font-weight: 600;")
        d_layout.addWidget(self.lbl_attach)

        d_layout.addStretch()

        # Approve and Reject buttons matching IMG_7455
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_approve = QPushButton("Approve")
        self.btn_approve.setStyleSheet("background-color: #5648A6; color: white; padding: 10px 20px; border-radius: 8px; font-weight: 700; font-size: 13px;")
        self.btn_approve.clicked.connect(lambda: self.set_status("Approved"))
        btn_row.addWidget(self.btn_approve)

        self.btn_reject = QPushButton("Reject")
        self.btn_reject.setStyleSheet("background-color: #EF4444; color: white; padding: 10px 18px; border-radius: 8px; font-weight: 700; font-size: 13px;")
        self.btn_reject.clicked.connect(lambda: self.set_status("Rejected"))
        btn_row.addWidget(self.btn_reject)

        self.btn_delete = QPushButton("🗑️ Delete / លុប")
        self.btn_delete.setStyleSheet("background-color: #FEE2E2; color: #DC2626; border: 1px solid #FECACA; padding: 10px 16px; border-radius: 8px; font-weight: 700; font-size: 13px;")
        self.btn_delete.clicked.connect(self.delete_request)
        btn_row.addWidget(self.btn_delete)

        d_layout.addLayout(btn_row)

        splitter.addWidget(self.detail_frame)
        splitter.setSizes([650, 420])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        self.selected_req_id = None
        self.load_requests()

    def load_requests(self):
        filt = self.combo_filter.currentText()
        reqs = database.get_staff_requests(filt)
        self.table.setRowCount(len(reqs))

        for r, req in enumerate(reqs):
            it_code = QTableWidgetItem(req["req_code"])
            it_code.setData(Qt.ItemDataRole.UserRole, req)
            it_code.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 0, it_code)

            it_staff = QTableWidgetItem(f"{req['name']} ({req['khmer_name']})")
            self.table.setItem(r, 1, it_staff)

            it_sub = QTableWidgetItem(req["subject"])
            self.table.setItem(r, 2, it_sub)

            it_date = QTableWidgetItem(req["submit_date"])
            it_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 3, it_date)

            badge_w = QWidget()
            badge_w.setStyleSheet("background: transparent;")
            bl = QHBoxLayout(badge_w)
            bl.setContentsMargins(6, 4, 6, 4)
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            badge = QLabel(req["status"])
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if req["status"] == "Approved":
                badge.setStyleSheet("background-color: #ECFDF5; color: #065F46; border: 1.5px solid #10B981; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 10px;")
            elif req["status"] == "Rejected":
                badge.setStyleSheet("background-color: #FEE2E2; color: #991B1B; border: 1.5px solid #EF4444; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 10px;")
            else:
                badge.setStyleSheet("background-color: #FEF3C7; color: #92400E; border: 1.5px solid #F59E0B; border-radius: 6px; font-weight: 700; font-size: 11px; padding: 3px 10px;")
            bl.addWidget(badge)
            self.table.setCellWidget(r, 4, badge_w)

        if len(reqs) > 0:
            self.table.selectRow(0)

    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item = self.table.item(row, 0)
        req = item.data(Qt.ItemDataRole.UserRole)
        if req:
            self.selected_req_id = req["id"]
            self.lbl_req_id.setText(f"Requests: {req['req_code']}")
            self.lbl_status.setText(f"Status: {req['status']}")
            self.lbl_date.setText(f"Submit Date: {req['submit_date']}")
            self.lbl_subject.setText(f"Subject: {req['subject']}")
            self.lbl_desc.setText(req["description"] or "No detailed description provided.")

            is_pending = req["status"] == "Pending"
            self.btn_approve.setEnabled(is_pending)
            self.btn_reject.setEnabled(is_pending)

    def set_status(self, status):
        if not self.selected_req_id:
            return
        database.update_staff_request_status(self.selected_req_id, status)
        QMessageBox.information(self, "Status Updated", f"Request marked as {status}.")
        self.load_requests()

    def delete_request(self):
        if not self.selected_req_id:
            return
        reply = QMessageBox.question(
            self, "បញ្ជាក់ការលុប (Confirm Delete)",
            "តើលោកអ្នកពិតជាចង់លុបសំណើនេះមែនទេ? (Are you sure you want to delete this staff request?)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_staff_request(self.selected_req_id)
            QMessageBox.information(self, "ជោគជ័យ", "បានលុបសំណើដោយជោគជ័យ!")
            self.selected_req_id = None
            self.load_requests()

    def new_request_dialog(self):
        QMessageBox.information(self, "New Request", "Staff request wizard ready.")

