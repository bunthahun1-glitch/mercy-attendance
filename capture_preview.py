"""
Render preview snapshots of Mercy Dental Care QT6 application.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import database
from main_window import MainWindow

def capture_screens():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    database.init_db()
    window = MainWindow()
    window.resize(1340, 860)
    window.show()

    # Process events to let everything render
    app.processEvents()

    # Capture Dashboard
    window.switch_page(0)
    app.processEvents()
    pix = window.grab()
    pix.save("mercy_dental_dashboard_preview.png")
    print("Saved mercy_dental_dashboard_preview.png")

    # Capture Employees View
    window.switch_page(1)
    app.processEvents()
    pix = window.grab()
    pix.save("mercy_dental_employees_preview.png")
    print("Saved mercy_dental_employees_preview.png")

    # Capture Kiosk View
    window.switch_page(6)
    app.processEvents()
    pix = window.grab()
    pix.save("mercy_dental_kiosk_preview.png")
    print("Saved mercy_dental_kiosk_preview.png")

    window.close()

if __name__ == "__main__":
    capture_screens()
