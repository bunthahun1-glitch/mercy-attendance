"""
Custom QPainter Donut / Pie Chart for Department Breakdown
Faithful to Click HR screenshot IMG_7444 with clean anti-aliasing and responsive legend.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
import math

class PieChartCanvas(QWidget):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setMinimumSize(50, 50)
        self.data = data or []

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = sum(d["emp_count"] for d in self.data)
        if total == 0:
            total = 1

        w = self.width()
        h = self.height()
        size = min(w, h) - 14
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)

        start_angle = 90.0 * 16.0

        for item in self.data:
            count = item.get("emp_count", 0)
            if count == 0:
                continue
            span_angle = (count / total) * 360.0 * 16.0
            color = QColor(item.get("color", "#6366F1"))

            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.setBrush(QBrush(color))
            painter.drawPie(rect, int(start_angle), int(-span_angle))

            # Draw percentage label
            pct = (count / total) * 100
            if pct > 8.0:
                mid_angle_deg = (start_angle - (span_angle / 2)) / 16.0
                rad = math.radians(mid_angle_deg)
                radius = size / 2 * 0.70
                center_x = w / 2
                center_y = h / 2
                px = center_x + radius * math.cos(rad)
                py = center_y - radius * math.sin(rad)

                painter.setPen(QPen(QColor("#FFFFFF")))
                font = QFont("Segoe UI", 8, QFont.Weight.Bold)
                painter.setFont(font)
                text = f"{pct:.0f}%"
                metrics = painter.fontMetrics()
                tw = metrics.horizontalAdvance(text)
                th = metrics.height()
                painter.drawText(int(px - tw / 2), int(py + th / 4), text)

            start_angle -= span_angle

        # Donut center hole
        inner_size = size * 0.46
        inner_rect = QRectF((w - inner_size) / 2, (h - inner_size) / 2, inner_size, inner_size)
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawEllipse(inner_rect)

        # Center number and label
        painter.setPen(QPen(QColor("#1E293B")))
        font_num = QFont("Segoe UI", 13, QFont.Weight.Bold)
        painter.setFont(font_num)
        sum_str = str(sum(d['emp_count'] for d in self.data))
        m_num = painter.fontMetrics()
        painter.drawText(int(w / 2 - m_num.horizontalAdvance(sum_str) / 2), int(h / 2 + m_num.height() / 4 - 2), sum_str)

        painter.end()


class DepartmentPieChartWidget(QFrame):
    department_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("whiteCard")
        self.setStyleSheet("""
            QFrame#whiteCard {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1.5px solid #CBD5E1;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Title
        self.title_lbl = QLabel("By Departments / តាមផ្នែកការងារ")
        self.title_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #1E293B;")
        layout.addWidget(self.title_lbl)

        # Canvas
        self.canvas = PieChartCanvas()
        layout.addWidget(self.canvas)

        # Grid Legend (Single-column vertical stack for clean narrow display)
        self.legend_frame = QWidget()
        self.legend_grid = QGridLayout(self.legend_frame)
        self.legend_grid.setContentsMargins(0, 4, 0, 0)
        self.legend_grid.setHorizontalSpacing(10)
        self.legend_grid.setVerticalSpacing(4)
        layout.addWidget(self.legend_frame)

    def set_data(self, data, is_khmer=True):
        filtered_data = [d for d in data if d.get("emp_count", 0) > 0]
        self.canvas.set_data(filtered_data)

        # Clear existing
        while self.legend_grid.count():
            child = self.legend_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total_emp = sum(d.get("emp_count", 0) for d in filtered_data) or 1
        for row, item in enumerate(filtered_data):
            cnt = item.get("emp_count", 0)
            pct = (cnt / total_emp) * 100

            item_widget = QFrame()
            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            item_widget.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border-radius: 6px;
                    padding: 1px 3px;
                }
                QFrame:hover {
                    background-color: #F1F5F9;
                }
            """)
            item_h = QHBoxLayout(item_widget)
            item_h.setContentsMargins(2, 1, 2, 1)
            item_h.setSpacing(5)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {item.get('color', '#6366F1')}; font-size: 11px;")
            item_h.addWidget(dot)

            name = item.get("name_kh" if is_khmer else "name", item.get("name", ""))
            lbl = QLabel(f"{name} ({cnt})")
            lbl.setStyleSheet("font-size: 10.5px; color: #334155; font-weight: 600; font-family: 'Kantumruy Pro', 'Khmer OS Siemreap', 'Segoe UI', sans-serif;")
            item_h.addWidget(lbl)

            item_h.addStretch()

            pct_lbl = QLabel(f"{pct:.0f}%")
            pct_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {item.get('color', '#6366F1')};")
            item_h.addWidget(pct_lbl)

            dept_name = item.get("name", "")
            item_widget.mousePressEvent = lambda event, dn=dept_name: self.department_clicked.emit(dn)

            self.legend_grid.addWidget(item_widget, row, 0)
