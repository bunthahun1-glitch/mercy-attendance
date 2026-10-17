"""
Metric / KPI Card Component matching Click HR purple dashboard cards.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal

class StatCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, title, value, icon_text="📊", bg_color="#5648A6", parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setMinimumSize(140, 78)
        self.setFixedHeight(82)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("ចុចដើម្បីមើលព័ត៌មានលម្អិត / Click to view details")
        self.setStyleSheet(f"""
            QFrame#kpiCard {{
                background-color: {bg_color};
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }}
            QFrame#kpiCard:hover {{
                background-color: #6858C2;
                border: 1.5px solid rgba(255, 255, 255, 0.5);
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        # Top row: icon and value
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel(icon_text)
        self.icon_label.setStyleSheet("font-size: 15px; color: #FFFFFF; background-color: rgba(255, 255, 255, 0.2); border-radius: 6px; padding: 2px 5px;")
        top_layout.addWidget(self.icon_label)

        top_layout.addStretch()

        self.val_label = QLabel(str(value))
        self.val_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF; background: transparent;")
        top_layout.addWidget(self.val_label)

        layout.addLayout(top_layout)

        # Bottom row: title
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 11.5px; font-weight: 700; color: #FFFFFF; background: transparent;")
        layout.addWidget(self.title_label)

    def update_value(self, new_val):
        self.val_label.setText(str(new_val))

    def update_title(self, new_title):
        self.title_label.setText(new_title)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
