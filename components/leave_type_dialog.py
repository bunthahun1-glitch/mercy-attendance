"""
Dialog for Creating and Editing Leave Types (ប្រភេទច្បាប់ឈប់សម្រាក)
Supports full customization of Display Name, Khmer Name, Code, Mode, and Validation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
import database

class LeaveTypeDialog(QDialog):
    def __init__(self, leave_type_data=None, parent=None):
        super().__init__(parent)
        self.leave_type_data = leave_type_data
        self.is_edit = leave_type_data is not None

        title = "កែប្រែប្រភេទច្បាប់ (Edit Leave Type)" if self.is_edit else "បន្ថែមប្រភេទច្បាប់ថ្មី (Create Leave Type)"
        self.setWindowTitle(title)
        self.setFixedWidth(520)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
                font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 13px;
                color: #334155;
                font-weight: 600;
            }
            QLineEdit, QComboBox {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #0F172A;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #5648A6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Frame
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5648A6, stop:1 #4338CA);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 6, 10, 6)
        icon_lbl = QLabel("🏖️" if not self.is_edit else "✏️")
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent;")
        h_layout.addWidget(icon_lbl)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        h_title = QLabel(title)
        h_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #FFFFFF;")
        title_v.addWidget(h_title)
        h_sub = QLabel("កំណត់ព័ត៌មាន និងលក្ខខណ្ឌនៃប្រភេទច្បាប់ឈប់សម្រាក" if not self.is_edit else "កែសម្រួលឈ្មោះ និងលក្ខខណ្ឌនៃប្រភេទច្បាប់")
        h_sub.setStyleSheet("font-size: 11.5px; color: #E0E7FF;")
        title_v.addWidget(h_sub)
        h_layout.addLayout(title_v)
        layout.addWidget(header)

        # Form Fields
        # 1. English Name
        layout.addWidget(QLabel("ឈ្មោះជាភាសាអង់គ្លេស (English Name) *:"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("ឧ. Paternity Leave, Maternity Leave...")
        layout.addWidget(self.txt_name)

        # 2. Khmer Name
        layout.addWidget(QLabel("ឈ្មោះជាភាសាខ្មែរ (Khmer Name) *:"))
        self.txt_name_kh = QLineEdit()
        self.txt_name_kh.setPlaceholderText("ឧ. ច្បាប់បិតាភាព, ច្បាប់ឈប់សម្រាក...")
        layout.addWidget(self.txt_name_kh)

        # 3. Code
        layout.addWidget(QLabel("អក្សរកាត់កូដ (Code / Short Code) *:"))
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("ឧ. PL, ML, AL...")
        self.txt_code.setMaxLength(6)
        layout.addWidget(self.txt_code)

        # 4. Mode
        layout.addWidget(QLabel("របៀបបែងចែក (Mode):"))
        self.cb_mode = QComboBox()
        self.cb_mode.addItems([
            "Allocated by HR only",
            "No Allocation Needed",
            "Free Allocation Request"
        ])
        layout.addWidget(self.cb_mode)

        # 5. Validation
        layout.addWidget(QLabel("ការអនុម័ត (Validation / Approval Level):"))
        self.cb_validation = QComboBox()
        self.cb_validation.addItems([
            "Leave Officer",
            "Team Leader and HR",
            "Manager / HR Admin",
            "Executive Approval"
        ])
        layout.addWidget(self.cb_validation)

        # Pre-fill data if editing
        if self.is_edit:
            self.txt_name.setText(self.leave_type_data.get("name", ""))
            self.txt_name_kh.setText(self.leave_type_data.get("name_kh", ""))
            self.txt_code.setText(self.leave_type_data.get("code", ""))
            mode = self.leave_type_data.get("mode", "")
            if mode:
                idx = self.cb_mode.findText(mode)
                if idx >= 0:
                    self.cb_mode.setCurrentIndex(idx)
                else:
                    self.cb_mode.addItem(mode)
                    self.cb_mode.setCurrentText(mode)
            val = self.leave_type_data.get("validation", "")
            if val:
                idx = self.cb_validation.findText(val)
                if idx >= 0:
                    self.cb_validation.setCurrentIndex(idx)
                else:
                    self.cb_validation.addItem(val)
                    self.cb_validation.setCurrentText(val)

        layout.addSpacing(6)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.addStretch()

        btn_cancel = QPushButton("បោះបង់ (Cancel)")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                padding: 8px 18px;
                border-radius: 8px;
                border: 1px solid #CBD5E1;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("💾 រក្សាទុក (Save)")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #5648A6;
                color: #FFFFFF;
                padding: 8px 22px;
                border-radius: 8px;
                font-weight: 700;
                border: none;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        btn_save.clicked.connect(self.save)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def save(self):
        name = self.txt_name.text().strip()
        name_kh = self.txt_name_kh.text().strip()
        code = self.txt_code.text().strip().upper()
        mode = self.cb_mode.currentText()
        validation = self.cb_validation.currentText()

        if not name:
            QMessageBox.warning(self, "ខ្វះទិន្នន័យ", "សូមបញ្ចូលឈ្មោះប្រភេទច្បាប់ជាភាសាអង់គ្លេស!")
            self.txt_name.setFocus()
            return

        if not name_kh:
            QMessageBox.warning(self, "ខ្វះទិន្នន័យ", "សូមបញ្ចូលឈ្មោះប្រភេទច្បាប់ជាភាសាខ្មែរ!")
            self.txt_name_kh.setFocus()
            return

        if not code:
            QMessageBox.warning(self, "ខ្វះទិន្នន័យ", "សូមបញ្ចូលអក្សរកាត់កូដ (Code)!")
            self.txt_code.setFocus()
            return

        if self.is_edit:
            type_id = self.leave_type_data["id"]
            database.update_leave_type(type_id, name, name_kh, code, mode, validation)
            QMessageBox.information(self, "ជោគជ័យ", "បានកែប្រែប្រភេទច្បាប់ដោយជោគជ័យ!")
        else:
            database.add_leave_type(name, name_kh, code, mode, validation)
            QMessageBox.information(self, "ជោគជ័យ", "បានបង្កើតប្រភេទច្បាប់ថ្មីដោយជោគជ័យ!")

        self.accept()
