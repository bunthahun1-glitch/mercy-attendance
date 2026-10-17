"""
Staff Password / PIN Code Verification Dialog for Mercy Dental Care.
Ensures employees authenticate with their password or PIN code when checking in,
checking out, or performing actions.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
import database
from theme import PRIMARY, BORDER

class StaffAuthDialog(QDialog):
    def __init__(self, emp_id, action_name="Check In / ស្រង់វត្តមាន", parent=None):
        super().__init__(parent)
        self.emp_id = emp_id
        self.emp = database.get_employee_by_id(emp_id) or {}

        self.setWindowTitle("Staff Verification / ផ្ទៀងផ្ទាត់ពាក្យសម្ងាត់")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        # Header Info Card
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: #F8FAFC;
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 10px;
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(2)

        name_lbl = QLabel(f"👤 {self.emp.get('name', 'Staff')} ({self.emp.get('khmer_name', '')})")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1E293B;")
        c_layout.addWidget(name_lbl)

        sub_lbl = QLabel(f"ID: {self.emp.get('emp_code', '')}  •  {self.emp.get('job_position', '')}")
        sub_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        c_layout.addWidget(sub_lbl)

        layout.addWidget(card)

        # Action label
        act_lbl = QLabel(f"🔒 សូមបញ្ចូល Password ឬ PIN ({action_name}):")
        act_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #334155;")
        layout.addWidget(act_lbl)

        # Password input box
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_pwd = QLineEdit()
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd.setPlaceholderText("Password or PIN Code")
        self.input_pwd.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1E293B;
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY};
            }}
        """)
        self.input_pwd.returnPressed.connect(self.verify_password)
        input_row.addWidget(self.input_pwd)

        self.btn_eye = QPushButton("👁️")
        self.btn_eye.setFixedSize(38, 36)
        self.btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eye.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.btn_eye.clicked.connect(self._toggle_eye)
        input_row.addWidget(self.btn_eye)

        layout.addLayout(input_row)

        self.err_lbl = QLabel()
        self.err_lbl.setStyleSheet("color: #DC2626; font-size: 11px; font-weight: 600;")
        self.err_lbl.setVisible(False)
        layout.addWidget(self.err_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_cancel = QPushButton("Cancel / បោះបង់")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                border: 1px solid #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_ok = QPushButton("Confirm / យល់ព្រម")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 700;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #6757C4;
            }}
        """)
        btn_ok.clicked.connect(self.verify_password)
        btn_row.addWidget(btn_ok)

        layout.addLayout(btn_row)
        self.input_pwd.setFocus()

    def _toggle_eye(self):
        if self.input_pwd.echoMode() == QLineEdit.EchoMode.Password:
            self.input_pwd.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_eye.setText("🔒")
        else:
            self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_eye.setText("👁️")

    def verify_password(self):
        entered = self.input_pwd.text().strip()
        if not entered:
            self.err_lbl.setText("សូមបញ្ចូល Password ឬ PIN Code!")
            self.err_lbl.setVisible(True)
            return

        if database.verify_employee_credentials(self.emp_id, entered):
            self.accept()
        else:
            self.err_lbl.setText("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
            self.err_lbl.setVisible(True)
            self.input_pwd.selectAll()
            self.input_pwd.setFocus()
